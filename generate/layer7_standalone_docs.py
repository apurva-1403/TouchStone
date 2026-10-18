"""Layer 7 - Standalone Confluence docs (50): the "official documentation" layer.

Not event-driven. Composed from Layer 3/4/5 entities plus hand-written sections:
  20 system guides, 12 project pages, 8 department process pages, 4 team pages, 6 reference pages.
A few of these deliberately restate *current practice* (e.g. the Engineering onboarding guide's
"do I need a CHG?" section, the Deal Desk process page), so that official docs can disagree with
each other as well as with policies - which is what a real wiki looks like.
"""
from __future__ import annotations

from events.dsl import D

# ---------------------------------------------------------------- system guides (20)
# name -> (created, last_updated, author, common_tasks[], known_issues[], support, sensitivity)
SYSTEM_GUIDES = {
    "Okta SSO": ("2025-07-14", "2026-05-06", "Lakshmi Narayanan",
        ["Log in at algoworks.okta.com; every app tile you are assigned appears on the dashboard.",
         "Enrol a second factor (Touch ID / Windows Hello or a security key) under Settings > Security Methods so you can self-service resets.",
         "Group-based app assignment: if an app tile is missing, you need the Okta group - request via the ServiceNow access catalog, not Slack.",
         "Admins: app configuration changes (SAML settings, attribute mappings) are Normal changes - raise a CHG."],
        ["Push notifications not arriving: check the phone's automatic time setting before re-enrolling.",
         "New joiners see only the default bundle plus their role bundle on Day 1; anything else is a catalog request.",
         "During an Okta vendor outage nothing behind SSO works, including ServiceNow and Slack - the office WhatsApp group is the fallback channel."],
        "IAM queue in ServiceNow; urgent lockouts by phone to the Service Desk (ext. 200).", "internal"),
    "GlobalProtect VPN": ("2025-07-14", "2026-06-04", "Lakshmi Narayanan",
        ["Install GlobalProtect from the Company Portal; portal address vpn.algoworks.io; sign in with Okta.",
         "Needed for: AlgoWorks Admin Console, Metabase, Snowflake private link, restricted Confluence spaces, office file shares.",
         "Split tunnel is the default; request the full-tunnel profile only for travel to high-risk locations.",
         "Employee VPN membership is via the vpn-employees Okta group and renews automatically while you are an active employee."],
        ["'Portal certificate is invalid' for everyone remote = expired certificate; see the certificate runbook.",
         "Connects then drops after ~20 seconds on some home routers: MTU issue - IAM can push a lower MTU for your gateway profile.",
         "Periodic disconnects every ~30 minutes on home Wi-Fi: under investigation as a problem record (rekey suspected); collect logs when it happens."],
        "IAM queue; gateway outages are Sev2 - post in #incidents.", "internal"),
    "1Password Business": ("2025-08-04", "2026-05-06", "Kavya Reddy",
        ["Everyone has a personal vault via Okta; install the desktop app and browser extension from the Company Portal.",
         "Shared credentials (service accounts, demo logins, vendor portals) live in team vaults; ask IAM to create a vault with your team lead's approval.",
         "Never paste credentials into Slack, email or Confluence - IAM will rotate them without notice if found."],
        ["Vault membership is managed by the vault owner, not IAM - ask the owner to add you.",
         "Break-glass local admin credentials are in a sealed vault; use is logged and reviewed."],
        "IAM queue.", "internal"),
    "Microsoft 365": ("2025-06-23", "2026-03-02", "Shruti Joshi",
        ["Outlook (mail/calendar), OneDrive (personal files), SharePoint (team libraries), Teams (external meetings).",
         "Shared mailboxes and distribution lists: request via ServiceNow with the owning manager's approval.",
         "Mailbox quota is 50 GB; enable the online archive before you hit it.",
         "Use the 'Report Phish' button in Outlook for suspicious mail - it goes straight to Security."],
        ["Calendar not syncing on mobile is almost always a lost Intune registration - re-register in Company Portal.",
         "Vendor emails with attachments can land in quarantine; the Service Desk can release them after verifying the sender."],
        "IT Service Desk queue or #it-helpdesk.", "internal"),
    "Slack": ("2025-06-23", "2026-02-20", "Deepak Verma",
        ["Public channels: anyone can create. Private channels and Slack Connect (external) channels: ServiceNow request.",
         "Company-wide: #general (announcements), #it-helpdesk, #incidents, #new-joiners, #kudos. Team and project channels are listed on each team's page.",
         "Retention is 2 years. Decisions that matter should be written to Confluence, not left in threads."],
        ["During a Slack vendor outage use Microsoft Teams chat and email (approvals by email so there is a record).",
         "Slack is behind Okta, so an Okta outage takes Slack with it."],
        "IT Service Desk queue.", "internal"),
    "ServiceNow ITSM": ("2025-06-30", "2026-06-08", "Shruti Joshi",
        ["Employee Service Portal: raise incidents (something is broken), requests (I need something) and see your approvals.",
         "Access requests: use the 'Request Access' catalog items (Salesforce, Zendesk, HubSpot, Metabase, GitHub in wave 1) - approvals route to your manager and the system owner automatically.",
         "Managers: approve from the email link or the portal; set a delegate in Darwinbox before going on leave so approvals do not stall.",
         "Ticket prefixes: INC (incident), RITM (request), CHG (change)."],
        ["Free-text incidents that are really access requests get redirected to the catalog - please start there.",
         "HR and Finance queues exist since 2026; HR queries and expense/PO questions go there, not to IT."],
        "IT Service Desk (ServiceNow administration); process questions to Rajesh Kumar.", "internal"),
    "Jira": ("2025-07-07", "2026-08-07", "Karthik Iyer",
        ["Projects: PLAT (platform), FE (frontend/mobile), DATA (data requests and access), SUP (support escalations), MKT (marketing content), DG (demand gen).",
         "Engineering and IT get Jira via the role bundle; other departments request a licence via ServiceNow with team lead approval.",
         "New Jira projects: raise a ServiceNow request - the Service Desk creates them from the standard template; Platform Backend owns schemes, workflows and integrations."],
        ["Data access requests must be raised in DATA with the 'Data access request' issue type - that is where the approvals are recorded.",
         "Ownership of project creation was unclear until August 2026 (Service Desk vs Platform); the rule above is the agreed one."],
        "Platform Backend (#eng-platform) for configuration; Service Desk for project creation and licences.", "internal"),
    "Microsoft Intune": ("2025-08-18", "2026-09-10", "Mohammed Irfan",
        ["All company laptops are enrolled at provisioning; compliance requires disk encryption, OS N-1, screen lock and Defender.",
         "Company Portal app: self-service software installs and device compliance status.",
         "Personal phones: the Service Desk enrols Outlook and Teams with app protection (MAM) on request - no full-device management, no approval needed.",
         "Company phones (on-call, leadership): full device management."],
        ["Automated Device Enrollment failing on new Macs: check the Apple Business Manager token and APNs certificate expiry (both in the IT token inventory).",
         "Non-compliant devices will lose access to M365 and Slack after the grace period once the compliance baseline project completes."],
        "IT Service Desk queue; endpoint questions to Mohammed Irfan.", "internal"),
    "Darwinbox HRMS": ("2025-08-11", "2026-07-21", "Rakesh Nair",
        ["Self-service: profile, leave, attendance, payslips (Documents > Payslips), tax declarations, letters, performance reviews.",
         "Managers: approve leave, set a delegate when you are away, complete onboarding and review tasks.",
         "Darwinbox drives Okta: your account and role bundle are created from your Darwinbox record; name or manager corrections must be made here first."],
        ["Payslips are pushed from Keka monthly; if a payslip is missing for a whole location, it is a sync mapping issue - raise with Payroll.",
         "Leave balances after a location transfer can need a manual correction."],
        "HR Ops queue in ServiceNow or #people-ops.", "internal"),
    "Zoho Expense": ("2025-11-17", "2026-06-30", "Ramesh Babu",
        ["Submit claims with itemised receipts; approvals go to your Darwinbox manager, then Finance AP.",
         "Reimbursement is with the monthly payroll - cut-off is the 20th.",
         "Corporate card transactions must also be reconciled here within 15 days of the statement.",
         "Categories: Travel, Per Diem, Team Meals, Learning & Development, Connectivity, Other."],
        ["The system rules (30-day window, Rs 2,000 per diem, Rs 500 receipt threshold) reflect the published T&E policy; Finance AP handles exceptions on appeal - raise a ticket in the Finance queue.",
         "Expense journals post to NetSuite daily since July 2026; detail stays in Zoho with a drill-back link."],
        "Finance AP queue or #expenses-help.", "internal"),
    "NetSuite ERP": ("2025-09-15", "2026-08-28", "Payal Shah",
        ["Finance-only by default (32 full-user licences). Read-only reporting access for non-Finance needs FP&A Manager approval plus CFO sign-off.",
         "Purchase orders are raised by Procurement from approved purchase requests; goods receipt is confirmed by the requester.",
         "Saved searches for AOP and management reporting are shared from the FP&A folder."],
        ["Licence shortage: expect a few days for new access while a licence is found; 3 more licences requested in the FY27 renewal.",
         "Integrations: Chargebee invoices nightly; Zoho expense journals daily (idempotent since August 2026)."],
        "Finance Systems (Payal Shah) via the Finance queue.", "restricted"),
    "GitHub Enterprise": ("2025-07-07", "2026-05-11", "Karthik Iyer",
        ["Org algoworks-tech; access via the github-engineering Okta group (role bundle) and GitHub teams per squad.",
         "Branch protection per the Code Review & Branch Protection Standard: one CODEOWNER approval (two for payments/auth/data-pipeline repos), green CI.",
         "Self-hosted Actions runners handle jobs needing VPC access; GitHub-hosted for the rest.",
         "Non-engineering users (designers, writers) get a paid seat on a single repo with an Engineering Manager's approval."],
        ["Seat count is close to the limit (120); top-up requested at renewal.",
         "Runners offline = usually disk full on the runner AMI; see the runner runbook."],
        "Platform Backend (#eng-platform); CI runner issues to #devops-sre.", "internal"),
    "AWS Production Account": ("2025-09-15", "2026-06-15", "Varun Chandra",
        ["Standing access is read-only (ProdReadOnly) via Identity Center for engineers; sandbox and staging accounts have developer access.",
         "Elevated access (ProdOperator/ProdAdmin) is a 4-hour session requested in ServiceNow with Cloud Infrastructure Lead approval and post-hoc review.",
         "Production changes go through ArgoCD (apps) or Terraform PRs in algoworks-infra (infrastructure, CAB)."],
        ["New joiner ProdReadOnly can wait on the Cloud Lead's approval - Harish Gowda can approve when Varun is travelling.",
         "Regions: ap-south-1 (active), ap-southeast-1 (warm standby; monitors are health/replication only)."],
        "Cloud Infrastructure (#devops-sre); on-call via PagerDuty.", "restricted"),
    "ArgoCD Deployment Platform": ("2025-12-01", "2026-04-30", "Siddharth Jain",
        ["Every environment is described in the algoworks-deploy repo; merging a reviewed PR to an environment directory deploys it.",
         "A merged algoworks-deploy PR is the approval record for standard application deployments - no CHG is needed for image tag, replica, resource or feature-flag config changes to an existing service.",
         "Rollback = 'Rollback' in the ArgoCD UI to the previous revision (under 2 minutes) or revert the PR.",
         "Infrastructure, network, identity, database and new services still need a CHG and CAB."],
        ["The Change Management Policy page (v2) predates ArgoCD and still says all deployments need a CHG - the CAB decision of September 2025 is the operating rule.",
         "Apps in the Singapore standby show Healthy with 0 replicas by design."],
        "Cloud Infrastructure (#devops-sre).", "internal"),
    "Datadog Monitoring": ("2025-09-22", "2026-07-06", "Nandini Rajan",
        ["Standard (read) role for engineers via role bundle; non-engineering viewer access (e.g. TAM dashboards) needs the Cloud Infrastructure Lead.",
         "Paging alerts route to PagerDuty schedules per the On-Call policy; every paging alert must link a runbook.",
         "Key dashboards: Platform SLOs, Tenant SLO (customer-facing), CI Runners, Chargebee Sync, Certificate Expiry."],
        ["Logs contain driver PII - log access is engineering-only.",
         "Standby-region monitors are limited to health and replication lag after the May 2026 alert storm."],
        "Cloud Infrastructure (#devops-sre).", "internal"),
    "Snowflake Data Warehouse": ("2025-07-28", "2026-06-23", "Ananya Chatterjee",
        ["Access is role-based via Okta groups: snowflake-analyst (curated marts), snowflake-engineer, snowflake-pii-reader, snowflake-admin.",
         "Request curated access with a Jira DATA 'Data access request' (Data Engineering Manager approves). PII schemas need the additional sign-off described in the Snowflake Data Access Policy.",
         "Warehouses per team since June 2026 (WH_ENG, WH_DBT, WH_SALES, WH_FIN, WH_MKT) with 60-second auto-suspend and FP&A-owned credit budgets.",
         "Metabase queries run on XS/S warehouses with a 5-minute statement timeout."],
        ["Query timeouts on a small warehouse: ask in #eng-data before requesting a bigger warehouse - a curated dashboard may exist.",
         "The DPO sign-off step for PII access has no named owner since February 2026; Data Engineering approves with purpose and expiry in the meantime."],
        "Data Engineering (#eng-data).", "internal"),
    "Metabase BI": ("2025-08-25", "2026-06-26", "Manish Tiwari",
        ["VPN required. Viewer access to collections via ServiceNow with team lead approval; SQL access needs the Data Engineering Manager.",
         "Collections: Sales, Support Metrics, Finance Reporting, Product Usage, Marketing Attribution, Customer 360 (in progress).",
         "Scheduled refreshes under 1 hour need Data Engineering review (a runaway hourly refresh blew the January 2026 Snowflake budget)."],
        ["Slow dashboards after June 2026: check the collection is on the right warehouse (Sev3, next business day).",
         "Public embeds are not enabled; the website team tested embeds against a scoped VPN contractor account."],
        "Data Engineering (#eng-data).", "internal"),
    "AlgoWorks Admin Console": ("2025-11-10", "2026-04-27", "Rohan Mehta",
        ["Internal tool: tenant lookup, device status, subscription state, feature flags, customer-user impersonation (operators only). Contains customer PII.",
         "Access levels: console-readonly, console-operator, console-admin (Platform Backend only).",
         "Prerequisites: 'Handling Customer Data' course in LearnHub within 12 months, line manager approval and Platform Engineering Manager approval; operators also need the IAM & Security Lead. No exceptions to the training rule since policy v2 (April 2026).",
         "Quarterly access review; 90 days without login = removal."],
        ["Before April 2026 a manager attestation could substitute for the training; some users granted under that route may not have completed the course.",
         "Feature-flag changes by operators are logged and appear in the weekly release notes."],
        "Platform Backend (#eng-platform); access via the IAM queue.", "restricted"),
    "Salesforce CRM": ("2025-10-20", "2026-07-13", "Megha Patil",
        ["Login via Okta only (SSO-only since 15 December 2025). Access via the salesforce-users Okta group plus a profile assigned by the Salesforce Administrator.",
         "Request through the ServiceNow 'Salesforce access' catalog item; licence availability is checked first (85 licences).",
         "CPQ (from April 2026) handles quotes and routes discount approvals automatically; Deal Desk tickets are created for discounts above 10%.",
         "Report export needs the 'Report Export' permission set - ask Sales Ops, not the Service Desk."],
        ["Duplicate leads from the HubSpot connector recur when workflows are re-published - report in #sales-ops; only the Salesforce Administrator merges.",
         "Licences assigned directly (not via Okta group) survive offboarding; direct assignments are being migrated to groups."],
        "Sales Ops queue / #sales-ops.", "internal"),
    "Zendesk Support Desk": ("2025-12-19", "2026-09-07", "Anita Desai",
        ["Agent seats are licence-limited (42 after September 2026); light-agent (view/internal notes) seats are free.",
         "Full agent seat: ServiceNow request with Head of Customer Success approval; IAM adds the Okta group, CS assigns the role.",
         "SLAs and priorities per the Customer Support SLA & Escalation Policy; escalate to Engineering via a linked Jira SUP issue and #customer-success.",
         "Login via Okta; customer portal users reach Zendesk through the portal SSO integration."],
        ["Login loops for all agents = Okta SAML app misconfiguration; IAM rolls back (July 2026).",
         "New joiners on the CS-SUPPORT bundle get a light seat automatically; the full seat is a separate, licence-dependent request."],
        "Customer Success (#customer-success); access via IAM.", "internal"),
}

