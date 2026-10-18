"""Layer 4 - Projects (24). Skeleton + descriptions. Staffing by employee name (cross-team allowed)."""
from __future__ import annotations

# (name, team, status, start, end_or_None, systems, staff, description)
PROJECTS = [
    ("AlgoWorks Fleet v4 API Platform Migration", "Platform Backend", "in_progress", "2026-01-12", None,
     ["AlgoWorks Fleet Production Platform", "GitHub Enterprise", "ArgoCD Deployment Platform", "Datadog Monitoring"],
     ["Rohan Mehta", "Priya Shah", "Sneha Kulkarni", "Karthik Iyer", "Daniel Fernandes", "Harish Gowda"],
     "Re-platforming the public and internal APIs from the v3 monolith to versioned v4 services (Go + PostgreSQL), "
     "with a compatibility layer so customers can migrate over 12 months. Includes connection-pooling changes, "
     "OpenAPI-first contracts and a new rate-limiting tier. Target GA: October 2026."),
    ("Multi-Region AWS Deployment", "Cloud Infrastructure & Security", "in_progress", "2025-11-03", None,
     ["AWS Production Account", "ArgoCD Deployment Platform", "Datadog Monitoring", "AlgoWorks Fleet Production Platform"],
     ["Varun Chandra", "Nandini Rajan", "Siddharth Jain", "Harish Gowda", "Sneha Kulkarni"],
     "Standing up a warm-standby production environment in ap-southeast-1 (Singapore) alongside ap-south-1 (Mumbai) "
     "to meet APAC customer data-residency asks and a 30-minute RTO. Active-passive design chosen over active-active "
     "for cost. Includes cross-region RDS replication and Route 53 failover."),
    ("Customer Portal Revamp", "Web & Mobile Frontend", "in_progress", "2026-02-02", None,
     ["AlgoWorks Fleet Customer Portal", "AlgoWorks Fleet Production Platform", "Okta SSO"],
     ["Meera Krishnan", "Aditya Rao", "Ishita Bose", "Neha Agarwal", "Priya Shah", "Varsha Pai"],
     "Rebuilding the customer web portal on the new design system with a focus on reporting performance and "
     "accessibility. Scope expanded in April 2026 to include SAML SSO with customers' own identity providers after "
     "enterprise deal feedback, which moved the launch from September to November 2026."),
    ("Driver App Offline Mode", "Web & Mobile Frontend", "completed", "2025-09-01", "2026-01-30",
     ["AlgoWorks Fleet Driver Mobile App", "AlgoWorks Fleet Production Platform"],
     ["Meera Krishnan", "Farhan Siddiqui", "Vikram Nair", "Karthik Iyer"],
     "Allowed drivers to capture trip events and proof-of-delivery without connectivity, syncing when back online. "
     "Uses a local SQLite queue with last-write-wins conflict resolution. Shipped in Driver App 3.5."),
    ("Okta SSO Rollout Phase 2", "Identity & Access Management", "completed", "2025-10-06", "2025-12-19",
     ["Okta SSO", "Salesforce CRM", "Zendesk Support Desk", "HubSpot Marketing Hub", "Darwinbox HRMS"],
     ["Nikhil Bhatt", "Kavya Reddy", "Lakshmi Narayanan", "Megha Patil", "Rakesh Nair"],
     "Moved the remaining business SaaS applications (Salesforce, Zendesk, HubSpot, Darwinbox) behind Okta SSO with "
     "local passwords disabled, group-based app assignment, and HR-driven provisioning from Darwinbox to Okta."),
    ("ArgoCD GitOps Migration", "Cloud Infrastructure & Security", "completed", "2025-08-04", "2025-11-28",
     ["ArgoCD Deployment Platform", "GitHub Enterprise", "AWS Production Account"],
     ["Varun Chandra", "Siddharth Jain", "Harish Gowda", "Rohan Mehta"],
     "Replaced Jenkins-driven deployments with ArgoCD GitOps: every environment is described in the algoworks-deploy "
     "repo, changes ship via reviewed pull requests, and ArgoCD reconciles clusters automatically. Went live for all "
     "production services on 1 December 2025."),
    ("ServiceNow Self-Service Catalog", "IT Service Desk & Endpoint", "in_progress", "2026-04-06", None,
     ["ServiceNow ITSM", "Okta SSO"],
     ["Rajesh Kumar", "Shruti Joshi", "Deepak Verma", "Kavya Reddy"],
     "Building catalog items for the 40 most common requests (application access, laptop, VPN, shared mailbox, "
     "software install) with approval routing derived from the system-owner table, so requests stop arriving as "
     "free-text incidents."),
    ("Intune Endpoint Compliance Baseline", "IT Service Desk & Endpoint", "in_progress", "2026-05-11", None,
     ["Microsoft Intune", "Microsoft 365"],
     ["Rajesh Kumar", "Mohammed Irfan", "Anjali Gupta", "Amit Saxena"],
     "Defining and enforcing a device compliance baseline (FileVault/BitLocker, OS N-1, screen lock, Defender) with "
     "conditional access in Okta so non-compliant devices lose access to M365 and Slack after a grace period."),
    ("Snowflake Cost Optimization", "Data & Analytics Engineering", "in_progress", "2026-06-01", None,
     ["Snowflake Data Warehouse", "Metabase BI"],
     ["Suresh Pillai", "Ananya Chatterjee", "Divya Menon", "Nithin George"],
     "Reducing Snowflake spend by ~35% after the January 2026 credit overrun: per-team warehouses, 60-second "
     "auto-suspend, query-timeout limits for Metabase, dbt model pruning and a monthly credit budget owned by FP&A."),
    ("Unified Customer 360 Dashboard", "Data & Analytics Engineering", "in_progress", "2026-03-09", None,
     ["Metabase BI", "Snowflake Data Warehouse", "Salesforce CRM", "Zendesk Support Desk"],
     ["Suresh Pillai", "Manish Tiwari", "Ravi Shankar", "Pooja Hegde", "Sonal Mehra"],
     "A single Metabase collection joining product usage, support tickets, billing status and CRM data per customer, "
     "for Customer Success and Sales. Feeds the planned Customer Health Score programme."),
    ("Salesforce CPQ Implementation", "Sales Operations & Deal Desk", "in_progress", "2026-02-16", None,
     ["Salesforce CRM", "Chargebee Billing"],
     ["Vinod Krishnamurthy", "Megha Patil", "Arun Prasad", "Anusha Rao", "Natasha D'Souza"],
     "Implementing Salesforce CPQ for quoting, price books and discount approval workflows, replacing spreadsheet "
     "quotes. Discount approval steps are configured to mirror the Deal Desk approval matrix; quotes push to Chargebee."),
    ("APAC Enterprise Expansion", "Enterprise Sales", "in_progress", "2026-01-05", None,
     ["Salesforce CRM", "HubSpot Marketing Hub"],
     ["Rahul Kapoor", "Natasha D'Souza", "Gaurav Thakur", "Wei Lin Tan", "Imran Qureshi"],
     "Go-to-market programme for Singapore, Malaysia and Indonesia logistics operators: territory setup in "
     "Salesforce, localised pricing, partner channel and the Singapore data-residency dependency on the "
     "multi-region deployment."),
    ("Zendesk-Customer Portal SSO Integration", "Customer Success & Support", "completed", "2025-12-01", "2026-02-27",
     ["Zendesk Support Desk", "AlgoWorks Fleet Customer Portal", "Okta SSO"],
     ["Anita Desai", "Preeti Nambiar", "Sameer Khan", "Aditya Rao", "Lakshmi Narayanan"],
     "Let customer portal users open and track Zendesk tickets without a second login by federating Zendesk with the "
     "portal's identity. Also moved internal agent login to Okta."),
    ("Customer Health Score Program", "Customer Success & Support", "planned", "2026-10-01", None,
     ["Zendesk Support Desk", "Metabase BI", "Salesforce CRM"],
     ["Anita Desai", "Kunal Shah", "Sameer Khan", "Ravi Shankar"],
     "Define a composite health score (usage, support load, billing health, NPS) surfaced in Salesforce for CSMs, "
     "built on the Customer 360 dataset. Kick-off planned for October 2026."),
    ("Campus Hiring Drive 2026", "Talent Acquisition", "completed", "2026-01-19", "2026-04-30",
     ["Greenhouse ATS", "Darwinbox HRMS"],
     ["Rohit Sinha", "Nisha Pandey", "Akhil Menon", "Bhavana Shetty"],
     "Hired 8 graduate engineers and 2 analysts from 6 campuses; ran Greenhouse pipelines, coding assessments and "
     "offer approvals; joiners start July-September 2026."),
    ("Darwinbox Onboarding Workflow Automation", "People Operations", "completed", "2026-02-09", "2026-05-29",
     ["Darwinbox HRMS", "ServiceNow ITSM", "Okta SSO"],
     ["Geeta Iyengar", "Rakesh Nair", "Swati Kulkarni", "Kavya Reddy", "Shruti Joshi"],
     "Automated new-joiner setup: Darwinbox pre-boarding triggers a ServiceNow onboarding ticket 10 days before the "
     "start date and creates the Okta account with a role-based application bundle, replacing the manual HR email "
     "to IT."),
    ("Manager Development Program", "Learning & Development", "in_progress", "2026-04-13", None,
     ["LearnHub LMS"],
     ["Madhavi Srinivasan", "Tarun Bhargava", "Leela Krishnan", "Dev Patel", "Swati Kulkarni"],
     "Six-month cohort programme for the 18 team leads: feedback, hiring, performance conversations and hybrid team "
     "management. Blended LearnHub modules and monthly in-person workshops."),
    ("Zoho Expense to NetSuite Integration", "Accounts Payable & Procurement", "in_progress", "2026-05-04", None,
     ["Zoho Expense", "NetSuite ERP"],
     ["Shalini Menon", "Alok Mishra", "Kritika Jain", "Payal Shah", "Manish Tiwari"],
     "Replacing the monthly manual expense journal upload with an automated daily summarised posting from Zoho "
     "Expense into NetSuite, including GST breakouts and cost-centre mapping."),
    ("FY27 Annual Operating Plan", "Financial Planning & Analysis", "in_progress", "2026-07-01", None,
     ["NetSuite ERP", "Metabase BI"],
     ["Ashwin Raman", "Payal Shah", "Nithin George", "Harsha Vardhan", "Meenakshi Sundaram", "Manish Tiwari"],
     "Building the FY27 (April 2027 - March 2028) operating plan: headcount, SaaS spend, cloud cost and revenue "
     "model, with department budget reviews in October and board approval in December 2026."),
    ("Chargebee Revenue Recognition Automation", "Billing, Payroll & Compliance", "in_progress", "2026-03-02", None,
     ["Chargebee Billing", "NetSuite ERP"],
     ["Deepa Subramanian", "Anusha Rao", "Sanjay Dutta", "Nithin George"],
     "Automating ASC 606 / Ind AS 115 revenue schedules from Chargebee subscriptions into NetSuite, replacing the "
     "quarterly spreadsheet, and fixing the invoice-sync gaps found during the May 2026 webhook incident."),
    ("Website Redesign & CMS Migration", "Content & Brand", "in_progress", "2026-04-20", None,
     ["Corporate Website CMS", "HubSpot Marketing Hub"],
     ["Ankit Chawla", "Omar Farooq", "Riya Sen", "Shreya Ghosh", "Ishita Bose", "Aparna Das"],
     "New brand site on headless WordPress + Next.js hosted on Vercel, with HubSpot forms embedded. Agency "
     "(Pixelcraft Studio) doing design production; launch aligned with the v4 campaign."),
    ("HubSpot-Salesforce Lead Sync Cleanup", "Demand Generation", "completed", "2025-10-13", "2026-01-16",
     ["HubSpot Marketing Hub", "Salesforce CRM"],
     ["Manoj Venkatesh", "Aparna Das", "Megha Patil", "Yash Agrawal"],
     "De-duplicated 14,000 contacts, fixed the field mapping that created duplicate leads, and documented ownership "
     "rules between Marketing and Sales Ops for the HubSpot-Salesforce connector."),
    ("AlgoWorks Fleet v4 Launch Campaign", "Product Marketing", "in_progress", "2026-06-15", None,
     ["HubSpot Marketing Hub", "Corporate Website CMS"],
     ["Sanya Kapadia", "Varsha Pai", "Rohini Pathak", "Lavanya Bhat", "Kabir Mehrotra", "Nikita Bansal"],
     "Launch positioning, customer webinar series, analyst briefings and sales enablement for the v4 API platform. "
     "Launch date moved from 15 September to 6 October 2026 to follow the engineering GA date."),
    ("Security Awareness & Phishing Simulation Program", "Identity & Access Management", "in_progress", "2026-03-16", None,
     ["Microsoft 365", "LearnHub LMS", "Okta SSO"],
     ["Nikhil Bhatt", "Amit Saxena", "Joseph Mathew", "Leela Krishnan"],
     "Quarterly phishing simulations, a refreshed security awareness course in LearnHub and a report-phish button in "
     "Outlook, started after the April 2026 CFO-impersonation phishing incident."),
]


def build_projects(reg) -> list[dict]:
    out = []
    for i, (name, team, status, start, end, systems, staff, desc) in enumerate(PROJECTS):
        out.append({
            "project_id": f"PROJ-{i + 1:02d}",
            "name": name,
            "team_id": reg.tid(team),
            "staffed_employee_ids": [reg.eid(s) for s in staff],
            "status": status,
            "start_date": start,
            "end_date": end,
            "related_system_ids": [reg.sid(s) for s in systems],
            "description": desc,
        })
    assert len(out) == 24
    return out
