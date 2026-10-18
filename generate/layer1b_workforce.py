"""Layer 1b - Workforce expansion to 1,000 people, plus access roles.

The 100 hand-authored people in layer1_employees.ROSTER keep their IDs (EMP-001..100) and roles, because the
80 curated events are written against them. This layer adds 900 generated people (EMP-101..1000, IDs in
join-date order among themselves), 3 new departments and 45 new teams, then assigns every employee an
`employment_type` and `access_roles` (the RBAC roles TouchStone enforces; see app/access.py and the
"Access Roles & Need-to-Know Standard" policy).

Rules that keep the curated scenarios intact:
- generated people never take a job title that a scenario relies on being unique or vacant
  (e.g. no new "Data Protection Officer", no second "Data Engineering Manager");
- generated people are never team leads of the original 18 teams or heads of the original 6 departments;
- every generated name is unique and differs from every roster name.
"""
from __future__ import annotations

from common import rng

TARGET_HEADCOUNT = 1000

NEW_DEPARTMENTS = [
    ("DEPT-07", "Product Management", "PM", "Product strategy, roadmap, product design and user research for AlgoWorks Fleet."),
    ("DEPT-08", "Legal & Compliance", "LEGAL", "Commercial contracts, privacy, regulatory compliance and internal audit."),
    ("DEPT-09", "Executive Office", "EXEC", "CEO, COO and the office of the CEO."),
]

# Department totals including the original roster (sums to 1,000).
DEPT_TARGETS = {"ENG": 380, "IT": 90, "SALES": 260, "HR": 55, "FIN": 60, "MKT": 75, "PM": 50, "LEGAL": 20, "EXEC": 10}

# New department heads (fixed, so docs and personas can name them).
NEW_HEADS = {
    "PM": ("Kiran Malhotra", "VP Product", "2021-04-05"),
    "LEGAL": ("Revathi Krishnaswamy", "General Counsel", "2021-09-13"),
    "EXEC": ("Rajiv Bhattacharya", "Chief Executive Officer", "2019-01-07"),
}