# ---------------------------------------------------------------- project pages (12)
# project name -> (created, last_updated, author, goals, scope_notes, milestones[(date, text)], risks)
PROJECT_PAGES = {
    "AlgoWorks Fleet v4 API Platform Migration": ("2026-01-12", "2026-08-12", "Rohan Mehta",
        "Replace the v3 monolith APIs with versioned v4 services, keep every customer integration working through a compatibility layer, and give customers 12 months to migrate.",
        "In scope: public API v4 (REST/OpenAPI-first), gateway with rate-limiting tiers, connection management, contract tests for the 34 direct integrations. Out of scope: gRPC externally, portal changes (see Customer Portal Revamp).",
        [("2026-01-20", "ADR-014 protocol decision (REST/OpenAPI-first)"), ("2026-03-17", "Sev1 outage after 4.2.0 pool change; postmortem actions added"), ("2026-05-05", "1.3.0 rate-limiting tier live"), ("2026-08-10", "GA re-baselined to 6 October 2026"), ("2026-10-06", "GA (planned)")],
        "Contract-test coverage of customer integrations (70% in August); staging load profile; month-end billing freeze windows."),
    "Multi-Region AWS Deployment": ("2025-11-11", "2026-05-12", "Varun Chandra",
        "Warm-standby production in ap-southeast-1 for a 30-minute RTO and APAC data residency, at ~40% of the cost of active-active.",
        "Terraform baseline, cross-region RDS replication, ArgoCD cluster registration with apps at zero replicas, Route 53 failover, quarterly failover drill. Phase 2 (Q3 2026): pin APAC tenants to Singapore.",
        [("2025-11-10", "ADR-011 topology decision"), ("2025-11-24", "Baseline built (CHG)"), ("2026-03-14", "First failover drill: 38 minutes"), ("2026-05-08", "Monitor alert storm; standby monitor set redefined"), ("2026-09-30", "APAC tenant pinning (planned)")],
        "Replication lag during telematics peaks; monitor hygiene; run-rate tracked as a separate FP&A cost line (~USD 9k/month)."),
    "Customer Portal Revamp": ("2026-02-02", "2026-04-16", "Meera Krishnan",
        "Rebuild the customer portal on the new design system with faster reporting, accessibility compliance and - since April 2026 - SSO with customers' own identity providers.",
        "React front-end, new reporting service, SAML SP-initiated SSO with per-tenant IdP metadata and JIT provisioning. SCIM deferred. Launch 2 November 2026 (was 15 September).",
        [("2026-02-02", "Kick-off"), ("2026-04-15", "Scope change: customer-IdP SAML SSO; launch moved to 2 Nov"), ("2026-06-19", "Export v2 shipped dark behind flag"), ("2026-09-15", "SSO security review (planned)"), ("2026-11-02", "Launch (planned)")],
        "Dependency on Meridian renewal timeline; security review of SAML/JIT; messaging alignment with the v4 launch."),
    "Okta SSO Rollout Phase 2": ("2025-10-06", "2026-01-09", "Nikhil Bhatt",
        "Bring the remaining business SaaS (Salesforce, Zendesk, HubSpot, Darwinbox) behind Okta with local passwords disabled, group-based assignment and HR-driven provisioning.",
        "Completed 19 December 2025. Cutover 15 December. One agreed exception (Salesforce demo account) closed in May 2026 with the Sales-Demo 1Password vault.",
        [("2025-10-27", "Cutover decision log"), ("2025-12-09", "CHGs approved at CAB"), ("2025-12-15", "Cutover day"), ("2025-12-19", "Project closed")],
        "Residual: Salesforce licences assigned directly rather than via group survive offboarding (found in the Q2 2026 access review)."),
    "ArgoCD GitOps Migration": ("2025-08-04", "2025-12-05", "Varun Chandra",
        "Replace Jenkins-driven deployments with GitOps: environments described in algoworks-deploy, changes via reviewed PRs, ArgoCD reconciles automatically.",
        "All production services live on ArgoCD from 1 December 2025. Process decision (CAB, 2 September 2025): merged PR = approval for standard app deployments; CAB retained for infra/network/identity/DB/new services.",
        [("2025-08-25", "GitOps approval process proposed"), ("2025-09-02", "CAB approval of the process change"), ("2025-11-28", "Last service migrated"), ("2025-12-01", "Go-live")],
        "Follow-up still open: Change Management Policy update to add the GitOps category (owner Varun Chandra)."),
    "ServiceNow Self-Service Catalog": ("2026-04-06", "2026-08-24", "Rajesh Kumar",
        "Turn the 40 most common requests into catalog items with automatic approval routing so requests stop arriving as free-text incidents.",
        "Wave 1 (8 June 2026): Salesforce, Zendesk, HubSpot, Metabase, GitHub access. Wave 2 (August): VPN, shared mailbox, laptop, software install, contractor account. Approvals: Darwinbox manager (delegate honoured) then system owner for admin roles.",
        [("2026-05-19", "Routing design decision"), ("2026-06-08", "Wave 1 live"), ("2026-08-24", "Wave 2 live"), ("2026-10-31", "Wave 3 - HR and Finance items (planned)")],
        "Adoption target 80% of access requests via catalog by September; the catalog deliberately does not auto-approve on SLA breach."),
    "Snowflake Cost Optimization": ("2026-06-01", "2026-09-07", "Suresh Pillai",
        "Cut Snowflake spend by ~35% from the January 2026 baseline through per-team warehouses, auto-suspend, Metabase limits and FP&A-owned budgets.",
        "Decisions of 16 June 2026 implemented via CHG on 23 June. Monthly cost review with FP&A on the first Monday.",
        [("2026-01-29", "Credit overrun incident (trigger)"), ("2026-06-16", "Decisions"), ("2026-06-23", "Warehouse restructure"), ("2026-08-03", "July actual 4,610 credits (-33%)")],
        "Analyst friction with small warehouses (FP&A AOP queries); temporary FP&A budget for the AOP window under discussion."),
    "Unified Customer 360 Dashboard": ("2026-03-09", "2026-08-31", "Suresh Pillai",
        "One Metabase collection per customer joining product usage, support tickets, billing status and CRM data, for CS and Sales.",
        "Curated marts CORE_MART, SALES_MART, SUPPORT_MART joined on a hashed account id; no PII in the dashboard. Feeds the planned Customer Health Score programme.",
        [("2026-03-09", "Kick-off"), ("2026-05-29", "Alpha with CS"), ("2026-07-31", "Sales Ops rollout"), ("2026-10-01", "Handover to Health Score programme (planned)")],
        "Data freshness of Zendesk extract (4 hours); Sales Ops requests for rep-level pivots that need SQL."),
    "Salesforce CPQ Implementation": ("2026-02-16", "2026-05-04", "Vinod Krishnamurthy",
        "Replace spreadsheet quoting with Salesforce CPQ: price books, quote templates and automated discount approval routing, pushing approved quotes to Chargebee.",
        "Approval steps: AE to 10%, Sales Manager to 20%, VP Sales to 30% (weekly CFO report), CEO above 30%. Pilot 6 April; all teams 4 May 2026.",
        [("2026-03-23", "Approval workflow decision"), ("2026-04-06", "Enterprise pilot"), ("2026-05-04", "All teams live"), ("2026-07-13", "Matrix v4 drafted for CFO sign-off")],
        "Published Discount Approval Matrix (v3) still lists the CFO for 20-30%; v4 pending."),
    "Darwinbox Onboarding Workflow Automation": ("2026-02-09", "2026-07-21", "Geeta Iyengar",
        "Automate new-joiner setup: Darwinbox pre-boarding creates the ServiceNow onboarding ticket 10 business days before start and the Okta account with a role-based application bundle.",
        "Live since 29 May 2026. Role bundle table published July 2026 (v1, incomplete). Managers request only what the bundle misses; licence-based apps are always manual.",
        [("2026-02-09", "Kick-off"), ("2026-04-20", "Darwinbox -> ServiceNow ticket creation live"), ("2026-05-29", "Role bundles live; project closed"), ("2026-07-21", "Bundle table published")],
        "Employee Onboarding SOP (v3) still describes the manual process; v4 in draft with HR Ops."),
    "Website Redesign & CMS Migration": ("2026-04-20", "2026-08-19", "Ankit Chawla",
        "New brand website on headless WordPress + Next.js hosted on Vercel, with HubSpot forms, built with Pixelcraft Studio.",
        "Stack decision 26 May 2026. Security review complete 4 June. Vercel onboarded as a vendor 19 August (single quote, Net-30). Production cutover with the v4 launch on 6 October 2026.",
        [("2026-05-26", "Stack decision"), ("2026-06-10", "Contractor accounts and Slack Connect"), ("2026-07-17", "Metabase embed test via contractor VPN"), ("2026-08-19", "Vercel PO"), ("2026-10-06", "Cutover (planned)")],
        "Agency account expiries (90-day, extended late August); procurement exceptions under review by Finance."),
    "AlgoWorks Fleet v4 Launch Campaign": ("2026-06-15", "2026-08-12", "Sanya Kapadia",
        "Launch positioning, webinar series, analyst briefings and sales enablement for the v4 API platform.",
        "Launch 6 October 2026 (moved from 15 September). Webinars 8/15/22 October; analyst briefings 1-2 October; enablement 29 September; website cutover on launch day.",
        [("2026-06-15", "Kick-off"), ("2026-08-12", "Re-plan for 6 October"), ("2026-09-29", "Sales enablement (planned)"), ("2026-10-06", "Launch (planned)")],
        "Portal revamp launches 2 November - messaging must separate the two; Diwali week limits November follow-up."),
}

