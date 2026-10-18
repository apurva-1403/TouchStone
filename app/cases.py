"""Similar-case comparison: did past tickets about the same issue get the same answer?

Retrieval groups similar tickets deterministically (retrieval.Retriever._case_groups). This module asks the
fast model (FAST_MODEL, a second, cheaper Gemini) to compare each group, so "same request, different outcome"
is detected by the pipeline instead of depending on the agent model noticing it.
"""
import json
import re
from concurrent.futures import ThreadPoolExecutor, wait

from google.genai import types

from app import config, llm
from app.kb import directory
from app.schema import Chunk

RESOLUTION_CHARS = 450
COMPARE_BUDGET_S = 4.0  # the comparison is an aid: past this, return the search without it (usually 1-2.5 s)

COMPARE_SCHEMA = {
    "type": "object",
    "properties": {
        "same_issue": {"type": "boolean",
                       "description": "True only if the cases are about the same problem or the same kind of request."},
        "same_outcome": {"type": "boolean",
                         "description": "True if they were answered/resolved the same way (same rule, fix or decision)."},
        "difference": {"type": "string",
                       "description": "If outcomes differ: one sentence naming each case ID, its date and what it got. Else empty."},
        "current_answer": {"type": "string",
                           "description": "Which case reflects the current handling and why (e.g. latest, or cites the newer policy)."},
        "still_open": {"type": "boolean", "description": "True if the latest case is unresolved or the problem recurred."},
    },
    "required": ["same_issue", "same_outcome", "difference", "current_answer", "still_open"],
}


def _resolution(text: str) -> str:
    m = re.search(r"\nResolution: (.*?)(?:\nWork notes:|\Z)", text, re.S)
    return m.group(1).strip() if m else ""


def case_summary(c: Chunk) -> dict:
    d = directory()
    handler = c.owner_employee_ids[0] if c.owner_employee_ids else None
    res = _resolution(c.text)
    return {
        "record_id": c.record_id,
        "date": c.created_date,
        "subject": c.title,
        "status": c.status,
        "handled_by": d.name(handler) if handler else None,
        "resolution": (res[:RESOLUTION_CHARS] + " …") if len(res) > RESOLUTION_CHARS else (res or "(no resolution recorded)"),
    }


def compare(question: str, cases: list[dict]) -> dict:
    prompt = (
        f"An employee asked: {question}\n\nPast ServiceNow tickets that look similar (oldest first):\n"
        + json.dumps(cases, indent=1, ensure_ascii=False)
        + "\n\nCompare them. Are they the same issue? If so, were they handled the same way? Compare what the "
          "employee would need to know: the answer or rule given, the fix applied, who handled it and through "
          "which route, and how long it took. These all count as DIFFERENT outcomes: different answers to the same "
          "question; different fixes for the same problem; one request granted while a comparable one was denied or "
          "put on hold; the same request handled by different teams or routed differently; very different "
          "turnaround. Ending in the same final state does not make the handling the same. But if the tickets "
          "themselves record why they differed (e.g. stock was available in one case, or the requests asked for "
          "different things), the handling was consistent: set same_outcome true and give that reason in "
          "current_answer. Be literal and use only these tickets."
    )
    try:
        r = llm.client().models.generate_content(
            model=config.FAST_MODEL, contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json",
                                               response_json_schema=COMPARE_SCHEMA, temperature=0.0))
        return json.loads(r.text)
    except Exception as e:  # comparison is an aid; never fail the search because of it
        return {"error": f"comparison unavailable: {str(e)[:80]}"}


def compare_groups(question: str, groups: list[list[Chunk]]) -> list[dict]:
    """Returns only groups the fast model judged to be the same issue, each with its comparison."""
    summaries = [[case_summary(c) for c in g] for g in groups]
    pool = ThreadPoolExecutor(max_workers=max(1, len(groups)))
    futures = [pool.submit(compare, question, cs) for cs in summaries]
    wait(futures, timeout=COMPARE_BUDGET_S)
    pool.shutdown(wait=False, cancel_futures=True)  # don't block on a slow comparison
    verdicts = [f.result() if f.done() else {"error": "comparison timed out"} for f in futures]
    out = []
    for cases, v in zip(summaries, verdicts):
        if "error" in v or v.get("same_issue"):
            out.append({"cases": cases, "comparison": v})
    return out