# team_key -> (name, dept_code, charter, slack channel, lead title)
NEW_TEAMS = {
    "ENG-ROUTE": ("Routing & Optimisation", "ENG", "Route optimisation engine, ETA models in production and dispatch constraints.", "#eng-routing", "Engineering Manager, Routing"),
    "ENG-TELEM": ("Telematics Ingestion", "ENG", "Device gateways, Kinesis streams and the telematics ingestion pipeline.", "#eng-telematics", "Engineering Manager, Telematics"),
    "ENG-MOBILE": ("Driver Mobile Apps", "ENG", "AlgoWorks Fleet Driver apps for Android and iOS: offline sync, check-ins, proof of delivery.", "#eng-mobile", "Engineering Manager, Mobile"),
    "ENG-INTEG": ("Public API & Integrations", "ENG", "Public REST API, webhooks, ERP/TMS connectors and the partner sandbox.", "#eng-integrations", "Engineering Manager, Integrations"),
    "ENG-BILLING": ("Billing & Payments Engineering", "ENG", "Subscription billing integration (Chargebee), invoicing and usage metering.", "#eng-billing", "Engineering Manager, Billing"),
    "ENG-QE": ("Quality Engineering", "ENG", "Test automation frameworks, release quality gates and performance testing.", "#eng-qa", "Quality Engineering Manager"),
    "ENG-ML": ("Machine Learning Platform", "ENG", "Feature store, model training pipelines and model serving.", "#eng-ml", "Engineering Manager, ML Platform"),
    "ENG-DEVEX": ("Developer Experience", "ENG", "CI pipelines, build tooling, internal developer portal and service templates.", "#eng-devex", "Engineering Manager, Developer Experience"),
    "ENG-APPSEC": ("Application Security", "ENG", "Secure code review, SAST/DAST, dependency scanning and the bug bounty programme.", "#eng-appsec", "Application Security Manager"),
    "ENG-MAPS": ("Maps & Geofencing", "ENG", "Map tiles, geocoding, geofences and location accuracy.", "#eng-maps", "Engineering Manager, Maps"),
    "ENG-DISPATCH": ("Dispatch & Scheduling", "ENG", "Dispatch console, job scheduling and driver assignment.", "#eng-dispatch", "Engineering Manager, Dispatch"),
    "ENG-INSIGHTS": ("Customer Analytics", "ENG", "Customer-facing reports, dashboards and scheduled exports.", "#eng-insights", "Engineering Manager, Customer Analytics"),
    "ENG-RELIAB": ("Performance & Reliability", "ENG", "Service performance, capacity planning and reliability engineering for the core platform.", "#eng-reliability", "Engineering Manager, Reliability"),
    "ENG-DATAPLAT": ("Data Platform", "ENG", "Streaming and batch data infrastructure, data quality and lineage.", "#eng-dataplatform", "Engineering Manager, Data Platform"),
    "ENG-EV": ("EV & Energy", "ENG", "Electric-vehicle charging, battery telemetry and energy-cost features.", "#eng-ev", "Engineering Manager, EV"),
    "ENG-ARCH": ("Architecture", "ENG", "Technical architecture, design reviews and platform standards.", "#eng-architecture", "Principal Architect"),
    "IT-NET": ("Network & Workplace Technology", "IT", "Office networks, meeting-room technology and workplace IT for all four offices.", "#it-network", "Network & Workplace Lead"),
    "IT-SECOPS": ("Security Operations", "IT", "SOC monitoring, incident response, vulnerability management and threat intelligence.", "#secops", "Security Operations Manager"),
    "IT-GRC": ("IT Governance & Risk", "IT", "IT risk register, ISO 27001 controls, vendor security reviews and audit evidence.", "#it-grc", "IT Governance Manager"),
    "SALES-APAC": ("APAC Sales", "SALES", "New business and expansion across Singapore, Malaysia and Indonesia.", "#sales-apac", "APAC Sales Director"),
    "SALES-WEST": ("India West Sales", "SALES", "Mid-market and enterprise sales for Maharashtra and Gujarat.", "#sales-west", "Regional Sales Manager, West"),
    "SALES-NORTH": ("India North Sales", "SALES", "Mid-market and enterprise sales for Delhi NCR and North India.", "#sales-north", "Regional Sales Manager, North"),
    "SALES-SOUTH": ("India South Sales", "SALES", "Mid-market and enterprise sales for Karnataka, Tamil Nadu and Telangana.", "#sales-south", "Regional Sales Manager, South"),
    "SALES-SDR": ("Sales Development", "SALES", "Outbound prospecting and inbound lead qualification.", "#sales-development", "Sales Development Manager"),
    "SALES-T1": ("Technical Support (Tier 1)", "SALES", "First-line customer support via Zendesk, phone and chat.", "#support-tier1", "Support Manager, Tier 1"),
    "SALES-T2": ("Technical Support (Tier 2)", "SALES", "Escalated technical support, bug triage and customer incident communication.", "#support-tier2", "Support Manager, Tier 2"),
    "SALES-ONB": ("Customer Onboarding", "SALES", "Implementation projects for new customers: data migration, device rollout and training.", "#cs-onboarding", "Customer Onboarding Manager"),
    "SALES-PS": ("Professional Services", "SALES", "Paid integrations, custom reports and solution consulting.", "#prof-services", "Professional Services Manager"),
    "SALES-PARTNER": ("Partnerships & Channel", "SALES", "Reseller, OEM and telematics hardware partnerships.", "#partnerships", "Partnerships Manager"),
    "HR-REWARDS": ("Total Rewards & Compensation", "HR", "Salary bands, bonus and incentive plans, benefits and the annual compensation review.", "#total-rewards", "Total Rewards Manager"),
    "HR-HRBP": ("HR Business Partnering", "HR", "HR business partners for Finance, Product, Legal and the Executive Office.", "#hrbp", "Senior HR Business Partner"),
    "HR-ER": ("Employee Relations", "HR", "Workplace investigations, grievances, disciplinary process and policy interpretation.", "#employee-relations", "Employee Relations Manager"),
    "FIN-TAX": ("Tax & Treasury", "FIN", "Direct and indirect tax, transfer pricing, cash management and banking.", "#finance-tax", "Tax & Treasury Manager"),
    "FIN-REVOPS": ("Revenue Operations & Collections", "FIN", "Order-to-cash, collections, credit control and revenue reporting.", "#finance-revops", "Revenue Operations Manager"),
    "FIN-ACC": ("Accounting & Close", "FIN", "General ledger, month-end close, consolidation and statutory audit support.", "#finance-close", "Financial Controller"),
    "MKT-EVENTS": ("Events & Field Marketing", "MKT", "Trade shows, customer events and regional field marketing.", "#marketing-events", "Events Marketing Manager"),
    "MKT-WEBOPS": ("Web & Marketing Operations", "MKT", "Website platform, marketing analytics and campaign operations.", "#marketing-ops", "Marketing Operations Manager"),
    "MKT-COMMS": ("Corporate Communications", "MKT", "Press, analyst relations, internal communications and the town hall.", "#corp-comms", "Corporate Communications Manager"),
    "PM-CORE": ("Core Product", "PM", "Fleet tracking, dispatch and driver-experience product areas.", "#product-core", "Group Product Manager, Core"),
    "PM-PLATFORM": ("Platform Product", "PM", "API, integrations, data and admin product areas.", "#product-platform", "Group Product Manager, Platform"),
    "PM-DESIGN": ("Product Design & Research", "PM", "Product design, design system ownership and user research.", "#product-design", "Head of Design"),
    "PM-GROWTH": ("Growth Product", "PM", "Self-serve onboarding, trials, pricing pages and in-product growth.", "#product-growth", "Group Product Manager, Growth"),
    "LEGAL-COMM": ("Commercial Legal", "LEGAL", "Customer and vendor contracts, MSAs, NDAs and negotiation support.", "#legal", "Senior Legal Counsel"),
    "LEGAL-PRIV": ("Privacy, Compliance & Audit", "LEGAL", "Privacy programme, regulatory compliance, internal audit and access reviews of confidential data.", "#compliance", "Compliance & Internal Audit Manager"),
    "EXEC-OFFICE": ("Office of the CEO", "EXEC", "CEO staff, strategy, board relations and company operations.", "#office-of-ceo", "Chief Operating Officer"),
}

