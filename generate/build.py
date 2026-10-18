"""Build the AlgoWorks synthetic enterprise dataset.

Runs Layers 0-7 in strict order, resolves every by-name reference to an ID (failing loudly on a miss),
assigns artifact IDs, resolves cross-artifact placeholders, attaches cross-cutting metadata,
validates referential integrity and writes data/*.json plus a manifest and demo queries.

    python generate/build.py
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (COMPANY, DATA_DIR, SEED, SIM_TODAY, Registry, LookupError_, rng, write_json)  # noqa: E402
from layer0_departments import build_departments  # noqa: E402
from layer1_employees import build_employees  # noqa: E402
from layer2_teams import build_teams  # noqa: E402
from layer3_systems import build_systems  # noqa: E402
from layer4_projects import build_projects  # noqa: E402
from layer5_policies import build_policies  # noqa: E402
from events import ALL_EVENTS, EXPECTED_TYPE_COUNTS  # noqa: E402
from layer7_noise import build_noise_tickets, build_noise_slack  # noqa: E402
from layer7_standalone_docs import build_standalone_docs  # noqa: E402

SPACE_TO_DEPT = {"ENG": "DEPT-01", "IT": "DEPT-02", "SALES": "DEPT-03", "HR": "DEPT-04", "FIN": "DEPT-05", "MKT": "DEPT-06",
                 "PRODUCT": "DEPT-07", "LEGAL": "DEPT-08", "COMPANY": "DEPT-09"}
CHANNEL_TO_DEPT = {
    "#it-helpdesk": "DEPT-02", "#it-access-requests": "DEPT-02", "#incidents": "DEPT-02", "#devops-sre": "DEPT-02",
    "#security": "DEPT-02", "#proj-multi-region": "DEPT-02", "#bengaluru-office": "DEPT-02", "#pune-office": "DEPT-02",
    "#hyderabad-office": "DEPT-02",
    "#eng-platform": "DEPT-01", "#eng-frontend": "DEPT-01", "#eng-data": "DEPT-01", "#eng-announcements": "DEPT-01",
    "#proj-v4-migration": "DEPT-01", "#proj-portal-revamp": "DEPT-01",
    "#sales-team": "DEPT-03", "#sales-ops": "DEPT-03", "#deal-desk": "DEPT-03", "#customer-success": "DEPT-03",
    "#hr-announcements": "DEPT-04", "#people-ops": "DEPT-04", "#talent-acquisition": "DEPT-04", "#learning": "DEPT-04",
    "#general": "DEPT-04", "#random": "DEPT-04", "#kudos": "DEPT-04", "#food-and-chai": "DEPT-04", "#new-joiners": "DEPT-04",
    "#finance": "DEPT-05", "#expenses-help": "DEPT-05",
    "#marketing": "DEPT-06", "#demand-gen": "DEPT-06", "#product-marketing": "DEPT-06", "#ext-pixelcraft": "DEPT-06",
}
PRIVATE_CHANNELS = {"#security", "#leadership"}
DISTRIBUTION_LISTS = {"IT-Access-Team", "IT-Helpdesk", "HR-Ops", "Finance-AP", "Security-Team", "Eng-All", "All-Company",
                      "Sales-Leadership", "Data-Eng"}
TICKET_PREFIX = {"request": "RITM", "incident": "INC", "change": "CHG"}
RESTRICTED_TICKET_CATEGORIES = {"security-incident", "offboarding", "privileged-access", "governance", "hr-systems"}
RESTRICTED_GROUPS = {"Payroll"}

PLACEHOLDER = re.compile(r"\{\{(ticket|doc|email|slack):(EVT-\d{3})#(\d+)\}\}")
POL_PLACEHOLDER = re.compile(r"\{\{pol:([^}]+)\}\}")
PROJ_PLACEHOLDER = re.compile(r"\{\{proj:([^}]+)\}\}")
ID_PATTERN = re.compile(r"\b(?:INC|RITM|CHG)-\d{5}\b|\bDOC-\d{4}\b|\bEMAIL-\d{4}\b|\bSLACK-\d{4}\b|\bPOL-\d{2}\b|\bEVT-\d{3}\b|\bPROJ-\d{2}\b|\bSYS-\d{2}\b")


class BuildError(Exception):
    pass


# ---------------------------------------------------------------- helpers

def meta(source_type, source_system, department, sensitivity, created, last_ref):
    return {"source_type": source_type, "source_system": source_system, "department": department,
            "sensitivity": sensitivity, "created_date": created, "last_referenced_date": last_ref}


def resolve_to(reg, to):
    """Email `to`: name | DL | list -> list of employee ids / DL names."""
    items = to if isinstance(to, (list, tuple)) else [to]
    out = []
    for x in items:
        if x in DISTRIBUTION_LISTS:
            out.append(x)
        else:
            out.append(reg.eid(x))
    return out


def walk_strings(obj, fn):
    """Apply fn to every string in a nested dict/list structure (in place); returns obj."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = walk_strings(v, fn)
        return obj
    if isinstance(obj, list):
        return [walk_strings(v, fn) for v in obj]
    if isinstance(obj, str):
        return fn(obj)
    return obj


