"""Tools the agent can call. Each instance is bound to the signed-in user (a Principal); the model cannot change it.

Every tool returns plain JSON-able dicts. `seen` records every record ID returned to the model, so
the agent can later reject citations to records the model never actually received.
"""
from google.genai import types

from app.access import Principal, can_see
from app.cases import compare_groups
from app.kb import directory
from app.retrieval import Hit, retriever
from app.schema import Chunk

HIT_CHARS = 1500  # text per search hit shown to the model
RELATED_CHARS = 400  # text per linked record
RECORD_CHARS = 6000  # text for get_record


def _clip(text: str, n: int) -> str:
    return text if len(text) <= n else text[:n].rstrip() + " …[truncated; call get_record for the full text]"


class AgentTools:
    def __init__(self, principal: Principal, question: str = ""):
        self.principal = principal
        self.question = question
        self.r = retriever()
        self.d = directory()
        self.seen: dict[str, Chunk] = {}  # record_id -> chunk the model was shown
        self.withheld_count = 0
        self.withheld_contacts: list[str] = []
        self.compared: set[frozenset] = set()  # case groups already compared in this conversation turn
        self.case_groups: list[dict] = []  # every compared group, for the response

    # ------------------------------------------------------------ helpers

    def _visible(self, record_id: str) -> Chunk | None:
        c = self.r.record(record_id)
        return c if c and can_see(self.principal, c) else None

    def _person(self, eid: str) -> str:
        e = self.d.employees.get(eid)
        if not e:
            return eid
        status = "" if e["status"] == "active" else f", {e['status'].upper()}"
        return f"{e['name']} ({eid}, {e['role']}{status})"

    def _signals(self, c: Chunk) -> dict:
        s = c.signals
        out = {"last_updated": c.last_updated, "days_since_update": s.days_since_update}
        if s.open_update_request_ids:
            out["open_update_requests"] = s.open_update_request_ids
        if s.inactive_people_mentioned:
            out["names_people_no_longer_active"] = [self._person(p) for p in s.inactive_people_mentioned]
        if s.owners_inactive:
            out["owners_no_longer_active"] = [self._person(p) for p in s.owners_inactive]
        if s.later_mention_ids:
            out["newer_records_referencing_this"] = len(s.later_mention_ids)
        return out

    def _card(self, h: Hit | Chunk, chars: int, text: str | None = None) -> dict:
        c = h.chunk if isinstance(h, Hit) else h
        self.seen.setdefault(c.record_id, c)
        card = {
            "record_id": c.record_id,
            "source": c.source_type,
            "title": c.title,
            "status": c.status,
            "signals": self._signals(c),
            "text": _clip(text if text is not None else c.text, chars),
        }
        if isinstance(h, Hit) and h.via != "search":
            card["linked_via"] = h.via
        return card

    # ------------------------------------------------------------ tools

    def search_docs(self, query: str) -> dict:
        res = self.r.search(query, self.principal, k=8)
        self.withheld_count = max(self.withheld_count, res.withheld_count)
        for e in res.withheld_contacts:
            if e not in self.withheld_contacts:
                self.withheld_contacts.append(e)
        out = {
            "results": [self._card(h, HIT_CHARS) for h in res.hits],
            "linked_records": [self._card(h, RELATED_CHARS) for h in res.related],
        }
        groups = [g for g in res.case_groups if frozenset(c.record_id for c in g) not in self.compared]
        if groups:
            self.compared.update(frozenset(c.record_id for c in g) for g in groups)
            for g in groups:
                for c in g:
                    self.seen.setdefault(c.record_id, c)
            compared = compare_groups(self.question or query, groups)
            self.case_groups.extend(compared)
            if compared:
                out["similar_past_cases"] = compared
        if res.withheld_count:
            out["restricted_records_withheld"] = {
                "count": res.withheld_count,
                "note": "Relevant confidential records exist that this user may not see. Do not guess their content.",
                "access_contacts": [self._person(e) for e in res.withheld_contacts],
            }
        return out

    def get_record(self, record_id: str) -> dict:
        c = self._visible(record_id.strip().upper())
        if not c:
            return {"error": f"{record_id} not found or not available to this user."}
        card = self._card(c, RECORD_CHARS, text=self.r.record_text(c.record_id))
        card["owners"] = [self._person(o) for o in c.owner_employee_ids]
        card["references"] = sorted(self.r.out_links[c.record_id])
        return card

    def get_related(self, record_id: str) -> dict:
        rid = record_id.strip().upper()
        c = self._visible(rid)
        if not c:
            return {"error": f"{record_id} not found or not available to this user."}
        relations = {}
        for t in c.signals.open_update_request_ids:
            relations.setdefault(t, "open update request against this record")
        for t in self.r.out_links[rid]:
            relations.setdefault(t, "referenced by this record")
        for t in self.r.in_links[rid]:
            relations.setdefault(t, "references this record")
        items, hidden = [], 0
        for t, rel in relations.items():
            tc = self._visible(t)
            if not tc:
                hidden += 1
                continue
            card = self._card(tc, RELATED_CHARS)
            card["relation"] = rel
            items.append(card)
        items.sort(key=lambda x: x["signals"]["last_updated"], reverse=True)
        out = {"record_id": rid, "related": items[:15]}
        if hidden:
            out["restricted_related_withheld"] = hidden
        return out

    def _may_see_leave_reason(self, employee_id: str) -> bool:
        """HR notes (e.g. the reason for leave) are health/leave personal data (POL-36)."""
        p = self.principal
        dept = self.d.employees[employee_id]["department_id"]
        return (p.is_system or p.employee_id == employee_id or p.has("hr_operations") or p.has("compliance_auditor")
                or (p.has("hr_business_partner") and dept in p.hrbp_department_ids))

    def _may_see_leave_dates(self, employee_id: str) -> bool:
        """Leave dates are also visible to the person's management chain (they plan around them)."""
        return self._may_see_leave_reason(employee_id) or employee_id in self.principal.reports

    def lookup_person(self, name_or_id: str) -> dict:
        q = name_or_id.strip().lower()
        matches = [e for eid, e in self.d.employees.items() if eid.lower() == q or q in e["name"].lower()]
        if not matches:
            return {"error": f"No employee matching '{name_or_id}'."}
        out = []
        for e in matches[:5]:
            eid = e["employee_id"]
            p = {
                "employee_id": eid,
                "name": e["name"],
                "role": e["role"],
                "team": self.d.teams[e["team_id"]]["name"],
                "department": self.d.departments[e["department_id"]]["name"],
                "status": e["status"],
                "manager": self._person(e["manager_id"]) if e.get("manager_id") else None,
            }
            if e.get("exit_date"):  # the bare fact and date someone left is not personal data
                p["exit_date"] = e["exit_date"]
            # Leave dates and HR notes are personal data; who sees them follows POL-36.
            if self._may_see_leave_dates(eid):
                for k in ("leave_from", "leave_until"):
                    if e.get(k):
                        p[k] = e[k]
            if e.get("notes") and self._may_see_leave_reason(eid):
                p["notes"] = e["notes"]
            if e["status"] != "active":
                alt = self.d.active_contact_for(eid)
                p["route_to_instead"] = self._person(alt) if alt else None
            out.append(p)
        return {"people": out}

    def find_owner(self, system_or_policy: str) -> dict:
        q = system_or_policy.strip()
        c = self._visible(q.upper())
        if c and c.source_type == "policy" and c.owner_team_id:
            team = self.d.teams[c.owner_team_id]
            lead = self.d.active_contact_for(team["lead_employee_id"])
            return {"policy": c.record_id, "owner_team": team["name"], "contact": self._person(lead) if lead else None}
        ql = q.lower()
        systems = [s for s in self.d.systems.values() if ql in s["name"].lower() or s["system_id"].lower() == ql]
        if not systems:
            return {"error": f"No system or policy matching '{system_or_policy}'."}
        out = []
        for s in systems[:3]:
            team = self.d.teams[s["owner_team_id"]]
            lead = self.d.active_contact_for(team["lead_employee_id"])
            out.append({
                "system_id": s["system_id"],
                "system": s["name"],
                "owner_team": team["name"],
                "contact": self._person(lead) if lead else None,
                "access_process": s["access_request_process_summary"],
            })
        return {"systems": out}

    # ------------------------------------------------------------ dispatch

    def call(self, name: str, args: dict) -> dict:
        fn = {
            "search_docs": self.search_docs,
            "get_record": self.get_record,
            "get_related": self.get_related,
            "lookup_person": self.lookup_person,
            "find_owner": self.find_owner,
        }.get(name)
        if not fn:
            return {"error": f"Unknown tool {name}"}
        try:
            return fn(**args)
        except TypeError as e:
            return {"error": f"Bad arguments for {name}: {e}"}


