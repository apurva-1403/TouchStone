"""The TouchStone agent: a Gemini function-calling loop over AgentTools, ending in submit_answer.

The model's answer is not trusted as-is. Post-validation in code:
- citations must point to records a tool actually returned for this user (others are dropped);
- conflict record IDs are filtered the same way;
- staleness flags are added from ingest-time signals for cited policies/docs the model didn't flag;
- the fallback contact must be an active employee (else re-routed up the manager chain);
- an access note is added when confidential records were withheld from the search.
"""
import json
import re
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

from google.genai import types

from app import config, llm
from app.kb import directory
from app.access import Principal, access_basis
from app.schema import (AgentResponse, AnswerMeta, Citation, Conflict, Fallback,
                        StalenessFlag, ToolCall)
from app.tools import DECLARATIONS, AgentTools

MAX_TOOL_CALLS = 3  # research calls per question (submit_answer not counted)
MAX_MODEL_CALLS = 5  # hard stop on model round-trips

SYSTEM_PROMPT = """You are TouchStone, the knowledge assistant for employees of AlgoWorks (a fleet-management \
SaaS company in India and Singapore). Today is {today}. You are answering {persona}. Tools only return records \
this employee may see; confidential records are need-to-know.

Sources are policies, Confluence pages, ServiceNow tickets, emails and Slack. A written policy is NOT automatically \
current: tickets, emails and Slack often show that practice has moved on.

Research (be quick: at most {max_calls} more tool calls; usually none are needed):
1. The first search_docs results come with the question. They already include linked records, staleness signals and similar_past_cases.
2. Only if something important is missing, make ONE more call (another search, get_record or get_related). Request \
independent lookups together in the same turn.
3. similar_past_cases with same_outcome false means the same question was answered differently before: report a \
conflicting_resolutions conflict. For "can X get / who approves / has this been solved" questions, check how \
comparable past cases were actually decided; an old outcome still in effect matters.
4. People in results are active unless listed as no longer active. Never point anyone to a person who left or is on leave.

Answer (call submit_answer once). The reader wants a quick, simple answer:
- At most 90 words. Start with the direct answer in one plain sentence. Then at most 3 short bullets with the key \
specifics (approver, number, step, date). No headings, no long explanations, no jargon.
- Cite facts inline with record IDs in square brackets, e.g. [POL-01] or [RITM-20538]. Only cite IDs tools returned.
- Do NOT name people to contact or list sources in the answer text; put the contact in fallback (an active \
employee_id) and the app shows sources and contacts at the end.
- If policy and practice disagree, say so in ONE sentence ("The policy says X, but in practice Y since <date>."), \
add a policy_vs_practice conflict and list the policy in stale_sources. Same for conflicting_resolutions or \
source_vs_source. Do not invent conflicts; only report one if it changes the answer to what was asked.
- If evidence is thin, say what you don't know in one sentence, set confidence low and set fallback.
- If restricted records were withheld, don't guess their content."""


def _thinking_config(model: str) -> types.ThinkingConfig:
    """Gemini 2.x takes a thinking token budget; Gemini 3.x takes a thinking level."""
    if model.startswith("gemini-2"):
        return types.ThinkingConfig(thinking_budget=config.AGENT_THINKING_BUDGET)
    return types.ThinkingConfig(thinking_level=config.AGENT_THINKING)


_hedge_pool = ThreadPoolExecutor(max_workers=16)


def _hedged_call(contents: list, cfg: types.GenerateContentConfig) -> tuple[str, types.GenerateContentResponse]:
    """Primary model first; if it hasn't answered within HEDGE_AFTER_S (or fails), the fallback model gets the
    same request and the first successful answer wins. Returns (model that answered, response)."""
    def call(model: str):
        c = cfg.model_copy(update={"thinking_config": _thinking_config(model)})
        return model, llm.client().models.generate_content(model=model, contents=contents, config=c)

    primary = _hedge_pool.submit(call, config.AGENT_MODEL)
    done, _ = wait([primary], timeout=config.HEDGE_AFTER_S)
    if done and primary.exception() is None:
        return primary.result()
    pending = {primary, _hedge_pool.submit(call, config.FALLBACK_MODEL)} - ({primary} if done else set())
    while pending:
        done, pending = wait(pending, return_when=FIRST_COMPLETED)
        for f in done:
            if f.exception() is None:
                return f.result()
    raise RuntimeError("Both the primary and the fallback model failed to answer.")


def _persona_line(p: Principal) -> str:
    if p.is_system:
        return "an evaluator with access to every record"
    return f"{p.name} ({p.employee_id}), {p.title}, {directory().departments[p.department_id]['name']}"


