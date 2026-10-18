"""Layer 1 - Employees.

The roster is hand-authored (names, roles, tiers, join dates) so that every downstream
layer can be written against known people. Structure (IDs, manager chain, email) is
computed. Three tiers: department heads -> team leads -> ICs. Layer 1b adds 900 generated people
(1,000 total) and assigns everyone access roles.

Roster tuple: (name, dept_code, team_key, tier, role, location, join_date, status, extra)
  tier      : "head" | "lead" | "ic"
  team_key  : the team the person sits in (heads sit with the first team of their dept)
  extra     : optional dict (exit_date, leave_from, notes)
"""
from __future__ import annotations

from common import slug_email

# team_key -> (team name, dept_code) ; the team_key is only used inside the generator.
TEAM_KEYS = {
    "ENG-PLAT": ("Platform Backend", "ENG"),
    "ENG-FE": ("Web & Mobile Frontend", "ENG"),
    "ENG-DATA": ("Data & Analytics Engineering", "ENG"),
    "IT-IAM": ("Identity & Access Management", "IT"),
    "IT-SD": ("IT Service Desk & Endpoint", "IT"),
    "IT-CLOUD": ("Cloud Infrastructure & Security", "IT"),
    "SALES-ENT": ("Enterprise Sales", "SALES"),
    "SALES-OPS": ("Sales Operations & Deal Desk", "SALES"),
    "SALES-CS": ("Customer Success & Support", "SALES"),
    "HR-TA": ("Talent Acquisition", "HR"),
    "HR-OPS": ("People Operations", "HR"),
    "HR-LD": ("Learning & Development", "HR"),
    "FIN-AP": ("Accounts Payable & Procurement", "FIN"),
    "FIN-FPA": ("Financial Planning & Analysis", "FIN"),
    "FIN-PAY": ("Billing, Payroll & Compliance", "FIN"),
    "MKT-BRAND": ("Content & Brand", "MKT"),
    "MKT-DG": ("Demand Generation", "MKT"),
    "MKT-PMM": ("Product Marketing", "MKT"),
}

BLR, PUNE, HYD, SG, REMOTE, REMOTE_US = "Bengaluru", "Pune", "Hyderabad", "Singapore", "Remote (India)", "Remote (US)"

