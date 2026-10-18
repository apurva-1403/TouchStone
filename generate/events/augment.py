"""Additional Layer 7 artifacts merged into the hand-authored event bundles.

Two kinds:
1. EXTRA - hand-written tickets/emails/Slack/docs appended to specific events (policy-update requests that
   the drift events triggered, follow-up problem records, announcement emails, extra chatter, two multi-hop docs).
2. approval_threads() - short "please approve my request" email threads generated for event tickets that have
   named approvers. These mirror the nudge/approve/fulfilled emails that surround every real ServiceNow request,
   cite the ticket ID (cross-reference), and are only generated for events that have fewer than two emails.

Appended artifacts get placeholder positions after the hand-authored ones (e.g. the first EXTRA ticket on an
event with two tickets is {{ticket:EVT-xxx#3}}).
"""
from __future__ import annotations

from common import rng, add_business_days, is_business_day, d
from events.dsl import T, M, S, D

EXTRA = {
    # ---- policy-update requests spawned by the drift events (all still open: the doc debt is real)
    "EVT-050": {
        "tickets": [T("Policy update request: Application Access Request Policy v4 - codify 5-day override and same-department approver",
                      "Following the review of {{ticket:EVT-050#1}} and {{ticket:EVT-050#2}}: the policy (v3) requires Department Head "
                      "escalation and forbids provisioning without recorded approval; IAM practice since Dec-2025 is a 5-business-day "
                      "override with a confirmation from the requester's side. Requesting a v4 that either codifies the override (5 business "
                      "days, confirmation from the Department Head or a manager in the same department, logged on the ticket) or "
                      "instructs IAM to stop. Owner: Nikhil Bhatt; approver: Sandeep Malhotra.",
                      "", "Nikhil Bhatt", "Sandeep Malhotra", "2026-08-27", status="open", group="IT Leadership",
                      category="policy-update", priority="P3")],
        "docs": [D("Access Policy Review - meeting notes (28 August 2026)",
                   "**Attendees:** Nikhil Bhatt (chair), Kavya Reddy, Sandeep Malhotra, Rohan Mehta, Anita Desai, Geeta Iyengar | **Purpose:** review of access-approval practice vs the Application Access Request Policy and the Privileged Access policy\n\n"
                   "## Cases discussed\n1. **{{ticket:EVT-050#1}}** (Ritika Sharma, Salesforce) and **{{ticket:EVT-050#2}}** (Sonal Mehra, Metabase): approved by IAM after 5 business days on informal confirmations - a peer in one case. Policy v3 says Department Head escalation; IAM has applied the override 14 times since January.\n"
                   "2. **{{ticket:EVT-067#1}}** vs **{{ticket:EVT-067#2}}**: same team, same role, Admin Console access granted with a manager attestation in January and denied pending training in April. **{{ticket:EVT-003#1}}** (May) shows the v2 process applied correctly.\n"
                   "3. HR Ops report that managers on leave rarely set a Darwinbox delegate, which is what stalls approvals in the first place.\n\n"
                   "## Decisions\n- IAM continues the override **only** with a confirmation from the Department Head or a manager in the same department (no peers), logged on the ticket, until v4 is published. Owner Kavya Reddy - queue checklist updated.\n"
                   "- Nikhil to draft Access Request Policy v4 ({{ticket:EVT-050#3}}); Sandeep to decide by end of September.\n- HR Ops to add 'set a delegate' to the leave-request confirmation email in Darwinbox (Geeta).\n"
                   "- Preeti Nambiar to complete 'Handling Customer Data' before the Q3 review or be removed from console-readonly at the review (Rohan).\n- Sameer Khan to complete the course and re-raise (Anita).\n\n"
                   "## Not decided\n- Whether the ServiceNow catalog should auto-escalate to the Department Head after 2 business days (Rajesh to estimate).",
                   doc_type="meeting_notes", space="IT", created="2026-08-28", authors=["Nikhil Bhatt"], sensitivity="restricted",
                   references=["{{ticket:EVT-050#1}}", "{{ticket:EVT-050#2}}", "{{ticket:EVT-067#1}}", "{{ticket:EVT-067#2}}", "{{ticket:EVT-003#1}}"],
                   related_events=["EVT-067", "EVT-003"], labels=["access-review", "policy", "iam"])],
    },
    "EVT-051": {
        "tickets": [T("Policy update request: Laptop & Endpoint Provisioning SOP v5 - realistic delivery SLA and loaner-first process",
                      "SOP v4 promises a 5-business-day delivery and a 4+4 buffer stock; since May the buffer is empty and MacBook Pro lead "
                      "time is 3-4 weeks (see {{ticket:EVT-051#1}}, {{ticket:EVT-051#2}}). Proposed v5: loaner within 1 business day; "
                      "standard device within 15 business days; buffer stock funded in FY27. Draft attached for Sandeep's review.",
                      "", "Rajesh Kumar", "Sandeep Malhotra", "2026-07-08", status="on_hold", group="IT Leadership",
                      category="policy-update", priority="P4",
                      work_notes="On hold pending FY27 buffer-stock budget decision (AOP, October).")],
    },
    "EVT-052": {
        "tickets": [T("Policy update request: Change Management Policy v3 - add 'GitOps standard deployment' category",
                      "Change Management Policy v2 still classifies all application deployments as Normal changes requiring CAB. Since "
                      "1-Dec-2025 the operating rule (CAB decision 2-Sep-2025, {{ticket:EVT-042#1}}) is that a merged algoworks-deploy PR is "
                      "the approval for standard app deployments. Two CHGs were raised and cancelled this year because engineers followed "
                      "the written policy ({{ticket:EVT-052#1}}, {{ticket:EVT-052#2}}). Requesting v3 with the GitOps category and an "
                      "explicit list of what still needs a CHG.",
                      "", "Karthik Iyer", "Varun Chandra", "2026-05-04", status="in_progress", group="Cloud Infrastructure",
                      category="policy-update", priority="P3", work_notes="Draft v3 exists (Varun, June); not yet reviewed by CAB.")],
    },
    "EVT-053": {
        "tickets": [T("Documentation update request: Deployment & Release Process SOP v4 (Friday rule, ArgoCD, CHG clarification)",
                      "The SOP (v3, April 2025) says no Friday deployments and describes a Jenkins-era release train. Since the 12-Mar-2026 "
                      "all-hands, Friday deploys are allowed before 14:00 IST when flagged or reversible. Please update the SOP so managers "
                      "and new joiners read the same rule the team follows. Reference: {{doc:EVT-053#1}}.",
                      "", "Meera Krishnan", "Rohan Mehta", "2026-06-22", status="in_progress", group="Platform Backend",
                      category="policy-update", priority="P4", work_notes="Rohan drafting v4 together with the CHG/GitOps clarification.")],
    },
    "EVT-054": {
        "tickets": [T("Policy update request: Snowflake Data Access Policy v3 - interim owner for PII sign-off",
                      "Section 2.2 requires written DPO sign-off for PII schema access. The DPO role has been vacant since Feb-2026 "
                      "({{ticket:EVT-005#2}}); Data Engineering has approved three PII requests since April with purpose and expiry "
                      "({{ticket:EVT-054#1}}, {{ticket:EVT-054#2}}). Requesting v3 naming an interim approver (proposal: IAM & Security "
                      "Lead + Data Engineering Manager jointly) and moving the semi-annual pii-reader review to IAM.",
                      "", "Suresh Pillai", "Nikhil Bhatt", "2026-05-13", status="open", group="IT Leadership",
                      category="policy-update", priority="P3", sensitivity="restricted")],
    },
    "EVT-055": {
        "tickets": [T("Policy update request: Hybrid Work Policy v3 - 2 days per week at team discretion",
                      "Leadership agreed in April 2026 to move from 3 days/week (Tue/Wed/Thu anchors) to 2 days/week with team-chosen days. "
                      "HR Ops is still answering from v2 (example: {{ticket:EVT-055#1}}) and new joiners get conflicting answers. v3 draft "
                      "attached; needs CPO sign-off.",
                      "", "Swati Kulkarni", "Sunita Raghavan", "2026-08-07", status="open", group="HR Leadership",
                      category="policy-update", priority="P3")],
    },
    "EVT-056": {
        "tickets": [T("Policy update request: Travel & Expense Reimbursement Policy v6 - 60-day window, Rs 2,500 per diem, Rs 1,000 receipt threshold",
                      "Finance AP has been approving claims up to 60 days on appeal and the domestic per diem is Rs 2,500 since April (CFO "
                      "email); Zoho still enforces v5 values, so valid claims auto-reject ({{ticket:EVT-056#1}}, {{ticket:EVT-056#2}}). "
                      "Requesting v6 and a matching Zoho rule change. Also needs a decision on a remote connectivity allowance "
                      "({{ticket:EVT-066#2}}).",
                      "", "Shalini Menon", "Vivek Anand", "2026-07-01", status="in_progress", group="Finance Leadership",
                      category="policy-update", priority="P3", work_notes="v6 draft with CFO since 15-Jul; Zoho rule change waits for the policy.")],
        "docs": [D("Finance AP - expense exceptions log (FY27 to date)",
                   "**Owner:** Accounts Payable (Ramesh Babu) | **Updated:** 31 August 2026 | **Classification:** Internal\n\n"
                   "Exceptions approved on appeal where the Zoho Expense rule (which mirrors T&E policy v5) rejected the claim. Kept so the "
                   "v6 policy draft reflects what we actually approve.\n\n"
                   "| Month | Cases | Reason | Position applied | Example |\n|---|---|---|---|---|\n"
                   "| Apr 2026 | 6 | Claim older than 30 days | Accepted up to 60 days with manager approval | - |\n"
                   "| Apr 2026 | 4 | Per diem Rs 2,500 vs rule Rs 2,000 | Approved at Rs 2,500 (CFO email 1-Apr) | - |\n"
                   "| May 2026 | 5 | Older than 30 days | Accepted up to 60 days | - |\n"
                   "| Jun 2026 | 7 | Older than 30 days | Accepted up to 60 days | {{ticket:EVT-056#1}} |\n"
                   "| Jun 2026 | 3 | Per diem Rs 2,500 | Approved | {{ticket:EVT-056#2}} |\n"
                   "| Mar-Jun 2026 | 2 | Home internet (not in policy) | **Inconsistent:** 1 approved (Rs 1,500/month), 1 rejected and on hold | {{ticket:EVT-066#1}}, {{ticket:EVT-066#2}} |\n"
                   "| Jul-Aug 2026 | 9 | Older than 30 days | Accepted up to 60 days | - |\n"
                   "| Jul-Aug 2026 | 2 | Receipts missing for Rs 500-1,000 items | Accepted (Zoho threshold configured at Rs 1,000) | - |\n\n"
                   "## Open decisions for v6 ({{ticket:EVT-056#3}})\n- Submission window: 60 days.\n- Domestic per diem: Rs 2,500.\n- Receipt threshold: Rs 1,000 (align policy to the Zoho configuration).\n- Remote connectivity allowance: yes/no and amount - CFO.\n\n"
                   "Until v6 is published: approve on appeal, record the reason on the claim, and do **not** approve new home-internet claims.",
                   doc_type="reference", space="FIN", created="2026-07-02", last_updated="2026-08-31", authors=["Ramesh Babu"],
                   references=["{{ticket:EVT-056#1}}", "{{ticket:EVT-056#2}}", "{{ticket:EVT-066#1}}", "{{ticket:EVT-066#2}}", "{{ticket:EVT-056#3}}"],
                   related_events=["EVT-066"], labels=["expenses", "exceptions", "policy"])],
    },
    "EVT-057": {
        "tickets": [T("Policy update request: Discount Approval Matrix v4 - VP Sales approves 20-30%",
                      "CPQ routes 20-30% discounts to the VP Sales per the Feb-2026 VP Sales/CFO agreement; the published matrix (v3) "
                      "says CFO. AEs keep asking which is right ({{ticket:EVT-057#1}}, {{ticket:EVT-057#2}}). v4 draft attached: AE to 10%, "
                      "Sales Manager to 20%, VP Sales to 30% with weekly CFO report, CEO above 30%. Needs VP Sales and CFO sign-off.",
                      "", "Vinod Krishnamurthy", "Vivek Anand", "2026-07-14", status="open", group="Finance Leadership",
                      category="policy-update", priority="P3", work_notes="Sent to Vivek 17-Jul; awaiting sign-off.")],
    },
    "EVT-058": {
        "tickets": [T("Policy update request: VPN & Remote Connectivity Policy v3 - 365-day employee renewal; align contractor access with Contractor policy",
                      "VPN policy v2 (May 2025) describes 90-day access with manual renewal and jump-host-only contractors. Actual: employee "
                      "VPN renews yearly via Okta group ({{ticket:EVT-058#1}}); contractors use the vpn-contractors group per the June 2026 "
                      "Contractor & Guest Access Policy ({{ticket:EVT-058#2}}). The two policies contradict each other. Requesting v3.",
                      "", "Nikhil Bhatt", "Sandeep Malhotra", "2026-06-01", status="open", group="IT Leadership",
                      category="policy-update", priority="P4")],
        "emails": [M("VPN policy needs a v3 - it now contradicts the contractor policy",
                     [("Nikhil Bhatt", ["Sandeep Malhotra"], "2026-06-01T10:20",
                       "Sandeep,\n\nWith the Contractor & Guest Access Policy v2 going live today, we have two policies that disagree: the VPN policy "
                       "(v2, last May) says contractors are jump-host only and employees renew every 90 days; the contractor policy says "
                       "vpn-contractors group with a security review, and in reality employees have been on 365-day auto-renewal since the "
                       "Okta integration. I've raised a ticket for v3 - it's a documentation fix, no practice change. OK to proceed with the "
                       "IAM & Security Lead approval route rather than a full review?\n\nNikhil"),
                      ("Sandeep Malhotra", ["Nikhil Bhatt"], "2026-06-02T09:05",
                       "Yes - keep it to a documentation update and note the contractor policy as the source for the contractor section. Please "
                       "batch it with the BYOD and access-policy updates so I review them together.\n\nSandeep")])],
    },
    "EVT-059": {
        "tickets": [T("Policy update request: Employee Onboarding SOP v4 - Darwinbox-triggered tickets and role bundles",
                      "SOP v3 (Aug 2025) says HR emails IT 5 days before start and managers request every app on Day 1. Since May 2026 the "
                      "Darwinbox automation creates the ticket 10 business days ahead and applies role bundles; managers request only the "
                      "exceptions. Confusion example: {{ticket:EVT-059#1}}. v4 draft in progress with IAM.",
                      "", "Rakesh Nair", "Geeta Iyengar", "2026-08-12", status="in_progress", group="HR Ops",
                      category="policy-update", priority="P3", work_notes="Draft v4 shared with Kavya Reddy for the bundle section; target end of September.")],
    },
    "EVT-060": {
        "tickets": [T("Policy update request: BYOD & Mobile Device Policy v2 - permit personal phones with Intune app protection",
                      "BYOD v1 (June 2025) prohibits personal phones and cites the lack of MAM licences; Intune P2 licences arrived in Feb-2026 "
                      "and the Service Desk enrols personal phones with app protection as standard ({{ticket:EVT-060#1}}, "
                      "{{ticket:EVT-060#2}}). Requesting v2: personal phones allowed for Outlook/Teams via MAM; company phones for on-call "
                      "and leadership; full-device management for company phones only.",
                      "", "Rajesh Kumar", "Sandeep Malhotra", "2026-04-06", status="open", group="IT Leadership",
                      category="policy-update", priority="P4")],
        "emails": [M("BYOD policy v2 - proposal",
                     [("Rajesh Kumar", ["Sandeep Malhotra", "Nikhil Bhatt"], "2026-04-06T15:10",
                       "Sandeep, Nikhil,\n\nThe BYOD policy still says personal phones may not access email. Since the P2 licences landed in "
                       "February we've enrolled 31 personal phones with Intune app protection - Outlook and Teams in a managed container, "
                       "selective wipe, no control over the rest of the phone. It's what every request asks for and it's more secure than "
                       "people forwarding mail to Gmail. Ticket raised for v2; proposal attached. Nikhil, any security objection?\n\nRajesh"),
                      ("Nikhil Bhatt", ["Rajesh Kumar", "Sandeep Malhotra"], "2026-04-07T09:40",
                       "No objection - MAM was always the plan once we had the licences. Add a line that Slack on personal phones stays "
                       "through the Slack app's own MDM-less controls and that restricted data must not be opened in unmanaged apps.\n\nNikhil")])],
    },
    "EVT-061": {
        "tickets": [T("Policy update request: L&D Reimbursement Policy v3 - Rs 40,000 certification cap; pre-approval waiver for passed certifications",
                      "Policy v2 (Dec 2025): Rs 25,000 cap, mandatory pre-approval. FY27 practice: Rs 40,000 for certifications, "
                      "pre-approval waived when the certification is passed and the manager confirms relevance ({{ticket:EVT-061#1}}, "
                      "{{ticket:EVT-061#2}}). v3 draft attached for CPO sign-off.",
                      "", "Madhavi Srinivasan", "Sunita Raghavan", "2026-07-28", status="open", group="HR Leadership",
                      category="policy-update", priority="P4")],
    },
    "EVT-062": {
        "tickets": [T("Policy decision request: Vendor Onboarding SOP v3 - SaaS single-source exemption and Net-30 threshold",
                      "Procurement has processed SaaS subscriptions on a single quote and accepted Net-30 under Rs 10 lakh without CFO "
                      "approval this year ({{ticket:EVT-062#1}} and earlier: Zendesk seats, Figma). SOP v2 requires three quotes for SaaS "
                      "and hosting and Net-45. Requesting a CFO decision: codify (SaaS exemption with single-source note; Net-30 accepted "
                      "under Rs 10 lakh) or revert.",
                      "", "Shalini Menon", "Vivek Anand", "2026-08-26", status="open", group="Finance Leadership",
                      category="policy-update", priority="P3")],
    },
    # ---- follow-ups on the contradictory events
    "EVT-063": {
        "tickets": [T("PROBLEM: GlobalProtect periodic disconnects (~30 min) on home Wi-Fi - multiple users, no confirmed root cause",
                      "Problem record consolidating {{ticket:EVT-063#1}} (closed: client reinstall) and {{ticket:EVT-063#2}} (closed: IPv6 "
                      "disabled) plus reports from Harsha Vardhan and Payal Shah in August. Both earlier fixes were assumed from short "
                      "observation windows and the issue persists. Hypothesis: gateway IKE rekey at 30 minutes failing on some home routers.",
                      "", "Lakshmi Narayanan", "Lakshmi Narayanan", "2026-08-04", status="in_progress", group="IAM", kind="incident",
                      category="problem", priority="P3",
                      work_notes="Logs collected from 3 users on 12-Aug and 19-Aug: all drops align with the 30-minute rekey. Test gateway with rekey at 8h scheduled for the week of 21-Sep (CHG to follow).")],
    },
    "EVT-064": {
        "tickets": [T("Assign 'Report Export' permission set to all Sales Ops and Deal Desk profiles",
                      "Following {{ticket:EVT-064#2}}: the January profile cleanup removed Export Reports from the base Sales Ops profiles. "
                      "Bulk-assign the 'Report Export' permission set to the Sales Ops Analyst, Deal Desk Analyst and Revenue Analyst "
                      "profiles so this stops arriving one user at a time.",
                      "Permission set assigned to 7 users across the three profiles 06-May; sandbox test first. Service Desk KB updated to "
                      "route Salesforce permission issues to Sales Ops.",
                      "Megha Patil", "Megha Patil", "2026-05-05", resolved="2026-05-06", group="Sales Ops", category="application",
                      approvers=["Vinod Krishnamurthy"])],
    },
    "EVT-065": {
        "tickets": [T("KB article update: 'Okta Verify push not arriving' - add device time-sync check before re-enrolment",
                      "Two tickets this year ({{ticket:EVT-065#1}}, {{ticket:EVT-065#2}}) resolved the same symptom differently. The KB "
                      "article KB0041 only says 're-enrol'. Add step 1: confirm the phone's automatic date & time is on; step 2: update Okta "
                      "Verify; step 3: re-enrol only if both fail.",
                      "KB0041 updated 02-Jul with the three-step order and a note that re-enrolment masks time-sync issues. Service Desk "
                      "briefed at the Thursday huddle.",
                      "Kavya Reddy", "Shruti Joshi", "2026-07-01", resolved="2026-07-02", group="IT Service Desk", category="knowledge")],
        "emails": [M("KB0041 updated - Okta Verify push troubleshooting",
                     [("Kavya Reddy", ["Deepak Verma", "Anjali Gupta", "Shruti Joshi"], "2026-07-02T14:30",
                       "Hi all,\n\nKB0041 now starts with 'check the phone's automatic date & time' before re-enrolling Okta Verify. Bhavana's "
                       "ticket yesterday was fixed in ten seconds that way; Riya's in April was 'fixed' by re-enrolment, which re-syncs the "
                       "factor and hides the real cause. Please follow the new order and note which step fixed it on the ticket so we can "
                       "see the pattern.\n\nKavya")])],
    },
    "EVT-066": {
        "tickets": [T("Decision needed: remote connectivity (home internet) allowance - policy gap",
                      "Two remote employees received opposite decisions on home-internet claims ({{ticket:EVT-066#1}} approved Rs 1,500/month, "
                      "{{ticket:EVT-066#2}} rejected). T&E policy v5 is silent. Requesting a CFO decision for inclusion in T&E v6: allowance "
                      "yes/no, amount, eligibility (designated remote roles only?).",
                      "", "Shalini Menon", "Vivek Anand", "2026-06-16", status="open", group="Finance Leadership",
                      category="policy-update", priority="P4", work_notes="Bundled into the T&E v6 draft; no decision yet.")],
        "slack": [S("#expenses-help", [
                      ("Ishita Bose", "2026-06-12T15:40", "Has anyone remote managed to claim home broadband? Mine just got rejected as 'not a category' but I heard Marketing gets it."),
                      ("Ethan Brooks", "2026-06-12T19:05", "I get Rs 1,500/month since March - Ramesh approved it under Connectivity."),
                      ("Ishita Bose", "2026-06-12T19:10", "So it depends who picks up the claim?? Raising it with Alok."),
                      ("Alok Mishra", "2026-06-15T10:25", "It's a gap in the policy - escalated to Shalini for a proper decision. Until then no new approvals, sorry Ishita."),
                  ])],
    },
    "EVT-067": {
        "tickets": [T("Q2 access review follow-up: console-readonly without training completion - Preeti Nambiar",
                      "Q2 review action ({{doc:EVT-016#1}}): Preeti Nambiar holds console-readonly granted in January under a manager "
                      "attestation ({{ticket:EVT-067#1}}); 'Handling Customer Data' still shows not completed. Per the 23-Apr agreement she "
                      "completes the course before the Q3 review or is removed.",
                      "Preeti completed 'Handling Customer Data' on 06-Jul (certificate on LearnHub). Access retained; recorded for the Q3 "
                      "review. Note: Sameer Khan ({{ticket:EVT-067#2}}) has still not completed the course or re-raised.",
                      "Rohan Mehta", "Kavya Reddy", "2026-07-02", resolved="2026-07-07", group="IAM", category="access-review",
                      sensitivity="restricted")],
    },
    "EVT-068": {
        "tickets": [T("Update Systems Directory: Jira project creation handled by Service Desk (template); Platform owns configuration",
                      "Per the Rohan/Rajesh agreement of 06-Aug ({{ticket:EVT-068#2}}): update the Jira entry in the Systems Directory and "
                      "the Jira user guide so requesters know the Service Desk creates projects from the standard template and Platform "
                      "Backend owns schemes, workflows and integrations.",
                      "Systems Directory Jira row and the Jira user guide updated 07-Aug; Service Desk KB article 'Create a Jira project "
                      "(template)' published; Shruti Joshi named owner.",
                      "Rohan Mehta", "Rajesh Kumar", "2026-08-06", resolved="2026-08-07", group="IT Service Desk", category="knowledge")],
    },
    "EVT-070": {
        "tickets": [T("Referral bonus payout - Aditya Rao (referee Ishaan Roy, 90 days on 28-Sep) - October payroll",
                      "Per the Referral Bonus Policy v2 (90 days), Aditya Rao's Rs 25,000 referral bonus for Ishaan Roy is due in the October "
                      "payroll. The earlier HR answer of 6 months ({{ticket:EVT-070#2}}) followed the superseded v1. TA confirmation form "
                      "attached.",
                      "", "Rohit Sinha", "Vijay Kumar", "2026-09-22", status="open", group="Payroll", category="payroll",
                      sensitivity="restricted", work_notes="Awaiting 28-Sep (referee completes 90 days) before inclusion in the October run.")],
    },
    # ---- extra emails / slack on events that had none or one
    "EVT-002": {
        "emails": [M("Welcome to the Data team - how we handle data access",
                     [("Suresh Pillai", ["Pooja Hegde"], "2026-07-20T09:30",
                       "Hi Pooja,\n\nWelcome! Two things about data access before you dive in: (1) everything goes through a Jira DATA ticket, "
                       "even when I've said yes in person - the ticket is the record; (2) you'll get the curated marts today or tomorrow, but "
                       "anything PII-tagged is a separate conversation with a purpose statement, and we're being careful there because the "
                       "DPO role is vacant. Ananya will get you set up. Customer 360 kick-off with Manish is Thursday.\n\nSuresh")])],
    },
    "EVT-004": {
        "slack": [S("#marketing", [
                      ("Ankit Chawla", "2026-06-10T15:20", "Pixelcraft's two accounts are live (ext-neha.prabhu, ext-sameer.lobo) - WordPress staging + the MKT Confluence space only. #ext-pixelcraft is our shared channel with them."),
                      ("Omar Farooq", "2026-06-10T15:22", "Do they get Figma through us or their own?"),
                      ("Ankit Chawla", "2026-06-10T15:24", "Their own Figma; we share files to their org. Accounts expire 8 Sep and I'll extend."),
                      ("Riya Sen", "2026-06-10T15:30", "Please remind them not to paste customer names in the shared channel - I've seen agencies do that."),
                  ])],
    },
    "EVT-007": {
        "emails": [M("HubSpot mapping change - plan and rollback",
                     [("Megha Patil", ["Manoj Venkatesh", "Aparna Das"], "2026-04-10T15:05",
                       "Manoj, Aparna,\n\nPlan for the Lead Source mapping fix (MKT-233): change the connector field mapping in the HubSpot "
                       "sandbox today, verify with 20 test leads, then apply to production Monday 11:00 with Aparna watching the sync log. "
                       "Rollback is reverting the mapping (2 minutes). I won't touch any workflows - only the field mapping.\n\nMegha"),
                      ("Aparna Das", ["Megha Patil", "Manoj Venkatesh"], "2026-04-10T15:30",
                       "Works for me. Note that saving the connector settings re-publishes the associated workflows - I'll check they're all "
                       "still in the state we expect afterwards.\n\nAparna")])],
    },
    "EVT-009": {
        "slack": [S("#demand-gen", [
                      ("Ethan Brooks", "2026-06-30T19:45", "VPN finally works from Denver - Lakshmi found my router was eating large packets. Metabase growth dashboards, here I come."),
                      ("Aparna Das", "2026-07-01T09:10", "No more screenshot requests then :tada:"),
                      ("Manoj Venkatesh", "2026-07-01T09:15", "Nice. Ethan, add the MTU thing to the remote setup guide if it's not there - you won't be the last US hire."),
                  ])],
    },
    "EVT-012": {
        "slack": [S("#sales-team", [
                      ("Simran Kaur", "2026-01-27T16:05", "Tip for AEs: you can get a read-only Chargebee 'Invoice Viewer' role to check overdue invoices before renewal calls - Deepa approves it. Took me 5 days, no more emailing Anusha every time."),
                      ("Aakash Bhatia", "2026-01-27T16:08", "Oh nice. Does it show all customers or just yours?"),
                      ("Simran Kaur", "2026-01-27T16:09", "All - so treat it as restricted, no exports."),
                  ])],
    },
    "EVT-013": {
        "emails": [M("Tier 2 - access and expectations",
                     [("Anita Desai", ["Preeti Nambiar"], "2026-07-08T09:20",
                       "Hi Preeti,\n\nCongratulations again. For Tier 2 you'll need the support@ shared mailbox and the Zendesk Tier 2 group - "
                       "please raise both in ServiceNow today and I'll approve. Escalations to Engineering go through a linked SUP issue and "
                       "#customer-success, P1s also to #incidents. And please do finish the 'Handling Customer Data' course this month - the "
                       "Admin Console access you got in January was on my attestation and the new policy expects the course.\n\nAnita")])],
    },
    "EVT-015": {
        "emails": [M("Datadog viewer - which dashboards to use in QBRs",
                     [("Varun Chandra", ["Sameer Khan"], "2026-08-28T10:30",
                       "Sameer,\n\nYou're set up as a viewer. For QBRs use 'Tenant SLO' (per-customer latency/uptime, already filtered to "
                       "exclude internal tenants) and 'Platform SLOs' for the overall picture. Please don't screenshot the infrastructure "
                       "dashboards - they include hostnames and account IDs we don't share externally.\n\nVarun"),
                      ("Sameer Khan", ["Varun Chandra"], "2026-08-28T10:45", "Understood, Tenant SLO only. Thanks Varun.\n\nSameer")])],
    },
    "EVT-018": {
        "slack": [S("#talent-acquisition", [
                      ("Nisha Pandey", "2026-05-27T17:30", "Campus pipelines restructured - new stages, scorecards and the campus offer chain are live in Greenhouse. My Site Admin drops tomorrow as planned."),
                      ("Bhavana Shetty", "2026-05-27T17:32", "The new scorecards are so much clearer, thank you!"),
                      ("Rohit Sinha", "2026-05-27T17:40", "Great work. Akhil, please use the new pipeline for the Hyderabad campus round."),
                  ])],
    },
    "EVT-020": {
        "emails": [M("Credentials in Slack - what happened today and what changes",
                     [("Amit Saxena", ["Natasha D'Souza", "Rahul Kapoor"], "2026-05-06T15:40",
                       "Natasha, Rahul,\n\nSummary of this morning: a demo tenant admin password was posted in #sales-team; it was deleted within "
                       "15 minutes and I rotated it. No sign of misuse (the demo tenant has no customer data). The Password & MFA Standard is "
                       "clear that shared credentials live in 1Password vaults, so from tomorrow the Sales-Demo vault is the only place for "
                       "demo logins - anything found in Slack, notes or email will be rotated without notice. Not a disciplinary matter, but "
                       "please reinforce it at the team meeting.\n\nAmit"),
                      ("Rahul Kapoor", ["Amit Saxena", "Natasha D'Souza"], "2026-05-06T17:10", "Will do. Thanks for the quick response.\n\nRahul")])],
    },
    "EVT-022": {
        "slack": [S("#eng-platform", [
                      ("Daniel Fernandes", "2026-05-27T16:10", "FYI: chargebee-sync dropped every webhook since Sunday because the signing secret was rotated on the Chargebee side. Replaying now. Lesson: any secret used by an integration needs a 'dependents' note in the rotation checklist."),
                      ("Priya Shah", "2026-05-27T16:15", "Could we validate signature failures as an alert? 3 days of silent 401s is rough."),
                      ("Daniel Fernandes", "2026-05-27T16:17", "Yes - PLAT-2318, monitor on signature failures > 10/hour."),
                      ("Rohan Mehta", "2026-05-27T16:25", "Good. Add the Secrets Manager entry name to the Chargebee runbook too."),
                  ])],
    },
    "EVT-023": {
        "emails": [M("Zendesk login loop - incident summary",
                     [("Nikhil Bhatt", ["Sandeep Malhotra", "Anita Desai"], "2026-07-15T14:30",
                       "Sandeep, Anita,\n\nToday's Zendesk login loop (10:40-12:35) was caused by an Okta SAML setting change made during cleanup "
                       "from the Q2 access review, without a change record. Lakshmi reverted it. No customer SLAs were missed thanks to CS "
                       "working the two enterprise P1s by phone. Actions: Okta app-configuration changes go through a CHG from now on (they "
                       "are in scope of the Change Management Policy already - we just didn't treat 'cleanup' as a change), and I'll review "
                       "the Okta admin change log weekly.\n\nNikhil"),
                      ("Anita Desai", ["Nikhil Bhatt", "Sandeep Malhotra"], "2026-07-15T14:50", "Thanks Nikhil - appreciated the fast rollback.\n\nAnita")])],
    },
    "EVT-025": {
        "emails": [M("CI runners restored - what happened",
                     [("Siddharth Jain", ["Eng-All"], "2026-06-11T12:45",
                       "All,\n\nThe self-hosted GitHub Actions runners were offline from 09:20 to 12:25 because the Docker layer cache filled "
                       "their disks - the nightly prune was lost when the runner AMI was rebuilt in April. Queue has drained. Permanent fix "
                       "(prune baked into the AMI + a disk alert) goes to Tuesday's CAB; the runner runbook is updated. Sorry for the lost "
                       "morning.\n\nSiddharth")])],
    },
    "EVT-028": {
        "emails": [M("Okta outage 18-Nov - post-incident note",
                     [("Nikhil Bhatt", ["Sandeep Malhotra"], "2025-11-19T09:40",
                       "Sandeep,\n\nPost-incident note for yesterday's Okta outage (09:38-10:19, vendor cell ap-1). What worked: the runbook, the "
                       "WhatsApp fallback, phone logging by the Service Desk (5 tickets). What didn't: about a third of staff aren't in the "
                       "WhatsApp group, and Slack/ServiceNow being behind Okta means we have no in-band channel. Proposals: (1) HR adds "
                       "everyone to the group at onboarding; (2) we keep a static status page outside Okta; (3) Okta Verify enrolment drive "
                       "so sessions survive longer. No config was touched; break-glass use is logged.\n\nNikhil"),
                      ("Sandeep Malhotra", ["Nikhil Bhatt"], "2025-11-19T11:00", "Agree with all three. Please take (1) to Geeta and (2) to Rajesh.\n\nSandeep")])],
    },
    "EVT-030": {
        "emails": [M("Certificate and token inventory - now on the IT Runbooks page",
                     [("Lakshmi Narayanan", ["Nikhil Bhatt", "Rajesh Kumar", "Varun Chandra"], "2026-06-04T16:20",
                       "All,\n\nAfter yesterday's VPN certificate expiry I've created a certificate & token inventory on the IT Runbooks page: "
                       "VPN portal/gateway certs, the Okta signing cert, Datadog and Vercel API tokens, and (added today at Rajesh's request) "
                       "the Apple Business Manager token and APNs certificate for Intune. Each row has an owner and a backup, and Datadog "
                       "synthetics now alert at 30 and 7 days for the public endpoints. Please add anything you own that I've missed.\n\nLakshmi")])],
    },
    "EVT-031": {
        "emails": [M("ABM token expiry - added to the inventory",
                     [("Mohammed Irfan", ["Rajesh Kumar"], "2026-09-09T13:10",
                       "Rajesh,\n\nRoot cause of the Mac enrolment failures was the Apple Business Manager MDM token expiring on 8 September "
                       "(annual). Renewed and uploaded; all three devices enrolled by noon. I've added the ABM token (next expiry 9 Sep 2027) "
                       "and the APNs certificate (14 Nov 2026) to Lakshmi's certificate & token inventory with calendar reminders at 30 and 7 "
                       "days - same failure pattern as the VPN cert in June, so same fix.\n\nMohammed")])],
    },
    "EVT-033": {
        "emails": [M("Standby monitoring - redesign after the alert storm",
                     [("Nandini Rajan", ["Varun Chandra", "Harish Gowda"], "2026-05-08T16:30",
                       "Varun, Harish,\n\nWrite-up of this morning: cloning the Mumbai monitors onto the Singapore standby produced ~340 pages "
                       "in two hours because every throughput monitor fired against zero traffic. I've replaced them with a 12-monitor standby "
                       "set (cluster health, node readiness, RDS replica lag, ArgoCD sync status, certificate expiry). The full set is "
                       "re-enabled only by the failover runbook. Abhishek has been taken off pager for the rest of the day. Proposal for the "
                       "SRE sync: any monitor that pages more than three times in a week without action gets reviewed.\n\nNandini"),
                      ("Varun Chandra", ["Nandini Rajan", "Harish Gowda"], "2026-05-08T17:05", "Approved; put the three-times rule into the On-Call policy update.\n\nVarun")])],
    },
    "EVT-034": {
        "slack": [S("#it-helpdesk", [
                      ("Deepak Verma", "2026-02-19T15:25", "Slack is back (vendor outage 13:10-15:20). If you emailed the Service Desk during the outage we've got it - no need to re-raise."),
                      ("Ankit Chawla", "2026-02-19T15:27", "Confirmed working here. That Teams channel was surprisingly usable."),
                      ("Rajesh Kumar", "2026-02-19T15:30", "Reminder that 'IT-Incidents' in Teams stays as the fallback channel - it's in the vendor outage runbook."),
                  ])],
    },
    "EVT-036": {
        "emails": [M("Wi-Fi controller firmware - process change",
                     [("Shruti Joshi", ["Rajesh Kumar"], "2026-03-31T14:20",
                       "Rajesh,\n\nFloor 3 was down 09:00-11:35 because the wireless controller auto-installed 8.10.3 overnight and reset the "
                       "floor-3 RADIUS profile (a known issue in the vendor release notes I hadn't read). Rolled back to 8.9.8. I've disabled "
                       "auto-update; from now on controller firmware goes through a CHG with a CAB slot and gets tested on the floor-4 AP "
                       "group first. Two spare docks went to FP&A as an interim and they'd like to keep them.\n\nShruti"),
                      ("Rajesh Kumar", ["Shruti Joshi"], "2026-03-31T14:45", "Good call on the CHG. They can keep the docks - update the asset records.\n\nRajesh")])],
    },
    "EVT-040": {
        "emails": [M("Offline mode - what Support needs to know",
                     [("Meera Krishnan", ["Anita Desai", "Preeti Nambiar"], "2025-09-24T11:15",
                       "Anita, Preeti,\n\nHeads-up on a design decision for Driver App offline mode (shipping in 3.5, January): when two devices "
                       "edit the same trip while offline, the later device timestamp wins and the overwritten value is kept in a server-side "
                       "audit table. Support will occasionally see 'my delivery time changed by itself' - the audit row in the Admin Console "
                       "will show what happened. We'll add a support note to the release. Design doc is on the ENG space.\n\nMeera"),
                      ("Anita Desai", ["Meera Krishnan", "Preeti Nambiar"], "2025-09-24T12:00", "Thanks - please make sure the audit view is readable by console-readonly users.\n\nAnita")])],
    },
    "EVT-043": {
        "emails": [M("New: request application access through the ServiceNow catalog",
                     [("Rajesh Kumar", ["All-Company"], "2026-06-08T09:30",
                       "All,\n\nFrom today, requests for Salesforce, Zendesk, HubSpot, Metabase and GitHub access are made through the new "
                       "'Request Access' items in the ServiceNow Employee Service Portal. Your manager's approval is routed automatically "
                       "(and to their delegate if they have set one in Darwinbox), then to the system owner where an admin role is requested. "
                       "Free-text requests will be redirected to the catalog. More applications (VPN, shared mailboxes, laptops, software) "
                       "follow in August.\n\nRajesh Kumar\nIT Service Desk")])],
    },
    "EVT-047": {
        "slack": [S("#finance", [
                      ("Alok Mishra", "2026-06-10T11:20", "Zoho-NetSuite parallel run starts today - the integration posts a summarised daily journal alongside my manual upload. If the two don't match I'll shout."),
                      ("Manish Tiwari", "2026-06-10T11:25", "Each journal has a zoho_batch_id and a drill-back link - click through if a total looks odd."),
                      ("Payal Shah", "2026-06-10T11:30", "Cost centre mapping matches the AOP structure, confirmed."),
                  ])],
    },
    "EVT-071": {
        "emails": [M("Welcome to Content & Brand - tools and first week",
                     [("Ankit Chawla", ["Kabir Mehrotra"], "2026-07-27T08:40",
                       "Hi Kabir,\n\nWelcome! Your role bundle gives you Confluence (MKT space) and Jira MKT; please raise HubSpot in the "
                       "ServiceNow catalog today and I'll approve - that's the standard route and it takes a day. Social accounts are in the "
                       "1Password vault 'Brand-Social' (never in Slack or notes). Riya is your buddy; content calendar review is Mondays 11:00. "
                       "First task: the v4 launch social plan with Sanya.\n\nAnkit"),
                      ("Kabir Mehrotra", ["Ankit Chawla"], "2026-07-28T14:10", "Thanks Ankit - HubSpot came through already. Reading the launch plan.\n\nKabir")])],
    },
    "EVT-072": {
        "slack": [S("#customer-success", [
                      ("Anita Desai", "2026-05-21T15:30", "Small PSA for anyone travelling: submit expenses within 30 days with receipts for anything over Rs 500 and they sail through - mine from Mumbai got approved in a day."),
                      ("Kunal Shah", "2026-05-21T15:33", "Noted, I have a Pune-Mumbai trip next week."),
                  ])],
    },
    "EVT-073": {
        "emails": [M("Planned maintenance: production database resize, Sunday 12 April 02:00-03:00 IST",
                     [("Nandini Rajan", ["Anita Desai", "Sanya Kapadia"], "2026-04-09T16:30",
                       "Anita, Sanya,\n\nCAB approved a production database resize for Sunday 12 April 02:00-03:00 IST (about 2 minutes of "
                       "failover; API requests may retry). Please post the standard maintenance notice on the status page 48 hours ahead and "
                       "let the APAC accounts know, as it's 04:30 Singapore time. Change record: {{ticket:EVT-073#1}}.\n\nNandini"),
                      ("Anita Desai", ["Nandini Rajan", "Sanya Kapadia"], "2026-04-09T17:00", "Notice scheduled for tomorrow 02:00; APAC CSMs informed.\n\nAnita")])],
    },
    "EVT-075": {
        "slack": [S("#talent-acquisition", [
                      ("Bhavana Shetty", "2026-08-28T15:10", "For anyone planning Diwali leave: 12 PL days carry forward, the rest lapse in March, and you need notice of twice the duration. HR queue answered mine in an hour."),
                      ("Akhil Menon", "2026-08-28T15:12", "Useful, thanks - applying for the Hyderabad week now."),
                  ])],
    },
    "EVT-076": {
        "slack": [S("#talent-acquisition", [
                      ("Rohit Sinha", "2026-03-10T10:05", "The TalentBridge contract recruiter finishes on Thursday - I've given IAM notice so the account is disabled that evening. Please hand over any Greenhouse candidates she owns by Wednesday."),
                      ("Nisha Pandey", "2026-03-10T10:08", "Taking her two engineering reqs."),
                      ("Akhil Menon", "2026-03-10T10:10", "I'll take the Hyderabad ones."),
                  ])],
    },
    "EVT-078": {
        "slack": [S("#marketing", [
                      ("Omar Farooq", "2026-02-24T10:30", "Figma Professional seats are live and behind Okta - Nikita, Ishita, you should see the tile. Pixelcraft joins via SSO guest."),
                      ("Nikita Bansal", "2026-02-24T10:32", "Got it!"),
                      ("Kavita Bhatnagar", "2026-02-24T10:40", "Good - a week from request to seats with the right approvals. That's how it should work."),
                  ])],
    },
    "EVT-079": {
        "slack": [S("#learning", [
                      ("Leela Krishnan", "2026-09-04T11:00", "Reimbursement for the instructional design certificate came through in a day - pre-approval in LearnHub, certificate attached, done. Highly recommend the course for anyone building training."),
                      ("Dev Patel", "2026-09-04T11:05", "Adding it to the recommended list on the L&D page."),
                  ])],
    },
    "EVT-080": {
        "emails": [M("Nimbus renewal - 15% approved",
                     [("Arun Prasad", ["Aakash Bhatia"], "2026-05-13T15:35",
                       "Aakash - Natasha approved the 15% on the ticket and in CPQ; quote is generated and the Chargebee renewal will update "
                       "from it. Nothing else needed at this level.\n\nArun")])],
    },
}