def _summarise(name: str, out: dict) -> str:
    if "error" in out:
        return out["error"]
    if name == "search_docs":
        s = f"{len(out['results'])} results, {len(out['linked_records'])} linked"
        groups = out.get("similar_past_cases", [])
        if groups:
            differ = sum(1 for g in groups if g["comparison"].get("same_outcome") is False)
            s += f", {len(groups)} similar-case group(s)" + (f" ({differ} with different outcomes)" if differ else "")
        w = out.get("restricted_records_withheld")
        return s + (f", {w['count']} restricted withheld" if w else "")
    if name == "get_related":
        return f"{len(out['related'])} related records"
    if name == "get_record":
        return out["title"]
    if name == "lookup_person":
        return ", ".join(f"{p['name']} ({p['status']})" for p in out["people"])
    if name == "find_owner":
        return ", ".join(x.get("owner_team", "") for x in out.get("systems", [out]))
    return "ok"


_CITE = re.compile(r"\[((?:[A-Z]{2,5}-\d{2,6})(?:\s*[,;]\s*[A-Z]{2,5}-\d{2,6})*)\]")


def _number_citations(answer: str, seen: dict) -> tuple[str, list[str], list[str]]:
    """Rewrites [ID] / [ID, ID] markers to [1][2], in order of first appearance. Unknown IDs are dropped."""
    order, dropped = [], []

    def repl(m):
        out = ""
        for rid in re.split(r"\s*[,;]\s*", m.group(1)):
            if rid in seen:
                if rid not in order:
                    order.append(rid)
                out += f"[{order.index(rid) + 1}]"
            elif rid not in dropped:
                dropped.append(rid)
        return out

    return _CITE.sub(repl, answer), order, dropped


def _signal_reasons(c) -> list[str]:
    s, d = c.signals, directory()
    reasons = []
    if s.inactive_people_mentioned:
        people = ", ".join(f"{d.name(p)} ({d.employees[p]['status'].replace('_', ' ')})" for p in s.inactive_people_mentioned)
        reasons.append(f"names people no longer active: {people}")
    if s.owners_inactive:
        reasons.append("owner no longer active: " + ", ".join(d.name(p) for p in s.owners_inactive))
    if s.open_update_request_ids:
        reasons.append("open update request " + ", ".join(s.open_update_request_ids))
    if reasons:
        reasons.append(f"last updated {c.last_updated} ({s.days_since_update} days ago)")
    return reasons


def _finalise(args: dict, tools: AgentTools) -> tuple[AgentResponse, list[str]]:
    d = directory()
    seen = tools.seen
    answer, order, dropped = _number_citations(args.get("answer", "").strip(), seen)

    citations = [
        Citation(n=i + 1, chunk_id=seen[rid].chunk_id, record_id=rid, title=seen[rid].title,
                 source_system=seen[rid].source_system, date=seen[rid].last_updated,
                 confidential=seen[rid].confidential,
                 access_basis=access_basis(tools.principal, seen[rid]) if seen[rid].confidential else None)
        for i, rid in enumerate(order)
    ]

    conflicts = []
    for c in args.get("conflicts") or []:
        ids = [r for r in c.get("record_ids", []) if r in seen]
        if len(ids) >= 1 and c.get("summary"):
            cv = c.get("current_view") or None
            conflicts.append(Conflict(kind=c["kind"], summary=c["summary"], record_ids=ids,
                                      current_view=cv if cv in seen else None))

    staleness = {s["record_id"]: StalenessFlag(**s) for s in args.get("stale_sources") or [] if s.get("record_id") in seen}
    for rid in order:  # add signal-based flags for cited policies/docs the model didn't flag
        c = seen[rid]
        if c.source_type in ("policy", "confluence") and rid not in staleness:
            reasons = _signal_reasons(c)
            if reasons:
                staleness[rid] = StalenessFlag(record_id=rid, reason="; ".join(reasons))

    fb = args.get("fallback") or {}
    fallback = Fallback(needed=bool(fb.get("needed")), reason=fb.get("reason") or None)
    contact = (fb.get("contact_employee_id") or "").strip().upper()
    if contact in d.employees:
        active = d.active_contact_for(contact)
        if active:
            e = d.employees[active]
            fallback.contact_employee_id, fallback.contact_name, fallback.contact_role = active, e["name"], e["role"]
            if active != contact:
                fallback.reason = (f"{d.name(contact)} is no longer active; routed to {e['name']}. "
                                   + (fallback.reason or ""))

    access_note = None
    if tools.withheld_count:
        # Contacts are ordered by how well the withheld records matched; the top one is the relevant data owner.
        who = ", ".join(f"{d.name(e)} ({d.employees[e]['role']})" for e in tools.withheld_contacts[:1])
        access_note = (f"{tools.withheld_count} confidential record(s) relevant to this question are not available "
                       f"to you." + (f" To request access, contact {who}." if who else ""))

    return AgentResponse(answer=answer, citations=citations, conflicts=conflicts,
                         staleness=list(staleness.values()), fallback=fallback, access_note=access_note), dropped