# ---------------------------------------------------------------- department process pages (8)
DEPT_PAGES = [
    D("How to get help from IT - Service Desk guide and SLAs",
      "**Owner:** IT Service Desk & Endpoint (Rajesh Kumar) | **Updated:** 24 August 2026\n\n"
      "## Channels\n1. **ServiceNow Employee Service Portal** - the only channel that creates a tracked ticket. Use it for anything you need fixed or provisioned.\n"
      "2. **#it-helpdesk** on Slack - quick questions and 'is it just me?' checks. If it needs work, we will ask you to raise a ticket.\n"
      "3. **Phone (ext. 200)** - lockouts, lost devices, anything urgent, and the only channel that works during an Okta outage (with the office WhatsApp group).\n\n"
      "## What goes where\n| Need | Raise | Handled by |\n|---|---|---|\n"
      "| Application access (Salesforce, Zendesk, HubSpot, Metabase, GitHub, VPN, shared mailbox) | Catalog: Request Access | IAM |\n"
      "| Laptop, peripherals, software, printers, Wi-Fi, M365, Slack | Incident or Request | Service Desk |\n"
      "| Production access, AWS, ArgoCD, Datadog | Request (Production elevated access / access) | Cloud Infrastructure |\n"
      "| HR questions (leave, payslips, letters) | HR queue | HR Ops / Payroll |\n"
      "| Expenses, POs, vendor payments | Finance queue | Finance AP / Procurement |\n\n"
      "## Response and resolution targets\n| Priority | Response | Resolution |\n|---|---|---|\n| P1 (many users / critical system) | 15 min | 4 h |\n| P2 (team blocked) | 30 min | 1 business day |\n| P3 (one user, workaround) | 4 business hours | 3 business days |\n| P4 (request) | 1 business day | 5 business days |\n\n"
      "## Things that speed you up\n- Set a delegate in Darwinbox before leave - approvals for your team stall otherwise.\n- Enrol a second Okta factor so you can self-service lockouts.\n"
      "- Replacement laptops: we issue a loaner on day one; the standard device depends on stock (currently 2-3 weeks for MacBook Pro).\n- Personal phones can have Outlook/Teams via Intune app protection - just ask.",
      doc_type="process_page", space="IT", created="2025-09-01", last_updated="2026-08-24", authors=["Rajesh Kumar"],
      related_systems=["ServiceNow ITSM", "Slack", "Okta SSO"], labels=["service-desk", "how-to"]),

    D("Engineering onboarding guide",
      "**Owner:** Engineering (Rohan Mehta) | **Updated:** 24 July 2026\n\n"
      "## Week one\n- Your role bundle gives you GitHub, Jira, Datadog (read) and the AWS sandbox; your manager requests anything else (production read-only, Snowflake) via the ServiceNow catalog.\n"
      "- Buddy: assigned by your manager; weekly check-ins for 30 days.\n- Mandatory LearnHub: Security Awareness, Code of Conduct; 'Handling Customer Data' if you will use the Admin Console.\n- Read: Code Review & Branch Protection Standard, Incident Management SOP, On-Call policy, ADR-014 (v4 API), the March 2026 postmortem.\n\n"
      "## How we ship\n- Merge to `main` with a CODEOWNER review and green CI. Promote via a PR in `algoworks-deploy`; ArgoCD does the rest.\n"
      "- **Do I need a CHG?** For a standard application deployment (image tag, replicas, resources, feature-flag config of an existing service): **no** - the merged algoworks-deploy PR is the approval (CAB decision, September 2025). For Terraform/infrastructure, network, Okta configuration, database schema or parameters, new services or new external endpoints: **yes**, raise a CHG for the Tuesday/Thursday CAB. *The Change Management Policy page has not yet been updated to say this; the rule here is the operating one.*\n"
      "- **Fridays:** deployments allowed before 14:00 IST if behind a feature flag or trivially reversible; stay online until 16:00. Month-end billing freeze (last two business days) still applies. Mobile releases follow the 48-hour internal-track soak.\n"
      "- Pool/limit/timeout changes: separate PR with the `high-risk-config` label and a second reviewer.\n\n"
      "## Environments\nSandbox (yours), staging (refreshed from prod snapshots Sundays), production (read-only; elevated access is a 4-hour break-glass session with Cloud Lead approval).\n\n"
      "## Where things live\nCode: GitHub algoworks-tech. Work: Jira PLAT/FE/DATA. Docs: this space. Chat: #eng-platform, #eng-frontend, #eng-data, #devops-sre, #incidents.",
      doc_type="process_page", space="ENG", created="2025-10-13", last_updated="2026-07-24", authors=["Rohan Mehta", "Priya Shah"],
      related_systems=["GitHub Enterprise", "ArgoCD Deployment Platform", "Jira"], related_policies=["Change Management Policy", "Deployment & Release Process SOP", "Code Review & Branch Protection Standard"],
      labels=["onboarding", "engineering", "how-we-ship"]),

    D("Working with Finance: month-end calendar, expenses and purchase requests",
      "**Owner:** Finance (Shalini Menon, Ashwin Raman) | **Updated:** 31 August 2026\n\n"
      "## Monthly rhythm\n- **20th:** expense claims cut-off for this month's payroll reimbursement.\n- **BD-2:** freeze on vendor bills dated in the closing month; no production deployments touching billing until BD+1.\n- **BD+6:** books locked.\n- **Wednesdays:** vendor payment run (invoices in by Monday 17:00, quoting the PO number).\n\n"
      "## Expenses (Zoho Expense)\nItemised receipts, correct category, manager then Finance AP approval. Per-diem days: no separate meal claims. If Zoho auto-rejects a claim you believe is valid (age, per-diem rate), raise a ticket in the Finance queue - AP reviews exceptions individually.\n\n"
      "## Buying something\n| Value | What you need |\n|---|---|\n| Up to Rs 25,000 | Team lead OK; expense or corporate card |\n| Rs 25,001 - 1,00,000 | Purchase request; Department Head |\n| Rs 1,00,001 - 5,00,000 | Purchase request; Department Head + AP & Procurement Manager; Security review for software |\n| Above Rs 5,00,000 | Above + CFO; Vendor Onboarding SOP (quotes / single-source justification) |\n"
      "New vendors need the vendor form, GSTIN/PAN, bank verification by call-back and, for SaaS, the Security questionnaire. Allow two weeks for a new vendor.\n\n"
      "## Contacts\nExpenses: #expenses-help / Ramesh Babu, Alok Mishra. Procurement: Kritika Jain, Zara Ahmed. Billing & payroll: Deepa Subramanian. FP&A / NetSuite: Payal Shah.",
      doc_type="process_page", space="FIN", created="2025-11-24", last_updated="2026-08-31", authors=["Shalini Menon"],
      related_systems=["Zoho Expense", "NetSuite ERP"], related_policies=["Travel & Expense Reimbursement Policy", "Procurement & Purchase Order Policy", "Month-End Close Checklist"],
      labels=["finance", "how-to", "month-end"]),

    D("Onboarding buddy guide (People Operations)",
      "**Owner:** People Operations (Swati Kulkarni) | **Updated:** 3 August 2026\n\n"
      "Thank you for being a buddy. You are the new joiner's first friendly face, not their manager or IT.\n\n"
      "## Before Day 1\n- Check with the manager that the onboarding ticket (auto-created from Darwinbox ~10 business days before start) shows the laptop and default bundle as ready.\n- Book a 30-minute coffee for Day 1 afternoon and a weekly 30-minute check-in for four weeks.\n\n"
      "## Day 1\n- Meet them after HR induction (finishes 11:00). Show them the floor, the pantry, the printers, the meeting-room booking in Outlook.\n- Slack: #general, #new-joiners, #it-helpdesk, #kudos, your team channels. Encourage them to introduce themselves in #new-joiners.\n- Point them to LearnHub for the mandatory modules (due in 30 days).\n\n"
      "## Weeks 1-4\n- Explain how your team actually works: which days you come in, where decisions are written down, who to ask for what.\n- If they are missing an application, tell the manager to raise it via the ServiceNow catalog; role bundles cover the basics only.\n- Flag to the manager or HRBP if something feels off - early is better.\n\n"
      "## Hybrid work\nOffice days are set by each department head; check with the manager what the team does and say so plainly. (HR Ops will point to the Hybrid Work Policy; the department practice may differ while the policy is being updated.)",
      doc_type="process_page", space="HR", created="2025-09-08", last_updated="2026-08-03", authors=["Swati Kulkarni"],
      related_systems=["Darwinbox HRMS", "LearnHub LMS"], related_policies=["Employee Onboarding SOP", "Hybrid Work Policy"],
      labels=["onboarding", "buddy"]),

    D("Deal Desk process - discounts, approvals and non-standard terms",
      "**Owner:** Sales Operations & Deal Desk (Arun Prasad) | **Updated:** 4 May 2026\n\n"
      "## When you need Deal Desk\nAny discount above 10%, any payment terms beyond Net-45, custom SLAs, or liability changes. CPQ creates the Deal Desk ticket automatically when you submit a quote above 10%.\n\n"
      "## Discount approvals (as configured in CPQ from April 2026)\n| Discount on TCV | Approver |\n|---|---|\n| Up to 10% | You (recorded on the opportunity) |\n| 10.01-20% | Enterprise Sales Manager / Head of Customer Success (renewals) |\n| 20.01-30% | VP Sales (CFO receives a weekly report of all approvals above 20%) |\n| Above 30% | CEO |\n"
      "_Note: the Discount Approval Matrix page shows the CFO for 20-30%; CPQ reflects the February 2026 agreement between the VP Sales and CFO, and a v4 of the matrix is in progress. Follow CPQ._\n\n"
      "## What Deal Desk checks\nDiscount calculation (free months count), competitor context, multi-year TCV basis, that the approval is recorded on both the ticket and the opportunity before the quote is sent, and that Chargebee is only updated from an approved quote.\n\n"
      "## Turnaround\nSame business day for approvals within Sales; allow two days when Legal or the CFO are involved.",
      doc_type="process_page", space="SALES", created="2025-10-27", last_updated="2026-05-04", authors=["Arun Prasad"],
      related_systems=["Salesforce CRM", "Chargebee Billing"], related_policies=["Discount Approval Matrix"], labels=["deal-desk", "discounts"]),

    D("Marketing content calendar and campaign request process",
      "**Owner:** Content & Brand (Ankit Chawla) | **Updated:** 17 August 2026\n\n"
      "## Requesting content or a campaign\nCreate an issue in Jira **MKT** (content) or **DG** (campaigns) using the request template: audience, goal, channel, target date, product claims to verify. Requests without a Jira issue are not scheduled.\n\n"
      "## Approvals\nBlog/web copy: Content & Brand Manager. Product claims: Product Marketing Lead. Pricing or legal statements: VP Marketing + Finance/Legal. Customer names, logos, quotes: the Sales owner of the account and a signed reference agreement in Salesforce.\n\n"
      "## Publishing\nWebsite changes are staged on WordPress staging (and, from the redesign, Vercel preview) and published by the agency only after written approval on the Jira issue. Email campaigns: build in HubSpot, send to the internal test list, schedule after the approver ticks Approved. No sends on public holidays in the recipient region.\n\n"
      "## Working with the agency\nPixelcraft Studio works in #ext-pixelcraft (Slack Connect). They have sponsored contractor accounts (90-day expiry, Ankit sponsors). They do not have VPN except by specific, time-boxed request.\n\n"
      "## Calendar\nThe content calendar is the MKT board's calendar view; the campaign calendar is DG's. Both are reviewed Mondays 11:00.",
      doc_type="process_page", space="MKT", created="2025-08-25", last_updated="2026-08-17", authors=["Ankit Chawla"],
      related_systems=["Jira", "HubSpot Marketing Hub", "Corporate Website CMS"], related_policies=["Marketing Content Approval & Publishing SOP", "Brand & External Communications Policy"],
      labels=["marketing", "content", "process"]),

    D("How to report a security incident or a phishing email",
      "**Owner:** IAM & Security (Amit Saxena) | **Updated:** 4 May 2026 | **Classification:** Internal\n\n"
      "## Phishing or suspicious email\nClick **Report Phish** in Outlook (desktop, web and mobile). That is all you need to do; Security sees it within minutes. If you clicked a link or entered your password: call the Service Desk (ext. 200) immediately - you will not be in trouble, and speed matters far more than embarrassment.\n\n"
      "## Other security incidents\nLost or stolen laptop/phone, credentials shared by mistake, suspected account compromise, data sent to the wrong recipient, unusual system behaviour: post in **#security** (private - ask to be added) or call the Service Desk out of hours. Do not investigate on your own.\n\n"
      "## What happens next\nSecurity classifies the incident (Incident Management SOP severities apply; a credential compromise is P1), contains it (sessions revoked, factors reset, devices wiped where needed), and follows up with you. Postmortems are blameless.\n\n"
      "## Reminders\n- AlgoWorks never asks for passwords or bank changes by email; vendor bank changes go through Finance AP with a call-back.\n- Credentials belong in 1Password shared vaults, never in Slack, email or documents.\n- Quarterly phishing simulations run under the Security Awareness programme; clicking one leads to a short refresher, nothing else.",
      doc_type="process_page", space="IT", created="2026-04-24", last_updated="2026-05-04", authors=["Amit Saxena"],
      related_systems=["Microsoft 365", "Okta SSO", "1Password Business"], related_policies=["Password & MFA Standard", "Incident Management & Severity Classification SOP"],
      labels=["security", "phishing", "how-to"]),

    D("Customer Success escalation playbook",
      "**Owner:** Customer Success & Support (Anita Desai) | **Updated:** 7 September 2026\n\n"
      "## Priorities\nP1: customer's fleet operations stopped - 30-minute first response 24x7, hourly updates, declare in #incidents. P2: major function impaired with a workaround - 2 business hours. P3: 8 business hours. P4: 2 business days.\n\n"
      "## Tier 1 -> Tier 2 -> Engineering\n1. Tier 1 diagnoses with the Zendesk history and the AlgoWorks Admin Console (read-only; requires the 'Handling Customer Data' course and approvals - plan for a week when onboarding a Support Engineer).\n"
      "2. Tier 2 (Preeti Nambiar, Sameer Khan) reproduces, checks Datadog Tenant SLO dashboards, and escalates to Engineering by creating a linked **Jira SUP** issue and posting in #customer-success. P1s also go to #incidents.\n"
      "3. Engineering on-call acknowledges per the On-Call policy. Customer updates stay with CS.\n\n"
      "## Communication\nUse Zendesk macros for standard updates. Commitments beyond the SLA table need the Head of Customer Success. Incident comms to customers are drafted by CS and reviewed by Marketing (Sanya Kapadia) before sending. Credits follow the Discount Approval Matrix thresholds via Deal Desk.\n\n"
      "## Useful\n- Admin Console impersonation (operators only) for reproducing portal issues.\n- Postmortems for Sev1/Sev2 are in the ENG space; share the customer-safe summary, not the internal doc.",
      doc_type="process_page", space="SALES", created="2025-12-15", last_updated="2026-09-07", authors=["Anita Desai"],
      related_systems=["Zendesk Support Desk", "AlgoWorks Admin Console", "Jira"], related_policies=["Customer Support SLA & Escalation Policy", "Incident Management & Severity Classification SOP"],
      labels=["customer-success", "escalation", "playbook"]),
]