# Which department the new departments' heads sit in (their first team).
HEAD_TEAM = {"PM": "PM-CORE", "LEGAL": "LEGAL-PRIV", "EXEC": "EXEC-OFFICE"}

# IC job titles by team (generated people get one of these; never a scenario-critical title).
IC_TITLES = {
    "ENG": ["Software Engineer", "Software Engineer II", "Senior Software Engineer", "Staff Software Engineer",
            "Backend Engineer", "Full-Stack Engineer", "Site Reliability Engineer", "Data Engineer", "QA Engineer"],
    "ENG-MOBILE": ["Android Engineer", "iOS Engineer", "Senior Mobile Engineer", "Mobile QA Engineer"],
    "ENG-FE": ["Frontend Engineer", "Senior Frontend Engineer", "UI Engineer", "QA Automation Engineer"],
    "ENG-QE": ["QA Engineer", "Senior QA Engineer", "Performance Test Engineer", "SDET"],
    "ENG-ML": ["Machine Learning Engineer", "Senior ML Engineer", "MLOps Engineer", "Data Scientist"],
    "ENG-DATA": ["Data Engineer", "Analytics Engineer", "Senior Data Engineer", "Data Analyst"],
    "ENG-DATAPLAT": ["Data Engineer", "Senior Data Engineer", "Data Platform Engineer"],
    "ENG-APPSEC": ["Application Security Engineer", "Security Engineer", "Product Security Analyst"],
    "ENG-ARCH": ["Solutions Architect", "Senior Architect"],
    "IT": ["IT Support Engineer (L1)", "IT Support Engineer (L2)", "Systems Administrator", "Endpoint Engineer", "Cloud Engineer", "DevOps Engineer"],
    "IT-IAM": ["IAM Analyst", "IAM Engineer", "Security Analyst"],
    "IT-SECOPS": ["SOC Analyst", "Senior SOC Analyst", "Incident Responder", "Vulnerability Management Analyst"],
    "IT-GRC": ["IT Risk Analyst", "GRC Analyst", "IT Auditor"],
    "IT-NET": ["Network Engineer", "Workplace Technology Specialist", "AV & Meeting Room Technician"],
    "SALES": ["Account Executive", "Senior Account Executive", "Enterprise Account Executive", "Sales Engineer", "Account Manager"],
    "SALES-SDR": ["Sales Development Representative", "Senior SDR"],
    "SALES-T1": ["Support Engineer", "Support Specialist", "Customer Support Associate"],
    "SALES-T2": ["Senior Support Engineer", "Support Engineer II", "Escalation Engineer"],
    "SALES-CS": ["Customer Success Manager", "Technical Account Manager", "Customer Success Associate"],
    "SALES-ONB": ["Implementation Consultant", "Onboarding Specialist", "Implementation Project Manager"],
    "SALES-PS": ["Solutions Consultant", "Integration Consultant"],
    "SALES-OPS": ["Sales Operations Analyst", "Deal Desk Analyst", "Revenue Analyst", "CRM Analyst"],
    "SALES-PARTNER": ["Partner Manager", "Channel Account Manager"],
    "HR": ["HR Generalist", "HR Operations Associate", "HR Coordinator"],
    "HR-TA": ["Recruiter", "Technical Recruiter", "Recruiting Coordinator", "Sourcer"],
    "HR-OPS": ["HR Operations Associate", "HR Operations Specialist", "HRIS Analyst"],
    "HR-LD": ["L&D Specialist", "Instructional Designer", "L&D Coordinator"],
    "HR-REWARDS": ["Compensation Analyst", "Benefits Specialist", "Total Rewards Analyst"],
    "HR-HRBP": ["HR Business Partner"],
    "HR-ER": ["Employee Relations Specialist", "Employee Relations Advisor"],
    "FIN": ["Financial Analyst", "Accountant", "Senior Accountant"],
    "FIN-PAY": ["Payroll Specialist", "Payroll Analyst", "Billing Analyst"],
    "FIN-AP": ["Accounts Payable Analyst", "Procurement Analyst", "Accounts Payable Specialist"],
    "FIN-FPA": ["FP&A Analyst", "Senior Financial Analyst"],
    "FIN-TAX": ["Tax Analyst", "Treasury Analyst"],
    "FIN-REVOPS": ["Collections Specialist", "Revenue Accountant", "Credit Controller"],
    "FIN-ACC": ["Accountant", "Senior Accountant", "GL Accountant"],
    "MKT": ["Marketing Specialist", "Content Writer", "Designer", "Marketing Analyst"],
    "MKT-EVENTS": ["Events Manager", "Field Marketing Specialist"],
    "MKT-WEBOPS": ["Web Developer", "Marketing Operations Analyst", "SEO Specialist"],
    "MKT-COMMS": ["Communications Specialist", "PR Manager", "Internal Communications Specialist"],
    "PM": ["Product Manager", "Senior Product Manager", "Associate Product Manager", "Product Analyst"],
    "PM-DESIGN": ["Product Designer", "Senior Product Designer", "UX Researcher", "Content Designer"],
    "LEGAL-COMM": ["Legal Counsel", "Contracts Manager", "Paralegal"],
    "LEGAL-PRIV": ["Privacy Counsel", "Compliance Analyst", "Internal Auditor"],
    "EXEC-OFFICE": ["Chief of Staff", "Strategy Manager", "Executive Assistant", "Business Operations Analyst"],
}

