"""Access-control tests: role-based + need-to-know rules (POL-36), sign-in/session security, audit, leak checks.

    python -m scripts.test_access            # rules + HTTP + retrieval/tool leak checks (no agent calls)
    python -m scripts.test_access --agent    # also run the agent as several employees and check citations

Records are found by content, not ID: ticket numbers change when the dataset is regenerated.
Exits non-zero on any failure.
"""
import argparse
import os
import sys

from fastapi.testclient import TestClient

from app import auth
from app.access import access_basis, can_see, principal_for
from app.kb import directory
from app.main import app
from app.retrieval import retriever
from app.tools import AgentTools

R = retriever()
D = directory()
failures: list[str] = []
RECORDS = {c.record_id: c for c in R.chunks if c.chunk_index == 0}


def check(ok: bool, label: str):
    print(("  ok    " if ok else "  FAIL  ") + label)
    if not ok:
        failures.append(label)


def emp(name: str) -> str:
    return next(eid for eid, e in D.employees.items() if e["name"] == name)


def rec(title_part: str, source_type: str | None = None) -> str:
    hits = [c for c in RECORDS.values() if title_part in c.title and (not source_type or c.source_type == source_type)]
    assert hits, f"no record titled like {title_part!r}"
    return sorted(hits, key=lambda c: c.record_id)[0].record_id


def sees(who: str, rid: str) -> bool:
    return can_see(principal_for(who), RECORDS[rid])


CONTRACTOR = next(eid for eid, e in sorted(D.employees.items())
                  if e.get("employment_type") == "contractor" and e["status"] == "active")


# ------------------------------------------------------------------ rules
def test_rules():
    print("role-based and need-to-know rules (POL-36)")
    referral = rec("Referral bonus not received - Aditya Rao", "ticket")
    admin = rec("AlgoWorks Admin Console read-only access - Kunal Shah", "ticket")
    dpo_mail = rec("DPO coverage after Pradeep", "email")
    update_req = rec("Policy update request: Application Access Request Policy", "ticket")
    r = RECORDS[referral]
    check(r.confidential and r.personal_data, f"referral-bonus ticket {referral} is confidential personal data ({r.personal_data_category})")
    meera, arjun = emp("Meera Krishnan"), emp("Arjun Venkataraman")
    cases = [
        (emp("Aditya Rao"), referral, True, "requester sees his own referral-bonus ticket"),
        (emp("Fatima Sheikh"), referral, True, "HR partner handling it sees it (involved)"),
        (meera, referral, True, "requester's manager sees it (people_manager, pay is not excluded)"),
        (arjun, referral, True, "head of Engineering sees it (reporting line)"),
        (emp("Swati Kulkarni"), referral, True, "HRBP for Engineering sees an Engineering employee's personal data"),
        (emp("Revathi Krishnaswamy"), referral, True, "compliance auditor sees it"),
        (emp("Harish Gowda"), referral, False, "unrelated engineer does not"),
        (emp("Vivek Anand"), referral, False, "CFO does not: executives get no personal data"),
        (emp("Sandeep Malhotra"), referral, False, "head of another department does not"),
        (emp("Kunal Shah"), admin, True, "requester sees his access request"),
        (emp("Nikhil Bhatt"), admin, True, "security admin sees a restricted access request"),
        (emp("Vivek Anand"), admin, True, "executive sees business-confidential records company-wide"),
        (emp("Harish Gowda"), admin, False, "IT engineer without a security role does not"),
        (emp("Swati Kulkarni"), admin, False, "HRBP does not see security records"),
        (emp("Harish Gowda"), "POL-11", True, "IT employee sees IT's restricted policy"),
        (emp("Kunal Shah"), "POL-11", False, "Sales employee does not"),
        (CONTRACTOR, "POL-11", False, "contractor does not see restricted documents"),
        (emp("Sunita Raghavan"), dpo_mail, True, "participant sees a restricted email"),
        (emp("Harish Gowda"), dpo_mail, False, "non-participant without a role does not"),
        (emp("Kunal Shah"), "POL-01", True, "everyone sees a non-confidential policy"),
        (CONTRACTOR, "POL-01", True, "contractor sees non-confidential policies"),
        (emp("Aditya Rao"), update_req, True, "employees see a non-confidential ticket"),
        (CONTRACTOR, update_req, False, "contractor does not see other people's tickets"),
    ]
    if r.personal_data_category == "pay":
        cases.append((emp("Vijay Kumar"), referral, True, "payroll admin sees pay data company-wide"))
    for who, rid, expected, label in cases:
        check(sees(who, rid) == expected, f"{label} ({D.name(who)} -> {rid})")

    health = [c for c in RECORDS.values() if c.personal_data_category == "health_or_leave_reason" and c.source_type == "ticket"]
    if health:
        h = health[0]
        requester = h.participant_employee_ids[0]
        manager = D.employees[requester].get("manager_id")
        check(sees(requester, h.record_id), f"requester sees their own leave/health ticket {h.record_id}")
        if manager and manager not in h.participant_employee_ids + h.owner_employee_ids:
            check(not sees(manager, h.record_id), "their manager does NOT see the health/leave reason")
        check(sees(emp("Rakesh Nair"), h.record_id), "HR operations sees leave/health data")
        check(not sees(emp("Vijay Kumar"), h.record_id), "payroll does not see leave/health data")
    check(principal_for("EMP-021") is None, "an employee who has left cannot be a principal (EMP-021)")
    basis = access_basis(principal_for(emp("Revathi Krishnaswamy")), RECORDS[referral])
    check(basis == "compliance_auditor role", f"auditor access is attributed to the auditor role ({basis})")