# ---------------------------------------------------------------- team pages (4)
TEAM_PAGES = [
    D("Platform Backend - team page",
      "**Manager:** Rohan Mehta | **Channel:** #eng-platform | **On-call:** PagerDuty schedule 'Platform Backend' (weekly, handover Monday 10:00)\n\n"
      "## What we own\nAlgoWorks Fleet Production Platform (core API, dispatch, telematics ingest), the AlgoWorks Admin Console, GitHub Enterprise and Jira administration (schemes, workflows, integrations), the v4 API migration.\n\n"
      "## Repos\nalgoworks-core, algoworks-api-v4, algoworks-admin-console, telemetry-ingest, algoworks-deploy (shared with Cloud).\n\n"
      "## Rituals\nTeam sync Tue/Thu 10:30 (Falcon). Sprint planning fortnightly Monday. Release manager rotates weekly. Office days: Tuesday and Thursday.\n\n"
      "## How to work with us\n- Bugs and requests: Jira PLAT. Support escalations arrive via SUP.\n- Admin Console access: see the Admin Console guide (training + approvals).\n- Jira project creation: Service Desk creates from the template; ask us for schemes/workflows.\n- Feature flags: Admin Console flags service; every flag has an owner and an expiry.",
      doc_type="team_page", space="ENG", created="2025-10-06", last_updated="2026-08-07", authors=["Rohan Mehta"],
      related_systems=["AlgoWorks Fleet Production Platform", "AlgoWorks Admin Console", "GitHub Enterprise", "Jira"], labels=["team", "engineering"]),
    D("Identity & Access Management - team page",
      "**Lead:** Nikhil Bhatt | **Channel:** #it-access-requests (requests), #security (private, incidents) | **Queue:** IAM in ServiceNow\n\n"
      "## What we own\nOkta, GlobalProtect VPN, 1Password, access request fulfilment, contractor accounts, quarterly access reviews, security engineering (Amit Saxena, Joseph Mathew), the Security Awareness programme, vendor security questionnaires.\n\n"
      "## SLAs\nAccess requests: fulfilled within 3 business days of recorded approval. Lockouts: same day. Contractor accounts: 2 business days.\n\n"
      "## How requests move\nCatalog item -> manager approval (Darwinbox delegate honoured) -> system-owner approval for admin roles -> IAM adds the Okta group -> system admin assigns the in-app role. If a manager is unavailable, ask them to set a delegate or escalate to the Department Head; the queue checklist also records how long a request has been waiting.\n\n"
      "## Reviews\nQuarterly access reviews (last: Q2 2026, next: week of 28 September). Note: the snowflake-pii-reader review has had no owner since the DPO left in February 2026.\n\n"
      "## People\nKavya Reddy (access fulfilment), Lakshmi Narayanan (Okta/VPN engineering), Amit Saxena (security engineering), Joseph Mathew (security analyst, joined June 2026).",
      doc_type="team_page", space="IT", created="2025-09-22", last_updated="2026-08-26", authors=["Nikhil Bhatt"],
      related_systems=["Okta SSO", "GlobalProtect VPN", "1Password Business"], labels=["team", "iam"]),
    D("People Operations - who to ask for what",
      "**Manager:** Geeta Iyengar | **Channel:** #people-ops | **Queue:** HR in ServiceNow\n\n"
      "| Topic | Ask |\n|---|---|\n| Onboarding logistics, Darwinbox records, letters | Rakesh Nair, Ayesha Khan (HR Ops) |\n| Leave, policy questions, general HR queries | HR queue (Ayesha Khan first line) |\n"
      "| Manager coaching, team issues, exceptions - Engineering & IT | Swati Kulkarni (HRBP) |\n| Manager coaching, team issues, exceptions - Sales & Marketing | Fatima Sheikh (HRBP) |\n| Finance & other departments | Geeta Iyengar |\n"
      "| Payslips, PF, Form 16, bank changes | Payroll (Vijay Kumar) - not HR Ops |\n| Referral bonuses | Talent Acquisition (Rohit Sinha) - single owner since September 2026 |\n| Learning budget and courses | L&D (Tarun Bhargava) |\n\n"
      "## Notes\n- HR Ops answers policy questions from the published policies. Where a department practice differs (e.g. office days), the HRBP will confirm the current position.\n- Role bundles for new joiners are documented on the 'Role-based application bundles' page; the Onboarding SOP is being updated to match.",
      doc_type="team_page", space="HR", created="2025-11-03", last_updated="2026-09-22", authors=["Geeta Iyengar"],
      related_systems=["Darwinbox HRMS", "Keka Payroll"], labels=["team", "hr"]),
    D("Data & Analytics Engineering - how to request data and access",
      "**Manager:** Suresh Pillai | **Channel:** #eng-data | **Jira:** DATA\n\n"
      "## Requests\n- **New dashboard or dataset:** DATA issue type 'Data request' with the question you are trying to answer, not the columns you think you need.\n- **Snowflake access:** DATA 'Data access request'. Curated marts: Suresh approves. PII schemas: purpose and expiry required; see the Snowflake Data Access Policy for the sign-off (currently handled by the Data Engineering Manager while the DPO role is vacant).\n- **Metabase:** ServiceNow catalog with your team lead's approval; SQL access needs Suresh.\n\n"
      "## Warehouses and cost\nPer-team warehouses since June 2026; budgets are owned by FP&A. If your query times out, ask in #eng-data first - there may be a dashboard, or we can look at the query - before asking for a larger warehouse.\n\n"
      "## Service accounts\ndbt, Metabase and Fivetran service accounts are ours; key-pair auth, rotated annually.\n\n"
      "## People\nAnanya Chatterjee (warehouse, access), Manish Tiwari (analytics engineering, Metabase, Finance integrations), Divya Menon (pipelines), Ravi Shankar (ML), Pooja Hegde (analyst, Customer 360).",
      doc_type="team_page", space="ENG", created="2025-10-20", last_updated="2026-08-26", authors=["Suresh Pillai"],
      related_systems=["Snowflake Data Warehouse", "Metabase BI", "Jira"], related_policies=["Snowflake Data Access Policy"], labels=["team", "data"]),
]

