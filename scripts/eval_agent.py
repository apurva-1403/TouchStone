"""End-to-end agent evaluation on the demo set (uses demo_queries.json as a TEST-ONLY answer key).

    python -m scripts.eval_agent                 # the 8 demo queries, evaluation principal (sees all)
    python -m scripts.eval_agent --ids DQ-05 DQ-18 --as EMP-046 -v
    python -m scripts.eval_agent --all --no-judge

Per query:
  drift     model reported policy_vs_practice or source_vs_source (policy vs policy counts as drift in the
            dataset, e.g. EVT-058)                          (expected: expected_drift_flag)
  confl     model reported conflicting_resolutions         (expected: expected_conflict_flag)
  pol       governing policy cited
  prec/rec  cited records vs evidence records
  judge     1-5 agreement with expected_answer_summary, scored by JUDGE_MODEL (default: the agent model; test-only)
"""
import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor

from google.genai import types

from app import config, llm
from app.agent import answer_question

# The fast model misjudged nuanced answers (e.g. treated the written policy as ground truth), so judge with the
# agent model. Test-only cost.
JUDGE_MODEL = os.getenv("JUDGE_MODEL", config.AGENT_MODEL)

DEMO_SET = ["DQ-01", "DQ-03", "DQ-05", "DQ-07", "DQ-14", "DQ-18", "DQ-25", "OUTAGE"]

# README demo #8 is not in demo_queries.json; its evidence comes from EVT-021's artifacts.
EXTRA = {
    "OUTAGE": {
        "query_id": "OUTAGE",
        "query": "What caused the March API outage and how was it fixed?",
        "event_type": "incident",
        "expected_drift_flag": False,
        "expected_conflict_flag": False,
        "expected_answer_summary": (
            "Sev1 on 2026-03-17: AlgoWorks Fleet API returned 5xx for ~60% of requests for 47 minutes (14:05-14:52 IST) "
            "after API gateway 4.2.0 changed the PgBouncer pool size from 200 to 50 per pod, exhausting RDS "
            "connections. Fixed by rolling back via ArgoCD; 38 customers affected; postmortem followed."),
        "evidence": {"policy_ids": [], "tickets": ["INC-20256", "INC-20258", "INC-20259", "CHG-20261"],
                     "emails": ["EMAIL-0022", "EMAIL-0021"], "slack": ["SLACK-0054", "SLACK-0055"],
                     "docs": ["DOC-0052"]},
    }
}

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "integer", "description": "1 = contradicts or misses the key facts, 5 = covers all key facts"},
        "missing": {"type": "string", "description": "Key facts from the reference that the answer misses or gets wrong"},
    },
    "required": ["score", "missing"],
}


