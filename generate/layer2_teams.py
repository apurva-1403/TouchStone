"""Layer 2 - Teams (18 original + 45 added in Layer 1b = 63). Patches employees' team_id.

Exited employees keep their historical team_id but are not listed as current members.
"""
from __future__ import annotations

from layer1_employees import TEAM_KEYS

TEAM_ORDER = [
    "ENG-PLAT", "ENG-FE", "ENG-DATA",
    "IT-IAM", "IT-SD", "IT-CLOUD",
    "SALES-ENT", "SALES-OPS", "SALES-CS",
    "HR-TA", "HR-OPS", "HR-LD",
    "FIN-AP", "FIN-FPA", "FIN-PAY",
    "MKT-BRAND", "MKT-DG", "MKT-PMM",
]

TEAM_CHARTERS = {
    "ENG-PLAT": ("Owns the AlgoWorks Fleet core API platform, service infrastructure code, Jira and GitHub administration. "
                 "Runs the v4 API migration.", "#eng-platform"),
    "ENG-FE": ("Owns the customer portal (web) and the AlgoWorks Fleet Driver mobile apps (Android/iOS), plus QA automation.",
               "#eng-frontend"),
    "ENG-DATA": ("Owns Snowflake, the analytics/ELT pipelines, Metabase BI, and ML models for ETA prediction and route scoring.",
                 "#eng-data"),
    "IT-IAM": ("Identity & access management (Okta, VPN, 1Password), access request fulfilment, security engineering, "
               "phishing/awareness programme and compliance follow-ups.", "#it-access-requests"),
    "IT-SD": ("First and second line IT support, laptops/endpoints (Intune), Microsoft 365, Slack, Confluence, "
              "ServiceNow administration and the Bengaluru/Pune office networks.", "#it-helpdesk"),
    "IT-CLOUD": ("AWS accounts, Kubernetes/ArgoCD deployment platform, Datadog monitoring, on-call tooling and "
                 "infrastructure change management.", "#devops-sre"),
    "SALES-ENT": ("New-logo and expansion sales for enterprise logistics customers in India and APAC.", "#sales-team"),
    "SALES-OPS": ("Salesforce administration, CPQ, deal desk & discount approvals, sales reporting and revenue analytics.",
                  "#sales-ops"),
    "SALES-CS": ("Customer success management, Tier 1/2 technical support (Zendesk) and technical account management.",
                 "#customer-success"),
    "HR-TA": ("Recruiting, campus hiring, employer branding and Greenhouse ATS.", "#talent-acquisition"),
    "HR-OPS": ("Onboarding/offboarding, HR business partnering, Darwinbox HRMS, leave & policy queries.", "#people-ops"),
    "HR-LD": ("Learning programmes, manager development, LearnHub LMS and L&D reimbursements.", "#learning"),
    "FIN-AP": ("Vendor onboarding, purchase orders, accounts payable, employee expense reimbursements (Zoho Expense).",
               "#finance"),
    "FIN-FPA": ("Budgeting, forecasting, the annual operating plan, NetSuite reporting and SaaS spend tracking.",
                "#finance"),
    "FIN-PAY": ("Customer billing (Chargebee), payroll (Keka), statutory compliance and revenue recognition.",
                "#finance"),
    "MKT-BRAND": ("Content, brand design, video, social media and the corporate website.", "#marketing"),
    "MKT-DG": ("Campaigns, HubSpot marketing automation, paid acquisition, email marketing and growth analytics.",
               "#demand-gen"),
    "MKT-PMM": ("Positioning, launches, sales enablement, competitive intelligence and solutions marketing.",
                "#product-marketing"),
}


def build_teams(departments: list[dict], employees: list[dict]) -> list[dict]:
    from layer1b_workforce import NEW_TEAMS
    dept_by_code = {x["code"]: x for x in departments}
    charters = dict(TEAM_CHARTERS)
    charters.update({k: (ch, sl) for k, (_n, _d, ch, sl, _lt) in NEW_TEAMS.items()})
    teams = []
    for i, key in enumerate(TEAM_ORDER + list(NEW_TEAMS)):
        name, dept_code = TEAM_KEYS[key]
        team_id = f"TEAM-{i + 1:02d}"
        members = [e for e in employees if e["_team_key"] == key]
        lead = [e for e in members if e["tier"] == "lead"]
        assert len(lead) == 1, f"team {key} must have exactly one lead"
        current = [e for e in members if e["status"] != "exited"]
        charter, channel = charters[key]
        teams.append({
            "team_id": team_id,
            "name": name,
            "department_id": dept_by_code[dept_code]["department_id"],
            "member_employee_ids": [e["employee_id"] for e in current],
            "lead_employee_id": lead[0]["employee_id"],
            "charter": charter,
            "slack_channel": channel,
        })
        for e in members:
            e["team_id"] = team_id
    assert len(teams) == len(TEAM_ORDER) + len(NEW_TEAMS) == 63
    return teams