# ---------------------------------------------------------------- reference pages (6, some generated)
BLR_OFFICE = D("Bengaluru office guide",
    "**Owner:** IT Service Desk (Facilities liaison: Deepak Verma) | **Updated:** 31 March 2026\n\n"
    "## Address and hours\nAlgoWorks, Floors 2-4, Skyline Tech Park, Outer Ring Road, Bengaluru 560103. Building access 07:00-22:00 with ID card; security desk 24x7.\n\n"
    "## Floors\n- **Floor 2:** Sales, Customer Success, Marketing, cafe, reception. Rooms: Heron (8), Kite (4).\n- **Floor 3:** Engineering, IT, Finance, Service Desk walk-up counter (10:00-18:00). Rooms: Falcon (12), Osprey (6), phone booths x4.\n- **Floor 4:** Leadership, HR, boardroom AlgoWorks (16), quiet floor.\n\n"
    "## Wi-Fi\nAlgoWorks-Corp (company devices, Intune profile). AlgoWorks-Guest (visitors, captive portal, 24 h, no internal access; password on the reception screen, rotates monthly).\n\n"
    "## Printing\nFollow-Me printing: send to 'AlgoWorks-Print' and tap your ID card at any printer.\n\n"
    "## Parking\nB1 cars (allocated), B2 two-wheelers (RFID on ID card - raise an IT ticket to map your card).\n\n"
    "## Facilities issues\nAC, chairs, lights, meeting-room AV: raise an IT ticket (category Facilities) - the Service Desk coordinates with the building team.\n\n"
    "## Anchor days\nDepartments choose their office days; most teams are in Tuesday and Thursday; Finance Tuesday-Thursday.",
    doc_type="reference", space="IT", created="2025-07-21", last_updated="2026-03-31", authors=["Deepak Verma"], labels=["office", "bengaluru"])

