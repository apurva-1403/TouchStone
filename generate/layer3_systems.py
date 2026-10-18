"""Layer 3 - Systems/Apps (30). Skeleton + descriptive text. Owner is a team (by name)."""
from __future__ import annotations

# (name, owner_team, category, criticality, access_request_process_summary, description, tags)
SYSTEMS = [
    ("AlgoWorks Fleet Production Platform", "Platform Backend", "customer-facing", "critical",
     "No direct end-user access. Engineers get non-prod access via GitHub team membership; production access is governed by the Production Access & Break-Glass Policy and granted through the AWS Production Account.",
     "The core multi-tenant SaaS platform (fleet tracking, dispatch, route optimisation, telematics ingestion) that customers "
     "buy. Runs on Kubernetes in AWS ap-south-1 with a warm standby in ap-southeast-1. Owned by Platform Backend; "
     "deployed via ArgoCD.", ["product", "kubernetes", "api"]),
    ("AlgoWorks Fleet Customer Portal", "Web & Mobile Frontend", "customer-facing", "high",
     "Customer users are provisioned by Customer Success from the AlgoWorks Admin Console. Internal staff log in with Okta SSO as 'impersonation viewers' after Customer Success approval.",
     "React web application customers use to manage fleets, drivers, geofences, reports and invoices. Currently being "
     "rebuilt under the Customer Portal Revamp project (new design system, SAML SSO for customer IdPs).",
     ["product", "react", "web"]),
    ("AlgoWorks Fleet Driver Mobile App", "Web & Mobile Frontend", "customer-facing", "high",
     "Public app (Play Store / App Store). Internal testers request TestFlight / Play internal-track access from the Frontend & Mobile team via Slack #eng-frontend.",
     "Android and iOS app used by customers' drivers for trip check-in, navigation, proof-of-delivery and offline "
     "trip capture. Released fortnightly; hotfixes as needed.", ["product", "mobile", "android", "ios"]),
    ("Salesforce CRM", "Sales Operations & Deal Desk", "customer-facing", "high",
     "Raise an Access Request in ServiceNow (catalog: 'Salesforce access'). Line manager approval required; Sales Ops (Salesforce Administrator) assigns profile/permission sets; licence availability is checked first. Login is via Okta SSO.",
     "System of record for accounts, opportunities, quotes (CPQ implementation in progress) and renewals. "
     "Integrated with HubSpot (lead sync), Chargebee (subscriptions) and Zendesk (account context).",
     ["crm", "sales", "sso"]),
    ("Zendesk Support Desk", "Customer Success & Support", "customer-facing", "high",
     "Agent seats are limited by licence count. Request via ServiceNow with Head of Customer Success approval; IT adds the Okta group; Customer Success assigns the agent role. Light-agent (view-only) seats are free and approved by any CS lead.",
     "Customer support ticketing and help centre. SSO-integrated with the Customer Portal since the Zendesk-Portal SSO "
     "project. Tier 1/2 support queues, SLA policies and the customer-facing knowledge base live here.",
     ["support", "ticketing", "sso"]),
    ("Chargebee Billing", "Billing, Payroll & Compliance", "customer-facing", "high",
     "Restricted to Finance by default. Non-Finance staff may request the 'Invoice Viewer (read-only)' role via ServiceNow with Payroll & Compliance Manager approval. Admin roles require CFO approval.",
     "Subscription billing, invoicing, dunning and payment collection for all AlgoWorks Fleet customers. Syncs invoices to "
     "NetSuite nightly; revenue-recognition automation project in progress.", ["billing", "finance", "restricted"]),
    ("HubSpot Marketing Hub", "Demand Generation", "customer-facing", "medium",
     "Marketing users: request via ServiceNow with Demand Generation Manager approval. Sales users get 'Sales Hub Starter' seats automatically through the Sales Okta group. Admin (super-admin) rights limited to Marketing Ops.",
     "Marketing automation: forms, landing pages, email nurture, lead scoring and the website chat widget. "
     "Bidirectional lead/contact sync with Salesforce.", ["marketing", "automation", "sso"]),
    ("Corporate Website CMS", "Content & Brand", "customer-facing", "medium",
     "WordPress editor/author roles are granted by the Content & Brand Manager directly (no ServiceNow ticket needed). External agencies get sponsored contractor accounts through IAM with a 90-day expiry.",
     "WordPress site at algoworks.io (marketing pages, blog, careers, pricing). Being migrated to a headless "
     "WordPress + Next.js stack under the Website Redesign project.", ["marketing", "wordpress", "public"]),
    ("AlgoWorks Admin Console", "Platform Backend", "internal", "high",
     "Governed by the Privileged Access & Admin Console Policy: requester must have completed the 'Handling Customer Data' training in LearnHub, the request needs Platform Engineering Manager approval, and IAM adds the user to the console-readonly or console-operator Okta group. Quarterly access review.",
     "Internal web tool for looking up customer tenants, feature flags, subscription state, driver devices and "
     "impersonating customer users for troubleshooting. Contains customer PII. Used by Engineering, Customer "
     "Success and (read-only) Sales Ops.", ["internal-tool", "pii", "privileged"]),
    ("Okta SSO", "Identity & Access Management", "internal", "critical",
     "Every employee gets an Okta account on Day -1 via the Darwinbox -> Okta HR-driven provisioning flow. Application assignments are driven by Okta group membership; group changes are requested via ServiceNow and fulfilled by IAM.",
     "Identity provider for all SaaS and internal apps. Enforces MFA (Okta Verify push / FIDO2). Source of truth for "
     "app assignments via groups. Phase 2 rollout (2025) moved Salesforce, Zendesk, HubSpot and Darwinbox to SSO-only.",
     ["identity", "sso", "mfa"]),
    ("GlobalProtect VPN", "Identity & Access Management", "internal", "critical",
     "Request via ServiceNow 'VPN access' catalog item with manager approval. IAM adds the user to the appropriate Okta VPN group. Contractors receive VPN through a sponsored account and must be explicitly scoped.",
     "Palo Alto GlobalProtect remote-access VPN. Required for the AlgoWorks Admin Console, Metabase, Snowflake private "
     "link, internal Confluence spaces flagged 'restricted' and the office file shares. Split-tunnel by default.",
     ["network", "remote-access"]),
    ("1Password Business", "Identity & Access Management", "internal", "high",
     "All employees are auto-provisioned a personal vault. Shared team vaults are created by IAM on request (ServiceNow) with team lead approval; vault membership is managed by the vault's designated owner.",
     "Company password manager. Shared vaults hold service-account credentials, demo-environment logins and "
     "vendor portal passwords. Sharing credentials over Slack or email is prohibited by the Password & MFA Standard.",
     ["security", "secrets"]),
    ("Microsoft 365", "IT Service Desk & Endpoint", "internal", "critical",
     "Mailbox, OneDrive and SharePoint access are provisioned automatically on joining. Shared mailboxes, distribution lists and SharePoint site access are requested via ServiceNow with the owning manager's approval.",
     "Outlook/Exchange Online email and calendar, OneDrive, SharePoint document libraries and Teams (used mainly for "
     "external meetings). Email is the formal channel for approvals, HR communications and vendor correspondence.",
     ["email", "collaboration"]),
    ("Slack", "IT Service Desk & Endpoint", "internal", "high",
     "Auto-provisioned via Okta on joining. Private channel creation and Slack Connect (external shared channels) are requested via ServiceNow; public channels can be created by anyone.",
     "Primary internal chat. Company-wide channels (#general, #it-helpdesk, #incidents), team channels, project "
     "channels and social channels. Retention: 2 years.", ["chat", "collaboration"]),
    ("ServiceNow ITSM", "IT Service Desk & Endpoint", "internal", "high",
     "All employees can raise tickets through the Employee Service Portal. Fulfiller (agent) roles for IT, HR and Finance queues are granted by the ServiceNow admin on request from the respective team lead.",
     "Ticketing system for IT incidents (INC), service requests (RITM), changes (CHG) and, since 2026, HR and Finance "
     "queues. The Self-Service Catalog project is adding access-request catalog items with automatic routing to system owners.",
     ["itsm", "ticketing"]),
    ("Confluence", "IT Service Desk & Endpoint", "internal", "medium",
     "Auto-provisioned via Okta. Space-level permissions are managed by each space's owner; restricted spaces (Security, Payroll, Leadership) require the space owner's explicit approval.",
     "Company wiki: policies, runbooks, project pages, meeting notes, onboarding guides and decision logs. Spaces per "
     "department plus project spaces.", ["wiki", "documentation"]),
    ("Jira", "Platform Backend", "dev-tooling", "high",
     "Auto-provisioned for Engineering and IT via Okta groups. Other departments request a Jira licence via ServiceNow with team lead approval. New Jira projects are created by Platform Backend (the Jira admins) on request in #eng-platform or via a ServiceNow request.",
     "Issue tracking for engineering sprints, bugs, infra changes, data requests and, increasingly, cross-functional "
     "marketing and sales-ops projects.", ["issue-tracking", "agile"]),
    ("Microsoft Intune", "IT Service Desk & Endpoint", "internal", "medium",
     "No end-user access. Devices are enrolled by the Endpoint Engineer at provisioning. Personal mobile devices needing Outlook are enrolled through the Intune Company Portal app on request to the Service Desk.",
     "Endpoint management and compliance for company laptops (macOS and Windows) and mobile devices. Enforces disk "
     "encryption, OS patch levels, screen lock and Defender. Compliance baseline project in progress.",
     ["endpoint", "mdm", "compliance"]),
    ("Darwinbox HRMS", "People Operations", "internal", "high",
     "All employees get self-service access on Day 1 (profile, leave, payslips, documents). Manager and HR admin roles are assigned by People Operations based on role in the org structure.",
     "HR system of record: employee master data, org structure, leave & attendance, onboarding workflows, performance "
     "reviews and letters. Drives Okta provisioning and (since 2026) auto-creates onboarding tickets in ServiceNow.",
     ["hr", "hris", "restricted"]),
    ("Greenhouse ATS", "Talent Acquisition", "internal", "medium",
     "Recruiters and coordinators are provisioned by the Talent Acquisition Lead. Hiring managers and interviewers get 'Interviewer' access automatically when added to an interview plan. Site Admin is limited to TA leads.",
     "Applicant tracking: job postings, pipelines, interview scheduling, scorecards and offer approvals. Integrated with "
     "Darwinbox for hired-candidate handoff.", ["recruiting", "hr"]),
    ("Keka Payroll", "Billing, Payroll & Compliance", "internal", "high",
     "Restricted to the Payroll team and the CFO. No self-service; employees view payslips through Darwinbox. Any additional access requires CFO approval and is logged for audit.",
     "Payroll processing, statutory deductions (PF, PT, TDS), Form 16 generation and reimbursement payouts. Payslip "
     "data is pushed to Darwinbox monthly.", ["payroll", "finance", "restricted"]),
    ("Zoho Expense", "Accounts Payable & Procurement", "internal", "medium",
     "Auto-provisioned for all employees. Approver roles follow the Darwinbox manager hierarchy. Finance admin roles are granted by the AP & Procurement Manager.",
     "Employee travel & expense claims, per-diem, corporate card reconciliation and reimbursement workflow. Being "
     "integrated with NetSuite for automated journal posting.", ["expenses", "finance"]),
    ("NetSuite ERP", "Financial Planning & Analysis", "internal", "high",
     "Finance-only by default (limited licences). Read-only reporting access for non-Finance staff requires FP&A Manager approval plus CFO sign-off and is reviewed quarterly.",
     "General ledger, AP/AR, fixed assets, month-end close and management reporting. Receives invoices from Chargebee "
     "and (soon) expense journals from Zoho Expense.", ["erp", "finance", "restricted"]),
    ("LearnHub LMS", "Learning & Development", "internal", "low",
     "All employees are auto-enrolled. Course authoring rights are granted by L&D. Mandatory trainings (security awareness, code of conduct, handling customer data) are assigned automatically.",
     "Learning management system (Docebo) hosting mandatory compliance training, the manager development programme, "
     "and self-paced technical courses.", ["learning", "hr"]),
    ("GitHub Enterprise", "Platform Backend", "dev-tooling", "critical",
     "Engineering and IT get access via Okta group on joining; repo/team membership is managed by the Platform Backend Jira/GitHub admins. Non-engineering users need an Engineering Manager's approval and a paid seat (checked against licence count).",
     "Source control, code review, GitHub Actions CI (self-hosted runners in AWS) and the container registry for all "
     "AlgoWorks software. Branch protection is enforced per the Code Review & Branch Protection Standard.",
     ["source-control", "ci"]),
    ("AWS Production Account", "Cloud Infrastructure & Security", "dev-tooling", "critical",
     "Standing read-only access for Platform Backend and Cloud teams via Okta -> AWS IAM Identity Center. Write/admin access is time-bound and follows the Production Access & Break-Glass Policy (Cloud Infrastructure Lead approval, 4-hour sessions, post-hoc review).",
     "AWS Organisations account hosting production workloads (EKS, RDS PostgreSQL, ElastiCache, S3, Kinesis). "
     "Separate sandbox and staging accounts exist with broader developer access.", ["cloud", "aws", "privileged"]),
    ("ArgoCD Deployment Platform", "Cloud Infrastructure & Security", "dev-tooling", "critical",
     "Read access for all engineers via Okta. Sync/rollback rights per application are granted to the owning team's GitHub team automatically. Cluster-admin is restricted to Cloud Infrastructure.",
     "GitOps continuous delivery for all Kubernetes workloads. Production deployments happen by merging to the "
     "environment repo; ArgoCD reconciles automatically. Replaced Jenkins in late 2025.", ["cd", "gitops", "kubernetes"]),
    ("Datadog Monitoring", "Cloud Infrastructure & Security", "dev-tooling", "high",
     "Standard (read) role for all engineers via Okta group. Non-engineering viewer access (e.g. TAMs for customer dashboards) requires Cloud Infrastructure Lead approval. Admin restricted to Cloud Infrastructure.",
     "APM, infrastructure metrics, logs, synthetics and alerting for the production platform. Alerts route to "
     "PagerDuty schedules defined in the On-Call & Escalation Policy.", ["observability", "alerting"]),
    ("Snowflake Data Warehouse", "Data & Analytics Engineering", "dev-tooling", "high",
     "Governed by the Snowflake Data Access Policy. Curated schemas: Data Engineering Manager approval via a Jira DATA ticket. PII-tagged schemas: additionally require Data Protection Officer sign-off. Access is role-based (Okta group -> Snowflake role).",
     "Central analytics warehouse: product telemetry, billing, CRM and support data modelled with dbt. Source for "
     "Metabase, the Customer 360 dashboard and FP&A reporting. Cost optimisation project in progress.",
     ["data", "warehouse", "pii"]),
    ("Metabase BI", "Data & Analytics Engineering", "internal", "medium",
     "Viewer access to curated collections is granted via ServiceNow with team lead approval; Data Engineering adds the Okta group. SQL/native-query access requires Data Engineering Manager approval.",
     "Self-service BI over curated Snowflake datasets: sales dashboards, support metrics, product usage, finance "
     "reporting. Accessible only over VPN.", ["bi", "reporting"]),
]


def build_systems(reg) -> list[dict]:
    out = []
    for i, (name, owner, cat, crit, access, desc, tags) in enumerate(SYSTEMS):
        out.append({
            "system_id": f"SYS-{i + 1:02d}",
            "name": name,
            "owner_team_id": reg.tid(owner),
            "category": cat,
            "criticality": crit,
            "access_request_process_summary": access,
            "description": desc,
            "tags": tags,
        })
    assert len(out) == 30
    return out