def collect_strings(obj, acc):
    if isinstance(obj, dict):
        for v in obj.values():
            collect_strings(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            collect_strings(v, acc)
    elif isinstance(obj, str):
        acc.append(obj)
    return acc


# ---------------------------------------------------------------- layer 6

def resolve_event(reg, b):
    ev = {
        "event_id": b["id"],
        "type": b["type"],
        "subtype": b["subtype"],
        "date": b["date"],
        "involved_employee_ids": [reg.eid(n) for n in b["people"]],
        "team_id": reg.tid(b["team"]),
        "related_system_id": reg.sid(b["system"]) if b["system"] else None,
        "related_policy_id": reg.polid(b["policy"]) if b["policy"] else None,
        "related_project_id": reg.pid(b["project"]) if b["project"] else None,
        "summary": b["summary"],
        "outcome": b["outcome"],
        "is_drift_scenario": bool(b["drift"]),
        "drift_note": b["drift_note"],
        "produces_artifacts": [],
        "artifact_ids": {"tickets": [], "emails": [], "slack": [], "docs": []},
        "related_event_ids": list(b["related_events"]),
        "tags": list(b["tags"]),
    }
    kinds = []
    if b["tickets"]:
        kinds.append("ticket")
    if b["emails"]:
        kinds.append("email")
    if b["slack"]:
        kinds.append("slack")
    if b["docs"]:
        kinds.append("confluence")
    ev["produces_artifacts"] = kinds
    return ev


# ---------------------------------------------------------------- layer 7 resolvers

def resolve_ticket(reg, t, event_id):
    req = reg.emp(t["requester"])
    asg = reg.emp(t["assignee"])
    dept = reg.by_id[req["department_id"]]
    sens = t["sensitivity"] or ("restricted" if (t["category"] in RESTRICTED_TICKET_CATEGORIES or t["group"] in RESTRICTED_GROUPS) else "internal")
    rec = {
        "ticket_id": None,
        "ticket_type": t["kind"],
        "event_id": event_id,
        "subject": t["subject"],
        "description": t["description"],
        "resolution": t["resolution"],
        "status": t["status"],
        "priority": t["priority"],
        "category": t["category"],
        "requester_employee_id": req["employee_id"],
        "requester_name": req["name"],
        "on_behalf_of_employee_id": reg.eid(t["on_behalf_of"]) if t.get("on_behalf_of") else None,
        "assigned_to_employee_id": asg["employee_id"],
        "assigned_to_name": asg["name"],
        "assignment_group": t["group"],
        "approver_employee_ids": [reg.eid(a) for a in t["approvers"]],
        "created_date": t["created"],
        "resolved_date": t["resolved"],
        "work_notes": t.get("work_notes"),
        "department": dept["name"],
        "referenced_ids": [],
        "metadata": meta("ticket", "servicenow", dept["department_id"], sens, t["created"], t["resolved"] or t["created"]),
    }
    return rec


def resolve_email(reg, m, event_id):
    msgs = []
    for frm, to, when, body in m["messages"]:
        sender = reg.emp(frm)
        msgs.append({"from_employee_id": sender["employee_id"], "from_name": sender["name"], "to": resolve_to(reg, to),
                     "date": when, "body": body})
    first_sender = reg.emp(m["messages"][0][0])
    dept_id = reg.did(m["department"]) if m.get("department") else first_sender["department_id"]
    participants = sorted({x["from_employee_id"] for x in msgs} | {t for x in msgs for t in x["to"] if t.startswith("EMP-")})
    return {
        "thread_id": None,
        "event_id": event_id,
        "subject": m["subject"],
        "participant_employee_ids": participants,
        "messages": msgs,
        "referenced_ids": [],
        "metadata": meta("email", "outlook", dept_id, m["sensitivity"] or "internal", msgs[0]["date"][:10], msgs[-1]["date"][:10]),
    }


def resolve_slack(reg, s, event_id):
    msgs = []
    for who, when, text in s["messages"]:
        e = reg.emp(who)
        msgs.append({"employee_id": e["employee_id"], "name": e["name"], "text": text, "ts": when})
    channel = s["channel"]
    if s.get("department"):
        dept_id = reg.did(s["department"])
    elif channel in CHANNEL_TO_DEPT:
        dept_id = CHANNEL_TO_DEPT[channel]
    else:
        dept_id = reg.emp(s["messages"][0][0])["department_id"]
    private = bool(s.get("private")) or channel in PRIVATE_CHANNELS
    sens = s["sensitivity"] or ("restricted" if private else "internal")
    return {
        "conversation_id": None,
        "event_id": event_id,
        "channel": channel,
        "channel_type": "private" if private else "public",
        "participant_employee_ids": sorted({x["employee_id"] for x in msgs}),
        "messages": msgs,
        "referenced_ids": [],
        "metadata": meta("slack", "slack", dept_id, sens, msgs[0]["ts"][:10], msgs[-1]["ts"][:10]),
    }


def resolve_doc(reg, dd, event_id):
    dept_id = reg.did(dd["department"]) if dd.get("department") else SPACE_TO_DEPT[dd["space"]]
    sens = dd["sensitivity"] or "internal"
    updated = dd.get("last_updated") or dd["created"]
    return {
        "doc_id": None,
        "event_id": event_id,
        "title": dd["title"],
        "space": dd["space"],
        "doc_type": dd["doc_type"],
        "body": dd["body"],
        "author_employee_ids": [reg.eid(a) for a in dd["authors"]],
        "created_date": dd["created"],
        "last_updated": updated,
        "labels": list(dd["labels"]),
        "related_event_ids": list(dd["related_events"]),
        "related_system_ids": [reg.sid(x) for x in dd["related_systems"]],
        "related_project_ids": [reg.pid(x) for x in dd["related_projects"]],
        "related_policy_ids": [reg.polid(x) for x in dd["related_policies"]],
        "referenced_ids": [],
        "metadata": meta("confluence", "confluence", dept_id, sens, dd["created"], updated),
    }


# ---------------------------------------------------------------- id assignment

def assign_ticket_ids(tickets):
    r = rng("ticket-ids")
    order = sorted(range(len(tickets)), key=lambda i: (tickets[i]["created_date"], i))
    n = 20031
    for i in order:
        n += r.randint(1, 3)
        tickets[i]["ticket_id"] = f"{TICKET_PREFIX[tickets[i]['ticket_type']]}-{n:05d}"


def assign_sequential(items, field, prefix, key):
    order = sorted(range(len(items)), key=lambda i: (key(items[i]), i))
    for n, i in enumerate(order, 1):
        items[i][field] = f"{prefix}-{n:04d}"


# ---------------------------------------------------------------- main build

def build():
    reg = Registry()
    print("Layer 0-2: departments, employees, teams")
    reg.departments = build_departments()
    reg.employees = build_employees(reg.departments)
    reg.teams = build_teams(reg.departments, reg.employees)
    reg.index()
    print("Layer 3-5: systems, projects, policies")
    reg.systems = build_systems(reg); reg.index()
    reg.projects = build_projects(reg); reg.index()
    reg.policies = build_policies(reg); reg.index()

    print("Layer 6: events")
    events = [resolve_event(reg, b) for b in ALL_EVENTS]
    reg.events = events
    reg.index()
    ev_by_id = {e["event_id"]: e for e in events}

    print("Layer 7: event-derived artifacts")
    tickets, emails, slacks, docs = [], [], [], []
    # per-event artifact position -> object, for placeholder resolution
    pos = {}
    for b in ALL_EVENTS:
        eid = b["id"]
        for i, t in enumerate(b["tickets"], 1):
            rec = resolve_ticket(reg, t, eid); tickets.append(rec); pos[("ticket", eid, i)] = rec
        for i, m in enumerate(b["emails"], 1):
            rec = resolve_email(reg, m, eid); emails.append(rec); pos[("email", eid, i)] = rec
        for i, s in enumerate(b["slack"], 1):
            rec = resolve_slack(reg, s, eid); slacks.append(rec); pos[("slack", eid, i)] = rec
        for i, dd in enumerate(b["docs"], 1):
            rec = resolve_doc(reg, dd, eid); docs.append(rec); pos[("doc", eid, i)] = rec
    n_event = (len(tickets), len(emails), len(slacks), len(docs))

    print("Layer 7: noise tickets / chatter, standalone docs")
    for t in build_noise_tickets(reg):
        tickets.append(resolve_ticket(reg, t, None))
    for s in build_noise_slack(reg):
        slacks.append(resolve_slack(reg, s, None))
    for dd in build_standalone_docs(reg):
        docs.append(resolve_doc(reg, dd, None))

    print("Assigning IDs")
    assign_ticket_ids(tickets)
    assign_sequential(emails, "thread_id", "EMAIL", lambda x: x["messages"][0]["date"])
    assign_sequential(slacks, "conversation_id", "SLACK", lambda x: x["messages"][0]["ts"])
    assign_sequential(docs, "doc_id", "DOC", lambda x: x["created_date"])

    id_field = {"ticket": "ticket_id", "email": "thread_id", "slack": "conversation_id", "doc": "doc_id"}

    def sub(text):
        def rep(m):
            key = (m.group(1), m.group(2), int(m.group(3)))
            if key not in pos:
                raise BuildError(f"placeholder {m.group(0)} does not resolve (no such artifact)")
            return pos[key][id_field[key[0]]]
        text = PLACEHOLDER.sub(rep, text)
        text = POL_PLACEHOLDER.sub(lambda m: reg.polid(m.group(1)), text)
        text = PROJ_PLACEHOLDER.sub(lambda m: reg.pid(m.group(1)), text)
        return text

    print("Resolving placeholders")
    for coll in (tickets, emails, slacks, docs, events):
        for rec in coll:
            walk_strings(rec, sub)

    # every person who acts in an event's artifacts is "involved" in the event (authored list first, then the rest)
    added = 0
    for rec in tickets:
        if rec["event_id"]:
            ids = [rec["requester_employee_id"], rec["assigned_to_employee_id"], rec["on_behalf_of_employee_id"]] + rec["approver_employee_ids"]
            inv = ev_by_id[rec["event_id"]]["involved_employee_ids"]
            for x in ids:
                if x and x not in inv:
                    inv.append(x); added += 1
    for coll in (emails, slacks):
        for rec in coll:
            if rec["event_id"]:
                inv = ev_by_id[rec["event_id"]]["involved_employee_ids"]
                for x in rec["participant_employee_ids"]:
                    if x not in inv:
                        inv.append(x); added += 1
    for rec in docs:
        if rec["event_id"]:
            inv = ev_by_id[rec["event_id"]]["involved_employee_ids"]
            for x in rec["author_employee_ids"]:
                if x not in inv:
                    inv.append(x); added += 1
    print(f"  involved_employee_ids: {added} participants added from artifacts")

    # link artifacts back to events
    for rec in tickets:
        if rec["event_id"]:
            ev_by_id[rec["event_id"]]["artifact_ids"]["tickets"].append(rec["ticket_id"])
    for rec in emails:
        if rec["event_id"]:
            ev_by_id[rec["event_id"]]["artifact_ids"]["emails"].append(rec["thread_id"])
    for rec in slacks:
        if rec["event_id"]:
            ev_by_id[rec["event_id"]]["artifact_ids"]["slack"].append(rec["conversation_id"])
    for rec in docs:
        if rec["event_id"]:
            ev_by_id[rec["event_id"]]["artifact_ids"]["docs"].append(rec["doc_id"])
            if rec["event_id"] not in rec["related_event_ids"]:
                rec["related_event_ids"].insert(0, rec["event_id"])

    print("Cross-references and last_referenced_date")
    all_ids = {}
    for rec in tickets:
        all_ids[rec["ticket_id"]] = rec
    for rec in emails:
        all_ids[rec["thread_id"]] = rec
    for rec in slacks:
        all_ids[rec["conversation_id"]] = rec
    for rec in docs:
        all_ids[rec["doc_id"]] = rec
    for rec in reg.policies:
        all_ids[rec["policy_id"]] = rec
    for rec in events:
        all_ids[rec["event_id"]] = rec

    def own_date(rec):
        return rec["metadata"]["created_date"] if "metadata" in rec else rec["date"]

    def bump(target_id, date):
        tgt = all_ids.get(target_id)
        if tgt is None or "metadata" not in tgt:
            return
        if date > tgt["metadata"]["last_referenced_date"]:
            tgt["metadata"]["last_referenced_date"] = date

    for coll in (tickets, emails, slacks, docs):
        for rec in coll:
            own = rec.get("ticket_id") or rec.get("thread_id") or rec.get("conversation_id") or rec.get("doc_id")
            found = set()
            for s in collect_strings({k: v for k, v in rec.items() if k not in ("referenced_ids", "metadata")}, []):
                found.update(ID_PATTERN.findall(s))
            found.discard(own)
            rec["referenced_ids"] = sorted(found)
            for fid in found:
                bump(fid, rec["metadata"]["last_referenced_date"])
    # policies referenced by events get last_referenced bumped to the event date
    for ev in events:
        if ev["related_policy_id"]:
            bump(ev["related_policy_id"], ev["date"])
        for t_id in ev["artifact_ids"]["tickets"]:
            bump(t_id, ev["date"])

    print("Validating")
    problems, warnings = validate(reg, events, tickets, emails, slacks, docs)
    for w in warnings:
        print("  WARN", w)
    if problems:
        for p in problems:
            print("  ERROR", p)
        raise BuildError(f"{len(problems)} validation errors")

    print("Writing data/")
    for e in reg.employees:
        e.pop("_team_key", None)
    write_json("departments.json", reg.departments)
    write_json("employees.json", reg.employees)
    write_json("teams.json", reg.teams)
    write_json("systems.json", reg.systems)
    write_json("projects.json", reg.projects)
    write_json("policies.json", reg.policies)
    write_json("events.json", events)
    write_json("tickets.json", tickets)
    write_json("emails.json", emails)
    write_json("slack.json", slacks)
    write_json("confluence.json", docs)

    demo = build_demo_queries(reg, events, ev_by_id)
    write_json("demo_queries.json", demo)
    write_demo_md(demo)

    manifest = {
        "dataset": f"{COMPANY['name']} - synthetic enterprise knowledge dataset",
        "generated_at": dt.datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "simulated_today": SIM_TODAY.isoformat(),
        "seed": SEED,
        "counts": {
            "departments": len(reg.departments), "employees": len(reg.employees), "teams": len(reg.teams),
            "systems": len(reg.systems), "projects": len(reg.projects), "policies": len(reg.policies),
            "policies_stale_by_design": sum(p["is_stale_by_design"] for p in reg.policies),
            "events": len(events),
            "tickets_total": len(tickets), "tickets_event_derived": n_event[0], "tickets_noise": len(tickets) - n_event[0],
            "email_threads": len(emails),
            "slack_conversations_total": len(slacks), "slack_event_derived": n_event[2], "slack_noise": len(slacks) - n_event[2],
            "confluence_docs_total": len(docs), "confluence_event_referencing": n_event[3], "confluence_standalone": len(docs) - n_event[3],
            "demo_queries": len(demo),
        },
        "event_type_distribution": dict(collections.Counter(e["type"] for e in events)),
        "drift_events": sum(e["is_drift_scenario"] for e in events),
        "ticket_type_distribution": dict(collections.Counter(t["ticket_type"] for t in tickets)),
        "sensitivity_distribution": dict(collections.Counter(
            r["metadata"]["sensitivity"] for coll in (tickets, emails, slacks, docs, reg.policies) for r in coll)),
        "validation": {"errors": 0, "warnings": warnings},
        "files": ["departments.json", "employees.json", "teams.json", "systems.json", "projects.json", "policies.json",
                  "events.json", "tickets.json", "emails.json", "slack.json", "confluence.json", "demo_queries.json",
                  "demo_queries.md", "manifest.json"],
    }
    write_json("manifest.json", manifest)
    print(json.dumps(manifest["counts"], indent=2))
    print(json.dumps(manifest["event_type_distribution"], indent=2))
    return manifest


# ---------------------------------------------------------------- validation

def validate(reg, events, tickets, emails, slacks, docs):
    problems, warnings = [], []
    emp = {e["employee_id"]: e for e in reg.employees}
    team_ids = {t["team_id"] for t in reg.teams}
    sys_ids = {s["system_id"] for s in reg.systems}
    proj_ids = {p["project_id"] for p in reg.projects}
    pol = {p["policy_id"]: p for p in reg.policies}
    dept_ids = {d["department_id"] for d in reg.departments}
    ev_ids = {e["event_id"] for e in events}

    def chk(cond, msg):
        if not cond:
            problems.append(msg)

    # counts
    chk(len(reg.departments) == 9, "expected 9 departments")
    chk(len(reg.employees) == 1000, "expected 1000 employees")
    chk(len(reg.teams) == 63, "expected 63 teams")
    chk(len({e["employee_id"] for e in reg.employees}) == len(reg.employees), "duplicate employee IDs")
    chk(len({e["name"] for e in reg.employees}) == len(reg.employees), "duplicate employee names")
    chk(len(reg.systems) == 30, "expected 30 systems")
    chk(len(reg.projects) == 24, "expected 24 projects")
    chk(len(reg.policies) == 36, "expected 36 policies")
    chk(len(events) == 80, f"expected 80 events, got {len(events)}")
    dist = collections.Counter(e["type"] for e in events)
    for k, v in EXPECTED_TYPE_COUNTS.items():
        chk(dist.get(k, 0) == v, f"event type {k}: expected {v}, got {dist.get(k, 0)}")
    chk(len({e["event_id"] for e in events}) == 80, "duplicate event ids")

    # org integrity
    for e in reg.employees:
        chk(e["department_id"] in dept_ids, f"{e['employee_id']} bad department")
        chk(e["team_id"] in team_ids, f"{e['employee_id']} bad team")
        if e["manager_id"] is None:
            chk(e["tier"] == "head", f"{e['employee_id']} has no manager but is not a head")
        else:
            chk(e["manager_id"] in emp, f"{e['employee_id']} manager missing")
            if e["manager_id"] in emp:
                chk(emp[e["manager_id"]]["department_id"] == e["department_id"], f"{e['employee_id']} manager in other department")
    for t in reg.teams:
        for m in t["member_employee_ids"]:
            chk(m in emp and emp[m]["team_id"] == t["team_id"], f"team {t['team_id']} member {m} inconsistent")
        chk(t["lead_employee_id"] in t["member_employee_ids"], f"team {t['team_id']} lead not a member")
    for e in reg.employees:
        if e["status"] != "exited":
            team = next(t for t in reg.teams if t["team_id"] == e["team_id"])
            chk(e["employee_id"] in team["member_employee_ids"], f"{e['employee_id']} not listed in team {e['team_id']}")
    for dpt in reg.departments:
        chk(dpt["head_employee_id"] in emp, f"{dpt['department_id']} head missing")
    for s in reg.systems:
        chk(s["owner_team_id"] in team_ids, f"{s['system_id']} owner team missing")
    for p in reg.projects:
        chk(p["team_id"] in team_ids, f"{p['project_id']} team missing")
        for x in p["staffed_employee_ids"]:
            chk(x in emp, f"{p['project_id']} staff {x} missing")
        for x in p["related_system_ids"]:
            chk(x in sys_ids, f"{p['project_id']} system {x} missing")
    for p in reg.policies:
        chk(p["owner_department_id"] in dept_ids, f"{p['policy_id']} owner dept missing")
        for x in p["related_system_ids"]:
            chk(x in sys_ids, f"{p['policy_id']} system {x} missing")
        age = (SIM_TODAY - dt.date.fromisoformat(p["last_updated"])).days
        if p["is_stale_by_design"]:
            chk(180 <= age <= 548, f"{p['policy_id']} marked stale but age is {age} days")
        else:
            chk(age < 180, f"{p['policy_id']} not marked stale but age is {age} days")

    # events
    for ev in events:
        for x in ev["involved_employee_ids"]:
            chk(x in emp, f"{ev['event_id']} employee {x} missing")
        chk(ev["team_id"] in team_ids, f"{ev['event_id']} team missing")
        if ev["related_system_id"]:
            chk(ev["related_system_id"] in sys_ids, f"{ev['event_id']} system missing")
        if ev["related_policy_id"]:
            chk(ev["related_policy_id"] in pol, f"{ev['event_id']} policy missing")
            if ev["is_drift_scenario"]:
                chk(pol[ev["related_policy_id"]]["is_stale_by_design"], f"{ev['event_id']} drift event references a non-stale policy")
                chk(ev["date"] > pol[ev["related_policy_id"]]["last_updated"], f"{ev['event_id']} drift event predates policy update")
        if ev["related_project_id"]:
            chk(ev["related_project_id"] in proj_ids, f"{ev['event_id']} project missing")
        for x in ev["related_event_ids"]:
            chk(x in ev_ids, f"{ev['event_id']} related event {x} missing")
        chk(ev["is_drift_scenario"] == (ev["type"] == "policy_drift"), f"{ev['event_id']} drift flag/type mismatch")
        total = sum(len(v) for v in ev["artifact_ids"].values())
        chk(total >= 2, f"{ev['event_id']} produces only {total} artifacts (min 2)")
        chk(len(ev["produces_artifacts"]) >= 1, f"{ev['event_id']} produces nothing")

    def person_active_on(pid, date, where):
        e = emp.get(pid)
        if e is None:
            problems.append(f"{where}: employee {pid} missing")
            return
        if date < e["join_date"]:
            problems.append(f"{where}: {e['name']} ({pid}) acts on {date} before joining {e['join_date']}")
        if e.get("exit_date") and date > e["exit_date"]:
            problems.append(f"{where}: {e['name']} ({pid}) acts on {date} after exit {e['exit_date']}")

    # artifacts
    seen_ids = set()
    for t in tickets:
        chk(t["ticket_id"] not in seen_ids, f"dup {t['ticket_id']}"); seen_ids.add(t["ticket_id"])
        chk(t["event_id"] is None or t["event_id"] in ev_ids, f"{t['ticket_id']} bad event")
        person_active_on(t["requester_employee_id"], t["created_date"], t["ticket_id"])
        person_active_on(t["assigned_to_employee_id"], t["created_date"], t["ticket_id"])
        for a in t["approver_employee_ids"]:
            person_active_on(a, t["resolved_date"] or t["created_date"], t["ticket_id"])
        if t["resolved_date"]:
            chk(t["resolved_date"] >= t["created_date"], f"{t['ticket_id']} resolved before created")
        else:
            chk(t["status"] in ("open", "in_progress", "on_hold"), f"{t['ticket_id']} no resolved date but status {t['status']}")
        chk(t["metadata"]["department"] in dept_ids, f"{t['ticket_id']} bad metadata dept")
    for m in emails:
        chk(m["thread_id"] not in seen_ids, f"dup {m['thread_id']}"); seen_ids.add(m["thread_id"])
        chk(m["event_id"] is None or m["event_id"] in ev_ids, f"{m['thread_id']} bad event")
        prev = ""
        for x in m["messages"]:
            person_active_on(x["from_employee_id"], x["date"][:10], m["thread_id"])
            for to in x["to"]:
                if to.startswith("EMP-"):
                    person_active_on(to, x["date"][:10], m["thread_id"])
            chk(x["date"] >= prev, f"{m['thread_id']} messages out of order"); prev = x["date"]
    for s in slacks:
        chk(s["conversation_id"] not in seen_ids, f"dup {s['conversation_id']}"); seen_ids.add(s["conversation_id"])
        chk(s["event_id"] is None or s["event_id"] in ev_ids, f"{s['conversation_id']} bad event")
        prev = ""
        for x in s["messages"]:
            person_active_on(x["employee_id"], x["ts"][:10], s["conversation_id"])
            chk(x["ts"] >= prev, f"{s['conversation_id']} messages out of order"); prev = x["ts"]
    for dd in docs:
        chk(dd["doc_id"] not in seen_ids, f"dup {dd['doc_id']}"); seen_ids.add(dd["doc_id"])
        chk(dd["event_id"] is None or dd["event_id"] in ev_ids, f"{dd['doc_id']} bad event")
        for a in dd["author_employee_ids"]:
            person_active_on(a, dd["created_date"], dd["doc_id"])
        for x in dd["related_event_ids"]:
            chk(x in ev_ids, f"{dd['doc_id']} related event {x} missing")

    # placeholders and metadata
    valid_sens = {"public", "internal", "restricted"}
    for coll, st in ((tickets, "ticket"), (emails, "email"), (slacks, "slack"), (docs, "confluence"), (reg.policies, "policy")):
        for rec in coll:
            md = rec["metadata"]
            chk(md["source_type"] == st and md["sensitivity"] in valid_sens and md["department"] in dept_ids
                and md["created_date"] and md["last_referenced_date"] >= md["created_date"],
                f"bad metadata on {rec.get('ticket_id') or rec.get('thread_id') or rec.get('conversation_id') or rec.get('doc_id') or rec.get('policy_id')}")
            for s in collect_strings(rec, []):
                if "{{" in s:
                    problems.append(f"unresolved placeholder in {rec.get('ticket_id') or rec.get('thread_id') or rec.get('conversation_id') or rec.get('doc_id')}: {s[:80]}")
                    break
    # dangling artifact-id references inside text
    known = set(seen_ids) | set(pol) | ev_ids | proj_ids | sys_ids
    for coll in (tickets, emails, slacks, docs):
        for rec in coll:
            for rid in rec["referenced_ids"]:
                chk(rid in known, f"{rec.get('ticket_id') or rec.get('thread_id') or rec.get('conversation_id') or rec.get('doc_id')} references unknown id {rid}")

    # soft checks
    n_event_tickets = sum(1 for t in tickets if t["event_id"])
    if not 130 <= n_event_tickets <= 170:
        warnings.append(f"event-derived tickets = {n_event_tickets} (target ~150)")
    if not 1200 <= len(tickets) <= 1450:
        warnings.append(f"total tickets = {len(tickets)} (target ~1,320 for 1,000 people)")
    if not 95 <= len(emails) <= 125:
        warnings.append(f"email threads = {len(emails)} (target ~110)")
    if not 260 <= len(slacks) <= 320:
        warnings.append(f"slack conversations = {len(slacks)} (target ~290)")
    if len(docs) != 140:
        warnings.append(f"confluence docs = {len(docs)} (target 140: 70 + 9 department rosters + 61 generated team pages)")
    multi = collections.Counter(e for p in reg.projects for e in p["staffed_employee_ids"])
    n_multi = sum(1 for v in multi.values() if v >= 2)
    if not 18 <= n_multi <= 32:
        warnings.append(f"employees on 2+ projects = {n_multi} (target 20-25%)")
    return problems, warnings


# ---------------------------------------------------------------- demo queries

def build_demo_queries(reg, events, ev_by_id):
    out = []
    n = 0
    for b in ALL_EVENTS:
        if not b.get("demo"):
            continue
        ev = ev_by_id[b["id"]]
        n += 1
        evidence = {"event_ids": [ev["event_id"]] + ev["related_event_ids"],
                    "policy_ids": [ev["related_policy_id"]] if ev["related_policy_id"] else [],
                    "tickets": list(ev["artifact_ids"]["tickets"]), "emails": list(ev["artifact_ids"]["emails"]),
                    "slack": list(ev["artifact_ids"]["slack"]), "docs": list(ev["artifact_ids"]["docs"])}
        for rel in ev["related_event_ids"]:
            r = ev_by_id[rel]
            for k in ("tickets", "emails", "slack", "docs"):
                evidence[k] += r["artifact_ids"][k]
            if r["related_policy_id"] and r["related_policy_id"] not in evidence["policy_ids"]:
                evidence["policy_ids"].append(r["related_policy_id"])
        pol_title = reg.by_id[ev["related_policy_id"]]["title"] if ev["related_policy_id"] else None
        out.append({
            "query_id": f"DQ-{n:02d}",
            "query": b["demo"]["query"],
            "primary_event_id": ev["event_id"],
            "event_type": ev["type"],
            "expected_drift_flag": bool(b["demo"].get("expected_drift", False)),
            "expected_conflict_flag": bool(b["demo"].get("expected_conflict", False)),
            "governing_policy": pol_title,
            "expected_answer_summary": ev["summary"],
            "drift_note": ev["drift_note"],
            "evidence": evidence,
        })
    return out


def write_demo_md(demo):
    lines = ["# Known-good demo queries", "",
             "Each query has a verified multi-source answer in the dataset. `expected_drift_flag` / `expected_conflict_flag` say whether the ",
             "knowledge bank *should* surface a policy-vs-practice gap or a contradictory-resolution warning. Queries where both are false are ",
             "false-positive controls: the correct answer is a clean one.", ""]
    for q in demo:
        flags = []
        if q["expected_drift_flag"]:
            flags.append("DRIFT expected")
        if q["expected_conflict_flag"]:
            flags.append("CONFLICT expected")
        if not flags:
            flags.append("clean - no flag expected")
        lines += [f"## {q['query_id']}: \"{q['query']}\"", "",
                  f"- **Primary event:** {q['primary_event_id']} ({q['event_type']}) | **Policy:** {q['governing_policy'] or '-'} | **{' / '.join(flags)}**",
                  f"- **Expected answer:** {q['expected_answer_summary']}"]
        if q["drift_note"]:
            lines.append(f"- **Drift note:** {q['drift_note']}")
        ev = q["evidence"]
        lines.append(f"- **Evidence:** events {', '.join(ev['event_ids'])}; policies {', '.join(ev['policy_ids']) or '-'}; "
                     f"tickets {', '.join(ev['tickets']) or '-'}; emails {', '.join(ev['emails']) or '-'}; "
                     f"slack {', '.join(ev['slack']) or '-'}; docs {', '.join(ev['docs']) or '-'}")
        lines.append("")
    (DATA_DIR / "demo_queries.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    try:
        build()
    except LookupError_ as e:
        print("NAME RESOLUTION ERROR:", e)
        sys.exit(1)
    except BuildError as e:
        print("BUILD FAILED:", e)
        sys.exit(1)