HOLIDAYS_2026 = D("Public holiday calendar 2026",
    "**Owner:** People Operations | **Published:** 12 January 2026\n\n"
    "12 holidays per location plus 2 optional (restricted) holidays chosen in Darwinbox.\n\n"
    "| Date | Holiday | Bengaluru | Pune | Hyderabad | Singapore |\n|---|---|---|---|---|---|\n"
    "| 1 Jan | New Year's Day | Y | Y | Y | Y |\n| 26 Jan | Republic Day | Y | Y | Y | - |\n| 4 Mar | Holi | Y | Y | Y | - |\n| 19 Mar | Ugadi / Gudi Padwa | Y | Y | Y | - |\n| 20 Mar | Hari Raya Puasa | - | - | - | Y |\n"
    "| 3 Apr | Good Friday | Y | Y | Y | Y |\n| 14 Apr | Ambedkar Jayanti | Y | Y | Y | - |\n| 1 May | Labour Day | Y | Y | Y | Y |\n| 9 Aug | National Day | - | - | - | Y |\n| 15 Aug | Independence Day | Y | Y | Y | - |\n"
    "| 14 Sep | Ganesh Chaturthi | Y | Y | Y | - |\n| 2 Oct | Gandhi Jayanti | Y | Y | Y | - |\n| 20 Oct | Dussehra | Y | Y | Y | - |\n| 1 Nov | Kannada Rajyotsava | Y | - | - | - |\n| 8 Nov | Deepavali | Y | Y | Y | Y |\n| 25 Dec | Christmas | Y | Y | Y | Y |\n\n"
    "Optional holidays and the full list for Singapore are in Darwinbox > Holidays. Office closures are announced in #general.",
    doc_type="reference", space="HR", created="2026-01-12", authors=["Rakesh Nair"], sensitivity="public", labels=["holidays", "2026"])

