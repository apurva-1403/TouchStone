"""Loads the raw dataset and exposes directory lookups (people, teams, systems).

Used by ingestion (owner resolution, signals) and later by the agent's routing tools.
Never reads the dataset's answer-key fields (see CHUNK_SCHEMA.md §3).
"""
import json
from functools import lru_cache

from app import config

SOURCE_FILES = {
    "policy": "policies",
    "ticket": "tickets",
    "email": "emails",
    "slack": "slack",
    "confluence": "confluence",
}
ID_FIELD = {
    "policy": "policy_id",
    "ticket": "ticket_id",
    "email": "thread_id",
    "slack": "conversation_id",
    "confluence": "doc_id",
}


def _load(name: str):
    with open(config.DATA_DIR / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)


class Directory:
    def __init__(self):
        self.departments = {d["department_id"]: d for d in _load("departments")}
        self.employees = {e["employee_id"]: e for e in _load("employees")}
        self.teams = {t["team_id"]: t for t in _load("teams")}
        self.systems = {s["system_id"]: s for s in _load("systems")}
        self.projects = {p["project_id"]: p for p in _load("projects")}

    def is_active(self, employee_id: str) -> bool:
        e = self.employees.get(employee_id)
        return bool(e) and e["status"] == "active"

    def name(self, employee_id: str) -> str:
        e = self.employees.get(employee_id)
        return e["name"] if e else employee_id

    def team_lead(self, team_id: str | None) -> str | None:
        t = self.teams.get(team_id or "")
        return t["lead_employee_id"] if t else None

    def manager_chain(self, employee_id: str):
        """Yields managers upward, for routing around an inactive owner."""
        seen = set()
        cur = self.employees.get(employee_id, {}).get("manager_id")
        while cur and cur not in seen:
            seen.add(cur)
            yield cur
            cur = self.employees.get(cur, {}).get("manager_id")

    def reporting_line(self, employee_id: str) -> set[str]:
        """Everyone who reports to this person, directly or indirectly."""
        if not hasattr(self, "_reports"):
            self._reports: dict[str, list[str]] = {}
            for eid, e in self.employees.items():
                if e.get("manager_id"):
                    self._reports.setdefault(e["manager_id"], []).append(eid)
        out, todo = set(), list(self._reports.get(employee_id, []))
        while todo:
            x = todo.pop()
            if x not in out:
                out.add(x)
                todo.extend(self._reports.get(x, []))
        return out

    def active_contact_for(self, employee_id: str) -> str | None:
        """The person to route to: the employee if active, else the nearest active manager."""
        if self.is_active(employee_id):
            return employee_id
        return next((m for m in self.manager_chain(employee_id) if self.is_active(m)), None)


@lru_cache(maxsize=1)
def directory() -> Directory:
    return Directory()


def load_sources() -> dict[str, list[dict]]:
    return {st: _load(fname) for st, fname in SOURCE_FILES.items()}