# ---------------------------------------------------------------- generated approval-nudge threads

_NUDGE = [
    "Hi {approver_first},\n\nCould you approve {tid} in ServiceNow when you have a minute? It's the {what}. The IAM clock only starts once the approval is recorded.\n\nThanks,\n{req_first}",
    "Hi {approver_first},\n\nGentle nudge on {tid} ({what}) - it's sitting in your approvals list. Happy to add any justification you need.\n\n{req_first}",
    "{approver_first} - {tid} needs your approval ({what}). The link is in the ServiceNow email from this morning; otherwise the portal > My Approvals.\n\nThanks!\n{req_first}",
]
_APPROVE = [
    "Approved on the ticket.\n\n{approver_first}",
    "Done - approved just now. {extra}\n\n{approver_first}",
    "Approved. {extra}\n\n{approver_first}",
]
_EXTRA = ["", "Let me know if it doesn't come through in a couple of days.", "Please keep it to what you actually need.",
          "FYI I've set a delegate in Darwinbox for next week in case anything else comes up."]
_DONE = [
    "Hi {req_first},\n\n{tid} is fulfilled - details on the ticket. Please confirm you can get in and I'll close it.\n\n{asg_first}",
    "{req_first} - your request {tid} is done; you should see it after your next login. Closing the ticket.\n\n{asg_first}",
]