GLOSSARY = D("AlgoWorks glossary and acronyms",
    "**Owner:** People Operations with Engineering | **Updated:** 15 June 2026\n\n"
    "| Term | Meaning |\n|---|---|\n| AOP | Annual Operating Plan (FY27 = April 2027 - March 2028) |\n| BD-2 / BD+n | Business days before/after month end (close calendar) |\n| Break-glass | Time-bound elevated production access with post-hoc review |\n"
    "| CAB | Change Advisory Board - Tuesdays/Thursdays 15:00 IST |\n| CHG / INC / RITM | ServiceNow change / incident / request item |\n| CPQ | Salesforce Configure-Price-Quote |\n| DPO | Data Protection Officer (role vacant since February 2026) |\n"
    "| DL | Distribution list (email) |\n| GitOps | Deployments driven by reviewed PRs in algoworks-deploy, reconciled by ArgoCD |\n| HRBP | HR Business Partner |\n| IAM | Identity & Access Management team |\n| JIT provisioning | Creating a user on first SSO login |\n"
    "| LWD | Last working day |\n| MAM | Mobile application management (Intune app protection on personal phones) |\n| PL | Privilege Leave |\n| POD | Proof of delivery (driver app) |\n| Role bundle | Okta groups applied automatically to a new joiner based on Darwinbox role code |\n"
    "| Sev1-4 | Incident severities (Incident Management SOP) |\n| SDR / AE / CSM / TAM | Sales Development Rep / Account Executive / Customer Success Manager / Technical Account Manager |\n| Tenant | A customer's isolated space in the AlgoWorks Fleet platform |\n| WH_* | Snowflake warehouses per team |",
    doc_type="reference", space="HR", created="2025-08-18", last_updated="2026-06-15", authors=["Rakesh Nair", "Priya Shah"], labels=["glossary"])

REMOTE_GUIDE = D("Remote work setup guide",
    "**Owner:** IT Service Desk | **Updated:** 30 June 2026\n\n"
    "## Before you leave the office\nInstall from the Company Portal: GlobalProtect, Okta Verify (phone), 1Password, Slack, Zoom. Test the VPN once from the office guest network.\n\n"
    "## At home\n- VPN is needed only for internal tools (Admin Console, Metabase, Snowflake, restricted Confluence, file shares). Email, Slack, Salesforce, Zendesk, GitHub work without it.\n- Router MTU problems show up as 'connects then drops'; IAM can push a lower MTU for your gateway profile.\n- Use the company laptop only. Personal phones can run Outlook/Teams with Intune app protection.\n\n"
    "## Security\nLock your screen, do not use public Wi-Fi without VPN, report lost devices immediately. Restricted data (payroll, contracts, customer PII) must not be downloaded to personal devices or printed at home.\n\n"
    "## Equipment\nThe office does not reimburse home monitors or chairs (Hybrid Work Policy). Designated remote employees may request a monitor from the Service Desk (shipped once). Connectivity allowances are decided by Finance - check with Finance AP for the current position.\n\n"
    "## Time zones\nCore collaboration hours 11:00-16:00 IST. Singapore and US staff overlap at least 3 hours; use the Outlook scheduling assistant.",
    doc_type="reference", space="IT", created="2025-10-06", last_updated="2026-06-30", authors=["Shruti Joshi"],
    related_systems=["GlobalProtect VPN", "Microsoft Intune"], related_policies=["Hybrid Work Policy", "VPN & Remote Connectivity Policy"], labels=["remote", "how-to"])


def _systems_directory(reg) -> dict:
    rows = []
    for s in reg.systems:
        team = reg.by_id[s["owner_team_id"]]
        lead = reg.by_id[team["lead_employee_id"]]["name"]
        rows.append(f"| {s['system_id']} | {s['name']} | {team['name']} ({lead}) | {s['category']} | {s['criticality']} | {s['access_request_process_summary']} |")
    body = ("**Owner:** IT Service Desk & Endpoint (Rajesh Kumar) with IAM | **Updated:** 24 August 2026\n\n"
            "The system-owner table below drives approval routing in the ServiceNow access catalog. Owning team leads approve admin-role "
            "requests; IAM fulfils the Okta group change; the owning team's administrator assigns in-app roles.\n\n"
            "| ID | System | Owner team (lead) | Category | Criticality | How to get access |\n|---|---|---|---|---|---|\n" + "\n".join(rows)
            + "\n\n_Note (August 2026): Jira project creation is handled by the Service Desk from the standard template although Platform Backend owns Jira._")
    return D("Systems Directory - owners, criticality and how to get access", body, doc_type="reference", space="IT",
             created="2025-09-29", last_updated="2026-08-24", authors=["Rajesh Kumar", "Kavya Reddy"],
             related_systems=[s["name"] for s in reg.systems], labels=["systems", "directory", "access"])


