"""Layer 5 - Policies / SOPs (36) with full document text.

13 of the 35 are deliberately stale (last_updated 6-18 months before SIM_TODAY = 2026-09-24).
Those are the ones the Layer 6 drift events contradict. The specific numbers in the text
(SLA days, thresholds, approver roles) are the "hooks" the events pull against.
"""
from __future__ import annotations

from textwrap import dedent

# (title, owner_dept, owner_team, systems, version, last_updated, status, sensitivity, stale?, text)
POLICIES = [
    # ============================================================ IT & Infrastructure
    ("Application Access Request Policy", "IT & Infrastructure", "Identity & Access Management",
     ["Okta SSO", "ServiceNow ITSM", "Salesforce CRM", "Zendesk Support Desk", "HubSpot Marketing Hub", "Metabase BI", "Jira"],
     "v3", "2025-05-12", "active", "internal", True, """
    # Application Access Request Policy (v3)

    **Owner:** Identity & Access Management (IT & Infrastructure) | **Approved by:** Head of IT & Infrastructure | **Effective:** 12 May 2025

    ## 1. Purpose
    This policy defines how AlgoWorks employees obtain access to business applications (Salesforce, Zendesk, HubSpot, Metabase, Jira, shared mailboxes and any other Okta-integrated application) and how Identity & Access Management (IAM) fulfils those requests. It exists to make sure every access grant is authorised, recorded and reviewable.

    ## 2. Scope
    All employees, contractors and interns. Applies to every application that is not part of the default new-joiner bundle (Microsoft 365, Slack, Confluence, Darwinbox self-service, Zoho Expense, LearnHub).

    ## 3. Policy
    3.1 All application access must be requested through ServiceNow (Employee Service Portal > Request Access). Requests made only over Slack, email or in person are not valid and will not be fulfilled.
    3.2 Every request requires approval from the requester's **line manager** as recorded in Darwinbox. The approval must be recorded on the ServiceNow ticket.
    3.3 If the line manager is unavailable (leave, travel) for more than **2 business days**, the requester or IAM must escalate the approval to the **Department Head**. No other person may approve on the manager's behalf.
    3.4 IAM will fulfil an approved request within **3 business days** of approval (the fulfilment SLA). The SLA clock starts only when approval is recorded.
    3.5 IAM must **not** provision access without a recorded approval, regardless of how long the request has been pending. A pending approval is not an authorisation.
    3.6 Where an application has a designated system owner (see the Systems Directory in Confluence), the system owner or their administrator performs the in-application role assignment after IAM adds the user to the Okta group.
    3.7 Access is granted at the lowest privilege level that meets the stated business need. Administrative roles require an additional approval from the system's owning team lead.
    3.8 Temporary access must have an end date on the ticket; IAM removes it on that date.

    ## 4. Procedure
    1. Requester raises "Request Access" in ServiceNow, selecting the application and the business justification.
    2. ServiceNow routes the approval to the line manager (auto-populated from Darwinbox).
    3. On approval, the ticket is assigned to the IAM queue. IAM adds the user to the relevant Okta group and, where applicable, notifies the system administrator for role assignment.
    4. IAM closes the ticket with a note of the group/role granted.

    ## 5. Exceptions
    Exceptions to 3.2-3.5 require written approval from the Head of IT & Infrastructure and must be attached to the ticket.

    ## 6. Review
    This policy is reviewed annually by IAM. Quarterly access reviews are performed for high-criticality applications.

    _Revision history: v1 (Mar 2023) initial; v2 (Feb 2024) added Okta group model; v3 (May 2025) added 3-business-day fulfilment SLA and Department Head escalation rule._
    """),

    ("VPN & Remote Connectivity Policy", "IT & Infrastructure", "Identity & Access Management",
     ["GlobalProtect VPN", "Okta SSO"], "v2", "2025-05-26", "active", "internal", True, """
    # VPN & Remote Connectivity Policy (v2)

    **Owner:** Identity & Access Management | **Effective:** 26 May 2025

    ## 1. Purpose
    Defines who may use the GlobalProtect VPN, how access is granted and renewed, and the controls applied to remote connectivity into the AlgoWorks network.

    ## 2. Policy
    2.1 VPN is required to reach internal-only services: the AlgoWorks Admin Console, Metabase, the Snowflake private link, restricted Confluence spaces and office file shares.
    2.2 VPN access is requested through the ServiceNow "VPN access" item and requires line manager approval. IAM adds the user to the `vpn-employees` Okta group.
    2.3 **VPN access is granted for a fixed period of 90 days.** Continued access requires a new, manager-approved renewal request before expiry. Access that is not renewed is removed automatically.
    2.4 Contractors and agency staff may **not** be added to `vpn-employees`. Contractor connectivity is provided exclusively through the **contractor jump host** (bastion) with a 30-day expiry, sponsored by a AlgoWorks employee.
    2.5 Split tunnelling is enabled by default; full-tunnel profiles are available on request for staff travelling to high-risk locations.
    2.6 Personal devices may not connect to the VPN. Only Intune-enrolled, compliant company devices are permitted.
    2.7 VPN sessions time out after 12 hours; re-authentication with Okta MFA is required.

    ## 3. Responsibilities
    - IAM: group management, renewals, contractor jump-host accounts, quarterly review of active VPN users.
    - Cloud Infrastructure: gateway availability, certificate renewal, capacity.
    - Users: keep the GlobalProtect client updated; report suspected compromise within 1 hour.

    ## 4. Exceptions
    Exceptions require approval from the IAM & Security Lead and are logged in the Security exceptions register.

    _Revision history: v1 (Jan 2024) initial; v2 (May 2025) formalised 90-day expiry and contractor jump-host requirement._
    """),

    ("Password & MFA Standard", "IT & Infrastructure", "Identity & Access Management",
     ["Okta SSO", "1Password Business"], "v4", "2026-05-04", "active", "internal", False, """
    # Password & MFA Standard (v4)

    **Owner:** Identity & Access Management | **Effective:** 4 May 2026

    ## 1. Requirements
    1.1 Okta is the single sign-on identity provider. Where an application supports SSO, local passwords must be disabled.
    1.2 The Okta password must be at least 14 characters, not contain the user's name or "algoworks", and must not be reused from the previous 12 passwords. Passwords do not expire on a schedule; they are rotated on suspicion of compromise.
    1.3 Multi-factor authentication is mandatory for every account. Accepted factors: Okta Verify push with number matching, FIDO2 security keys and platform authenticators (Touch ID / Windows Hello). SMS is not an accepted factor.
    1.4 Service accounts and shared credentials (demo environments, vendor portals, social media accounts) must be stored in a **1Password shared vault**, never in Slack messages, email, Confluence pages or spreadsheets. Each vault has a named owner responsible for membership.
    1.5 Credentials found in Slack, email or a repository will be rotated by IAM without prior notice and the owner informed.
    1.6 Break-glass local administrator credentials for Okta outages are held in a sealed 1Password vault accessible to the IAM & Security Lead and the Head of IT & Infrastructure, and their use is logged and reviewed.

    ## 2. Lost or compromised factors
    Users who lose their MFA device must contact the IT Service Desk, who verify identity (video call + manager confirmation) before IAM resets the factor. Self-service factor reset is available if a second enrolled factor exists.

    ## 3. Enforcement
    Non-compliant applications are blocked in Okta. Repeated credential sharing is treated as a Code of Conduct matter.

    _Revision history: v3 (Jun 2025); v4 (May 2026) added number matching, removed SMS, added 1Password vault ownership rule._
    """),

    ("Laptop & Endpoint Provisioning SOP", "IT & Infrastructure", "IT Service Desk & Endpoint",
     ["Microsoft Intune", "ServiceNow ITSM"], "v4", "2025-08-18", "active", "internal", True, """
    # Laptop & Endpoint Provisioning SOP (v4)

    **Owner:** IT Service Desk & Endpoint | **Effective:** 18 August 2025

    ## 1. Standard devices
    | Role family | Standard device |
    |---|---|
    | Engineering, Data, Design | MacBook Pro 14" (M-series, 16 GB / 512 GB) |
    | All other roles | Lenovo ThinkPad T14 (16 GB / 512 GB) or MacBook Air on request |
    Non-standard configurations (32 GB RAM, larger storage) require a written justification approved by the requester's Department Head.

    ## 2. Lead times
    2.1 New-joiner laptops are ordered when the onboarding ticket is received and are provisioned and ready on Day 1.
    2.2 For replacement or additional device requests, the Service Desk **delivers the device within 5 business days** of the request being approved by the line manager. The Service Desk maintains a buffer stock of 4 MacBook Pros and 4 ThinkPads to meet this.
    2.3 Where a device is under repair for more than 2 business days, a loaner device is issued.

    ## 3. Provisioning steps
    1. Asset tagged and recorded in the ServiceNow CMDB (asset tag, serial, assigned user).
    2. Enrolled in Microsoft Intune; compliance policy applied (disk encryption, OS updates, screen lock, Defender).
    3. Okta Verify, Slack, GlobalProtect, 1Password and Microsoft 365 apps installed via the Company Portal.
    4. Local admin rights are **not** granted by default; engineers may request admin rights via ServiceNow (manager approval).
    5. Handover form signed in ServiceNow by the user.

    ## 4. Refresh and return
    Devices are refreshed on a **4-year cycle** or when repair cost exceeds 50% of replacement. Devices are returned to the Service Desk on the last working day (see the Offboarding SOP) and wiped within 5 business days.

    ## 5. Peripherals
    One external monitor, keyboard and mouse per desk are provided from stock on request; no approval needed. Second monitors require manager approval.

    _Revision history: v3 (Nov 2024); v4 (Aug 2025) updated standard models and confirmed 5-business-day delivery SLA and buffer stock._
    """),

    ("Employee Offboarding & Access Revocation SOP", "IT & Infrastructure", "Identity & Access Management",
     ["Okta SSO", "Darwinbox HRMS", "ServiceNow ITSM", "GitHub Enterprise", "1Password Business"],
     "v3", "2026-04-06", "active", "internal", False, """
    # Employee Offboarding & Access Revocation SOP (v3)

    **Owner:** Identity & Access Management with People Operations | **Effective:** 6 April 2026

    ## 1. Trigger
    People Operations records the exit in Darwinbox, which creates an offboarding ticket in ServiceNow assigned to IAM at least 5 business days before the last working day (same day for involuntary exits).

    ## 2. Timeline
    | When | Action | Owner |
    |---|---|---|
    | LWD - 5 days | Manager completes the "knowledge & ownership transfer" checklist in the ticket: documents, approvals/queues, shared vaults, on-call rotations, recurring meetings, system-owner roles. | Line manager |
    | LWD 18:00 IST | Okta account disabled; all sessions revoked; mail forwarding to manager for 30 days. | IAM |
    | LWD + 1 business day | Removal from all Okta groups, GitHub org, AWS Identity Center, Slack deactivation, shared vault ownership transferred. | IAM |
    | LWD + 5 business days | Laptop returned and wiped; asset record updated. | Service Desk |
    | LWD + 30 days | Mailbox converted to shared and archived; OneDrive transferred to manager. | Service Desk |

    ## 3. Ownership transfer
    3.1 Any approval role held by the leaver (e.g. ServiceNow approver, Jira approval step, Snowflake role owner, system owner in the Systems Directory) **must be reassigned before LWD** and the new owner named on the offboarding ticket. IAM will not close the ticket until this section is complete.
    3.2 Leavers who are named in a policy or SOP as an approver: the policy owner must update the document within 10 business days.

    ## 4. Contractors
    Contractor accounts follow the same timeline, triggered by the sponsor's notice or the account expiry date, whichever is earlier.

    _Revision history: v2 (Jul 2025); v3 (Apr 2026) added section 3 (ownership transfer) after the February 2026 DPO exit left approval queues unowned._
    """),

    ("Production Access & Break-Glass Policy", "IT & Infrastructure", "Cloud Infrastructure & Security",
     ["AWS Production Account", "ArgoCD Deployment Platform", "Datadog Monitoring"], "v2", "2026-06-15", "active", "restricted", False, """
    # Production Access & Break-Glass Policy (v2)

    **Owner:** Cloud Infrastructure & Security | **Effective:** 15 June 2026 | **Classification:** Restricted

    ## 1. Standing access
    1.1 Engineers in Platform Backend, Frontend & Mobile, Data Engineering and Cloud Infrastructure receive **read-only** access to the AWS production account (IAM Identity Center permission set `ProdReadOnly`) via their Okta group.
    1.2 No individual holds standing write or administrator access to production. Production changes are made through ArgoCD (application workloads) or reviewed infrastructure-as-code pull requests.

    ## 2. Elevated (break-glass) access
    2.1 Elevated access (`ProdOperator` or `ProdAdmin`) is time-bound to a **4-hour session** and must be requested in ServiceNow using the "Production elevated access" item, stating the incident or change reference.
    2.2 Approval: the Cloud Infrastructure Lead, or during a declared Sev1/Sev2 incident, the on-call incident commander. Approval must be recorded on the ticket before the session is activated.
    2.3 All elevated sessions are logged to CloudTrail and Datadog; a **post-hoc review** is performed by the Cloud Infrastructure Lead within 2 business days and recorded on the ticket.
    2.4 Elevated access is never used to bypass ArgoCD for routine deployments.

    ## 3. Database access
    Direct production database access is via the bastion with per-user credentials issued for 24 hours. Query logs are retained for 1 year. Bulk exports of customer data require Data Protection review.

    ## 4. Violations
    Any use of elevated access without a ticket is a security incident and is reported to the Head of IT & Infrastructure.

    _Revision history: v1 (Sep 2025); v2 (Jun 2026) shortened sessions from 8h to 4h and added the incident-commander approval path._
    """),

    ("Software Procurement & SaaS Approval Policy", "IT & Infrastructure", "Identity & Access Management",
     ["Okta SSO", "ServiceNow ITSM", "NetSuite ERP"], "v3", "2026-04-20", "active", "internal", False, """
    # Software Procurement & SaaS Approval Policy (v3)

    **Owner:** IAM & Security (with Finance Procurement) | **Effective:** 20 April 2026

    ## 1. Purpose
    Prevents unmanaged SaaS sprawl and ensures every tool that holds AlgoWorks data is security-reviewed, SSO-integrated where possible and budgeted.

    ## 2. Approval thresholds (annual contract value)
    | Value | Approver |
    |---|---|
    | Up to Rs 1,00,000 | Team lead + Security review |
    | Rs 1,00,001 - 5,00,000 | Department Head + Security review + Procurement |
    | Above Rs 5,00,000 | CFO + Department Head + Security review + Procurement (competitive quotes per the Vendor Onboarding SOP) |

    ## 3. Requirements for any new SaaS tool
    3.1 A ServiceNow "New software / SaaS" request naming the business owner, data to be stored and expected users.
    3.2 Security review by IAM & Security: SSO (SAML/OIDC) support, data residency, SOC 2 / ISO 27001 report, DPA where personal data is processed. Tools that cannot integrate with Okta need a documented exception.
    3.3 Procurement adds the vendor in NetSuite and records the renewal date; auto-renewals must be flagged 60 days before renewal.
    3.4 Free tiers and personal-card purchases of software that will hold company data are not permitted.

    ## 4. Renewals
    Renewals of existing tools follow the same thresholds but do not require a new security review unless scope or data changes.

    _Revision history: v2 (Aug 2025); v3 (Apr 2026) raised the team-lead threshold from Rs 50,000 to Rs 1,00,000._
    """),

    ("Incident Management & Severity Classification SOP", "IT & Infrastructure", "Cloud Infrastructure & Security",
     ["Datadog Monitoring", "ServiceNow ITSM", "Slack", "AlgoWorks Fleet Production Platform"], "v4", "2026-04-01", "active", "internal", False, """
    # Incident Management & Severity Classification SOP (v4)

    **Owner:** Cloud Infrastructure & Security | **Effective:** 1 April 2026

    ## 1. Severity levels
    | Sev | Definition | Response | Update cadence |
    |---|---|---|---|
    | Sev1 | Production platform down or degraded for >25% of customers; data breach; payment processing down | Acknowledge in 15 min, incident commander assigned, #incidents channel + status page | Every 30 min |
    | Sev2 | Major feature unavailable, single large customer down, internal critical system (Okta, VPN, M365) down for all staff | Acknowledge in 30 min | Every 60 min |
    | Sev3 | Minor feature degraded, workaround exists, internal tool down for a team | Next business day | Daily |
    | Sev4 | Cosmetic / single user | Standard ticket SLA | - |

    ## 2. Process
    1. Anyone can declare an incident by posting in **#incidents** with `!incident` or by paging via PagerDuty. A ServiceNow INC is opened (or linked) for every Sev1-Sev3.
    2. The incident commander (on-call lead for the affected system) coordinates, assigns a scribe and posts updates at the cadence above.
    3. Customer-facing Sev1/Sev2: Customer Success posts to the status page and drafts customer comms; Marketing reviews external wording.
    4. Resolution is announced in #incidents and on the ticket with a summary and time-to-resolve.

    ## 3. Postmortems
    A blameless postmortem is **mandatory for Sev1 and Sev2 within 5 business days**, published in the Engineering Confluence space, with action items tracked in Jira. Sev3 postmortems are at the team's discretion.

    ## 4. Vendor incidents
    Outages of vendor systems (Okta, Slack, AWS regional events) are handled as incidents for communication purposes; the runbook for each critical vendor is linked from the IT Runbooks page.

    _Revision history: v3 (Sep 2025); v4 (Apr 2026) added Sev2 definition for internal critical systems and the 5-day postmortem deadline._
    """),

    ("Change Management Policy", "IT & Infrastructure", "Cloud Infrastructure & Security",
     ["ServiceNow ITSM", "AWS Production Account", "ArgoCD Deployment Platform", "AlgoWorks Fleet Production Platform"],
     "v2", "2025-06-09", "active", "internal", True, """
    # Change Management Policy (v2)

    **Owner:** Cloud Infrastructure & Security | **Approved by:** Head of IT & Infrastructure | **Effective:** 9 June 2025

    ## 1. Purpose
    To ensure changes to production systems are planned, reviewed, approved and reversible.

    ## 2. Scope
    All changes to production infrastructure and **all production application deployments** of the AlgoWorks Fleet platform, customer portal, mobile backend services, and internal systems (Okta configuration, VPN gateways, ServiceNow workflows, network equipment).

    ## 3. Policy
    3.1 Every production change requires a **Change Request (CHG) record in ServiceNow** describing the change, risk, test evidence, rollback plan and implementation window.
    3.2 Change Requests are reviewed and approved by the **Change Advisory Board (CAB)**, which meets on **Tuesdays and Thursdays at 15:00 IST**. Changes must be submitted at least one business day before the CAB meeting at which they are to be reviewed.
    3.3 CAB membership: Cloud Infrastructure Lead (chair), IAM & Security Lead, Engineering Manager (Platform), IT Service Desk Manager, Head of Customer Success (for customer-impacting changes).
    3.4 **Emergency changes** (to restore service during an incident) may be approved verbally by the Cloud Infrastructure Lead and must have a CHG raised retrospectively within 1 business day and reviewed at the next CAB.
    3.5 Changes are implemented only within the approved window. Unapproved changes are treated as incidents.
    3.6 The CHG record must be updated with the outcome (successful / rolled back / failed) within 1 business day of implementation.

    ## 4. Change categories
    - **Standard**: pre-approved, repeatable, low-risk (e.g. adding a user to a group). Logged but not reviewed at CAB.
    - **Normal**: everything else, including application deployments. Requires CAB approval.
    - **Emergency**: see 3.4.

    _Revision history: v1 (Feb 2024) initial; v2 (Jun 2025) moved CAB to twice weekly and clarified that application deployments are Normal changes._
    """),

    ("Data Classification & Handling Standard", "IT & Infrastructure", "Identity & Access Management",
     ["Snowflake Data Warehouse", "Microsoft 365", "Confluence", "AlgoWorks Admin Console"], "v2", "2026-05-18", "active", "internal", False, """
    # Data Classification & Handling Standard (v2)

    **Owner:** IAM & Security | **Effective:** 18 May 2026

    ## 1. Classes
    | Class | Examples | Handling |
    |---|---|---|
    | Public | Website content, published pricing, press releases | No restrictions |
    | Internal | Most Confluence pages, Slack channels, tickets, internal reports | AlgoWorks staff and sponsored contractors only; no public sharing |
    | Restricted | Payroll, compensation, performance reviews, security runbooks, customer contracts, source code | Named-group access only; encrypted at rest; no personal devices; no external sharing without DPA |
    | Confidential-PII | Customer driver and end-user personal data, employee personal data | Restricted controls plus access logging, purpose limitation and Data Protection review for new uses |

    ## 2. Labelling
    Confluence spaces, SharePoint libraries and Snowflake schemas must carry a classification label. Snowflake schemas containing PII are tagged `pii=true` and gated by the Snowflake Data Access Policy.

    ## 3. Handling rules
    3.1 Restricted and Confidential-PII data may not be pasted into Slack public channels, personal email, or third-party AI tools that are not on the approved list.
    3.2 Exports of PII from production systems (Admin Console, Snowflake, Zendesk) require a ticket stating purpose and retention period.
    3.3 Customer data used for demos must be anonymised or come from the demo tenant.

    ## 4. Data Protection role
    Data Protection review is performed by the Data Protection Officer. (See the Snowflake Data Access Policy and the Offboarding SOP regarding ownership transfer of this role.)

    _Revision history: v1 (Oct 2024); v2 (May 2026) added Confidential-PII class and AI-tool restriction._
    """),

    ("Privileged Access & Admin Console Policy", "IT & Infrastructure", "Identity & Access Management",
     ["AlgoWorks Admin Console", "Okta SSO", "LearnHub LMS"], "v2", "2026-04-27", "active", "restricted", False, """
    # Privileged Access & Admin Console Policy (v2)

    **Owner:** IAM & Security with Platform Backend | **Effective:** 27 April 2026 | **Classification:** Restricted

    ## 1. Scope
    The AlgoWorks Admin Console (tenant lookup, feature flags, subscription state, user impersonation) and any other internal tool that exposes customer PII or allows changes to customer tenants.

    ## 2. Access levels
    - `console-readonly`: view tenant configuration, devices, subscription state. No impersonation.
    - `console-operator`: read-only plus feature-flag changes and customer-user impersonation (logged).
    - `console-admin`: Platform Backend engineers only.

    ## 3. Requirements for access
    3.1 The requester must have **completed the "Handling Customer Data" course in LearnHub within the last 12 months** before access is granted. IAM verifies completion on the ticket.
    3.2 The request is raised in ServiceNow and requires approval from the requester's line manager **and** the **Engineering Manager, Platform** (as system owner).
    3.3 `console-operator` additionally requires approval from the IAM & Security Lead.
    3.4 IAM adds the user to the Okta group only after 3.1-3.3 are recorded on the ticket. **There are no exceptions to the training requirement**; urgent customer issues are handled by an existing operator on the requester's behalf.

    ## 4. Review and revocation
    Access is reviewed quarterly by the Platform Engineering Manager; users with no console login in 90 days are removed. Impersonation sessions are logged and sampled monthly.

    _Revision history: v1 (Nov 2025) initial; v2 (Apr 2026) made the training requirement explicit and removed the "manager attestation in lieu of training" option._
    """),

    ("BYOD & Mobile Device Policy", "IT & Infrastructure", "IT Service Desk & Endpoint",
     ["Microsoft Intune", "Microsoft 365", "Slack"], "v1", "2025-06-23", "active", "internal", True, """
    # BYOD & Mobile Device Policy (v1)

    **Owner:** IT Service Desk & Endpoint | **Effective:** 23 June 2025

    ## 1. Policy
    1.1 **Personal mobile devices (phones and tablets) are not permitted to access corporate email, calendar, OneDrive or Slack.**
    1.2 Employees whose role requires mobile access to email (Sales, Customer Success, leadership, on-call engineers) are issued a **company-owned mobile device** enrolled in Microsoft Intune with full device management.
    1.3 Company mobile devices are requested through ServiceNow with Department Head approval and are subject to the same return rules as laptops.
    1.4 Personal laptops may never be used for AlgoWorks work; see the Laptop & Endpoint Provisioning SOP.
    1.5 Exceptions to 1.1 require written approval from the Head of IT & Infrastructure and are limited to 30 days.

    ## 2. Rationale
    Intune application-protection policies for unmanaged devices were evaluated in 2025 and not adopted at that time pending a licence review.

    ## 3. Security requirements for company mobiles
    Device PIN/biometric, automatic OS updates, remote wipe enabled, no jailbroken/rooted devices.

    _Revision history: v1 (Jun 2025) initial policy._
    """),

    ("Contractor & Guest Access Policy", "IT & Infrastructure", "Identity & Access Management",
     ["Okta SSO", "GlobalProtect VPN", "Slack", "Corporate Website CMS", "GitHub Enterprise"], "v2", "2026-06-01", "active", "internal", False, """
    # Contractor & Guest Access Policy (v2)

    **Owner:** IAM & Security | **Effective:** 1 June 2026

    ## 1. Sponsorship
    Every contractor, agency or vendor user must have a named AlgoWorks **sponsor** (a team lead or above) who is accountable for the account. Sponsors request accounts in ServiceNow using the "Contractor account" item, attaching the signed NDA/MSA reference.

    ## 2. Account lifecycle
    2.1 Contractor Okta accounts are created with the `ext-` prefix and a **90-day expiry**. Sponsors may extend in 90-day increments; IAM sends a reminder 10 days before expiry.
    2.2 Accounts are disabled automatically on expiry and deleted after 30 days.
    2.3 Contractors are assigned only the applications named on the request; the default new-joiner bundle does not apply.

    ## 3. Connectivity
    3.1 Contractors who need internal services are added to the **`vpn-contractors` Okta group**, which provides GlobalProtect access scoped to the subnets listed on the request. A security review by IAM is required before the group is assigned.
    3.2 Contractors must use a device that meets the endpoint baseline; the sponsor attests to this on the request.

    ## 4. Guest Wi-Fi
    Office visitors use the `AlgoWorks-Guest` network (captive portal, 24-hour access) which has no route to internal systems.

    _Revision history: v1 (Feb 2025); v2 (Jun 2026) introduced the `vpn-contractors` group model for contractor connectivity._
    """),

    # ============================================================ Engineering
    ("Code Review & Branch Protection Standard", "Engineering", "Platform Backend",
     ["GitHub Enterprise"], "v3", "2026-05-11", "active", "internal", False, """
    # Code Review & Branch Protection Standard (v3)

    **Owner:** Platform Backend (Engineering) | **Effective:** 11 May 2026

    ## 1. Branch protection (all repositories under the algoworks-tech GitHub org)
    - `main` is protected: no direct pushes, linear history, required status checks (build, unit tests, lint, security scan).
    - At least **one approving review** from a CODEOWNER is required. Repositories tagged `payments`, `auth` or `data-pipeline` require **two** approvals.
    - Stale approvals are dismissed on new commits. Force-pushes are disabled.

    ## 2. Review expectations
    2.1 Reviewers respond within one business day; authors keep PRs under ~400 changed lines where possible.
    2.2 PR description must link the Jira issue and state test evidence and rollback approach for production-affecting changes.
    2.3 Infrastructure and deployment repositories (`algoworks-deploy`, `algoworks-infra`) follow the same rules; a merged PR to an environment directory is the record of approval for that deployment.

    ## 3. Exceptions
    Emergency hotfixes may be merged with one approval from the on-call lead and must be followed by a retrospective review within 2 business days.

    _Revision history: v2 (Oct 2025); v3 (May 2026) added security-scan status check and two-approval rule for data-pipeline repos._
    """),

    ("Deployment & Release Process SOP", "Engineering", "Platform Backend",
     ["ArgoCD Deployment Platform", "GitHub Enterprise", "AlgoWorks Fleet Production Platform", "AlgoWorks Fleet Customer Portal"],
     "v3", "2025-04-14", "active", "internal", True, """
    # Deployment & Release Process SOP (v3)

    **Owner:** Platform Backend (Engineering) | **Effective:** 14 April 2025

    ## 1. Deployment windows
    1.1 Production deployments of the AlgoWorks Fleet platform, customer portal and mobile backend services take place **Monday to Thursday between 10:00 and 16:00 IST**.
    1.2 **No production deployments on Fridays**, on the day before a public holiday, or during the last two business days of a month (billing run).
    1.3 Deployments outside the window require approval from the VP Engineering and must have an engineer on standby for 2 hours afterwards.

    ## 2. Release roles
    A weekly **release manager** (rotating within Platform Backend) coordinates the release train, confirms staging sign-off from QA, announces in #eng-announcements and monitors Datadog for 30 minutes post-deploy.

    ## 3. Steps
    1. Merge to `main`; CI builds and publishes the image.
    2. Release manager promotes the image to staging; QA runs the regression suite.
    3. Release manager raises the production change (see Change Management Policy) and, once approved, promotes to production.
    4. Post-deploy checks: error rate, p95 latency, queue depth. Roll back immediately on regression.

    ## 4. Feature flags
    Risky changes should ship dark behind a feature flag and be enabled progressively (1% -> 10% -> 100%).

    ## 5. Mobile releases
    Driver App releases go to the Play internal track / TestFlight for 48 hours before staged rollout (10% -> 50% -> 100%) over 3 days.

    _Revision history: v2 (Sep 2024); v3 (Apr 2025) added Friday deployment freeze and month-end freeze._
    """),

    ("On-Call & Escalation Policy", "Engineering", "Cloud Infrastructure & Security",
     ["Datadog Monitoring", "Slack", "AlgoWorks Fleet Production Platform"], "v2", "2026-07-06", "active", "internal", False, """
    # On-Call & Escalation Policy (v2)

    **Owner:** Engineering with Cloud Infrastructure | **Effective:** 6 July 2026

    ## 1. Rotations
    Weekly rotations in PagerDuty for: Platform Backend, Frontend & Mobile (business hours only), Data Engineering (business hours only) and Cloud Infrastructure (24x7). Handover is Monday 10:00 IST.

    ## 2. Escalation ladder
    Primary on-call (ack within 5 minutes for Sev1, 15 for Sev2) -> secondary on-call (after 10 minutes) -> team lead / Engineering Manager (after 20 minutes) -> VP Engineering / Head of IT (after 30 minutes).

    ## 3. Expectations
    On-call engineers have a company mobile with PagerDuty installed, keep their laptop reachable and do not deploy non-urgent changes while on call. Time off in lieu: half a day per overnight page.

    ## 4. Alert hygiene
    Every paging alert must have a linked runbook. Alerts that page more than 3 times in a week without action are reviewed at the weekly SRE sync and downgraded or fixed.

    _Revision history: v1 (Jan 2025); v2 (Jul 2026) added business-hours rotations for Frontend and Data, and the alert-hygiene rule after the May 2026 alert storm._
    """),

    ("Feature Flag & Rollback Guidelines", "Engineering", "Platform Backend",
     ["AlgoWorks Admin Console", "AlgoWorks Fleet Production Platform", "ArgoCD Deployment Platform"], "v1", "2026-06-22", "active", "internal", False, """
    # Feature Flag & Rollback Guidelines (v1)

    **Owner:** Platform Backend | **Effective:** 22 June 2026

    1. Feature flags are managed in the AlgoWorks Admin Console (flags service). Every flag has an owner, a Jira reference and an expiry date; flags older than 90 days are reviewed monthly.
    2. New customer-visible behaviour ships dark and is enabled for internal tenants first, then 5% of customers, then 25%, then 100%, with at least 24 hours at each stage unless the change is a bug fix.
    3. Rollback preference order: disable the flag; roll back the ArgoCD application to the previous revision; restore data from backup (requires incident commander approval).
    4. Any deployment that cannot be rolled back within 10 minutes must be called out in the PR and the release announcement.
    5. Flag changes on production tenants by `console-operator` users are logged and included in the weekly release notes.
    """),

    ("Snowflake Data Access Policy", "Engineering", "Data & Analytics Engineering",
     ["Snowflake Data Warehouse", "Metabase BI", "Jira", "Okta SSO"], "v2", "2025-07-21", "active", "internal", True, """
    # Snowflake Data Access Policy (v2)

    **Owner:** Data & Analytics Engineering | **Effective:** 21 July 2025

    ## 1. Access model
    Snowflake access is role-based. Okta groups map to Snowflake roles: `snowflake-analyst` (curated marts, read), `snowflake-engineer` (raw + curated, read/write in dev), `snowflake-pii-reader` (PII-tagged schemas), `snowflake-admin` (Data Engineering only).

    ## 2. Requesting access
    2.1 Curated (non-PII) schema access: raise a Jira ticket in the **DATA** project using the "Data access request" issue type. Approval by the **Data Engineering Manager**. Data Engineering adds the Okta group.
    2.2 **PII-tagged schemas** (customer contact details, driver identities, employee data): the DATA ticket must additionally carry **written sign-off from the Data Protection Officer (DPO)**, recorded as a comment on the ticket, before the `snowflake-pii-reader` role is granted. Purpose and retention must be stated.
    2.3 Native SQL access for non-engineering teams is discouraged; use Metabase curated collections where possible.

    ## 3. Reviews
    Membership of `snowflake-pii-reader` is reviewed every 6 months by the DPO and the Data Engineering Manager. Unused roles (no query in 90 days) are revoked.

    ## 4. Service accounts
    Service accounts (dbt, Metabase, Fivetran) are owned by Data Engineering, use key-pair auth and are rotated annually.

    _Revision history: v1 (Nov 2024); v2 (Jul 2025) introduced the pii-reader role and DPO sign-off requirement._
    """),

    # ============================================================ Human Resources
    ("Employee Onboarding SOP", "Human Resources", "People Operations",
     ["Darwinbox HRMS", "Okta SSO", "ServiceNow ITSM", "Microsoft 365", "Slack"], "v3", "2025-08-04", "active", "internal", True, """
    # Employee Onboarding SOP (v3)

    **Owner:** People Operations | **Effective:** 4 August 2025

    ## 1. Before Day 1
    | When | Action | Owner |
    |---|---|---|
    | Offer accepted | Candidate record created in Darwinbox pre-boarding; documents collected | Talent Acquisition / HR Ops |
    | Start date - 5 business days | HR Ops **emails IT-Helpdesk** with the new joiner's name, role, team, manager, location and start date; IT raises the onboarding ticket | HR Ops |
    | Start date - 5 business days | Laptop ordered/allocated per the Laptop & Endpoint Provisioning SOP | Service Desk |
    | Start date - 1 business day | Okta account, Microsoft 365 mailbox, Slack, Confluence, Darwinbox self-service, Zoho Expense and LearnHub created (the default bundle) | IAM / Service Desk |
    | Start date - 1 business day | Buddy assigned; manager prepares 30-60-90 plan | Line manager |

    ## 2. Day 1
    2.1 HR induction (09:30-11:00), ID card and desk allocation, laptop handover.
    2.2 **The line manager raises a separate ServiceNow access request for each business application the new joiner needs** (Salesforce, Zendesk, GitHub, Jira, Metabase, etc.) following the Application Access Request Policy. Applications are not provisioned automatically based on role.
    2.3 Mandatory trainings (Security Awareness, Code of Conduct, Handling Customer Data where relevant) assigned in LearnHub; due within 30 days.

    ## 3. First 30 days
    Buddy check-ins weekly; manager 30-day review recorded in Darwinbox; HR Ops 30-day survey.

    ## 4. Hybrid work orientation
    New joiners are briefed on the Hybrid Work Policy (in-office days) during induction.

    _Revision history: v2 (Jan 2025); v3 (Aug 2025) moved the IT notification to 5 business days before start and added the buddy programme._
    """),

    ("Leave & Time-Off Policy", "Human Resources", "People Operations",
     ["Darwinbox HRMS"], "v4", "2026-04-13", "active", "internal", False, """
    # Leave & Time-Off Policy (v4)

    **Owner:** People Operations | **Effective:** 13 April 2026 (FY27)

    ## 1. Entitlements (per financial year, April-March)
    - **Privilege Leave (PL):** 24 days, accrued at 2 days per month. Up to **12 days** may be carried forward to the next financial year; the balance above 12 lapses on 31 March. Encashment only at exit.
    - **Sick Leave:** 10 days; a medical certificate is required for more than 3 consecutive days.
    - **Public holidays:** 12 per year per location (list published each January).
    - **Parental leave:** 26 weeks maternity; 4 weeks paternity/secondary caregiver; adoption 12 weeks.
    - **Bereavement:** 5 days. **Marriage:** 3 days.

    ## 2. Applying
    All leave is applied for and approved in Darwinbox. Notice: at least twice the duration of the leave for PL (e.g. 10 working days' notice for a 5-day leave); sick leave should be logged on the day. Leave without a Darwinbox record is treated as unauthorised absence.

    ## 3. Approvals
    Line manager approves; leaves longer than 10 consecutive working days also require Department Head approval. Managers should nominate a delegate in Darwinbox when they are on leave so approvals (including application access approvals) do not stall.

    ## 4. Comp-off
    Work on a weekend or public holiday approved in advance by the manager earns a compensatory off to be used within 60 days.

    _Revision history: v3 (Apr 2025); v4 (Apr 2026) increased carry-forward from 10 to 12 days and added the delegate guidance._
    """),

    ("Hybrid Work Policy", "Human Resources", "People Operations",
     ["Darwinbox HRMS"], "v2", "2025-09-08", "active", "internal", True, """
    # Hybrid Work Policy (v2)

    **Owner:** People Operations | **Approved by:** Chief People Officer | **Effective:** 8 September 2025

    ## 1. Policy
    1.1 AlgoWorks operates a hybrid model. Employees assigned to an office (Bengaluru, Pune, Hyderabad, Singapore) are expected in the office a **minimum of 3 days per week**.
    1.2 **Tuesday, Wednesday and Thursday are anchor days** on which all office-based employees are expected on site, so that teams overlap. Monday and Friday may be worked remotely.
    1.3 Attendance is recorded via the Darwinbox badge integration and reviewed monthly by HR Business Partners with Department Heads.
    1.4 Employees hired into designated remote roles (location "Remote" in Darwinbox) are exempt from 1.1-1.2 and are expected to visit their nearest office once per quarter.
    1.5 Temporary exceptions (caregiving, medical, relocation) of up to 30 days may be approved by the HR Business Partner with the line manager; longer exceptions require the Chief People Officer.

    ## 2. Working hours
    Core collaboration hours are 11:00-16:00 IST; teams may flex around them. Singapore and US-based staff follow local core hours and overlap with India for at least 3 hours.

    ## 3. Equipment
    Remote-day equipment (monitor, chair) is not reimbursed; the office provides hot-desks and meeting rooms bookable in Outlook.

    _Revision history: v1 (Apr 2024) 2 days/week; v2 (Sep 2025) increased to 3 days/week with anchor days._
    """),

    ("Performance Review Process", "Human Resources", "People Operations",
     ["Darwinbox HRMS"], "v3", "2026-08-03", "active", "internal", False, """
    # Performance Review Process (v3)

    **Owner:** People Operations | **Effective:** 3 August 2026

    1. Two cycles per year: mid-year (October, development-focused) and annual (April, ratings and compensation). Both run in Darwinbox.
    2. Steps: self-review (1 week) -> peer feedback (up to 4 peers nominated by the employee, approved by the manager) -> manager review -> department calibration -> conversation.
    3. Ratings are on a 5-point scale; distribution guidance (not a forced curve) is shared with Department Heads. Ratings are Restricted data and are visible only to the employee, the manager chain and HR.
    4. Promotions are proposed in the annual cycle with a written case reviewed by a cross-department panel.
    5. Employees who joined less than 90 days before a cycle opens receive a check-in instead of a rating.
    6. Performance improvement plans are 60 days, agreed with the HRBP, and documented in Darwinbox.

    _Revision history: v2 (Mar 2025); v3 (Aug 2026) added peer feedback step and clarified new-joiner eligibility._
    """),

    ("Employee Referral Bonus Policy", "Human Resources", "Talent Acquisition",
     ["Greenhouse ATS", "Darwinbox HRMS", "Keka Payroll"], "v2", "2026-04-13", "active", "internal", False, """
    # Employee Referral Bonus Policy (v2)

    **Owner:** Talent Acquisition | **Effective:** 13 April 2026

    1. Employees who refer a candidate through the Greenhouse referral link who is subsequently hired receive a referral bonus: **Rs 50,000** for Engineering, Data and IT roles; **Rs 25,000** for all other roles; Rs 75,000 for roles flagged "hard-to-fill" on the job posting.
    2. **The bonus is paid in the payroll cycle following the referred employee's completion of 90 days of employment**, provided both referrer and referee are active employees on that date.
    3. Not eligible: Talent Acquisition team members, the hiring manager and interview panel for that role, Department Heads for roles in their department, and referrals of former employees who left within the last 12 months.
    4. The referral must be logged in Greenhouse before the candidate applies through any other channel; Greenhouse timestamps decide ownership.
    5. Payment is processed by Payroll on confirmation from Talent Acquisition; the bonus is taxable.

    _Revision history: v1 (Jun 2024) 6-month vesting; v2 (Apr 2026) reduced the payout trigger from 6 months to 90 days and introduced the hard-to-fill tier._
    """),

    ("Learning & Development Reimbursement Policy", "Human Resources", "Learning & Development",
     ["LearnHub LMS", "Zoho Expense"], "v2", "2025-12-01", "active", "internal", True, """
    # Learning & Development Reimbursement Policy (v2)

    **Owner:** Learning & Development | **Effective:** 1 December 2025

    ## 1. Entitlement
    Each employee may claim up to **Rs 25,000 per financial year** for external courses, certifications, conferences and books relevant to their current or next role.

    ## 2. Pre-approval
    2.1 **Pre-approval is mandatory.** Before enrolling or paying, the employee submits an L&D request in LearnHub stating the course, cost, dates and relevance; the line manager and the L&D team both approve.
    2.2 **Claims without pre-approval are not reimbursed.**

    ## 3. Claiming
    3.1 Submit the claim in Zoho Expense under category "Learning & Development" within 30 days of course completion, attaching the invoice and the completion certificate (or exam pass report for certifications).
    3.2 Failed certification exams are reimbursed once; the retake is at the employee's cost.
    3.3 Conference travel follows the Travel & Expense Reimbursement Policy and counts against the L&D cap only for the registration fee.

    ## 4. Clawback
    If the employee resigns within 6 months of a reimbursement above Rs 15,000, the amount is recovered from the final settlement.

    _Revision history: v1 (Apr 2024) Rs 20,000 cap; v2 (Dec 2025) raised to Rs 25,000 and moved requests into LearnHub._
    """),

    ("Code of Conduct & Anti-Harassment Policy", "Human Resources", "People Operations",
     ["Darwinbox HRMS", "LearnHub LMS"], "v3", "2026-07-20", "active", "internal", False, """
    # Code of Conduct & Anti-Harassment Policy (v3)

    **Owner:** People Operations | **Effective:** 20 July 2026

    1. AlgoWorks expects professional, respectful behaviour in all work settings including Slack, email, video calls, customer sites and company events.
    2. Harassment, discrimination and retaliation are prohibited. The Internal Committee constituted under the POSH Act handles complaints of sexual harassment; contact details are on the HR Confluence space and every office noticeboard.
    3. Conflicts of interest (outside employment, vendor relationships, hiring relatives) must be disclosed to HR in Darwinbox.
    4. Confidential and customer information must be handled per the Data Classification & Handling Standard.
    5. Gifts from vendors or customers above Rs 5,000 in value must be declared; cash gifts are never accepted.
    6. Concerns may be raised with a manager, any HRBP, the Chief People Officer, or anonymously via the ethics form; reports are investigated within 30 days.
    7. Annual acknowledgement and the LearnHub Code of Conduct module are mandatory for all employees.

    _Revision history: v2 (Jul 2025); v3 (Jul 2026) added AI-tool and social media guidance references._
    """),

    # ============================================================ Finance
    ("Travel & Expense Reimbursement Policy", "Finance", "Accounts Payable & Procurement",
     ["Zoho Expense", "NetSuite ERP", "Keka Payroll"], "v5", "2025-11-10", "active", "internal", True, """
    # Travel & Expense Reimbursement Policy (v5)

    **Owner:** Accounts Payable & Procurement (Finance) | **Approved by:** CFO | **Effective:** 10 November 2025

    ## 1. Submission
    1.1 All claims are submitted in **Zoho Expense**. Paper or email claims are not accepted.
    1.2 **Claims must be submitted within 30 days of the expense date.** Claims older than 30 days are rejected automatically by Zoho Expense and are not eligible for reimbursement.
    1.3 **Itemised receipts are mandatory for every single expense above Rs 500.** Claims without receipts above this threshold are rejected.
    1.4 Claims are approved by the line manager and then by Finance AP. Approved claims are reimbursed with the next monthly payroll (cut-off: 20th of the month).

    ## 2. Travel
    2.1 Flights: economy class for all domestic and international travel under 8 hours; premium economy allowed above 8 hours with Department Head approval. Book through the corporate travel desk.
    2.2 Hotels: up to Rs 6,000/night metro, Rs 4,000/night non-metro, USD 180/night international.
    2.3 **Per diem (meals & incidentals): Rs 2,000 per day domestic; USD 60 per day international.** Per diem is claimed without receipts; no other meal claims are permitted on per-diem days.
    2.4 Local travel: metered taxi/ride-hailing at actuals; personal vehicle at Rs 12/km (car) or Rs 5/km (two-wheeler).

    ## 3. Non-travel expenses
    3.1 Team meals and celebrations: up to Rs 1,500 per person, manager pre-approval, attendee list required.
    3.2 Mobile phone bills: reimbursed up to Rs 1,000/month for roles designated by the Department Head.
    3.3 Software and subscriptions may not be expensed; see the Software Procurement & SaaS Approval Policy.
    3.4 Items not listed in this policy are not reimbursable unless approved in writing by the CFO before the expense is incurred.

    ## 4. Corporate cards
    See the Corporate Card Usage Policy. Card transactions must still be submitted in Zoho Expense with receipts.

    _Revision history: v4 (Feb 2025); v5 (Nov 2025) updated hotel caps and confirmed the 30-day submission window and Rs 500 receipt threshold._
    """),

    ("Procurement & Purchase Order Policy", "Finance", "Accounts Payable & Procurement",
     ["NetSuite ERP", "ServiceNow ITSM"], "v3", "2026-05-25", "active", "internal", False, """
    # Procurement & Purchase Order Policy (v3)

    **Owner:** Accounts Payable & Procurement | **Effective:** 25 May 2026

    ## 1. When a PO is required
    A purchase order raised in NetSuite is required for any single purchase or annual commitment **above Rs 25,000**. Invoices without a matching PO are returned to the requester.

    ## 2. Approval matrix (per purchase / annual contract value)
    | Value | Approvals |
    |---|---|
    | Up to Rs 25,000 | Team lead (no PO; expense or card) |
    | Rs 25,001 - 1,00,000 | Department Head |
    | Rs 1,00,001 - 5,00,000 | Department Head + AP & Procurement Manager |
    | Rs 5,00,001 - 25,00,000 | Above + CFO; competitive quotes per the Vendor Onboarding SOP |
    | Above Rs 25,00,000 | Above + CEO |

    ## 3. Process
    1. Requester raises a "Purchase request" in ServiceNow (Finance queue) with quotes and business case.
    2. Procurement confirms the vendor is onboarded (or starts onboarding), checks budget with FP&A, and raises the PO.
    3. Goods/services receipt is confirmed by the requester in NetSuite before AP releases payment.

    ## 4. Split purchases
    Splitting a purchase to stay under a threshold is a policy violation.

    _Revision history: v2 (Jun 2025); v3 (May 2026) added the ServiceNow Finance queue as the intake channel._
    """),

    ("Corporate Card Usage Policy", "Finance", "Accounts Payable & Procurement",
     ["Zoho Expense", "NetSuite ERP"], "v2", "2026-06-08", "active", "internal", False, """
    # Corporate Card Usage Policy (v2)

    **Owner:** Accounts Payable & Procurement | **Effective:** 8 June 2026

    1. Corporate cards are issued to Department Heads, team leads who travel frequently, the travel desk and designated Marketing/IT purchasers. Requests go through ServiceNow with CFO approval.
    2. Card limits: Rs 2,00,000/month standard; temporary increases via Finance AP.
    3. Permitted: travel, team events, approved SaaS renewals under Rs 1,00,000, event sponsorships, office supplies. Not permitted: personal expenses, cash withdrawals, gift cards, cryptocurrency, expenses for other employees' personal use.
    4. Every transaction must be reconciled in Zoho Expense with a receipt within 15 days of the statement date. Unreconciled transactions after 30 days are deducted from salary after notice.
    5. Lost or stolen cards are reported to the bank and Finance AP immediately.

    _Revision history: v1 (Mar 2025); v2 (Jun 2026) allowed SaaS renewals under Rs 1,00,000 on card._
    """),

    ("Vendor Onboarding & Payment Terms SOP", "Finance", "Accounts Payable & Procurement",
     ["NetSuite ERP", "ServiceNow ITSM"], "v2", "2026-01-19", "active", "internal", True, """
    # Vendor Onboarding & Payment Terms SOP (v2)

    **Owner:** Accounts Payable & Procurement | **Effective:** 19 January 2026

    ## 1. Vendor onboarding checklist
    1. Vendor registration form (legal name, address, contact, GSTIN, PAN, MSME status).
    2. Cancelled cheque or bank letter for account verification; a call-back to a number obtained independently of the invoice to confirm bank details.
    3. For SaaS/IT vendors: the IAM & Security questionnaire and DPA where personal data is processed.
    4. Vendor created in NetSuite by Procurement; AP verifies bank details before the first payment.

    ## 2. Competitive quotes
    2.1 **Any new vendor engagement with an annual value above Rs 5,00,000 requires three competitive quotes** (or a documented single-source justification approved by the CFO) attached to the purchase request. **This applies equally to SaaS subscriptions, hosting and professional services.**
    2.2 Renewals of existing contracts above Rs 5,00,000 require a benchmark check by Procurement every 2 years.

    ## 3. Payment terms
    3.1 **Standard payment terms are Net-45** from receipt of a valid invoice.
    3.2 Net-30 or shorter terms may be agreed only with **CFO approval**, recorded in the vendor record.
    3.3 Advance payments require CFO approval and a proforma invoice.
    3.4 Payment runs happen every Wednesday; invoices must be received by AP by Monday 17:00 to be included.

    ## 4. Invoicing
    Invoices must quote the PO number and be sent to ap@algoworks.io. Invoices without PO reference are returned.

    _Revision history: v1 (Mar 2025); v2 (Jan 2026) added the bank call-back control and made the three-quote rule explicit for SaaS and hosting._
    """),

    ("Month-End Close Checklist", "Finance", "Financial Planning & Analysis",
     ["NetSuite ERP", "Chargebee Billing", "Zoho Expense", "Keka Payroll"], "v6", "2026-08-31", "active", "restricted", False, """
    # Month-End Close Checklist (v6)

    **Owner:** FP&A with Billing, Payroll & Compliance | **Effective:** 31 August 2026 | **Classification:** Restricted

    | Day | Task | Owner |
    |---|---|---|
    | BD-2 | Freeze: no new vendor bills dated in the closing month after this point; expense claims for the month due in Zoho Expense | AP |
    | BD-1 | Chargebee invoice run reconciled to NetSuite AR; failed webhooks re-driven | Billing |
    | BD+1 | Payroll journal from Keka posted; PF/PT/TDS accruals | Payroll |
    | BD+2 | Expense journal posted from Zoho Expense (automated daily posting from June 2026; verify no duplicates) | AP |
    | BD+2 | Prepaid/SaaS amortisation and fixed-asset depreciation | FP&A |
    | BD+3 | Revenue recognition schedules reviewed; deferred revenue roll-forward | Billing / FP&A |
    | BD+3 | Bank and credit-card reconciliations | AP |
    | BD+4 | Intercompany (Singapore entity) and FX revaluation | FP&A |
    | BD+5 | Management pack: P&L vs budget, cash, ARR, headcount | FP&A |
    | BD+6 | CFO review and close lock in NetSuite | CFO |

    Notes: production deployments that touch billing are frozen on BD-2 to BD+1 (coordinate with Engineering). Any integration incident (Chargebee, Zoho Expense) during close is Sev2 for Finance.

    _Revision history: v5 (May 2026); v6 (Aug 2026) added the duplicate-journal check after the August 2026 Zoho integration incident._
    """),

    # ============================================================ Sales
    ("Discount Approval Matrix", "Sales", "Sales Operations & Deal Desk",
     ["Salesforce CRM", "Chargebee Billing"], "v3", "2025-10-20", "active", "internal", True, """
    # Discount Approval Matrix (v3)

    **Owner:** Sales Operations & Deal Desk | **Approved by:** VP Sales and CFO | **Effective:** 20 October 2025

    ## 1. Purpose
    Sets who may approve pricing discounts on AlgoWorks Fleet subscriptions and services, to protect margin and keep pricing consistent across regions.

    ## 2. Matrix (discount from list price, per deal)
    | Discount | Approver |
    |---|---|
    | Up to 10% | Account Executive (self-approved, recorded on the opportunity) |
    | 10.01% - 20% | Sales Manager (Enterprise Sales Manager or Head of Customer Success for renewals) |
    | **20.01% - 30%** | **CFO** |
    | Above 30% | CEO |
    Multi-year deals: the discount is measured on total contract value. Free months count as discount.

    ## 3. Process
    3.1 Every discount above 10% requires a **Deal Desk ticket** (ServiceNow, Sales Ops queue) raised by the AE with the business case, competitor context and the proposed terms.
    3.2 The Deal Desk Analyst validates the calculation and routes the approval to the approver above. Approval must be recorded on the ticket **and** on the Salesforce opportunity before the quote is sent.
    3.3 Chargebee subscriptions are created only from an approved quote.

    ## 4. Non-standard terms
    Payment terms beyond Net-45, custom SLAs, or liability changes require Legal and CFO review regardless of discount level.

    _Revision history: v2 (Mar 2025); v3 (Oct 2025) lowered the Sales Manager ceiling from 25% to 20%._
    """),

    ("CRM Data Hygiene & Lead Ownership Policy", "Sales", "Sales Operations & Deal Desk",
     ["Salesforce CRM", "HubSpot Marketing Hub"], "v2", "2026-07-13", "active", "internal", False, """
    # CRM Data Hygiene & Lead Ownership Policy (v2)

    **Owner:** Sales Operations | **Effective:** 13 July 2026

    1. Salesforce is the system of record for accounts, contacts, opportunities and renewals. HubSpot is the system of record for marketing engagement and lead scoring.
    2. Lead ownership: inbound leads are created in HubSpot and synced to Salesforce; the SDR round-robin assigns ownership within 1 business hour. Marketing may not reassign a lead once it is synced; Sales may not delete leads (mark "Disqualified" with a reason instead).
    3. Required fields on every opportunity: amount, close date, stage, next step, competitor, region. Opportunities without a next-step update in 21 days are flagged in the weekly pipeline review.
    4. Duplicates: report to Sales Ops via #sales-ops; only the Salesforce Administrator merges records. Do not create accounts without searching first.
    5. Exports of contact data from Salesforce or HubSpot for use outside the tools require the Sales Operations Manager's approval (see the Data Classification & Handling Standard).
    6. Field mappings between HubSpot and Salesforce are owned jointly by Marketing Ops and the Salesforce Administrator; changes require a Jira ticket and a test in the sandbox.

    _Revision history: v1 (Jan 2026, after the lead sync cleanup); v2 (Jul 2026) added the field-mapping ownership rule._
    """),

    ("Customer Support SLA & Escalation Policy", "Sales", "Customer Success & Support",
     ["Zendesk Support Desk", "AlgoWorks Admin Console", "Slack"], "v3", "2026-05-04", "active", "internal", False, """
    # Customer Support SLA & Escalation Policy (v3)

    **Owner:** Customer Success & Support | **Effective:** 4 May 2026

    ## 1. Priorities and SLAs (Zendesk)
    | Priority | Definition | First response | Update | Target resolution |
    |---|---|---|---|---|
    | P1 | Customer's fleet operations stopped | 30 min (24x7) | 1 hour | 4 hours |
    | P2 | Major function impaired, workaround exists | 2 business hours | 4 hours | 1 business day |
    | P3 | Minor issue / question | 8 business hours | daily | 3 business days |
    | P4 | Feature request / cosmetic | 2 business days | - | backlog |

    ## 2. Escalation to Engineering
    2.1 Tier 2 escalates to Engineering by creating a linked Jira issue in the SUP project and posting in #customer-success with the Zendesk link. P1s are also declared in #incidents per the Incident Management SOP.
    2.2 Support Engineers use the AlgoWorks Admin Console (read-only) for diagnosis; impersonation (`console-operator`) is limited to designated Tier 2 staff with the required training.

    ## 3. Customer communication
    Templates in Zendesk macros; any commitment on timelines beyond the SLA table needs the Head of Customer Success. Credits or refunds follow the Discount Approval Matrix thresholds.

    _Revision history: v2 (Nov 2025); v3 (May 2026) tightened P1 first response from 1 hour to 30 minutes._
    """),

    # ============================================================ Marketing
    ("Brand & External Communications Policy", "Marketing", "Content & Brand",
     ["Corporate Website CMS", "HubSpot Marketing Hub", "Slack"], "v2", "2026-04-27", "active", "public", False, """
    # Brand & External Communications Policy (v2)

    **Owner:** Content & Brand (Marketing) | **Effective:** 27 April 2026

    1. Only designated spokespeople (CEO, VP Marketing, VP Sales, VP Engineering) speak to press and analysts. Media enquiries go to press@algoworks.io.
    2. All external material (website, decks, one-pagers, social posts, event booths) uses the AlgoWorks brand system: approved logo files, colour palette, typography and templates in the Brand Portal (Confluence "Brand" space).
    3. Customer names, logos and quotes may be used externally only with a signed reference agreement recorded in Salesforce.
    4. Employees may share company posts on personal social media and identify themselves as AlgoWorks employees, but may not disclose unreleased features, customer information, financial results or security incidents.
    5. Incident and outage communications to customers are drafted by Customer Success and reviewed by Marketing before publication (see Incident Management SOP).
    6. Open-source contributions and conference talks by engineers are encouraged; slides that mention AlgoWorks systems are reviewed by the engineer's manager and Marketing for confidentiality.

    _Revision history: v1 (Aug 2024); v2 (Apr 2026) refreshed brand system references for the new website._
    """),

    ("Marketing Content Approval & Publishing SOP", "Marketing", "Content & Brand",
     ["Corporate Website CMS", "HubSpot Marketing Hub", "Jira"], "v2", "2026-08-17", "active", "internal", False, """
    # Marketing Content Approval & Publishing SOP (v2)

    **Owner:** Content & Brand | **Effective:** 17 August 2026

    1. Every content piece (blog, web page, email campaign, social post, video) is tracked as an issue in the Jira **MKT** project with owner, channel, target date and approval status.
    2. Approvals: blog/web copy - Content & Brand Manager; product claims - Product Marketing Lead; pricing or legal statements - VP Marketing and Finance/Legal; customer references - Sales owner of the account.
    3. Email campaigns are built in HubSpot, sent to the internal test list first, and scheduled only after the approver ticks "Approved" on the Jira issue. No sends on public holidays in the recipient region.
    4. Website changes are staged on the WordPress staging site and reviewed by the Content & Brand Manager; the agency publishes to production only after written approval on the Jira issue.
    5. Accessibility (alt text, contrast) and SEO checklist must be completed before publishing.
    6. Urgent corrections (broken links, factual errors) may be made directly by the Content & Brand Manager and logged afterwards.

    _Revision history: v1 (Feb 2025); v2 (Aug 2026) moved tracking from a spreadsheet to Jira MKT._
    """),
    # ============================================================ Legal & Compliance (added with the 1,000-person expansion)
    ("Access Roles & Need-to-Know Standard", "Legal & Compliance", "Privacy, Compliance & Audit",
     ["Okta SSO", "Darwinbox HRMS", "Confluence", "ServiceNow ITSM"],
     "v1", "2026-08-31", "active", "internal", False, """
    # Access Roles & Need-to-Know Standard (v1)

    **Owner:** Privacy, Compliance & Audit (Legal & Compliance) | **Approved by:** General Counsel and Head of IT & Infrastructure | **Effective:** 31 August 2026

    ## 1. Purpose
    Defines who may see confidential information in AlgoWorks's knowledge systems (Confluence, ServiceNow, email archives, Slack exports and TouchStone). Access follows two principles: **need to know** (you see confidential information only when your work requires it) and **least privilege** (roles grant the narrowest data category and scope that the job needs). Seniority alone grants nothing.

    ## 2. Classification
    2.1 **Non-confidential** (public or internal): policies, Confluence pages, tickets, emails and public Slack channels that contain no personal data. Visible to every employee and intern.
    2.2 **Confidential - personal data**: information about an identifiable person that they would not expect colleagues to read: pay, bonus and reimbursement amounts; health details and reasons for leave; performance and disciplinary matters; exit details; personal contact details and ID numbers. Records are checked for personal data automatically when they are indexed, whatever label they carry.
    2.3 **Confidential - business**: records labelled restricted by their owner (for example privileged-access requests, security incidents, contract negotiations, month-end close material). Each has a domain: security, finance, HR, commercial, legal or general.

    ## 3. Baseline rules (everyone)
    3.1 Employees and interns see all non-confidential content.
    3.2 Contractors see policies and Confluence documentation, plus any record they are personally involved in. They do not see other tickets, emails or Slack conversations.
    3.3 Anyone involved in a record (requester, on-behalf-of, assignee, approver, participant or author) may see it, whatever its classification.
    3.4 Business-confidential policies and Confluence pages are visible to employees of the owning department.
    3.5 Employees who have left lose all access on their last working day.

    ## 4. Access roles
    Roles are assigned from Darwinbox (job and team) and synchronised to Okta groups. Each role adds the grants below.

    | Role | Grants |
    |---|---|
    | people_manager (team leads and above) | Confidential records involving anyone in their reporting line, except health/leave reasons and personal contact details |
    | department_head | Business-confidential records owned by their department |
    | executive (CEO, COO, CFO) | Business-confidential records company-wide; no personal data |
    | hr_business_partner | All personal data for employees in the departments they support |
    | hr_operations (People Operations, Employee Relations) | Leave, health, exit and personal-contact data company-wide; HR business-confidential records |
    | compensation_admin (Total Rewards, Chief People Officer) | Pay and performance data company-wide |
    | payroll_admin (Billing, Payroll & Compliance) | Pay data company-wide |
    | finance_controller (CFO, FP&A and Accounting leads) | Finance business-confidential records company-wide |
    | security_admin (IAM, Security Operations, IT Governance & Risk, Head of IT) | Security business-confidential records company-wide |
    | legal_counsel (Commercial Legal, General Counsel) | Legal and commercial business-confidential records company-wide |
    | compliance_auditor (Privacy, Compliance & Audit, General Counsel) | All confidential records, read-only, for audits and investigations |

    ## 5. Controls
    5.1 Every access to a confidential record through TouchStone is written to the audit log with the user, the record and the rule that allowed it.
    5.2 Access by compliance_auditor is additionally flagged for monthly review by the General Counsel.
    5.3 Role membership is reviewed quarterly by department heads; removals take effect within one business day.
    5.4 When TouchStone withholds a record, it tells the user that confidential records exist and who owns them, never their content.

    ## 6. Requesting access
    Raise "Request Access - confidential data" in ServiceNow with the business reason. The owning department head approves; Privacy, Compliance & Audit records the grant. Temporary grants must have an end date.

    _Revision history: v1 (Aug 2026) introduced role-based access with the 1,000-person organisation and TouchStone._
    """),
]


def build_policies(reg) -> list[dict]:
    out = []
    for i, (title, dept, team, systems, version, updated, status, sens, stale, text) in enumerate(POLICIES):
        out.append({
            "policy_id": f"POL-{i + 1:02d}",
            "title": title,
            "owner_department_id": reg.did(dept),
            "owner_team_id": reg.tid(team),
            "related_system_ids": [reg.sid(s) for s in systems],
            "version": version,
            "last_updated": updated,
            "status": status,
            "is_stale_by_design": stale,
            "full_text": dedent(text).strip() + "\n",
            "metadata": {
                "source_type": "policy",
                "source_system": "confluence",
                "department": reg.did(dept),
                "sensitivity": sens,
                "created_date": updated,
                "last_referenced_date": updated,  # bumped by build when artifacts cite the policy
            },
        })
    assert len(out) == 36, len(out)
    return out