def judge(question: str, reference: str, answer: str) -> dict:
    prompt = (f"Question: {question}\n\nReference answer (ground truth):\n{reference}\n\nCandidate answer:\n{answer}\n\n"
              "Score how well the candidate agrees with the reference on the key facts (who/what/numbers/dates, and "
              "whether it notices that policy and practice differ when the reference says so). The reference may describe "
              "both the written policy and actual practice; an answer that reports both and says which is followed now "
              "agrees with it. Extra correct detail is fine. Citation markers like [1] are fine.")
    r = llm.client().models.generate_content(
        model=JUDGE_MODEL, contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json", response_json_schema=JUDGE_SCHEMA))
    return json.loads(r.text)


def run_one(q: dict, principal, use_judge: bool) -> dict:
    try:
        return _run_one(q, principal, use_judge)
    except Exception as e:  # one failed query shouldn't sink the whole run
        return {"id": q["query_id"], "query": q["query"], "error": str(e)[:200]}


def _run_one(q: dict, principal, use_judge: bool) -> dict:
    r = answer_question(q["query"], principal)
    ev = q["evidence"]
    policies = set(ev["policy_ids"])
    evidence = policies | set(ev["tickets"] + ev["emails"] + ev["slack"] + ev["docs"])
    cited = {c.record_id for c in r.citations}
    kinds = {c.kind for c in r.conflicts}
    row = {
        "id": q["query_id"],
        "query": q["query"],
        "drift": bool(kinds & {"policy_vs_practice", "source_vs_source"}),
        "drift_exp": q["expected_drift_flag"],
        "confl": "conflicting_resolutions" in kinds,
        "confl_exp": q["expected_conflict_flag"],
        "pol": bool(policies & cited) if policies else None,
        "prec": len(cited & evidence) / len(cited) if cited else 0.0,
        "rec": len(cited & evidence) / len(evidence) if evidence else 0.0,
        "latency": r.meta.latency_s,
        "tools": len(r.trace),
        "timing": {"model": r.meta.model_call_secs, "tools": r.meta.tool_secs},
        "response": r.model_dump(),
    }
    if use_judge:
        callouts = [f"CONFLICT ({c.kind}): {c.summary}" for c in r.conflicts]
        callouts += [f"POSSIBLY OUT OF DATE {s.record_id}: {s.reason}" for s in r.staleness]
        shown = r.answer + ("\n\nCallouts shown with the answer:\n" + "\n".join(callouts) if callouts else "")
        row["judge"] = judge(q["query"], q["expected_answer_summary"], shown)
    return row


def resolve_principal(who: str):
    """--as value -> Principal. "system" (default) sees every record: measures quality on the full corpus."""
    from app.access import SYSTEM, principal_for
    if who.lower() == "system":
        return SYSTEM
    p = principal_for(who.upper())
    if not p:
        raise SystemExit(f"{who}: unknown employee, or they have left and can't sign in")
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="*", help="query ids (default: the 8-query demo set)")
    ap.add_argument("--all", action="store_true", help="all 27 demo queries")
    ap.add_argument("--as", dest="who", default="system", help="employee_id, or system")
    ap.add_argument("--no-judge", action="store_true")
    ap.add_argument("--workers", type=int, default=2, help="parallel questions (higher risks 429 quota errors)")
    ap.add_argument("--repeat", type=int, default=1, help="run each question N times (stability check)")
    ap.add_argument("--out", help="write full results JSON here")
    ap.add_argument("-v", action="store_true", help="print each answer")
    args = ap.parse_args()

    bank = {q["query_id"]: q for q in json.loads((config.DATA_DIR / "demo_queries.json").read_text(encoding="utf-8"))}
    bank.update(EXTRA)
    ids = list(bank) if args.all else (args.ids or DEMO_SET)
    queries = [bank[i] for i in ids] * args.repeat
    principal = resolve_principal(args.who)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda q: run_one(q, principal, not args.no_judge), queries))
    failed = [r for r in results if "error" in r]
    rows = [r for r in results if "error" not in r]
    for f in failed:
        print(f"FAILED {f['id']}: {f['error']}")

    ok = lambda got, exp: "ok" if got == exp else ("MISS" if exp else "FP")
    print(f"model={config.AGENT_MODEL} thinking={config.AGENT_THINKING} as={args.who}\n")
    print(f"{'id':7} {'drift':6} {'confl':6} {'pol':4} {'prec':>5} {'rec':>5} {'judge':>5} {'secs':>5} {'tools':>5}  query")
    for r in rows:
        pol = "-" if r["pol"] is None else ("Y" if r["pol"] else "N")
        j = r.get("judge", {}).get("score", "")
        print(f"{r['id']:7} {ok(r['drift'], r['drift_exp']):6} {ok(r['confl'], r['confl_exp']):6} {pol:4} "
              f"{r['prec']:5.2f} {r['rec']:5.2f} {j!s:>5} {r['latency']:5.1f} {r['tools']:5}  {r['query'][:55]}")
    n = len(rows)
    flags_ok = sum((r["drift"] == r["drift_exp"]) and (r["confl"] == r["confl_exp"]) for r in rows)
    pol_rows = [r for r in rows if r["pol"] is not None]
    judged = [r["judge"]["score"] for r in rows if "judge" in r]
    print(f"\nflags correct {flags_ok}/{n} · policy cited {sum(r['pol'] for r in pol_rows)}/{len(pol_rows)} · "
          f"precision {sum(r['prec'] for r in rows) / n:.2f} · recall {sum(r['rec'] for r in rows) / n:.2f} · "
          + (f"judge {sum(judged) / len(judged):.1f}/5 · " if judged else "")
          + f"median latency {sorted(r['latency'] for r in rows)[n // 2]:.1f}s")

    if args.repeat > 1:
        print("\nstability (runs with both flags correct / judge scores):")
        for qid in ids:
            rs = [r for r in rows if r["id"] == qid]
            good = sum((r["drift"] == r["drift_exp"]) and (r["confl"] == r["confl_exp"]) for r in rs)
            js = [r["judge"]["score"] for r in rs if "judge" in r]
            print(f"  {qid:7} {good}/{len(rs)}  judge {js}  secs {[r['latency'] for r in rs]}")
    if args.v:
        for r in rows:
            print(f"\n=== {r['id']}: {r['query']}\n{r['response']['answer']}")
            if "judge" in r:
                print(f"--- judge {r['judge']['score']}/5: {r['judge']['missing']}")
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=1)


if __name__ == "__main__":
    main()