ROSTER = [
    # ---------------- Engineering (19)
    ("Arjun Venkataraman", "ENG", "ENG-PLAT", "head", "VP Engineering", BLR, "2022-06-01", "active", {}),
    ("Rohan Mehta", "ENG", "ENG-PLAT", "lead", "Engineering Manager, Platform", BLR, "2022-08-15", "active", {}),
    ("Priya Shah", "ENG", "ENG-PLAT", "ic", "Senior Software Engineer", BLR, "2023-03-14", "active", {}),
    ("Karthik Iyer", "ENG", "ENG-PLAT", "ic", "Software Engineer II", BLR, "2023-09-04", "active", {}),
    ("Sneha Kulkarni", "ENG", "ENG-PLAT", "ic", "Staff Software Engineer", PUNE, "2022-10-17", "active", {}),
    ("Daniel Fernandes", "ENG", "ENG-PLAT", "ic", "Software Engineer", BLR, "2024-06-10", "active", {}),
    ("Tanvi Deshpande", "ENG", "ENG-PLAT", "ic", "Software Engineer", BLR, "2026-08-03", "active", {}),
    ("Meera Krishnan", "ENG", "ENG-FE", "lead", "Engineering Manager, Frontend & Mobile", BLR, "2022-11-01", "active", {}),
    ("Aditya Rao", "ENG", "ENG-FE", "ic", "Senior Frontend Engineer", BLR, "2023-01-23", "active", {}),
    ("Farhan Siddiqui", "ENG", "ENG-FE", "ic", "Android Engineer", HYD, "2023-07-10", "active", {}),
    ("Ishita Bose", "ENG", "ENG-FE", "ic", "Frontend Engineer", REMOTE, "2024-02-19", "active", {}),
    ("Vikram Nair", "ENG", "ENG-FE", "ic", "iOS Engineer", BLR, "2023-11-06", "active", {}),
    ("Neha Agarwal", "ENG", "ENG-FE", "ic", "QA Automation Engineer", PUNE, "2024-09-02", "active", {}),
    ("Suresh Pillai", "ENG", "ENG-DATA", "lead", "Data Engineering Manager", HYD, "2023-01-09", "active", {}),
    ("Ananya Chatterjee", "ENG", "ENG-DATA", "ic", "Senior Data Engineer", HYD, "2023-05-15", "active", {}),
    ("Manish Tiwari", "ENG", "ENG-DATA", "ic", "Analytics Engineer", BLR, "2024-01-08", "active", {}),
    ("Divya Menon", "ENG", "ENG-DATA", "ic", "Data Engineer", HYD, "2024-08-05", "active", {}),
    ("Ravi Shankar", "ENG", "ENG-DATA", "ic", "Machine Learning Engineer", BLR, "2025-03-03", "active", {}),
    ("Pooja Hegde", "ENG", "ENG-DATA", "ic", "Data Analyst", BLR, "2026-07-20", "active", {}),
    # ---------------- IT & Infrastructure (17)
    ("Sandeep Malhotra", "IT", "IT-IAM", "head", "Head of IT & Infrastructure", BLR, "2022-07-01", "active", {}),
    ("Nikhil Bhatt", "IT", "IT-IAM", "lead", "IAM & Security Lead", BLR, "2022-10-03", "active", {}),
    ("Kavya Reddy", "IT", "IT-IAM", "ic", "IAM Analyst", BLR, "2023-04-17", "active", {}),
    ("Amit Saxena", "IT", "IT-IAM", "ic", "Security Engineer", BLR, "2023-08-21", "active", {}),
    ("Lakshmi Narayanan", "IT", "IT-IAM", "ic", "IAM Engineer", BLR, "2024-04-01", "active", {}),
    ("Joseph Mathew", "IT", "IT-IAM", "ic", "Security Analyst", BLR, "2026-06-29", "active", {}),
    ("Pradeep Chauhan", "IT", "IT-IAM", "ic", "Data Protection Officer & Compliance Lead", BLR, "2023-02-13", "exited",
     {"exit_date": "2026-02-28", "notes": "Resigned; DPO responsibilities not formally reassigned at exit."}),
    ("Rajesh Kumar", "IT", "IT-SD", "lead", "IT Service Desk Manager", BLR, "2022-09-12", "active", {}),
    ("Deepak Verma", "IT", "IT-SD", "ic", "IT Support Engineer (L1)", BLR, "2023-06-05", "active", {}),
    ("Shruti Joshi", "IT", "IT-SD", "ic", "IT Support Engineer (L2)", BLR, "2023-02-27", "active", {}),
    ("Mohammed Irfan", "IT", "IT-SD", "ic", "Endpoint Engineer", BLR, "2024-03-11", "active", {}),
    ("Anjali Gupta", "IT", "IT-SD", "ic", "IT Support Engineer (L1)", PUNE, "2024-11-18", "active", {}),
    ("Varun Chandra", "IT", "IT-CLOUD", "lead", "Cloud Infrastructure Lead", BLR, "2023-02-20", "active", {}),
    ("Harish Gowda", "IT", "IT-CLOUD", "ic", "Site Reliability Engineer", BLR, "2023-10-09", "active", {}),
    ("Nandini Rajan", "IT", "IT-CLOUD", "ic", "Cloud Engineer", BLR, "2024-05-06", "active", {}),
    ("Siddharth Jain", "IT", "IT-CLOUD", "ic", "DevOps Engineer", PUNE, "2024-10-14", "active", {}),
    ("Abhishek Yadav", "IT", "IT-CLOUD", "ic", "Site Reliability Engineer", BLR, "2023-12-04", "on_leave",
     {"leave_from": "2026-09-01", "leave_until": "2026-11-30", "notes": "Parental leave."}),
    # ---------------- Sales (17)
    ("Rahul Kapoor", "SALES", "SALES-ENT", "head", "VP Sales", BLR, "2022-09-01", "active", {}),
    ("Natasha D'Souza", "SALES", "SALES-ENT", "lead", "Enterprise Sales Manager", BLR, "2023-04-03", "active", {}),
    ("Aakash Bhatia", "SALES", "SALES-ENT", "ic", "Enterprise Account Executive", BLR, "2023-06-19", "active", {}),
    ("Simran Kaur", "SALES", "SALES-ENT", "ic", "Enterprise Account Executive", BLR, "2024-01-15", "active", {}),
    ("Gaurav Thakur", "SALES", "SALES-ENT", "ic", "Account Executive, APAC", SG, "2025-02-03", "active", {}),
    ("Wei Lin Tan", "SALES", "SALES-ENT", "ic", "Sales Development Representative", SG, "2025-08-11", "active", {}),
    ("Ritika Sharma", "SALES", "SALES-ENT", "ic", "Sales Development Representative", BLR, "2026-08-17", "active", {}),
    ("Vinod Krishnamurthy", "SALES", "SALES-OPS", "lead", "Sales Operations Manager", BLR, "2022-12-05", "active", {}),
    ("Megha Patil", "SALES", "SALES-OPS", "ic", "Salesforce Administrator", BLR, "2023-03-27", "active", {}),
    ("Arun Prasad", "SALES", "SALES-OPS", "ic", "Deal Desk Analyst", BLR, "2024-07-22", "active", {}),
    ("Sonal Mehra", "SALES", "SALES-OPS", "ic", "Sales Operations Analyst", PUNE, "2024-04-15", "active", {}),
    ("Dhruv Malik", "SALES", "SALES-OPS", "ic", "Revenue Analyst", BLR, "2026-08-10", "active", {}),
    ("Anita Desai", "SALES", "SALES-CS", "lead", "Head of Customer Success", PUNE, "2023-01-16", "active", {}),
    ("Kunal Shah", "SALES", "SALES-CS", "ic", "Customer Success Manager", PUNE, "2023-08-07", "active", {}),
    ("Preeti Nambiar", "SALES", "SALES-CS", "ic", "Support Engineer", PUNE, "2024-02-05", "active", {}),
    ("Sameer Khan", "SALES", "SALES-CS", "ic", "Technical Account Manager", BLR, "2023-11-20", "active", {}),
    ("Tara Sequeira", "SALES", "SALES-CS", "ic", "Support Engineer", PUNE, "2026-09-01", "active", {}),
    # ---------------- Human Resources (15)
    ("Sunita Raghavan", "HR", "HR-OPS", "head", "Chief People Officer", BLR, "2022-06-15", "active", {}),
    ("Rohit Sinha", "HR", "HR-TA", "lead", "Talent Acquisition Lead", BLR, "2023-03-06", "active", {}),
    ("Nisha Pandey", "HR", "HR-TA", "ic", "Senior Technical Recruiter", BLR, "2023-05-22", "active", {}),
    ("Akhil Menon", "HR", "HR-TA", "ic", "Recruiter", HYD, "2024-06-03", "active", {}),
    ("Bhavana Shetty", "HR", "HR-TA", "ic", "Recruiting Coordinator", BLR, "2024-10-07", "active", {}),
    ("Ishaan Roy", "HR", "HR-TA", "ic", "Employer Branding Specialist", BLR, "2026-06-30", "active", {}),
    ("Geeta Iyengar", "HR", "HR-OPS", "lead", "People Operations Manager", BLR, "2022-08-01", "active", {}),
    ("Swati Kulkarni", "HR", "HR-OPS", "ic", "HR Business Partner (Engineering & IT)", BLR, "2023-04-10", "active", {}),
    ("Rakesh Nair", "HR", "HR-OPS", "ic", "HR Operations Specialist", BLR, "2023-09-18", "active", {}),
    ("Fatima Sheikh", "HR", "HR-OPS", "ic", "HR Business Partner (Sales & Marketing)", BLR, "2024-03-04", "active", {}),
    ("Ayesha Khan", "HR", "HR-OPS", "ic", "HR Operations Associate", PUNE, "2026-07-06", "active", {}),
    ("Madhavi Srinivasan", "HR", "HR-LD", "lead", "Learning & Development Manager", HYD, "2023-06-12", "active", {}),
    ("Tarun Bhargava", "HR", "HR-LD", "ic", "L&D Specialist", HYD, "2024-01-22", "active", {}),
    ("Leela Krishnan", "HR", "HR-LD", "ic", "Instructional Designer", BLR, "2024-08-19", "active", {}),
    ("Dev Patel", "HR", "HR-LD", "ic", "L&D Coordinator", BLR, "2025-05-12", "active", {}),
    # ---------------- Finance (15)
    ("Vivek Anand", "FIN", "FIN-FPA", "head", "Chief Financial Officer", BLR, "2022-06-01", "active", {}),
    ("Shalini Menon", "FIN", "FIN-AP", "lead", "AP & Procurement Manager", BLR, "2022-11-14", "active", {}),
    ("Ramesh Babu", "FIN", "FIN-AP", "ic", "Accounts Payable Specialist", BLR, "2023-02-06", "active", {}),
    ("Kritika Jain", "FIN", "FIN-AP", "ic", "Procurement Analyst", BLR, "2024-02-12", "active", {}),
    ("Alok Mishra", "FIN", "FIN-AP", "ic", "Accounts Payable Analyst", BLR, "2024-09-16", "active", {}),
    ("Zara Ahmed", "FIN", "FIN-AP", "ic", "Procurement Associate", BLR, "2026-08-24", "active", {}),
    ("Ashwin Raman", "FIN", "FIN-FPA", "lead", "FP&A Manager", BLR, "2023-02-06", "active", {}),
    ("Payal Shah", "FIN", "FIN-FPA", "ic", "Financial Analyst", BLR, "2023-07-24", "active", {}),
    ("Nithin George", "FIN", "FIN-FPA", "ic", "Senior Financial Analyst", BLR, "2023-10-30", "active", {}),
    ("Harsha Vardhan", "FIN", "FIN-FPA", "ic", "Financial Analyst", HYD, "2025-01-06", "active", {}),
    ("Meenakshi Sundaram", "FIN", "FIN-FPA", "ic", "FP&A Analyst", BLR, "2026-09-07", "active", {}),
    ("Deepa Subramanian", "FIN", "FIN-PAY", "lead", "Payroll & Compliance Manager", BLR, "2022-09-19", "active", {}),
    ("Vijay Kumar", "FIN", "FIN-PAY", "ic", "Payroll Specialist", BLR, "2023-05-08", "active", {}),
    ("Anusha Rao", "FIN", "FIN-PAY", "ic", "Billing Analyst", BLR, "2024-04-22", "active", {}),
    ("Sanjay Dutta", "FIN", "FIN-PAY", "ic", "Compliance Analyst", BLR, "2024-11-04", "active", {}),
    # ---------------- Marketing (17)
    ("Kavita Bhatnagar", "MKT", "MKT-PMM", "head", "VP Marketing", BLR, "2022-10-10", "active", {}),
    ("Ankit Chawla", "MKT", "MKT-BRAND", "lead", "Content & Brand Manager", BLR, "2023-05-08", "active", {}),
    ("Riya Sen", "MKT", "MKT-BRAND", "ic", "Content Writer", REMOTE, "2024-01-29", "active", {}),
    ("Omar Farooq", "MKT", "MKT-BRAND", "ic", "Brand Designer", BLR, "2023-09-25", "active", {}),
    ("Nikita Bansal", "MKT", "MKT-BRAND", "ic", "Video Producer", BLR, "2024-07-08", "active", {}),
    ("Shreya Ghosh", "MKT", "MKT-BRAND", "ic", "Content Marketing Specialist", PUNE, "2025-04-07", "active", {}),
    ("Kabir Mehrotra", "MKT", "MKT-BRAND", "ic", "Social Media Manager", BLR, "2026-07-27", "active", {}),
    ("Manoj Venkatesh", "MKT", "MKT-DG", "lead", "Demand Generation Manager", BLR, "2023-07-17", "active", {}),
    ("Aparna Das", "MKT", "MKT-DG", "ic", "Marketing Operations Specialist", BLR, "2024-03-18", "active", {}),
    ("Yash Agrawal", "MKT", "MKT-DG", "ic", "Performance Marketing Specialist", BLR, "2024-11-11", "active", {}),
    ("Chitra Mohan", "MKT", "MKT-DG", "ic", "Email Marketing Specialist", HYD, "2025-06-02", "active", {}),
    ("Ethan Brooks", "MKT", "MKT-DG", "ic", "Growth Analyst", REMOTE_US, "2025-09-15", "active", {}),
    ("Sanya Kapadia", "MKT", "MKT-PMM", "lead", "Product Marketing Lead", BLR, "2023-08-21", "active", {}),
    ("Varsha Pai", "MKT", "MKT-PMM", "ic", "Product Marketing Manager", BLR, "2024-05-20", "active", {}),
    ("Imran Qureshi", "MKT", "MKT-PMM", "ic", "Competitive Intelligence Analyst", BLR, "2025-01-20", "active", {}),
    ("Rohini Pathak", "MKT", "MKT-PMM", "ic", "Solutions Marketing Manager", PUNE, "2024-10-21", "active", {}),
    ("Lavanya Bhat", "MKT", "MKT-PMM", "ic", "Product Marketing Manager", BLR, "2026-09-15", "active", {}),
]