# ------------------------------------------------------------------ HTTP / sessions / audit
def test_http():
    print("sign-in, sessions and audit")
    c = TestClient(app)  # not used as a context manager: skips the Gemini warm-up
    pw = os.getenv("DEMO_PASSWORD", "")
    check(bool(pw), "DEMO_PASSWORD is configured")
    check(c.post("/api/chat", json={"question": "hi"}).status_code == 401, "chat without a session -> 401")
    check(c.post("/api/search", json={"query": "vpn"}).status_code == 401, "search without a session -> 401")
    check(c.get("/api/me").status_code == 401, "me without a session -> 401")
    c.cookies.set(auth.COOKIE, "not.a-valid-token")
    check(c.get("/api/me").status_code == 401, "garbage session cookie -> 401")
    harish = emp("Harish Gowda")
    payload, sig = auth.issue(harish).split(".")
    forged = auth._b64(auth._unb64(payload).replace(harish.encode(), b"EMP-004")) + "." + sig
    c.cookies.set(auth.COOKIE, forged)
    check(c.get("/api/me").status_code == 401, "session edited to another employee (bad signature) -> 401")
    c.cookies.clear()

    ip = {"x-forwarded-for": "203.0.113.7"}
    check(c.post("/api/login", json={"employee_id": harish, "password": "wrong"}, headers=ip).status_code == 401, "wrong password -> 401")
    check(c.post("/api/login", json={"employee_id": "EMP-021", "password": pw}, headers=ip).status_code == 401,
          "employee who left cannot sign in -> 401")
    for _ in range(auth.MAX_FAILED_LOGINS):
        c.post("/api/login", json={"employee_id": harish, "password": "wrong"}, headers=ip)
    check(c.post("/api/login", json={"employee_id": harish, "password": pw}, headers=ip).status_code == 429,
          f"after {auth.MAX_FAILED_LOGINS} failures from one IP, even the right password is refused -> 429")

    r = c.post("/api/login", json={"employee_id": harish, "password": pw}, headers={"x-forwarded-for": "198.51.100.4"})
    check(r.status_code == 200, "correct sign-in -> 200")
    set_cookie = r.headers.get("set-cookie", "").lower()
    check("httponly" in set_cookie and "samesite=lax" in set_cookie, "session cookie is HttpOnly and SameSite=Lax")
    me = c.get("/api/me").json()
    check(me["employee_id"] == harish and "employee" in me["roles"], "me returns the employee and their roles")
    check(c.get("/api/audit").status_code == 403, "audit log refused to a non-auditor -> 403")
    referral = rec("Referral bonus not received - Aditya Rao", "ticket")
    hidden, missing = c.get(f"/api/records/{referral}"), c.get("/api/records/RITM-99999")
    check(hidden.status_code == 404 and hidden.json() == missing.json(),
          "record viewer: a confidential record outside scope looks exactly like a missing one -> 404")
    check(c.get("/api/records/POL-01").status_code == 200, "record viewer opens a record in scope")
    check(c.get("/api/roles").status_code == 200, "role catalogue is available")
    c.post("/api/logout")
    check(c.get("/api/me").status_code == 401, "after sign-out -> 401")

    r = c.post("/api/login", json={"employee_id": emp("Revathi Krishnaswamy"), "password": pw},
               headers={"x-forwarded-for": "198.51.100.5"})
    check(r.status_code == 200 and c.get("/api/audit").status_code == 200, "compliance auditor can read the audit log")
    c.post("/api/logout")


