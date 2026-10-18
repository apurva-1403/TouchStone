"""Layer 6/7 - Routine / no-conflict baseline events EVT-071..EVT-080.

Deliberately boring: practice matches the written policy. These are the false-positive
controls - drift detection must NOT fire on them.
"""
from events.dsl import E, T, M, S, D

EVENTS = [
    # ------------------------------------------------------------------ EVT-071
    E("EVT-071", "routine_baseline", "standard_access_request_per_policy", "2026-07-28",
      ["Kabir Mehrotra", "Ankit Chawla", "Kavya Reddy", "Aparna Das"], "Content & Brand",
      system="HubSpot Marketing Hub", policy="Application Access Request Policy",
      summary="Kabir Mehrotra (new Social Media Manager) requested HubSpot access on his second day. Line manager Ankit Chawla approved "
              "within the hour; IAM added the Okta group and Aparna Das assigned the permission set the same day - well inside the "
              "3-business-day fulfilment SLA. Exactly what the Application Access Request Policy describes.",
      outcome="resolved", drift=False, related_events=["EVT-050"], tags=["baseline", "access", "policy-consistent", "demo"],
      demo={"query": "How do I get access to HubSpot?", "expected_drift": False},
      tickets=[
          T("HubSpot Marketing Hub access (social publishing) - Kabir Mehrotra",
            "I joined yesterday as Social Media Manager. I need HubSpot with social publishing and the reporting dashboards. Manager: "
            "Ankit Chawla.",
            "Ankit Chawla approved 28-Jul 10:05. Added to Okta group hubspot-marketing 28-Jul 11:30; Aparna Das assigned the 'Marketing - "
            "Social & Content' permission set 28-Jul 14:00. Fulfilled within SLA (same day).",
            "Kabir Mehrotra", "Kavya Reddy", "2026-07-28", resolved="2026-07-28", group="IAM", approvers=["Ankit Chawla"]),
      ],
      slack=[
          S("#marketing", [
              ("Kabir Mehrotra", "2026-07-28T09:50", "Raised my HubSpot access request - Ankit, it's waiting on you :)"),
              ("Ankit Chawla", "2026-07-28T10:06", "Approved."),
              ("Aparna Das", "2026-07-28T14:02", "@Kabir you're set up - social publishing and reporting. Welcome!"),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-072
    E("EVT-072", "routine_baseline", "expense_claim_within_policy", "2026-05-21",
      ["Anita Desai", "Rahul Kapoor", "Ramesh Babu"], "Accounts Payable & Procurement",
      system="Zoho Expense", policy="Travel & Expense Reimbursement Policy",
      summary="Anita Desai's Mumbai customer-visit claim (submitted 9 days after travel, itemised receipts for every item over Rs 500, "
              "hotel under the metro cap, per-diem claimed without meal receipts) was approved by her manager and by Finance AP in two "
              "days. A textbook claim under the T&E policy - no exceptions needed.",
      outcome="resolved", drift=False, related_events=["EVT-056"], tags=["baseline", "expenses", "policy-consistent", "demo"],
      demo={"query": "How do I submit a travel expense claim?", "expected_drift": False},
      tickets=[
          T("Expense claim query: Mumbai customer visits 11-13 May - Anita Desai (status check)",
            "Submitted my Mumbai trip claim in Zoho on 20-May (Rs 21,340: flights, 2 nights hotel at Rs 5,800, per diem 3 days, airport "
            "taxis). Rahul has approved. Just checking it will make the 20th cut-off for this month's payroll.",
            "Claim reviewed 21-May: within 30 days of expense, receipts attached for all items above Rs 500, hotel within the Rs 6,000 metro "
            "cap, per diem at Rs 2,000 x 3 with no separate meal claims. Approved by Finance AP 21-May; included in the May reimbursement "
            "run (cut-off met).",
            "Anita Desai", "Ramesh Babu", "2026-05-21", resolved="2026-05-21", group="Finance AP", category="expenses",
            approvers=["Rahul Kapoor"]),
      ],
      emails=[
          M("RE: Mumbai trip claim - approved",
            [("Ramesh Babu", "Anita Desai", "2026-05-21T15:10",
              "Hi Anita,\n\nApproved - everything's in order (receipts, caps, per diem). It's in this month's run, so it'll be with your May "
              "salary.\n\nRamesh"),
             ("Anita Desai", "Ramesh Babu", "2026-05-21T15:20", "Great, thanks Ramesh.\n\nAnita")]),
      ]),

    # ------------------------------------------------------------------ EVT-073
    E("EVT-073", "routine_baseline", "infrastructure_change_via_cab", "2026-04-07",
      ["Nandini Rajan", "Varun Chandra", "Rohan Mehta", "Nikhil Bhatt"], "Cloud Infrastructure & Security",
      system="AWS Production Account", policy="Change Management Policy",
      summary="RDS production instance resize (db.r6g.2xlarge to 4xlarge) raised as a Normal change with rollback plan, reviewed and "
              "approved at the Thursday CAB, implemented in the approved window with the outcome recorded next day. Infrastructure changes "
              "still follow the Change Management Policy exactly as written.",
      outcome="resolved", drift=False, related_events=["EVT-052"], tags=["baseline", "change-management", "policy-consistent", "demo"],
      demo={"query": "How do I get an infrastructure change approved?", "expected_drift": False},
      tickets=[
          T("Change: resize production RDS prod-postgres from db.r6g.2xlarge to db.r6g.4xlarge",
            "Connection and CPU headroom for the v4 migration (postmortem action). Multi-AZ instance; resize causes ~2 min failover. "
            "Window: Sun 12-Apr 02:00-03:00 IST. Test evidence: same resize done in staging 01-Apr. Rollback: resize back (same downtime). "
            "Customer comms: status page maintenance notice 48h ahead.",
            "Reviewed at CAB Thu 09-Apr: approved (Varun Chandra, Nikhil Bhatt, Rohan Mehta). Implemented 12-Apr 02:05-02:41; failover "
            "1m50s; no errors. Outcome recorded 13-Apr: successful. Closed.",
            "Nandini Rajan", "Varun Chandra", "2026-04-07", resolved="2026-04-13", group="Cloud Infrastructure", kind="change",
            category="infrastructure-change", priority="P2"),
      ],
      slack=[
          S("#devops-sre", [
              ("Nandini Rajan", "2026-04-07T15:30", "CHG raised for the prod RDS resize (Sunday 2am window). Going to Thursday's CAB."),
              ("Varun Chandra", "2026-04-09T15:40", "Approved at CAB. Status page notice please, Nandini."),
              ("Nandini Rajan", "2026-04-12T02:45", "Resize done, failover under 2 min, all green."),
              ("Rohan Mehta", "2026-04-13T09:10", "Connection headroom looks much better on the dashboard. Thanks."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-074
    E("EVT-074", "routine_baseline", "laptop_refresh_within_sla", "2026-07-16",
      ["Nisha Pandey", "Rohit Sinha", "Deepak Verma"], "IT Service Desk & Endpoint",
      system="Microsoft Intune", policy="Laptop & Endpoint Provisioning SOP",
      summary="Nisha Pandey's 4-year laptop refresh (ThinkPad T14) was approved by her manager and delivered in 4 business days from a "
              "ThinkPad that had just arrived on the July stock order - within the SOP's 5-business-day target. (Contrast with EVT-051, "
              "where MacBook Pro stock made the same SLA impossible.)",
      outcome="resolved", drift=False, related_events=["EVT-051"], tags=["baseline", "laptop", "policy-consistent"],
      tickets=[
          T("Laptop refresh (4-year cycle) - Nisha Pandey (ThinkPad T14)",
            "My ThinkPad turned 4 in June and the fan is constantly on. Requesting the standard refresh. Manager: Rohit Sinha.",
            "Approved by Rohit Sinha 16-Jul. ThinkPad T14 Gen 5 from the July stock delivery (arrived 20-Jul) assigned: KT-LT-0416. "
            "Enrolled in Intune, apps installed, data migrated via OneDrive, handed over 22-Jul (4 business days). Old device wiped 24-Jul.",
            "Nisha Pandey", "Deepak Verma", "2026-07-16", resolved="2026-07-22", group="IT Service Desk", category="laptop",
            approvers=["Rohit Sinha"]),
      ],
      slack=[
          S("#it-helpdesk", [
              ("Nisha Pandey", "2026-07-22T11:30", "New laptop handed over, thanks Deepak - 4 working days, the wiki was right this time :)"),
              ("Deepak Verma", "2026-07-22T11:32", "ThinkPads we have, it's the Macs that are the problem right now."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-075
    E("EVT-075", "routine_baseline", "leave_policy_query_answered_per_policy", "2026-08-28",
      ["Bhavana Shetty", "Ayesha Khan", "Rohit Sinha"], "People Operations",
      system="Darwinbox HRMS", policy="Leave & Time-Off Policy",
      summary="Bhavana Shetty asked how many privilege-leave days carry forward and how much notice a 5-day leave needs. HR Ops answered "
              "from the Leave & Time-Off Policy v4 (12 days carry forward; notice of twice the duration; Department Head for >10 days) and "
              "Darwinbox enforced the same rules. No gap between policy and practice.",
      outcome="resolved", drift=False, tags=["baseline", "leave", "hr", "policy-consistent", "demo"],
      demo={"query": "How many leave days can I carry forward to next year?", "expected_drift": False},
      tickets=[
          T("HR query: PL carry-forward and notice period for a 5-day leave in October",
            "I have 19 days of PL. How many carry forward to next April, and how much notice do I need to give for 5 days off around "
            "Diwali? Also does Rohit or someone higher need to approve?",
            "Per the Leave & Time-Off Policy (v4, April 2026): up to 12 PL days carry forward to the next financial year; the balance above "
            "12 lapses on 31 March (so plan to use at least 7 days before then). Notice: at least twice the duration - 10 working days for a "
            "5-day leave. Approval: line manager (Rohit Sinha); Department Head approval is only needed above 10 consecutive working days. "
            "Apply in Darwinbox. Closed.",
            "Bhavana Shetty", "Ayesha Khan", "2026-08-28", resolved="2026-08-28", group="HR Ops", category="hr-query"),
      ],
      emails=[
          M("RE: Leave carry-forward question",
            [("Ayesha Khan", "Bhavana Shetty", "2026-08-28T14:20",
              "Hi Bhavana,\n\nShort version: 12 days carry forward, anything above lapses on 31 March; give 10 working days' notice for 5 "
              "days off; Rohit approves (Department Head only above 10 days). Darwinbox will apply the same rules when you submit. Full "
              "details are in the Leave & Time-Off Policy on the HR space.\n\nAyesha"),
             ("Bhavana Shetty", "Ayesha Khan", "2026-08-28T14:30", "Perfect, thank you - applying now.\n\nBhavana")]),
      ]),

    # ------------------------------------------------------------------ EVT-076
    E("EVT-076", "routine_baseline", "contractor_offboarding_on_expiry", "2026-03-12",
      ["Kavya Reddy", "Rohit Sinha", "Nikhil Bhatt"], "Identity & Access Management",
      system="Okta SSO", policy="Employee Offboarding & Access Revocation SOP",
      summary="A recruitment-agency contractor's engagement ended on 12-Mar; the sponsor (Rohit Sinha) gave notice, and IAM disabled the "
              "ext- account at 18:00 on the last day, removed Greenhouse and Slack access the next morning and transferred nothing (no "
              "owned resources). Offboarding SOP followed to the letter.",
      outcome="resolved", drift=False, related_events=["EVT-005"], tags=["baseline", "offboarding", "contractor", "policy-consistent"],
      tickets=[
          T("Contractor offboarding: ext-meera.d (TalentBridge agency recruiter) - end of engagement 12-Mar",
            "Sponsor notice: the TalentBridge contract recruiter's engagement ends 12-Mar. Please disable ext-meera.d and remove Greenhouse "
            "and Slack access. No owned resources or approvals.",
            "Okta account ext-meera.d disabled 12-Mar 18:00; Greenhouse seat removed and Slack deactivated 13-Mar 09:15. Sponsor confirmed "
            "no documents or approvals to transfer. Account scheduled for deletion 12-Apr. Closed.",
            "Rohit Sinha", "Kavya Reddy", "2026-03-10", resolved="2026-03-13", group="IAM", category="offboarding",
            on_behalf_of=None),
      ],
      emails=[
          M("Contractor offboarding complete - TalentBridge recruiter",
            [("Kavya Reddy", "Rohit Sinha", "2026-03-13T09:30",
              "Hi Rohit,\n\nDone - account disabled at 6pm yesterday, Greenhouse and Slack removed this morning. It'll be deleted in 30 days. "
              "Thanks for the advance notice, it makes this easy.\n\nKavya"),
             ("Rohit Sinha", "Kavya Reddy", "2026-03-13T09:40", "Thanks Kavya.\n\nRohit")]),
      ]),

    # ------------------------------------------------------------------ EVT-077
    E("EVT-077", "routine_baseline", "sev3_incident_handled_per_sop", "2026-06-26",
      ["Sonal Mehra", "Manish Tiwari", "Suresh Pillai"], "Data & Analytics Engineering",
      system="Metabase BI", policy="Incident Management & Severity Classification SOP",
      summary="Metabase sales dashboards loading slowly for Sales Ops after the warehouse restructure. Classified Sev3 (internal tool "
              "degraded for one team, workaround exists), picked up next business day, fixed by re-pointing the collection to the right "
              "warehouse. Handled and documented per the Incident Management SOP; no postmortem required for Sev3.",
      outcome="resolved", drift=False, related_events=["EVT-044"], tags=["baseline", "incident", "sev3", "policy-consistent"],
      tickets=[
          T("Metabase sales dashboards slow (30-60s) since Tuesday - Sales Ops",
            "The pipeline and forecast dashboards take 30-60 seconds to load since Tuesday; they used to be ~5s. Not blocking (we can wait) "
            "but the Friday pipeline review is painful.",
            "Classified Sev3 per SOP (internal tool degraded for one team, workaround exists) - next business day response. Cause: the "
            "'Sales' Metabase collection was still pointed at WH_MKT (XS) after the 23-Jun restructure instead of WH_SALES (S). Re-pointed "
            "26-Jun 10:30; load times back to ~5s. No postmortem required for Sev3; noted in the cost project log.",
            "Sonal Mehra", "Manish Tiwari", "2026-06-25", resolved="2026-06-26", group="Data Engineering", kind="incident",
            category="performance", priority="P3"),
      ],
      slack=[
          S("#eng-data", [
              ("Sonal Mehra", "2026-06-25T16:40", "Sales dashboards in Metabase have been really slow since Tuesday - 30-60s. Not urgent but flagging."),
              ("Manish Tiwari", "2026-06-25T16:50", "Thanks - that's a Sev3, I'll pick it up first thing tomorrow. Probably a collection still on the XS warehouse."),
              ("Manish Tiwari", "2026-06-26T10:35", "Fixed - Sales collection was on WH_MKT, moved to WH_SALES. Should be ~5s again."),
              ("Sonal Mehra", "2026-06-26T10:40", "Confirmed, thanks!"),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-078
    E("EVT-078", "routine_baseline", "small_saas_purchase_per_policy", "2026-02-17",
      ["Omar Farooq", "Ankit Chawla", "Kavita Bhatnagar", "Kritika Jain", "Amit Saxena"], "Accounts Payable & Procurement",
      system="NetSuite ERP", policy="Software Procurement & SaaS Approval Policy",
      summary="Marketing bought 5 Figma Professional seats (Rs 1.8 lakh/year): under Rs 5 lakh, so Department Head approval, a Security "
              "review (SSO supported) and a Procurement PO - no competitive quotes required. Processed in 5 business days exactly as the "
              "SaaS Approval and Purchase Order policies describe.",
      outcome="resolved", drift=False, related_events=["EVT-062"], tags=["baseline", "procurement", "saas", "policy-consistent", "demo"],
      demo={"query": "What approvals do I need to buy a new SaaS tool under 5 lakh?", "expected_drift": False},
      tickets=[
          T("Purchase request: Figma Professional x5 seats (annual, Rs 1,80,000) - Content & Brand",
            "Requesting 5 Figma Professional seats for the design team (Omar, Nikita, two Pixelcraft designers via SSO, one for Ishita). "
            "Annual Rs 1,80,000 (quote attached). Figma supports SAML SSO via Okta. Business owner: Ankit Chawla. Budget: Marketing tools line.",
            "Value in the Rs 1-5 lakh band: Department Head (Kavita Bhatnagar, approved 18-Feb) + Security review (Amit Saxena 19-Feb: SAML "
            "SSO enforced, SOC 2 report on file, no customer data) + Procurement. Vendor already onboarded (existing Figma account). PO "
            "KT-PO-26-0214 raised 23-Feb; seats provisioned 24-Feb; renewal date recorded in NetSuite. Closed.",
            "Omar Farooq", "Kritika Jain", "2026-02-17", resolved="2026-02-24", group="Procurement", category="purchase-request",
            approvers=["Kavita Bhatnagar", "Amit Saxena"]),
      ],
      emails=[
          M("Figma seats - approved and ordered",
            [("Kritika Jain", ["Omar Farooq", "Ankit Chawla"], "2026-02-23T16:05",
              "Hi Omar, Ankit,\n\nFigma PO is raised (KT-PO-26-0214). Kavita approved, Amit's security review is on the ticket, and since "
              "it's under 5 lakh we didn't need additional quotes. Seats should be active tomorrow; Kavya will put Figma behind Okta.\n\nKritika"),
             ("Omar Farooq", ["Kritika Jain", "Ankit Chawla"], "2026-02-24T10:15", "Seats are live and SSO works. Thanks Kritika!\n\nOmar")]),
      ]),

    # ------------------------------------------------------------------ EVT-079
    E("EVT-079", "routine_baseline", "ld_claim_with_preapproval_within_cap", "2026-09-03",
      ["Leela Krishnan", "Madhavi Srinivasan", "Tarun Bhargava"], "Learning & Development",
      system="LearnHub LMS", policy="Learning & Development Reimbursement Policy",
      summary="Leela Krishnan pre-approved a Rs 12,000 instructional-design course in LearnHub in July (manager + L&D), completed it, and "
              "claimed within 30 days with certificate and invoice. Approved next day. Within the cap and process under both the written "
              "policy and current practice - no drift either way.",
      outcome="resolved", drift=False, related_events=["EVT-061"], tags=["baseline", "learning", "policy-consistent"],
      tickets=[
          T("L&D reimbursement - Advanced Instructional Design certificate (Rs 12,000) - Leela Krishnan",
            "Claiming Rs 12,000 for the Advanced Instructional Design course (completed 28-Aug). Pre-approval LH-REQ-0412 approved by "
            "Madhavi and L&D on 6-Jul. Invoice and certificate attached in Zoho.",
            "Pre-approval on file (LH-REQ-0412), claim within 30 days of completion, certificate attached, within annual cap. Approved by "
            "Tarun Bhargava 04-Sep; reimbursement in September payroll. Closed.",
            "Leela Krishnan", "Tarun Bhargava", "2026-09-03", resolved="2026-09-04", group="L&D", category="learning",
            approvers=["Madhavi Srinivasan", "Tarun Bhargava"]),
      ],
      emails=[
          M("RE: Instructional design course - claim approved",
            [("Tarun Bhargava", "Leela Krishnan", "2026-09-04T10:20",
              "Approved - pre-approval, certificate and invoice all in order. It'll be in September payroll. Nice one on the distinction.\n\nTarun"),
             ("Leela Krishnan", "Tarun Bhargava", "2026-09-04T10:25", "Thanks Tarun!\n\nLeela")]),
      ]),

    # ------------------------------------------------------------------ EVT-080
    E("EVT-080", "routine_baseline", "discount_within_sales_manager_authority", "2026-05-13",
      ["Aakash Bhatia", "Natasha D'Souza", "Arun Prasad"], "Sales Operations & Deal Desk",
      system="Salesforce CRM", policy="Discount Approval Matrix", project="Salesforce CPQ Implementation",
      summary="Aakash Bhatia requested a 15% discount for a mid-market renewal. Under both the published Discount Approval Matrix and the "
              "CPQ configuration, 10-20% is the Sales Manager's call; Natasha D'Souza approved in CPQ and on the Deal Desk ticket the same "
              "afternoon. No policy question arises at this discount level.",
      outcome="resolved", drift=False, related_events=["EVT-057"], tags=["baseline", "discount", "deal-desk", "policy-consistent", "demo"],
      demo={"query": "Who approves a 15% discount?", "expected_drift": False},
      tickets=[
          T("Deal Desk: 15% discount - Nimbus Couriers renewal (1-year, 120 vehicles)",
            "15% renewal discount for Nimbus Couriers (1-year, 120 vehicles) to match last year's effective rate. Opportunity SF-00867.",
            "10.01-20% band: Sales Manager approval. Natasha D'Souza approved in CPQ and on this ticket 13-May 15:20. Quote sent 13-May; "
            "Chargebee renewal updated from the approved quote. Closed.",
            "Aakash Bhatia", "Arun Prasad", "2026-05-13", resolved="2026-05-13", group="Deal Desk", category="deal-desk",
            approvers=["Natasha D'Souza"]),
      ],
      slack=[
          S("#deal-desk", [
              ("Aakash Bhatia", "2026-05-13T14:50", "Nimbus renewal at 15% is in CPQ - @Natasha it's yours to approve."),
              ("Natasha D'Souza", "2026-05-13T15:21", "Approved."),
              ("Arun Prasad", "2026-05-13T15:30", "Ticket closed, quote's out."),
          ]),
      ]),
]
