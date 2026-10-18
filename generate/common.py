"""Shared helpers for the AlgoWorks synthetic enterprise dataset.

Everything downstream imports from here: paths, the deterministic RNG, date helpers,
and the Registry that resolves human-readable names -> IDs (and refuses to resolve
anything that doesn't exist upstream, which is what keeps the layers consistent).
"""
from __future__ import annotations

import datetime as dt
import difflib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

SEED = 20260924
SIM_TODAY = dt.date(2026, 9, 24)  # "now" for the simulated company

COMPANY = {
    "name": "AlgoWorks Pvt. Ltd.",
    "short_name": "AlgoWorks",
    "product": "AlgoWorks Fleet",
    "email_domain": "algoworks.io",
    "hq": "Bengaluru",
    "offices": ["Bengaluru", "Pune", "Hyderabad", "Singapore"],
    "fiscal_year_start": "April",
}

# Indian public holidays used for business-day math (2025-2026, national + Karnataka).
HOLIDAYS = {
    "2025-01-26", "2025-03-14", "2025-03-31", "2025-04-14", "2025-04-18", "2025-05-01",
    "2025-08-15", "2025-08-27", "2025-10-02", "2025-10-20", "2025-11-01", "2025-12-25",
    "2026-01-01", "2026-01-26", "2026-03-04", "2026-03-20", "2026-04-03", "2026-04-14",
    "2026-05-01", "2026-08-15", "2026-09-14", "2026-10-02", "2026-10-20", "2026-11-01",
    "2026-11-08", "2026-12-25",
}


def rng(salt: str) -> random.Random:
    """A fresh, deterministic RNG keyed by a salt so generators don't perturb each other."""
    return random.Random(f"{SEED}:{salt}")


# ---------------------------------------------------------------- dates

def d(s: str) -> dt.date:
    return dt.date.fromisoformat(s[:10])


def iso(x: dt.date | dt.datetime) -> str:
    if isinstance(x, dt.datetime):
        return x.strftime("%Y-%m-%dT%H:%M")
    return x.isoformat()


def add_days(s: str, n: int) -> str:
    return iso(d(s) + dt.timedelta(days=n))


def is_business_day(x: dt.date) -> bool:
    return x.weekday() < 5 and x.isoformat() not in HOLIDAYS


def add_business_days(s: str, n: int) -> str:
    cur = d(s)
    step = 1 if n >= 0 else -1
    remaining = abs(n)
    while remaining:
        cur += dt.timedelta(days=step)
        if is_business_day(cur):
            remaining -= 1
    return iso(cur)


def business_days_between(a: str, b: str) -> int:
    """Number of business days strictly after a, up to and including b."""
    cur, end, n = d(a), d(b), 0
    while cur < end:
        cur += dt.timedelta(days=1)
        if is_business_day(cur):
            n += 1
    return n


def ts(date: str, hhmm: str) -> str:
    """'2026-06-02' + '09:14' -> '2026-06-02T09:14'."""
    return f"{date[:10]}T{hhmm}"


def random_date(r: random.Random, start: str, end: str, business_only: bool = True) -> str:
    a, b = d(start), d(end)
    span = (b - a).days
    for _ in range(1000):
        cand = a + dt.timedelta(days=r.randint(0, span))
        if not business_only or is_business_day(cand):
            return iso(cand)
    return iso(a)


def random_time(r: random.Random, start_h: int = 9, end_h: int = 18) -> str:
    return f"{r.randint(start_h, end_h - 1):02d}:{r.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]):02d}"


# ---------------------------------------------------------------- io

def write_json(name: str, obj) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / name
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


def read_json(name: str):
    with (DATA_DIR / name).open("r", encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------- registry

class LookupError_(KeyError):
    pass


class Registry:
    """Name -> entity resolution across all layers.

    Authoring happens by name ("Priya Shah", "Okta SSO", "Hybrid Work Policy");
    the build resolves these to IDs. A miss raises with close-match suggestions
    so typos are caught at build time rather than becoming dangling references.
    """

    def __init__(self):
        self.departments: list[dict] = []
        self.employees: list[dict] = []
        self.teams: list[dict] = []
        self.systems: list[dict] = []
        self.projects: list[dict] = []
        self.policies: list[dict] = []
        self.events: list[dict] = []
        self._idx: dict[str, dict[str, dict]] = {}

    # -- indexing
    def index(self):
        self._idx = {
            "department": {x["name"]: x for x in self.departments},
            "employee": {x["name"]: x for x in self.employees},
            "team": {x["name"]: x for x in self.teams},
            "system": {x["name"]: x for x in self.systems},
            "project": {x["name"]: x for x in self.projects},
            "policy": {x["title"]: x for x in self.policies},
        }
        self.by_id = {}
        for coll, key in ((self.departments, "department_id"), (self.employees, "employee_id"),
                          (self.teams, "team_id"), (self.systems, "system_id"), (self.projects, "project_id"),
                          (self.policies, "policy_id"), (self.events, "event_id")):
            for x in coll:
                self.by_id[x[key]] = x

    def _get(self, kind: str, name: str) -> dict:
        table = self._idx[kind]
        if name in table:
            return table[name]
        close = difflib.get_close_matches(name, table.keys(), n=3, cutoff=0.5)
        raise LookupError_(f"Unknown {kind} {name!r}. Did you mean: {close}")

    # -- typed accessors (return full record)
    def emp(self, name: str) -> dict:
        return self._get("employee", name)

    def team(self, name: str) -> dict:
        return self._get("team", name)

    def system(self, name: str) -> dict:
        return self._get("system", name)

    def project(self, name: str) -> dict:
        return self._get("project", name)

    def policy(self, title: str) -> dict:
        return self._get("policy", title)

    def department(self, name: str) -> dict:
        return self._get("department", name)

    # -- id accessors
    def eid(self, name: str) -> str:
        return self.emp(name)["employee_id"]

    def tid(self, name: str) -> str:
        return self.team(name)["team_id"]

    def sid(self, name: str) -> str:
        return self.system(name)["system_id"]

    def pid(self, name: str) -> str:
        return self.project(name)["project_id"]

    def polid(self, title: str) -> str:
        return self.policy(title)["policy_id"]

    def did(self, name: str) -> str:
        return self.department(name)["department_id"]

    # -- convenience
    def dept_of_emp(self, name: str) -> dict:
        e = self.emp(name)
        return self.by_id[e["department_id"]]

    def first_name(self, name: str) -> str:
        return self.emp(name)["name"].split()[0]

    def email_of(self, name: str) -> str:
        return self.emp(name)["email"]


def slug_email(name: str, domain: str = COMPANY["email_domain"]) -> str:
    parts = [p for p in name.lower().replace("'", "").replace(".", "").split() if p]
    return f"{parts[0]}.{parts[-1]}@{domain}"
