"""Re-validate data/*.json without rebuilding (the handover's "every foreign key resolves" checklist).

    python generate/validate.py

Exit code 0 = clean. Prints every problem found. Safe to run after hand-editing the JSON.
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
SIM_TODAY = dt.date(2026, 9, 24)
EXPECTED = {"departments": 9, "employees": 1001, "teams": 63, "systems": 30, "projects": 24, "policies": 36, "events": 80}
EXPECTED_TYPES = {"access_request": 20, "incident": 16, "project_decision": 13, "policy_drift": 13,
                  "contradictory_resolution": 8, "routine_baseline": 10}
SOURCE = {"tickets": ("ticket", "servicenow"), "emails": ("email", "outlook"), "slack": ("slack", "slack"),
          "confluence": ("confluence", "confluence"), "policies": ("policy", "confluence")}
ID_FIELD = {"tickets": "ticket_id", "emails": "thread_id", "slack": "conversation_id", "confluence": "doc_id", "policies": "policy_id"}


def load(name):
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


def main() -> int:
    problems = []

    def chk(cond, msg):
        if not cond:
            problems.append(msg)

    departments, employees, teams = load("departments"), load("employees"), load("teams")
    systems, projects, policies, events = load("systems"), load("projects"), load("policies"), load("events")
    tickets, emails, slack, docs = load("tickets"), load("emails"), load("slack"), load("confluence")
    entity_colls = {"departments": departments, "employees": employees, "teams": teams, "systems": systems,
                    "projects": projects, "policies": policies, "events": events}

    for name, n in EXPECTED.items():
        chk(len(entity_colls[name]) == n, f"{name}: expected {n}, found {len(entity_colls[name])}")

    dept = {d["department_id"]: d for d in departments}
    emp = {e["employee_id"]: e for e in employees}
    team = {t["team_id"]: t for t in teams}
    sysm = {s["system_id"] for s in systems}
    proj = {p["project_id"] for p in projects}
    pol = {p["policy_id"]: p for p in policies}
    ev = {e["event_id"]: e for e in events}

    # --- org graph
    for d in departments:
        chk(d["head_employee_id"] in emp, f"{d['department_id']}: head missing")
    for e in employees:
        chk(e["department_id"] in dept, f"{e['employee_id']}: department missing")
        chk(e["team_id"] in team, f"{e['employee_id']}: team missing")
        if e["manager_id"] is None:
            chk(e["tier"] == "head", f"{e['employee_id']}: no manager but tier {e['tier']}")
        else:
            chk(e["manager_id"] in emp, f"{e['employee_id']}: manager missing")
        if e["status"] != "exited":
            chk(e["employee_id"] in team[e["team_id"]]["member_employee_ids"], f"{e['employee_id']}: not in team member list")
    for t in teams:
        chk(t["department_id"] in dept, f"{t['team_id']}: department missing")
        chk(t["lead_employee_id"] in t["member_employee_ids"], f"{t['team_id']}: lead not a member")
        for m in t["member_employee_ids"]:
            chk(m in emp and emp[m]["team_id"] == t["team_id"], f"{t['team_id']}: member {m} inconsistent")
    for s in systems:
        chk(s["owner_team_id"] in team, f"{s['system_id']}: owner team missing")
    for p in projects:
        chk(p["team_id"] in team, f"{p['project_id']}: team missing")
        chk(all(x in emp for x in p["staffed_employee_ids"]), f"{p['project_id']}: staff missing")
        chk(all(x in sysm for x in p["related_system_ids"]), f"{p['project_id']}: system missing")
    for p in policies:
        chk(p["owner_department_id"] in dept, f"{p['policy_id']}: owner dept missing")
        chk(all(x in sysm for x in p["related_system_ids"]), f"{p['policy_id']}: system missing")
        age = (SIM_TODAY - dt.date.fromisoformat(p["last_updated"])).days
        chk(p["is_stale_by_design"] == (age >= 180), f"{p['policy_id']}: stale flag inconsistent with age {age}d")

    # --- events
    dist = collections.Counter(e["type"] for e in events)
    for k, v in EXPECTED_TYPES.items():
        chk(dist.get(k, 0) == v, f"event type {k}: expected {v}, found {dist.get(k, 0)}")
    for e in events:
        chk(all(x in emp for x in e["involved_employee_ids"]), f"{e['event_id']}: employee missing")
        chk(e["team_id"] in team, f"{e['event_id']}: team missing")
        chk(e["related_system_id"] is None or e["related_system_id"] in sysm, f"{e['event_id']}: system missing")
        chk(e["related_policy_id"] is None or e["related_policy_id"] in pol, f"{e['event_id']}: policy missing")
        chk(e["related_project_id"] is None or e["related_project_id"] in proj, f"{e['event_id']}: project missing")
        chk(all(x in ev for x in e["related_event_ids"]), f"{e['event_id']}: related event missing")
        if e["is_drift_scenario"]:
            chk(e["related_policy_id"] and pol[e["related_policy_id"]]["is_stale_by_design"], f"{e['event_id']}: drift without stale policy")
        chk(sum(len(v) for v in e["artifact_ids"].values()) >= 2, f"{e['event_id']}: fewer than 2 artifacts")

    # --- artifacts
    def active(pid, date, where):
        p = emp.get(pid)
        if p is None:
            problems.append(f"{where}: employee {pid} missing")
        elif date < p["join_date"] or (p.get("exit_date") and date > p["exit_date"]):
            problems.append(f"{where}: {p['name']} not employed on {date}")

    back = {k: collections.defaultdict(list) for k in ("tickets", "emails", "slack", "docs")}
    all_ids = set(pol) | set(ev) | proj | sysm
    for coll_name, coll in (("tickets", tickets), ("emails", emails), ("slack", slack), ("confluence", docs), ("policies", policies)):
        idf = ID_FIELD[coll_name]
        st, ss = SOURCE[coll_name]
        seen = set()
        for r in coll:
            rid = r[idf]
            chk(rid not in seen, f"duplicate id {rid}"); seen.add(rid); all_ids.add(rid)
            md = r["metadata"]
            chk(md["source_type"] == st and md["source_system"] == ss, f"{rid}: wrong source_type/system")
            chk(md["department"] in dept, f"{rid}: metadata department invalid")
            chk(md["sensitivity"] in ("public", "internal", "restricted"), f"{rid}: sensitivity invalid")
            chk(md["last_referenced_date"] >= md["created_date"], f"{rid}: last_referenced before created")
            chk("{{" not in json.dumps(r), f"{rid}: unresolved placeholder")
            if coll_name != "policies":
                chk(r["event_id"] is None or r["event_id"] in ev, f"{rid}: event missing")
    for t in tickets:
        active(t["requester_employee_id"], t["created_date"], t["ticket_id"])
        active(t["assigned_to_employee_id"], t["created_date"], t["ticket_id"])
        chk(t["ticket_id"].split("-")[0] == {"request": "RITM", "incident": "INC", "change": "CHG"}[t["ticket_type"]], f"{t['ticket_id']}: prefix/type mismatch")
        if t["event_id"]:
            back["tickets"][t["event_id"]].append(t["ticket_id"])
    for m in emails:
        for x in m["messages"]:
            active(x["from_employee_id"], x["date"][:10], m["thread_id"])
        if m["event_id"]:
            back["emails"][m["event_id"]].append(m["thread_id"])
    for s in slack:
        for x in s["messages"]:
            active(x["employee_id"], x["ts"][:10], s["conversation_id"])
        if s["event_id"]:
            back["slack"][s["event_id"]].append(s["conversation_id"])
    for d in docs:
        for a in d["author_employee_ids"]:
            active(a, d["created_date"], d["doc_id"])
        chk(all(x in ev for x in d["related_event_ids"]), f"{d['doc_id']}: related event missing")
        if d["event_id"]:
            back["docs"][d["event_id"]].append(d["doc_id"])
    for e in events:
        for k in ("tickets", "emails", "slack", "docs"):
            chk(sorted(e["artifact_ids"][k]) == sorted(back[k].get(e["event_id"], [])), f"{e['event_id']}: artifact_ids.{k} out of sync with artifacts")
    for coll in (tickets, emails, slack, docs):
        for r in coll:
            for rid in r["referenced_ids"]:
                chk(rid in all_ids, f"{r.get('ticket_id') or r.get('thread_id') or r.get('conversation_id') or r.get('doc_id')}: dangling reference {rid}")

    counts = {"tickets": len(tickets), "emails": len(emails), "slack": len(slack), "confluence": len(docs)}
    if problems:
        print(f"FAILED - {len(problems)} problem(s):")
        for p in problems:
            print("  -", p)
        return 1
    print("OK - all foreign keys resolve; counts:", {**{k: len(v) for k, v in entity_colls.items()}, **counts})
    return 0


if __name__ == "__main__":
    sys.exit(main())