def build_employees(departments: list[dict]) -> list[dict]:
    from layer1b_workforce import assign_access_roles, build_workforce

    dept_by_code = {x["code"]: x for x in departments}
    names = [r[0] for r in ROSTER]
    assert len(names) == len(set(names)), "duplicate names in roster"
    assert len(ROSTER) == 100, f"roster has {len(ROSTER)} people, expected 100"

    # Roster IDs (EMP-001..100) are assigned in join-date order exactly as before the expansion, so the
    # curated events keep their people. Generated people get EMP-101.. in their own join-date order.
    ordered = sorted(ROSTER, key=lambda r: (r[6], r[0]))
    id_by_name = {r[0]: f"EMP-{i + 1:03d}" for i, r in enumerate(ordered)}

    roster_people = [{"name": n, "dept": dc, "team_key": tk, "tier": t, "role": ro, "location": lo, "join_date": j,
                      "status": st, "extra": ex, "employment_type": "employee"}
                     for n, dc, tk, t, ro, lo, j, st, ex in ROSTER]
    generated, all_team_keys = build_workforce(roster_people, TEAM_KEYS)
    TEAM_KEYS.update({k: v for k, v in all_team_keys.items() if k not in TEAM_KEYS})
    for i, g in enumerate(sorted(generated, key=lambda x: (x["join_date"], x["name"]))):
        id_by_name[g["name"]] = f"EMP-{101 + i:03d}"
    people = roster_people + generated

    head_by_dept = {p["dept"]: p["name"] for p in people if p["tier"] == "head"}
    lead_by_team = {p["team_key"]: p["name"] for p in people if p["tier"] == "lead"}
    assert len(head_by_dept) == len(departments), head_by_dept.keys()

    employees = []
    for p in people:
        if p["tier"] == "head":
            manager = None
        elif p["tier"] == "lead":
            manager = id_by_name[head_by_dept[p["dept"]]]
        else:
            manager = id_by_name[lead_by_team[p["team_key"]]]
        rec = {
            "employee_id": id_by_name[p["name"]],
            "name": p["name"],
            "email": slug_email(p["name"]),
            "department_id": dept_by_code[p["dept"]]["department_id"],
            "team_id": None,  # patched in Layer 2
            "role": p["role"],
            "tier": p["tier"],
            "employment_type": p["employment_type"],
            "manager_id": manager,
            "join_date": p["join_date"],
            "status": p["status"],
            "location": p["location"],
        }
        rec.update(p["extra"])
        rec["_team_key"] = p["team_key"]  # stripped before writing; used by Layer 2 and role assignment
        employees.append(rec)

    employees.sort(key=lambda e: e["employee_id"])
    assign_access_roles(employees, departments)

    # patch department heads
    for dept in departments:
        dept["head_employee_id"] = id_by_name[head_by_dept[dept["code"]]]
    return employees