# ------------------------------------------------------------------ retrieval / tool leaks
QUERIES = [
    "When is the referral bonus paid?",
    "Can Customer Success get access to the AlgoWorks Admin Console?",
    "Who approves Snowflake PII access now that the DPO has left?",
    "Can remote employees claim home internet on expenses?",
    "Medical leave extension",
    "Variable pay payout query",
    "MSA redlines",
    "Phishing email reported",
]


def test_leaks():
    print("retrieval and tool leak checks")
    people = [emp(n) for n in ("Harish Gowda", "Kunal Shah", "Aditya Rao", "Swati Kulkarni", "Vivek Anand",
                               "Vijay Kumar", "Nikhil Bhatt")] + [CONTRACTOR]
    for who in people:
        p = principal_for(who)
        leaked = []
        for q in QUERIES:
            res = R.search(q, p)
            shown = [h.chunk for h in res.hits + res.related] + [c for g in res.case_groups for c in g]
            leaked += [c.record_id for c in shown if not can_see(p, c)]
        check(not leaked, f"{D.name(who)}: nothing outside scope in search results, links or similar cases {leaked or ''}")
    t = AgentTools(principal_for(emp("Harish Gowda")))
    check("error" in t.get_record(rec("Referral bonus not received - Aditya Rao", "ticket")),
          "get_record refuses a confidential record outside scope")
    rel = t.get_related("POL-26")
    check(all(can_see(t.principal, RECORDS[x["record_id"]]) for x in rel.get("related", [])),
          "get_related only lists records in scope")
    on_leave = next(e["name"] for e in D.employees.values() if e["status"] == "on_leave" and e.get("notes"))
    person = AgentTools(principal_for(emp("Harish Gowda"))).lookup_person(on_leave)["people"][0]
    check("notes" not in person and "leave_until" not in person, f"leave reason and dates hidden from colleagues ({on_leave})")
    person = AgentTools(principal_for(emp("Rakesh Nair"))).lookup_person(on_leave)["people"][0]
    check("notes" in person, "HR operations sees the leave reason")


def test_agent():
    print("agent answers (live Gemini calls)")
    from app.agent import answer_question
    for who, q in [(emp("Harish Gowda"), "When is the referral bonus paid?"),
                   (emp("Aditya Rao"), "When will my referral bonus be paid?"),
                   (emp("Swati Kulkarni"), "Has anyone in Engineering had problems getting their referral bonus paid?"),
                   (CONTRACTOR, "When is the referral bonus paid?")]:
        p = principal_for(who)
        r = answer_question(q, p)
        leaked = [c.record_id for c in r.citations if not can_see(p, RECORDS[c.record_id])]
        unexplained = [c.record_id for c in r.citations if c.confidential and not c.access_basis]
        conf = [f"{c.record_id}:{c.access_basis}" for c in r.citations if c.confidential]
        check(not leaked and not unexplained,
              f"{D.name(who)} '{q[:45]}': citations in scope; confidential shown: {conf or 'none'}")