def answer_question(question: str, principal: Principal, history: list[dict] | None = None) -> AgentResponse:
    started = time.perf_counter()
    tools = AgentTools(principal, question)
    system = SYSTEM_PROMPT.format(today=config.TODAY.isoformat(), persona=_persona_line(principal),
                                  max_calls=MAX_TOOL_CALLS - 1)  # the first search is done for the model
    contents: list[types.Content] = []
    for turn in history or []:
        contents.append(types.Content(role="user", parts=[types.Part(text=turn["question"])]))
        contents.append(types.Content(role="model", parts=[types.Part(text=turn["answer"])]))
    trace: list[ToolCall] = []
    tool_calls = model_calls = tokens_in = tokens_out = 0
    call_secs: list[float] = []
    tool_secs = 0.0
    final: dict | None = None
    nudged = False

    # Pre-retrieval: every question starts with a search anyway, so run it before the first model call and hand
    # the results over. Saves a full model round trip (the one that would only decide to search).
    t0 = time.perf_counter()
    first = tools.search_docs(question)
    tool_secs += time.perf_counter() - t0
    tool_calls += 1
    trace.append(ToolCall(tool="search_docs", args={"query": question}, summary=_summarise("search_docs", first),
                          secs=round(time.perf_counter() - t0, 1)))
    contents.append(types.Content(role="user", parts=[types.Part(text=(
        f"{question}\n\n[search_docs results for this question, already retrieved. Answer from them; call more tools "
        f"only if something important is missing.]\n{json.dumps(first, ensure_ascii=False)}"))]))

    model = config.AGENT_MODEL
    while final is None and model_calls < MAX_MODEL_CALLS:
        must_submit = tool_calls >= MAX_TOOL_CALLS or model_calls == MAX_MODEL_CALLS - 1
        cfg = types.GenerateContentConfig(
            system_instruction=system,
            tools=[types.Tool(function_declarations=DECLARATIONS)],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            thinking_config=_thinking_config(model),
            tool_config=types.ToolConfig(function_calling_config=types.FunctionCallingConfig(
                mode="ANY", allowed_function_names=["submit_answer"]) if must_submit else
                types.FunctionCallingConfig(mode="AUTO")),
        )
        t0 = time.perf_counter()
        if model == config.AGENT_MODEL and config.FALLBACK_MODEL:
            model, resp = _hedged_call(contents, cfg)
        else:
            resp = llm.client().models.generate_content(model=model, contents=contents, config=cfg)
        call_secs.append(round(time.perf_counter() - t0, 1))
        model_calls += 1
        if resp.usage_metadata:
            tokens_in += resp.usage_metadata.prompt_token_count or 0
            tokens_out += (resp.usage_metadata.candidates_token_count or 0) + (resp.usage_metadata.thoughts_token_count or 0)
        if not resp.candidates or not resp.candidates[0].content:
            break
        contents.append(resp.candidates[0].content)

        calls = resp.function_calls or []
        if not calls:
            text = "".join(p.text or "" for p in resp.candidates[0].content.parts or [] if not p.thought)
            if nudged or not text.strip():
                final = {"answer": text, "confidence": "low"}
            else:
                nudged = True
                contents.append(types.Content(role="user", parts=[types.Part(
                    text="Now call submit_answer with your final answer in the required structure.")]))
            continue

        responses = []
        for fc in calls:
            args = dict(fc.args or {})
            if fc.name == "submit_answer":
                final = args
                break
            t0 = time.perf_counter()
            out = tools.call(fc.name, args)
            dt = time.perf_counter() - t0
            tool_secs += dt
            tool_calls += 1
            trace.append(ToolCall(tool=fc.name, args=args, summary=_summarise(fc.name, out), secs=round(dt, 1)))
            responses.append(types.Part.from_function_response(name=fc.name, response={"result": out}))
        if final is None and responses:
            contents.append(types.Content(role="user", parts=responses))

    if final is None:
        final = {"answer": "I couldn't finish researching this question. Please try rephrasing it.", "confidence": "low"}

    result, dropped = _finalise(final, tools)
    result.trace = trace
    result.meta = AnswerMeta(model=model, user_id=principal.employee_id, confidence=final.get("confidence") or "low",
                             latency_s=round(time.perf_counter() - started, 1), model_calls=model_calls,
                             input_tokens=tokens_in, output_tokens=tokens_out, dropped_citations=dropped,
                             model_call_secs=call_secs, tool_secs=round(tool_secs, 1),
                             retrieved_record_ids=sorted(tools.seen))
    return result