FIRST = """Aarav Aditi Akash Alisha Amitabh Ananya Anika Ankur Anusha Arnav Arpita Asha Ashwin Avani Bhavna Chetan Chitra
Darshan Deepika Dev Dhruv Diya Eshan Gaurav Gayatri Girish Hari Harsha Hemant Ira Isha Jai Janani Jaya Jatin Kabir Kamal
Kavitha Keerthi Kiran Krish Lavanya Madhav Mahesh Maya Mihir Mira Mohan Naina Naveen Nisha Nitin Ojas Omkar Pallavi Parth
Pavan Prakash Pranav Pratibha Preeti Radhika Raghav Rahul Rajat Ramya Ranjit Rashmi Reema Rhea Ritesh Rohini Rudra Sahil
Sakshi Samir Sanjana Santosh Sarita Shalini Shankar Shilpa Shiv Shreya Shyam Simran Smita Sonia Srinivas Sudha Sumit Sunil
Swara Tanmay Tara Tejas Uday Uma Utkarsh Vaibhav Varsha Ved Vidya Vinay Vishal Yamini Yash Zoya Aditya Bharat Charu Dinesh
Ekta Farah Geetika Harini Imran Jyoti Kunal Leela Manoj Nalini Omar Parvati Qasim Rekha Salim Tanya Usha Vikas Wasim
Arjun Bindu Deepa Feroz Gopal Hina Indira Javed Kriti Lokesh Mansi Nikita Pooja Rakesh Seema Tarun Vivek Yusuf
Wei Ling Jun Hui Mei Daniel Sarah Rachel Kevin Grace""".split()
LAST = """Acharya Agarwal Ahuja Ansari Arora Bajaj Banerjee Bansal Basu Bhat Bhatia Bose Chakraborty Chandra Chawla Chopra
Das Dasgupta Desai Dhillon Dixit Dutta Gill Goel Gokhale Goswami Gupta Hegde Iyer Jain Jha Joshi Kamath Kapoor Karnik
Kaur Khan Khanna Kohli Krishnan Kulkarni Kumar Lal Mahajan Malik Mehta Menon Mishra Mukherjee Murthy Nair Naidu Narang
Pandey Parekh Patel Pillai Prasad Puri Qureshi Raghavan Rajan Rao Rastogi Reddy Saini Sarkar Sethi Shah Sharma Shetty
Shukla Singh Sinha Srinivasan Subramanian Suri Talwar Thakur Thomas Tiwari Trivedi Upadhyay Varma Venkatesh Verma Wadhwa
Yadav Zaveri Fernandes Mathew DSouza Pinto Rodrigues Sequeira Lim Tan Ng Wong Chua""".split()
LOCATIONS = [("Bengaluru", 46), ("Pune", 18), ("Hyderabad", 16), ("Singapore", 6), ("Remote (India)", 12), ("Remote (US)", 2)]