def _login(c: TestClient, who: str, ip: str):
    r = c.post("/api/login", json={"employee_id": who, "password": os.getenv("DEMO_PASSWORD", "")},
               headers={"x-forwarded-for": ip})
    assert r.status_code == 200, r.text


def test_chats():
    print("chat history (in-memory store; no Gemini calls)")
    from app import history
    from app.main import ChatRequest, _context
    from app.schema import AgentResponse
    history._store = history._Memory()  # never write test chats into the real Firestore database

    harish, other = emp("Harish Gowda"), emp("Swati Kulkarni")
    p = principal_for(harish)
    visible = next(r for r, c in RECORDS.items() if not c.confidential)
    hidden = next(r for r, c in RECORDS.items() if c.confidential and not can_see(p, c))
    scope = history.scope_key(p)
    answer = lambda text: AgentResponse(answer=text).model_dump(mode="json")
    cid = history.save_turn(harish, None, "first question", answer("first answer"), [], [visible], scope)
    check(history.save_turn(harish, cid, "follow-up", answer("second answer"), [], [visible], scope) == cid,
          "a follow-up with the chat_id stays in the same chat")
    history.save_turn(harish, cid, "answer built on a record he can no longer see", answer("leaky"), [], [hidden], scope)
    history.save_turn(harish, cid, "answer from a different access scope", answer("old scope"), [], [visible], "other-scope")

    c = TestClient(app)
    _login(c, harish, "198.51.100.21")
    chats = c.get("/api/chats").json()
    check(len(chats) == 1 and chats[0]["chat_id"] == cid and chats[0]["turn_count"] == 4,
          "chat list shows one conversation with 4 turns (chat-wise, not question-wise)")
    turns = c.get(f"/api/chats/{cid}").json()["turns"]
    check([bool(t["response"]) for t in turns] == [True, True, False, False],
          "reopening shows stored answers, but hides ones built on records now out of scope or from another access scope")
    ctx = _context(p, ChatRequest(question="next", chat_id=cid))
    check([t["answer"] for t in ctx] == ["first answer", "second answer"],
          "follow-up context uses only answers the user may still see")

    o = TestClient(app)
    _login(o, other, "198.51.100.22")
    check(o.get(f"/api/chats/{cid}").status_code == 404, "another employee can't open the chat (404)")
    check(cid not in [x["chat_id"] for x in o.get("/api/chats").json()], "another employee doesn't see it listed")
    o.delete(f"/api/chats/{cid}")
    check(c.get(f"/api/chats/{cid}").status_code == 200, "another employee can't delete it")
    c.delete(f"/api/chats/{cid}")
    check(c.get(f"/api/chats/{cid}").status_code == 404, "the owner can delete it")
    check(c.get("/api/chats").status_code == 200 and TestClient(app).get("/api/chats").status_code == 401,
          "chat list requires sign-in")


def test_chat_live():
    print("chat follow-up (live Gemini calls)")
    from app import history
    history._store = history._Memory()
    c = TestClient(app)
    _login(c, emp("Harish Gowda"), "198.51.100.23")
    a = c.post("/api/chat", json={"question": "Do I need a change request to deploy to production?"}).json()
    b = c.post("/api/chat", json={"question": "And for infrastructure changes?", "chat_id": a["chat_id"]}).json()
    check(bool(a.get("chat_id")) and b.get("chat_id") == a["chat_id"], "a live follow-up lands in the same chat")
    turns = c.get(f"/api/chats/{a['chat_id']}").json()["turns"]
    check(len(turns) == 2 and all(t["response"] for t in turns), "the chat holds both turns with their answers")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()
    test_rules()
    test_http()
    test_leaks()
    test_chats()
    if args.agent:
        test_agent()
        test_chat_live()
    print(f"\n{'ALL PASSED' if not failures else f'{len(failures)} FAILED'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