def _fn(name: str, description: str, props: dict, required: list[str]) -> types.FunctionDeclaration:
    return types.FunctionDeclaration(
        name=name,
        description=description,
        parameters_json_schema={"type": "object", "properties": props, "required": required},
    )


_STR = {"type": "string"}

SUBMIT_ANSWER = _fn(
    "submit_answer",
    "Submit the final answer. Call exactly once, when done researching.",
    {
        "answer": {"type": "string", "description": "Markdown answer. Cite records inline as [RECORD-ID]."},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "conflicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "kind": {"type": "string", "enum": ["policy_vs_practice", "conflicting_resolutions", "source_vs_source"]},
                    "summary": {"type": "string", "description": "One sentence: what disagrees, with dates."},
                    "record_ids": {"type": "array", "items": _STR},
                    "current_view": {"type": "string", "description": "record_id that reflects current reality, or empty if unclear"},
                },
                "required": ["kind", "summary", "record_ids", "current_view"],
            },
        },
        "stale_sources": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"record_id": _STR, "reason": _STR},
                "required": ["record_id", "reason"],
            },
        },
        "fallback": {
            "type": "object",
            "description": "Who the user should contact when the answer is uncertain or needs a human decision.",
            "properties": {
                "needed": {"type": "boolean"},
                "contact_employee_id": {"type": "string", "description": "An ACTIVE employee_id, or empty"},
                "reason": _STR,
            },
            "required": ["needed", "contact_employee_id", "reason"],
        },
    },
    ["answer", "confidence", "conflicts", "stale_sources", "fallback"],
)

DECLARATIONS = [
    _fn("search_docs",
        "Hybrid search over policies, Confluence, ServiceNow tickets, emails and Slack. Returns the best records "
        "(with staleness signals) plus linked records. Search again with different wording if results miss.",
        {"query": _STR}, ["query"]),
    _fn("get_record", "Full text, owners and references of one record, e.g. 'POL-01' or 'RITM-20538'.",
        {"record_id": _STR}, ["record_id"]),
    _fn("get_related",
        "Records linked to a record: open update requests against it, records it references, records that "
        "reference it. Use it to find how a policy is applied in practice.",
        {"record_id": _STR}, ["record_id"]),
    _fn("lookup_person",
        "Employee directory: role, team, status (active / exited / on_leave) and who to route to instead.",
        {"name_or_id": _STR}, ["name_or_id"]),
    _fn("find_owner", "Owning team, active contact and access process for a system name or a policy ID.",
        {"system_or_policy": _STR}, ["system_or_policy"]),
    SUBMIT_ANSWER,
]
