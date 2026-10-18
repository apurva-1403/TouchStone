"""Who can see what: role-based access on top of need-to-know. The single source of truth for access decisions.

Mirrors the "Access Roles & Need-to-Know Standard" (POL-36). Every decision returns the rule that allowed it
(`access_basis`), which is shown on confidential citations and written to the audit log.

Classification of a record (computed at ingest, app/ingest.py):
  - not confidential: no personal data and not labelled restricted;
  - confidential, personal data: `personal_data_category` in
      pay | health_or_leave_reason | performance_or_disciplinary | exit_details | personal_contact_or_ids | other;
  - confidential, business: labelled restricted, no personal data; `data_domain` in
      security | finance | hr | commercial | legal | general.

Baseline (everyone): non-confidential records (contractors: only policies and Confluence); anything you are
involved in; business-confidential policies/Confluence of your own department. Roles add grants (ROLE_GRANTS).
"""
from dataclasses import dataclass, field
from functools import lru_cache

from app.kb import directory
from app.schema import Chunk


# Personal-data categories a line manager does not get through their reporting line.
MANAGER_EXCLUDED = {"health_or_leave_reason", "personal_contact_or_ids"}

# Plain-language description of every role (shown on the login page and via /api/roles).
ROLE_CATALOG: dict[str, str] = {
    "employee": "All non-confidential knowledge, plus records you are involved in.",
    "intern": "All non-confidential knowledge, plus records you are involved in.",
    "contractor": "Policies and Confluence documentation, plus records you are involved in.",
    "people_manager": "Confidential records involving your reporting line, except health/leave reasons and personal contact details.",
    "department_head": "Business-confidential records owned by your department.",
    "executive": "Business-confidential records company-wide (no personal data).",
    "hr_business_partner": "All personal data for employees in the departments you support.",
    "hr_operations": "Leave, health, exit and personal-contact data company-wide, plus HR business-confidential records.",
    "compensation_admin": "Pay and performance data company-wide.",
    "payroll_admin": "Pay data company-wide.",
    "finance_controller": "Finance business-confidential records company-wide.",
    "security_admin": "Security business-confidential records company-wide.",
    "legal_counsel": "Legal and commercial business-confidential records company-wide.",
    "compliance_auditor": "All confidential records (read-only, every access flagged for review).",
}
# Company-wide grants: role -> personal-data categories / business domains it may see. Scoped grants
# (HR business partner, people manager, department head) are evaluated in access_basis().
PERSONAL_GRANTS = {
    "hr_operations": {"health_or_leave_reason", "exit_details", "personal_contact_or_ids", "other"},
    "compensation_admin": {"pay", "performance_or_disciplinary"},
    "payroll_admin": {"pay"},
}
DOMAIN_GRANTS = {
    "hr_operations": {"hr"},
    "finance_controller": {"finance"},
    "security_admin": {"security"},
    "legal_counsel": {"legal", "commercial"},
}


@dataclass(frozen=True)
class Principal:
    employee_id: str
    name: str
    title: str
    department_id: str
    team_id: str
    tier: str  # head | lead | ic
    employment_type: str = "employee"  # employee | contractor | intern
    roles: tuple = ()
    hrbp_department_ids: frozenset = field(default_factory=frozenset)
    reports: frozenset = field(default_factory=frozenset)  # everyone in this person's reporting line
    is_system: bool = False  # evaluation only; never issued to a user session

    def has(self, role: str) -> bool:
        return role in self.roles


@lru_cache(maxsize=2048)
def principal_for(employee_id: str) -> Principal | None:
    """The principal for an employee who may sign in (exists and has not exited)."""
    d = directory()
    e = d.employees.get(employee_id)
    if not e or e["status"] == "exited":
        return None
    return Principal(employee_id=employee_id, name=e["name"], title=e["role"], department_id=e["department_id"],
                     team_id=e["team_id"], tier=e["tier"], employment_type=e.get("employment_type", "employee"),
                     roles=tuple(e.get("access_roles", ["employee"])),
                     hrbp_department_ids=frozenset(e.get("hrbp_department_ids", [])),
                     reports=frozenset(d.reporting_line(employee_id)))


# Sees everything. Used only by offline evaluation scripts to measure answer quality on the full corpus.
SYSTEM = Principal(employee_id="SYSTEM", name="Evaluation", title="evaluation", department_id="", team_id="",
                   tier="head", roles=("system",), is_system=True)


def owning_departments(c: Chunk) -> set[str]:
    """The record's department, plus for tickets the department of the team that handled it: the dataset tags
    tickets with the requester's department, so an HR query raised by an engineer would otherwise be
    invisible to the HR leadership whose team handled it."""
    owning = {c.department_id}
    if c.source_type == "ticket":
        d = directory()
        owning |= {d.employees[o]["department_id"] for o in c.owner_employee_ids if o in d.employees}
    return owning


def access_basis(p: Principal, c: Chunk) -> str | None:
    """Why `p` may see `c` (a short rule name), or None if they may not."""
    if p.is_system:
        return "evaluation"
    involved = set(c.participant_employee_ids) | set(c.owner_employee_ids)
    if p.employee_id in involved:
        return "involved in this record"
    if p.employment_type == "contractor":  # documentation only, nothing confidential
        return "company-wide" if not c.confidential and c.source_type in ("policy", "confluence") else None
    if not c.confidential:
        return "company-wide"
    if p.has("compliance_auditor"):
        return "compliance_auditor role"
    if not c.personal_data:  # business-confidential
        if c.source_type in ("policy", "confluence") and p.department_id == c.department_id:
            return "own department's restricted document"
        if p.has("department_head") and p.department_id in owning_departments(c):
            return "department_head role"
        if p.has("executive"):
            return "executive role"
        for role, domains in DOMAIN_GRANTS.items():
            if p.has(role) and c.data_domain in domains:
                return f"{role} role ({c.data_domain} records)"
    else:  # personal data
        cat = c.personal_data_category or "other"
        if p.has("hr_business_partner") and c.department_id in p.hrbp_department_ids:
            return "hr_business_partner role (supported department)"
        for role, cats in PERSONAL_GRANTS.items():
            if p.has(role) and cat in cats:
                return f"{role} role ({cat.replace('_', ' ')})"
    if p.has("people_manager") and involved & p.reports and (not c.personal_data or
                                                             (c.personal_data_category or "other") not in MANAGER_EXCLUDED):
        return "people_manager role (your reporting line)"
    return None


def can_see(p: Principal, c: Chunk) -> bool:
    return access_basis(p, c) is not None


def access_contact(c: Chunk) -> str | None:
    """Who to ask for access to a confidential record: the owning department's head (or their active stand-in)."""
    d = directory()
    return d.active_contact_for(d.departments[c.department_id]["head_employee_id"])