def _weighted(r, pairs):
    total = sum(w for _, w in pairs)
    x, acc = r.uniform(0, total), 0.0
    for v, w in pairs:
        acc += w
        if x <= acc:
            return v
    return pairs[-1][0]


def _titles_for(team_key: str, dept: str) -> list[str]:
    return IC_TITLES.get(team_key) or IC_TITLES[dept]


def build_workforce(roster_people: list[dict], team_keys: dict) -> tuple[list[dict], dict]:
    """Returns (generated people, all team keys incl. new ones). Each person is the raw dict shape used by
    layer1 (name, dept code, team_key, tier, role, location, join_date, status, extra)."""
    r = rng("workforce")
    taken = {p["name"] for p in roster_people}
    all_teams = dict(team_keys)
    for key, (name, dept, *_rest) in NEW_TEAMS.items():
        all_teams[key] = (name, dept)

    def new_name() -> str:
        for _ in range(10000):
            n = f"{r.choice(FIRST)} {r.choice(LAST)}"
            if n not in taken:
                taken.add(n)
                return n
        raise RuntimeError("ran out of unique names")

    people = []

    def person(dept, team_key, tier, role, joined, status="active", extra=None, emp_type="employee", loc=None):
        people.append({"name": new_name(), "dept": dept, "team_key": team_key,
                       "tier": tier, "role": role, "location": loc or _weighted(r, LOCATIONS), "join_date": joined,
                       "status": status, "extra": extra or {}, "employment_type": emp_type})
        return people[-1]

    # New department heads (fixed names, which must not collide with anyone in the roster).
    for dept, (name, title, joined) in NEW_HEADS.items():
        assert name not in taken, f"fixed head name {name!r} already used in the roster"
        taken.add(name)
        people.append({"name": name, "dept": dept, "team_key": HEAD_TEAM[dept], "tier": "head", "role": title,
                       "location": "Bengaluru", "join_date": joined, "status": "active", "extra": {}, "employment_type": "employee"})
    # Leads of new teams.
    for key, (_name, dept, _ch, _sl, lead_title) in NEW_TEAMS.items():
        joined = f"{r.randint(2019, 2024)}-{r.randint(1, 12):02d}-{r.randint(1, 28):02d}"
        person(dept, key, "lead", lead_title, joined)

    # Fill departments to target with ICs spread over the department's teams.
    roster_count = {}
    for p in roster_people:
        roster_count[p["dept"]] = roster_count.get(p["dept"], 0) + 1
    for dept, target in DEPT_TARGETS.items():
        have = roster_count.get(dept, 0) + sum(1 for p in people if p["dept"] == dept)
        teams = [k for k, (_n, dcode) in all_teams.items() if dcode == dept]
        for _ in range(target - have):
            key = r.choice(teams)
            joined_year = _weighted(r, [(2019, 4), (2020, 7), (2021, 12), (2022, 16), (2023, 18), (2024, 18), (2025, 16), (2026, 9)])
            month = r.randint(1, 9 if joined_year == 2026 else 12)
            joined = f"{joined_year}-{month:02d}-{r.randint(1, 28):02d}"
            emp_type, role = "employee", r.choice(_titles_for(key, dept))
            if dept in ("ENG", "MKT", "IT") and r.random() < 0.06:
                emp_type = "contractor"
                role = f"Contract {role}"
            elif joined >= "2026-05-01" and r.random() < 0.25:
                emp_type = "intern"
                role = f"{role.split(' (')[0]} Intern"
            status, extra = "active", {}
            roll = r.random()
            if roll < 0.035 and joined < "2025-06-01":
                status = "exited"
                extra = {"exit_date": f"2026-{r.randint(1, 8):02d}-{r.randint(1, 28):02d}"}
            elif roll < 0.055:
                status = "on_leave"
                extra = {"leave_from": f"2026-0{r.randint(7, 9)}-{r.randint(1, 20):02d}",
                         "leave_until": f"2026-{r.randint(10, 12)}-{r.randint(1, 28):02d}",
                         "notes": r.choice(["Parental leave.", "Medical leave.", "Sabbatical.", "Family care leave."])}
            person(dept, key, "ic", role, joined, status, extra, emp_type)
    assert len(roster_people) + len(people) == TARGET_HEADCOUNT, len(roster_people) + len(people)
    return people, all_teams


