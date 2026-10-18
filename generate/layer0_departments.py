"""Layer 0 - Departments. Purely scripted. head_employee_id is patched after Layer 1."""

DEPARTMENTS = [
    ("DEPT-01", "Engineering", "ENG", "Builds and runs the AlgoWorks Fleet product: backend platform, web/mobile apps, data & analytics."),
    ("DEPT-02", "IT & Infrastructure", "IT", "Corporate IT, identity & access, service desk, endpoints, cloud infrastructure and security operations."),
    ("DEPT-03", "Sales", "SALES", "Enterprise sales, sales operations & deal desk, and customer success/support."),
    ("DEPT-04", "Human Resources", "HR", "Talent acquisition, people operations (onboarding, HRBP, HR ops) and learning & development."),
    ("DEPT-05", "Finance", "FIN", "Accounts payable & procurement, FP&A, billing, payroll and compliance."),
    ("DEPT-06", "Marketing", "MKT", "Content & brand, demand generation and product marketing."),
]


def build_departments() -> list[dict]:
    from layer1b_workforce import NEW_DEPARTMENTS
    return [
        {
            "department_id": did,
            "name": name,
            "code": code,
            "description": desc,
            "head_employee_id": None,  # patched in Layer 1
        }
        for did, name, code, desc in DEPARTMENTS + NEW_DEPARTMENTS
    ]
