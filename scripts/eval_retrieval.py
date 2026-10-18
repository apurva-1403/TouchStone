"""Retrieval quality against data/demo_queries.json (test-only answer key).

    python -m scripts.eval_retrieval [--k 8] [--as EMP-046] [-v]

Metrics per query (as the evaluation principal, i.e. no access filtering, unless --as EMP-xxx is given):
  pol@k   governing policy among the top-k records
  prac@5  at least one non-policy evidence record (ticket/email/slack/doc) in the top 5
  rec@k   share of evidence records in the top k
  rec+x   share of evidence records in the top k plus linked-record expansion
"""
import argparse
import json

from app import config
from app.retrieval import retriever


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
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--as", dest="who", default="system", help="employee_id, or system")
    ap.add_argument("-v", action="store_true", help="print top records per query")
    args = ap.parse_args()

    r = retriever()
    principal = resolve_principal(args.who)
    queries = json.loads((config.DATA_DIR / "demo_queries.json").read_text(encoding="utf-8"))
    print(f"mode: {'hybrid (Gemini + BM25)' if r.dense else 'BM25 only'} · k={args.k} · as={args.who}\n")
    print(f"{'id':6} {'type':10} {'pol@k':>5} {'prac@5':>6} {'rec@k':>6} {'rec+x':>6}  query")
    tot = {"pol": 0, "prac": 0, "rec": 0.0, "recx": 0.0}
    for q in queries:
        ev = q["evidence"]
        policies = set(ev["policy_ids"])
        practice = set(ev["tickets"] + ev["emails"] + ev["slack"] + ev["docs"])
        evidence = policies | practice
        res = r.search(q["query"], principal, k=args.k)
        top = [h.chunk.record_id for h in res.hits]
        extra = [h.chunk.record_id for h in res.related]
        pol = bool(policies & set(top))
        prac = bool(practice & set(top[:5]))
        rec = len(evidence & set(top)) / len(evidence)
        recx = len(evidence & set(top + extra)) / len(evidence)
        tot["pol"] += pol
        tot["prac"] += prac
        tot["rec"] += rec
        tot["recx"] += recx
        print(f"{q['query_id']:6} {q['event_type'][:10]:10} {'Y' if pol else '-':>5} {'Y' if prac else '-':>6} "
              f"{rec:6.2f} {recx:6.2f}  {q['query'][:60]}")
        if args.v:
            print("       top:", " ".join(f"{t}{'*' if t in evidence else ''}" for t in top))
            print("       +x :", " ".join(f"{t}{'*' if t in evidence else ''}" for t in extra))
    n = len(queries)
    print(f"\n{'ALL':17} {tot['pol'] / n:5.0%} {tot['prac'] / n:6.0%} {tot['rec'] / n:6.2f} {tot['recx'] / n:6.2f}")


if __name__ == "__main__":
    main()