# ---------------------------------------------------------------- access roles (RBAC)

# Fixed role grants for named roster people (by name); everyone else is assigned by job function below.
ROSTER_ROLES = {
    "Swati Kulkarni": (["hr_business_partner"], ["DEPT-01", "DEPT-02"]),
    "Fatima Sheikh": (["hr_business_partner"], ["DEPT-03", "DEPT-06"]),
    "Geeta Iyengar": (["hr_operations"], []),
    "Rakesh Nair": (["hr_operations"], []),
    "Ayesha Khan": (["hr_operations"], []),
    "Sunita Raghavan": (["hr_operations", "compensation_admin"], []),
    "Vijay Kumar": (["payroll_admin"], []),
    "Vivek Anand": (["executive", "finance_controller"], []),
    "Nikhil Bhatt": (["security_admin"], []),
    "Amit Saxena": (["security_admin"], []),
    "Joseph Mathew": (["security_admin"], []),
    "Sandeep Malhotra": (["security_admin"], []),
}

# By team for generated people (and roster people not named above).
TEAM_ROLES = {
    "IT-IAM": ["security_admin"], "IT-SECOPS": ["security_admin"], "IT-GRC": ["security_admin"],
    "HR-OPS": ["hr_operations"], "HR-REWARDS": ["compensation_admin"], "HR-ER": ["hr_operations"],
    "FIN-PAY": ["payroll_admin"], "LEGAL-COMM": ["legal_counsel"], "LEGAL-PRIV": ["compliance_auditor"],
}
LEAD_ROLES = {"FIN-FPA": ["finance_controller"], "FIN-ACC": ["finance_controller"]}


def assign_access_roles(employees: list[dict], departments: list[dict]):
    """Adds employment_type (if missing), access_roles and hrbp_department_ids to every employee in place."""
    dept_by_code = {x["code"]: x["department_id"] for x in departments}
    unsupported = [dept_by_code[c] for c in ("FIN", "PM", "LEGAL", "EXEC", "HR")]
    hrbps_generated = []
    for e in employees:
        e.setdefault("employment_type", "employee")
        roles = {"employee": ["employee"], "contractor": ["contractor"], "intern": ["intern"]}[e["employment_type"]]
        if e["tier"] == "lead":
            roles.append("people_manager")
        if e["tier"] == "head":
            roles += ["people_manager", "department_head"]
        hrbp_depts: list[str] = []
        if e["name"] in ROSTER_ROLES:
            extra, hrbp_depts = ROSTER_ROLES[e["name"]]
            roles += extra
        elif e["employment_type"] == "employee":
            key = e["_team_key"]
            roles += TEAM_ROLES.get(key, [])
            if e["tier"] == "lead":
                roles += LEAD_ROLES.get(key, [])
            if key == "HR-HRBP":
                roles.append("hr_business_partner")
                hrbps_generated.append(e)
        if e["department_id"] == dept_by_code["EXEC"] and e["tier"] in ("head", "lead"):
            roles.append("executive")
        if e["department_id"] == dept_by_code["LEGAL"] and e["tier"] == "head":
            roles += ["legal_counsel", "compliance_auditor"]
        e["access_roles"] = sorted(set(roles), key=roles.index)
        if hrbp_depts:
            e["hrbp_department_ids"] = hrbp_depts
    # Generated HRBPs cover the departments the two roster HRBPs don't.
    for i, e in enumerate(sorted(hrbps_generated, key=lambda x: x["name"])):
        e["hrbp_department_ids"] = [unsupported[i % len(unsupported)]]