def approval_threads(bundles, max_threads=24):
    """Generate nudge/approve/fulfilled email threads for event tickets with approvers."""
    r = rng("approval-threads")
    out = {}
    count = 0
    for b in bundles:
        if count >= max_threads:
            break
        existing = len(b["emails"]) + len(EXTRA.get(b["id"], {}).get("emails", []))
        if existing >= 2:
            continue
        for i, t in enumerate(b["tickets"], 1):
            if count >= max_threads:
                break
            if not t["approvers"] or t["status"] in ("cancelled",) or t["kind"] == "incident":
                continue
            approver = t["approvers"][0]
            if approver == t["requester"]:
                continue
            req_first, appr_first, asg_first = t["requester"].split()[0], approver.split()[0], t["assignee"].split()[0]
            what = t["subject"].split(" - ")[0]
            created = t["created"]
            nudge_day = created if is_business_day(d(created)) else add_business_days(created, 1)
            approve_day = add_business_days(nudge_day, r.choice([0, 0, 1]))
            if t["resolved"] and approve_day > t["resolved"]:
                approve_day = t["resolved"]
            tid = f"{{{{ticket:{b['id']}#{i}}}}}"
            msgs = [
                (t["requester"], approver, f"{nudge_day}T{r.randint(9, 11):02d}:{r.choice(['05', '20', '35', '50'])}",
                 r.choice(_NUDGE).format(approver_first=appr_first, tid=tid, what=what, req_first=req_first)),
                (approver, t["requester"], f"{approve_day}T{r.randint(12, 17):02d}:{r.choice(['10', '25', '40', '55'])}",
                 r.choice(_APPROVE).format(approver_first=appr_first, extra=r.choice(_EXTRA)).replace("  ", " ").rstrip()),
            ]
            if t["resolved"] and t["assignee"] not in (t["requester"], approver) and r.random() < 0.7:
                done_day = t["resolved"]
                if done_day < approve_day:
                    done_day = approve_day
                msgs.append((t["assignee"], t["requester"], f"{done_day}T{r.randint(14, 18):02d}:{r.choice(['00', '15', '30', '45'])}",
                             r.choice(_DONE).format(req_first=req_first, tid=tid, asg_first=asg_first)))
            # keep chronological order
            msgs.sort(key=lambda m: m[2])
            out.setdefault(b["id"], []).append(M(f"Approval needed: {tid} - {t['subject'].split(' - ')[0]}", msgs,
                                                 sensitivity=t.get("sensitivity")))
            count += 1
            break  # one generated thread per event
    return out


def apply(bundles):
    """Merge EXTRA and generated approval threads into the bundles (in place)."""
    generated = approval_threads(bundles)
    for b in bundles:
        extra = EXTRA.get(b["id"], {})
        b["tickets"] += extra.get("tickets", [])
        b["emails"] += extra.get("emails", []) + generated.get(b["id"], [])
        b["slack"] += extra.get("slack", [])
        b["docs"] += extra.get("docs", [])
    unknown = set(EXTRA) - {b["id"] for b in bundles}
    assert not unknown, f"EXTRA references unknown events: {unknown}"
    return bundles