SPACE = {"DEPT-01": "ENG", "DEPT-02": "IT", "DEPT-03": "SALES", "DEPT-04": "HR", "DEPT-05": "FIN", "DEPT-06": "MKT",
         "DEPT-07": "PRODUCT", "DEPT-08": "LEGAL", "DEPT-09": "COMPANY"}


def _org_chart(reg) -> dict:
    """Company overview: departments, heads and teams with their leads (member lists live in the department rosters)."""
    active = [e for e in reg.employees if e["status"] != "exited"]
    on_leave = sum(1 for e in active if e["status"] == "on_leave")
    ceo = next(e for e in reg.employees if e["role"] == "Chief Executive Officer")
    lines = []
    for dpt in reg.departments:
        head = reg.by_id[dpt["head_employee_id"]]
        size = sum(1 for e in active if e["department_id"] == dpt["department_id"])
        lines.append(f"## {dpt['name']} - {head['name']} ({head['role']}) - {size} people")
        for t in reg.teams:
            if t["department_id"] == dpt["department_id"]:
                lead = reg.by_id[t["lead_employee_id"]]
                lines.append(f"- **{t['name']}** - lead {lead['name']} ({lead['role']}); {t['slack_channel']}; "
                             f"{len(t['member_employee_ids'])} members")
        lines.append("")
    body = (f"**Owner:** People Operations | **Generated from Darwinbox:** 22 September 2026 | Headcount: {len(active)} "
            f"({on_leave} on leave)\n\n"
            f"{len(reg.departments)} departments, {len(reg.teams)} teams. Team leads report to department heads; department heads "
            f"report to the CEO, {ceo['name']}. Full member lists are in each department's roster page.\n\n" + "\n".join(lines))
    return D("Organisation chart and department overview", body, doc_type="reference", space="HR", created="2025-08-04",
             last_updated="2026-09-22", authors=["Geeta Iyengar"], labels=["org-chart", "teams"])


def _department_rosters(reg) -> list[dict]:
    docs = []
    for dpt in reg.departments:
        head = reg.by_id[dpt["head_employee_id"]]
        lines = [f"**Owner:** People Operations | **Department head:** {head['name']} ({head['role']}) | **Updated:** 22 September 2026\n"]
        for t in reg.teams:
            if t["department_id"] != dpt["department_id"]:
                continue
            lead = reg.by_id[t["lead_employee_id"]]
            members = [reg.by_id[m] for m in t["member_employee_ids"] if m != t["lead_employee_id"]]
            lines.append(f"## {t['name']}\nLead: {lead['name']} ({lead['role']}) | Channel: {t['slack_channel']}\n")
            lines += [f"- {m['name']} - {m['role']} ({m['location']})" for m in members]
            lines.append("")
        docs.append(D(f"{dpt['name']} - department roster", "\n".join(lines), doc_type="reference", space=SPACE[dpt["department_id"]],
                      created="2025-08-04", last_updated="2026-09-22", authors=["Geeta Iyengar"],
                      labels=["roster", "org-chart", dpt["code"].lower()]))
    return docs


def _generated_team_pages(reg, existing_titles: set) -> list[dict]:
    """A short team page for every team without a hand-written one."""
    from common import rng
    r = rng("team-pages")
    docs = []
    for t in reg.teams:
        title = f"{t['name']} - team page"
        if title in existing_titles:
            continue
        lead = reg.by_id[t["lead_employee_id"]]
        dept = reg.by_id[t["department_id"]]
        members = [reg.by_id[m] for m in t["member_employee_ids"] if m != t["lead_employee_id"]]
        updated = f"2026-0{r.randint(5, 9)}-{r.randint(1, 22):02d}"
        body = (f"**Manager:** {lead['name']} ({lead['role']}) | **Department:** {dept['name']} | **Channel:** {t['slack_channel']} | "
                f"**Team size:** {len(t['member_employee_ids'])} | **Updated:** {updated}\n\n"
                f"## What we do\n{t['charter']}\n\n"
                f"## How to work with us\n- Questions: post in {t['slack_channel']} (we answer within one business day).\n"
                f"- Requests: raise a ServiceNow ticket and mention the {t['name']} team, or ask {lead['name'].split()[0]} for anything urgent.\n"
                f"- Escalations: {lead['name']}, then {reg.by_id[dept['head_employee_id']]['name']} ({dept['name']} head).\n\n"
                f"## Who's who\n" + "\n".join(f"- {m['name']} - {m['role']}" for m in members[:30])
                + (f"\n- ...and {len(members) - 30} more (see the {dept['name']} roster)" if len(members) > 30 else ""))
        docs.append(D(title, body, doc_type="team_page", space=SPACE[t["department_id"]], created="2025-06-02",
                      last_updated=updated, authors=[lead["name"]], labels=["team", dept["code"].lower()]))
    return docs


def build_standalone_docs(reg) -> list[dict]:
    docs = []
    # system guides
    for name, (created, updated, author, tasks, issues, support, sens) in SYSTEM_GUIDES.items():
        s = reg.system(name)
        team = reg.by_id[s["owner_team_id"]]
        body = (f"**System ID:** {s['system_id']} | **Owner team:** {team['name']} | **Criticality:** {s['criticality']} | **Category:** {s['category']} | **Updated:** {updated}\n\n"
                f"## What it is\n{s['description']}\n\n"
                f"## How to get access\n{s['access_request_process_summary']}\n\n"
                "## Common tasks\n" + "\n".join(f"- {t}" for t in tasks) + "\n\n"
                "## Known issues and gotchas\n" + "\n".join(f"- {i}" for i in issues) + "\n\n"
                f"## Support\n{support}")
        space = SPACE[team["department_id"]]
        docs.append(D(f"{name} - user guide", body, doc_type="system_guide", space=space, created=created, last_updated=updated,
                      authors=[author], sensitivity=sens, related_systems=[name], labels=["system-guide", s["system_id"].lower()]))
    # project pages
    for name, (created, updated, author, goals, scope, milestones, risks) in PROJECT_PAGES.items():
        p = reg.project(name)
        team = reg.by_id[p["team_id"]]
        staff = ", ".join(reg.by_id[e]["name"] for e in p["staffed_employee_ids"])
        systems = ", ".join(reg.by_id[s]["name"] for s in p["related_system_ids"])
        body = (f"**Project ID:** {p['project_id']} | **Team:** {team['name']} | **Status:** {p['status']} | **Start:** {p['start_date']}"
                + (f" | **End:** {p['end_date']}" if p.get("end_date") else "") + f" | **Updated:** {updated}\n\n"
                f"## Goal\n{goals}\n\n## Summary\n{p['description']}\n\n## Scope notes\n{scope}\n\n"
                "## Milestones\n| Date | Milestone |\n|---|---|\n" + "\n".join(f"| {dte} | {txt} |" for dte, txt in milestones) + "\n\n"
                f"## Team\n{staff}\n\n## Systems\n{systems}\n\n## Risks and open items\n{risks}")
        space = SPACE[team["department_id"]]
        docs.append(D(f"{name} - project page", body, doc_type="project_page", space=space, created=created, last_updated=updated,
                      authors=[author], related_projects=[name], related_systems=[reg.by_id[s]["name"] for s in p["related_system_ids"]],
                      labels=["project", p["project_id"].lower()]))
    docs += DEPT_PAGES + TEAM_PAGES
    docs += [BLR_OFFICE, HOLIDAYS_2026, GLOSSARY, REMOTE_GUIDE, _systems_directory(reg), _org_chart(reg)]
    assert len(docs) == 50, len(docs)  # the hand-written and per-system set
    docs += _department_rosters(reg)
    docs += _generated_team_pages(reg, {x["title"] for x in docs})
    return docs
