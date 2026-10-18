"""Layer 6/7 - Access & onboarding events EVT-011..EVT-020 (with derived artifacts)."""
from events.dsl import E, T, M, S, D

EVENTS = [
    # ------------------------------------------------------------------ EVT-011
    E("EVT-011", "access_request", "new_joiner_onboarding_bundle_licence_shortfall", "2026-09-01",
      ["Tara Sequeira", "Anita Desai", "Rahul Kapoor", "Rakesh Nair", "Anjali Gupta", "Kavya Reddy", "Kritika Jain", "Rohan Mehta"],
      "Customer Success & Support", system="Zendesk Support Desk", policy="Software Procurement & SaaS Approval Policy",
      summary="Tara Sequeira (Support Engineer, Pune) joined 1-Sep-2026. Default bundle and laptop were ready, but no Zendesk agent seat "
              "was free: Anita Desai raised a purchase request for two seats (Rs 1.2L/yr -> Department Head + Procurement), Rahul Kapoor "
              "approved, Kritika Jain processed, and the seat was added on 7-Sep. Tara worked as a light agent meanwhile. Admin Console "
              "read-only followed the training gate and was granted on 4-Sep.",
      outcome="resolved", drift=False, tags=["onboarding", "new-joiner", "licence", "procurement"],
      tickets=[
          T("Onboarding: Tara Sequeira - Support Engineer, Customer Success (start 01-Sep-2026, Pune)",
            "Auto-created from Darwinbox pre-boarding workflow.\nNew joiner: Tara Sequeira\nRole: Support Engineer\nTeam: Customer Success & "
            "Support (manager: Anita Desai)\nLocation: Pune\nStart date: 2026-09-01\nDefault bundle + role bundle CS-SUPPORT. Laptop: "
            "ThinkPad T14 (Pune stock).",
            "Okta/M365/Slack/Confluence/Darwinbox/Zoho/LearnHub provisioned 31-Aug. ThinkPad KT-LT-0419 handed over in Pune office 01-Sep "
            "10:00. Role bundle CS-SUPPORT applied (Zendesk light agent, Jira SUP project, Confluence CS space). Full Zendesk agent seat and "
            "Admin Console are separate requests (licence / privileged).",
            "Rakesh Nair", "Anjali Gupta", "2026-08-18", resolved="2026-09-01", group="IT Service Desk", category="onboarding",
            on_behalf_of="Tara Sequeira"),
          T("Zendesk full agent seat - Tara Sequeira",
            "Tara Sequeira starts as Support Engineer today and needs a full Zendesk agent seat (Tier 1 queue) - light agent isn't enough to "
            "reply to customers. Manager approval: Anita Desai.",
            "01-Sep: 0 of 40 agent seats free (Tier 1 backfill in July used the last one). Ticket ON HOLD pending purchase request "
            "{{ticket:EVT-011#3}}. 07-Sep: 2 additional seats provisioned by Zendesk; added Tara to Okta group zendesk-agents and Anita "
            "assigned the Tier 1 agent role. Light-agent access removed.",
            "Anita Desai", "Kavya Reddy", "2026-09-01", resolved="2026-09-07", group="IAM", approvers=["Anita Desai"],
            on_behalf_of="Tara Sequeira"),
          T("Purchase request: 2 x Zendesk Suite agent seats (annual)",
            "Requesting 2 additional Zendesk Suite Professional agent seats: one for new Support Engineer Tara Sequeira (started today) and "
            "one buffer for the Q4 support hire. Cost: Rs 60,000/seat/yr = Rs 1,20,000/yr (quote from Zendesk attached; existing contract, "
            "co-termed to March renewal). Budget: Customer Success SaaS line.",
            "Rs 1,20,000 falls in the Department Head + Procurement band (SaaS policy 2 / PO policy 2). Approved by Rahul Kapoor (VP Sales) "
            "02-Sep. No new security review needed (existing vendor, same scope). PO KT-PO-26-0871 raised in NetSuite 04-Sep; Zendesk "
            "order form countersigned 05-Sep; seats live 07-Sep. Renewal date recorded.",
            "Anita Desai", "Kritika Jain", "2026-09-01", resolved="2026-09-05", group="Procurement", kind="request",
            category="purchase-request", approvers=["Rahul Kapoor", "Shalini Menon"]),
          T("AlgoWorks Admin Console read-only - Tara Sequeira (Support Engineer)",
            "New Support Engineer Tara Sequeira needs console-readonly for tenant diagnosis (Tier 1). She will complete 'Handling Customer "
            "Data' this week. Manager approval: Anita Desai.",
            "Training completion verified in LearnHub 03-Sep. Approvals: Anita Desai 01-Sep, Rohan Mehta (Platform EM) 04-Sep. Added to "
            "console-readonly 04-Sep.",
            "Anita Desai", "Kavya Reddy", "2026-09-01", resolved="2026-09-04", group="IAM", approvers=["Anita Desai", "Rohan Mehta"],
            on_behalf_of="Tara Sequeira", sensitivity="restricted"),
      ],
      emails=[
          M("Approval needed: 2 Zendesk agent seats (Rs 1.2L/yr)",
            [("Anita Desai", "Rahul Kapoor", "2026-09-01T12:30",
              "Rahul - we're out of Zendesk agent seats and Tara (new Support Engineer, started today) can't reply to customers on a light "
              "seat. I've raised a purchase request for two seats (Rs 1,20,000/yr, co-termed). It needs your approval as Department Head; "
              "Procurement will handle the PO. Budget is in the CS SaaS line.\n\nAnita"),
             ("Rahul Kapoor", "Anita Desai", "2026-09-02T08:15",
              "Approved on the ticket. Let's also make sure the FY27 plan has seats for the two Q4 hires so we're not doing this per person.\n\nRahul"),
             ("Anita Desai", "Rahul Kapoor", "2026-09-02T08:40", "Will do - I'll add it to the AOP headcount sheet. Thanks.\n\nAnita")]),
      ],
      slack=[
          S("#customer-success", [
              ("Anita Desai", "2026-09-01T09:30", "Welcome Tara Sequeira, joining us in Pune as Support Engineer! Tara will shadow Preeti on Tier 1 this week."),
              ("Preeti Nambiar", "2026-09-01T09:32", "Welcome Tara!"),
              ("Tara Sequeira", "2026-09-01T10:15", "Thanks all! Small thing - Zendesk lets me view tickets but not reply. Is that expected?"),
              ("Anita Desai", "2026-09-01T10:20", "That's the light-agent seat from the role bundle. We're out of full seats - purchase request is in, should be a few days. Draft replies in a private comment and Preeti will send them for now."),
              ("Kavya Reddy", "2026-09-07T11:05", "@Tara full agent seat is live now."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-012
    E("EVT-012", "access_request", "restricted_billing_read_access", "2026-01-22",
      ["Simran Kaur", "Natasha D'Souza", "Deepa Subramanian", "Anusha Rao"], "Enterprise Sales",
      system="Chargebee Billing", policy="Application Access Request Policy",
      summary="Simran Kaur (Enterprise AE) requested Chargebee access to see invoice status for her accounts before renewal calls. Chargebee "
              "is Finance-restricted; the 'Invoice Viewer (read-only)' role needs Payroll & Compliance Manager approval. Granted after a "
              "scope clarification (the role is global read, not per-account).",
      outcome="resolved", drift=False, tags=["restricted", "billing", "sales", "policy-consistent"],
      tickets=[
          T("Chargebee read-only (Invoice Viewer) - Simran Kaur (Enterprise AE)",
            "Before renewal calls I need to see whether my accounts have overdue invoices - currently I email Anusha each time. Requesting "
            "read-only Chargebee access for my 11 accounts. Manager: Natasha D'Souza.",
            "Chargebee is restricted to Finance by default; 'Invoice Viewer (read-only)' role requires Payroll & Compliance Manager approval "
            "(system access summary). Deepa Subramanian clarified the role is global read (all customers) and approved 26-Jan after Simran "
            "acknowledged the Data Classification handling rules. Anusha Rao assigned the role 27-Jan. Natasha approval 22-Jan.",
            "Simran Kaur", "Anusha Rao", "2026-01-22", resolved="2026-01-27", group="Finance Systems",
            approvers=["Natasha D'Souza", "Deepa Subramanian"], sensitivity="restricted"),
      ],
      emails=[
          M("RE: Chargebee read access - scope",
            [("Deepa Subramanian", ["Simran Kaur", "Natasha D'Souza"], "2026-01-23T10:40",
              "Hi Simran,\n\nHappy to approve, one clarification first: Chargebee doesn't let us scope a viewer to 'your' accounts - the "
              "Invoice Viewer role sees invoices and payment status for all customers. It doesn't show card details or payroll data. If "
              "that's acceptable, please reply confirming you've read the Data Classification standard (customer billing = Restricted, no "
              "exports outside Finance without approval) and I'll approve.\n\nDeepa"),
             ("Simran Kaur", ["Deepa Subramanian", "Natasha D'Souza"], "2026-01-26T09:15",
              "Understood and confirmed - I only need to look up status before calls, no exports. Thanks Deepa.\n\nSimran"),
             ("Deepa Subramanian", ["Simran Kaur", "Natasha D'Souza"], "2026-01-26T09:50", "Approved on the ticket; Anusha will set it up.\n\nDeepa")],
            sensitivity="restricted"),
      ]),

    # ------------------------------------------------------------------ EVT-013
    E("EVT-013", "access_request", "shared_mailbox_and_queue_membership", "2026-07-08",
      ["Preeti Nambiar", "Anita Desai", "Deepak Verma", "Kavya Reddy"], "Customer Success & Support",
      system="Microsoft 365", policy="Application Access Request Policy",
      summary="Preeti Nambiar moved up to Tier 2 and needed the support@ shared mailbox and the Zendesk Tier 2 group. Two straightforward "
              "requests approved by Anita Desai and fulfilled by the Service Desk and IAM the next day.",
      outcome="resolved", drift=False, tags=["shared-mailbox", "zendesk", "policy-consistent"],
      tickets=[
          T("Shared mailbox access: support@algoworks.io - Preeti Nambiar",
            "I've moved to Tier 2 and need Send-As and Full Access on the support@ shared mailbox to handle escalations that come in by "
            "email. Manager approval: Anita Desai.",
            "Anita approved 08-Jul. Added Full Access + Send As on support@ shared mailbox in Exchange Online 09-Jul; mailbox auto-mapped "
            "in Outlook within an hour.",
            "Preeti Nambiar", "Deepak Verma", "2026-07-08", resolved="2026-07-09", group="IT Service Desk", approvers=["Anita Desai"]),
          T("Zendesk group membership: Tier 2 Escalations - Preeti Nambiar",
            "Please add me to the Zendesk 'Tier 2 - Escalations' group and the SUP Jira project as an assignee, following my move to Tier 2. "
            "Manager: Anita Desai.",
            "Added to Okta group zendesk-tier2 (maps to the Zendesk group) and jira-sup-assignees on 09-Jul. Anita's approval on ticket.",
            "Preeti Nambiar", "Kavya Reddy", "2026-07-08", resolved="2026-07-09", group="IAM", approvers=["Anita Desai"]),
      ],
      slack=[
          S("#customer-success", [
              ("Anita Desai", "2026-07-08T09:45", "Team - Preeti is officially Tier 2 from this week :tada: Please route escalations to her and Sameer."),
              ("Preeti Nambiar", "2026-07-08T09:50", "Thanks Anita! I've raised the tickets for the support@ mailbox and the Tier 2 Zendesk group."),
              ("Kunal Shah", "2026-07-08T09:52", "Congrats Preeti!"),
              ("Preeti Nambiar", "2026-07-09T14:30", "Both done - mailbox appeared in Outlook and I can see the Tier 2 view."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-014
    E("EVT-014", "access_request", "non_engineering_github_seat", "2026-02-11",
      ["Omar Farooq", "Ankit Chawla", "Rohan Mehta", "Kavya Reddy"], "Content & Brand",
      system="GitHub Enterprise", policy="Application Access Request Policy",
      summary="Omar Farooq (Brand Designer) needed GitHub access to maintain the brand-assets repository used by the product UI. "
              "Non-engineering GitHub access needs an Engineering Manager's approval and a paid seat; Rohan Mehta approved write on the "
              "single repo, IAM confirmed seat availability (2 left) and granted it.",
      outcome="resolved", drift=False, tags=["github", "cross-department", "licence"],
      tickets=[
          T("GitHub access (algoworks-brand-assets repo) - Omar Farooq (Brand Designer)",
            "The product UI pulls logos/icons from the algoworks-brand-assets repo. Currently I send files to Aditya who commits them. "
            "Requesting write access to that single repo so I can open PRs myself. Manager: Ankit Chawla.",
            "Non-engineering GitHub access requires an Engineering Manager approval and a paid seat (access summary). Ankit Chawla approved "
            "11-Feb; Rohan Mehta approved 12-Feb for write on algoworks-brand-assets only (via GitHub team brand-contributors). Seat count "
            "checked: 118/120 used. Added Omar to Okta group github-external-collab 13-Feb. Branch protection on main still requires a "
            "Frontend CODEOWNER review.",
            "Omar Farooq", "Kavya Reddy", "2026-02-11", resolved="2026-02-13", group="IAM", approvers=["Ankit Chawla", "Rohan Mehta"]),
      ],
      emails=[
          M("GitHub seats - non-engineering users",
            [("Kavya Reddy", "Rohan Mehta", "2026-02-12T11:20",
              "Rohan - with Omar we'll be at 119 of 120 GitHub seats. Three more designers/writers have asked informally. Do you want to "
              "keep approving these case by case or should we ask Procurement for a 10-seat top-up at the April renewal?\n\nKavya"),
             ("Rohan Mehta", "Kavya Reddy", "2026-02-12T13:05",
              "Case by case for now, but yes - put 10 seats in the renewal request; I'll back it. For designers, write on the assets repo only, "
              "and always via the brand-contributors team so we can review it in one place.\n\nRohan")]),
      ],
      slack=[
          S("#eng-platform", [
              ("Omar Farooq", "2026-02-11T15:40", "Hi! I've raised a request for GitHub access to algoworks-brand-assets so I can PR icon updates directly instead of sending zips to Aditya."),
              ("Aditya Rao", "2026-02-11T15:42", "Please yes :pray:"),
              ("Rohan Mehta", "2026-02-12T09:30", "Approved - write on that repo only. Aditya, add the CODEOWNERS entry so frontend reviews the PRs."),
              ("Omar Farooq", "2026-02-13T12:10", "I'm in, first PR is up. Thanks!"),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-015
    E("EVT-015", "access_request", "monitoring_viewer_for_tam", "2026-08-27",
      ["Sameer Khan", "Anita Desai", "Varun Chandra", "Nandini Rajan"], "Customer Success & Support",
      system="Datadog Monitoring", policy="Application Access Request Policy",
      summary="Sameer Khan (TAM) requested Datadog read-only to show customer-specific API latency dashboards in QBRs. Non-engineering "
              "viewer access needs the Cloud Infrastructure Lead; Anita and Varun approved and Nandini added the viewer group next day.",
      outcome="resolved", drift=False, tags=["monitoring", "cross-department", "policy-consistent"],
      tickets=[
          T("Datadog read-only (viewer) - Sameer Khan (TAM) - customer dashboards",
            "For enterprise QBRs I want to show the per-tenant API latency and uptime dashboards that Cloud built for the multi-region "
            "project rather than screenshots from Harish. Requesting Datadog viewer access. Manager: Anita Desai.",
            "Anita Desai approved 27-Aug; Varun Chandra (Cloud Infra Lead, required for non-engineering viewer access) approved 27-Aug. "
            "Added to Okta group datadog-viewer 28-Aug. Access limited to dashboards; no log access (customer PII in logs).",
            "Sameer Khan", "Nandini Rajan", "2026-08-27", resolved="2026-08-28", group="Cloud Infrastructure",
            approvers=["Anita Desai", "Varun Chandra"]),
      ],
      slack=[
          S("#devops-sre", [
              ("Sameer Khan", "2026-08-27T10:05", "Request raised for Datadog viewer so I can use the tenant latency dashboards in QBRs. @Varun it needs your approval."),
              ("Varun Chandra", "2026-08-27T10:30", "Approved. Viewer role only - the logs index has driver PII so that stays engineering-only."),
              ("Nandini Rajan", "2026-08-28T09:15", "@Sameer added to datadog-viewer. The 'Tenant SLO' dashboard is the one you want."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-016
    E("EVT-016", "access_request", "quarterly_access_review", "2026-06-30",
      ["Kavya Reddy", "Nikhil Bhatt", "Sandeep Malhotra", "Megha Patil", "Payal Shah", "Vinod Krishnamurthy"],
      "Identity & Access Management", system="Okta SSO", policy="Application Access Request Policy",
      summary="Q2 2026 quarterly access review run by Kavya Reddy. Findings: 14 Salesforce licences unused for 90+ days, 3 contractor "
              "accounts past expiry still enabled (created before the Contractor policy v2), 2 NetSuite full licences unused. Cleanup "
              "tickets raised to Sales Ops and Finance Systems; findings documented in Confluence.",
      outcome="resolved", drift=False, tags=["access-review", "licences", "governance"],
      tickets=[
          T("Q2 2026 access review - Salesforce: 14 licences with no login in 90+ days",
            "Per the Q2 access review (Okta + Salesforce login reports, cut-off 30-Jun), 14 Salesforce users have not logged in since "
            "before 1-Apr: 9 Marketing (HubSpot-only users who were given SF during the sync cleanup), 3 Finance, 2 former interns whose "
            "Okta is disabled but SF licence still assigned. Please confirm and release the licences. List attached (restricted).",
            "Megha Patil reviewed with Vinod: 12 licences released 08-Jul (2 Finance users confirmed they still need read access for "
            "collections work - kept, will re-check in Q3). Licence count now 71/85. Also fixed: interns' licences released - "
            "deprovisioning from Okta had not removed the SF licence because SF was assigned directly rather than via group.",
            "Kavya Reddy", "Megha Patil", "2026-06-30", resolved="2026-07-10", group="Sales Ops", category="access-review",
            sensitivity="restricted"),
          T("Q2 2026 access review - 3 expired contractor accounts still enabled",
            "ext-arjun.k (Pixelcraft, expired 15-May), ext-devika.m (Pixelcraft, expired 15-May) and ext-tarun.s (recruitment agency, "
            "expired 02-Jun) are past expiry but still enabled. These were created under the old process before the Contractor policy v2 "
            "auto-expiry was configured (June).",
            "All three disabled 01-Jul and sponsors informed; the Pixelcraft accounts were superseded by the new ext- accounts created in "
            "June ({{ticket:EVT-004#1}}). Okta expiry policy now applied retroactively to all ext- accounts (auto-disable).",
            "Kavya Reddy", "Kavya Reddy", "2026-06-30", resolved="2026-07-02", group="IAM", category="access-review"),
          T("Q2 2026 access review - NetSuite: 2 full-user licences with no login since March",
            "NetSuite login report shows two full-user licences unused since March: one Sales Ops analyst and one former Finance intern "
            "(Okta disabled). Given the licence shortage please confirm whether these can be released.",
            "Payal Shah: intern licence released 03-Jul. Sales Ops user (Sonal Mehra) contacted - initially wanted to keep it; released "
            "on 27-Aug when a new joiner needed one ({{ticket:EVT-006#2}}). Closed.",
            "Kavya Reddy", "Payal Shah", "2026-07-01", resolved="2026-08-27", group="Finance Systems", category="access-review"),
      ],
      emails=[
          M("Q2 2026 access review - summary and actions",
            [("Kavya Reddy", ["Nikhil Bhatt", "Sandeep Malhotra"], "2026-07-01T17:20",
              "Nikhil, Sandeep,\n\nQ2 review is done (Okta, Salesforce, NetSuite, Admin Console, AWS). Summary:\n- Salesforce: 14 stale "
              "licences -> ticket to Sales Ops.\n- Contractors: 3 accounts past expiry still enabled (pre-June process) -> disabled today; "
              "auto-expiry now applied to all ext- accounts.\n- NetSuite: 2 stale full licences -> ticket to Finance Systems.\n- Admin "
              "Console: 31 members of console-readonly; 4 with no login in 90 days -> Rohan removing.\n- AWS: no findings.\n\nOne process "
              "note: Salesforce licences assigned directly (not via Okta group) survive Okta deprovisioning. Megha and I will migrate the "
              "remaining direct assignments to groups in Q3.\n\nFull write-up on Confluence: Q2 2026 Quarterly Access Review.\n\nKavya"),
             ("Nikhil Bhatt", ["Kavya Reddy", "Sandeep Malhotra"], "2026-07-02T09:10",
              "Good work. Please add the direct-assignment migration to the Q3 plan and include the pii-reader membership in the Q3 review - "
              "that one hasn't been reviewed since Pradeep left.\n\nNikhil")]),
      ],
      docs=[
          D("Q2 2026 Quarterly Access Review - Findings and Actions",
            "**Review period:** 1 April - 30 June 2026 | **Performed by:** Kavya Reddy (IAM) | **Reviewed by:** Nikhil Bhatt\n\n"
            "## Scope\nOkta assignments, Salesforce, NetSuite, AlgoWorks Admin Console groups, AWS Identity Center, contractor (ext-) accounts.\n\n"
            "## Findings\n| Area | Finding | Action | Ticket |\n|---|---|---|---|\n"
            "| Salesforce | 14 users with no login for 90+ days (9 Marketing, 3 Finance, 2 ex-interns) | 12 licences released; 2 Finance kept pending Q3 | {{ticket:EVT-016#1}} |\n"
            "| Contractor accounts | 3 ext- accounts past expiry still enabled (created before policy v2 auto-expiry) | Disabled; auto-expiry applied to all ext- accounts | {{ticket:EVT-016#2}} |\n"
            "| NetSuite | 2 full-user licences unused since March | 1 released; 1 released in August when reassigned to a new joiner | {{ticket:EVT-016#3}} |\n"
            "| Admin Console | 4 console-readonly members with no login in 90 days | Removed by Platform EM | - |\n"
            "| AWS Identity Center | No findings | - | - |\n\n"
            "## Process observations\n1. Salesforce licences assigned directly in Salesforce (rather than via Okta group) are not removed "
            "when the Okta account is deprovisioned. Migration of direct assignments to group-based assignment planned for Q3.\n"
            "2. The `snowflake-pii-reader` group has not been reviewed since the DPO left in February (the Snowflake Data Access Policy "
            "assigns that review to the DPO). Added to the Q3 scope; ownership question tracked in {{ticket:EVT-005#2}}.\n"
            "3. NetSuite licence pressure: FP&A to include 3 additional licences in the FY27 renewal.\n\n"
            "## Next review\nQ3 2026 review scheduled for the week of 28 September 2026.",
            doc_type="review_notes", space="IT", created="2026-07-01", authors=["Kavya Reddy"], sensitivity="restricted",
            references=["{{ticket:EVT-016#1}}", "{{ticket:EVT-016#2}}", "{{ticket:EVT-016#3}}", "{{ticket:EVT-005#2}}"],
            related_events=["EVT-005"], labels=["access-review", "iam", "q2-2026"]),
      ]),

    # ------------------------------------------------------------------ EVT-017
    E("EVT-017", "access_request", "new_joiner_onboarding_bundle_clean", "2026-09-15",
      ["Lavanya Bhat", "Sanya Kapadia", "Rakesh Nair", "Deepak Verma", "Aparna Das", "Megha Patil"], "Product Marketing",
      system="HubSpot Marketing Hub", policy="Employee Onboarding SOP", project="AlgoWorks Fleet v4 Launch Campaign",
      summary="Lavanya Bhat (Product Marketing Manager) joined 15-Sep-2026 - a clean onboarding. Default bundle and laptop ready Day 1; "
              "Sanya Kapadia raised HubSpot and Salesforce read-only on Day 1 and both were granted within a day.",
      outcome="resolved", drift=False, tags=["onboarding", "new-joiner", "marketing", "clean"],
      tickets=[
          T("Onboarding: Lavanya Bhat - Product Marketing Manager (start 15-Sep-2026)",
            "Auto-created from Darwinbox pre-boarding workflow.\nNew joiner: Lavanya Bhat\nRole: Product Marketing Manager\nTeam: Product "
            "Marketing (manager: Sanya Kapadia)\nLocation: Bengaluru\nStart date: 2026-09-15\nDefault bundle + role bundle MKT-PMM. "
            "Laptop: MacBook Air.",
            "Provisioned default bundle 14-Sep (holiday - automated). MacBook Air KT-LT-0427 handed over 15-Sep 09:30. Role bundle MKT-PMM "
            "applied (Confluence MKT space, Jira MKT project). Day-1 checklist signed by Sanya Kapadia.",
            "Rakesh Nair", "Deepak Verma", "2026-09-01", resolved="2026-09-15", group="IT Service Desk", category="onboarding",
            on_behalf_of="Lavanya Bhat"),
          T("HubSpot (Marketing Hub user) + Salesforce read-only - Lavanya Bhat",
            "New PMM Lavanya Bhat needs HubSpot (campaign and content permissions, no super-admin) for the v4 launch campaign and Salesforce "
            "read-only to see opportunity context for enablement. Manager approval: Sanya Kapadia.",
            "Sanya approved 15-Sep. Aparna Das added Lavanya to HubSpot with 'Marketing - Content & Campaigns' permission set 15-Sep. Megha "
            "Patil assigned Salesforce 'Read Only - Marketing' profile 16-Sep (licence available, 72/85).",
            "Sanya Kapadia", "Aparna Das", "2026-09-15", resolved="2026-09-16", group="Marketing Ops", approvers=["Sanya Kapadia"],
            on_behalf_of="Lavanya Bhat"),
      ],
      emails=[
          M("Welcome to Product Marketing!",
            [("Sanya Kapadia", "Lavanya Bhat", "2026-09-15T08:05",
              "Hi Lavanya,\n\nWelcome! Today: IT handover 9:30, HR induction 9:30-11 (yes, they overlap - IT will be quick), then lunch with "
              "the team at 12:30. I've requested HubSpot and Salesforce read-only for you; both should be through by tomorrow. Varsha will "
              "be your buddy and will walk you through the v4 launch plan - we're four weeks out from 6 October.\n\nSanya"),
             ("Lavanya Bhat", "Sanya Kapadia", "2026-09-16T10:20",
              "Thanks Sanya - HubSpot came through yesterday and Salesforce this morning. Reading the launch plan now.\n\nLavanya")]),
      ],
      slack=[
          S("#new-joiners", [
              ("Rakesh Nair", "2026-09-15T09:10", "Welcome Lavanya Bhat, joining Product Marketing today as PMM! :tada:"),
              ("Varsha Pai", "2026-09-15T09:12", "Welcome Lavanya! Buddy here :wave:"),
              ("Lavanya Bhat", "2026-09-15T09:45", "Thank you! Laptop's set up and everything worked first time, very smooth."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-018
    E("EVT-018", "access_request", "temporary_admin_elevation", "2026-04-28",
      ["Nisha Pandey", "Rohit Sinha"], "Talent Acquisition", system="Greenhouse ATS", policy="Application Access Request Policy",
      summary="Nisha Pandey needed temporary Greenhouse Site Admin for 30 days to configure the campus pipeline stages and scorecards. "
              "Rohit Sinha (TA Lead, Greenhouse admin) approved and granted with an end date; access reverted automatically on 28-May.",
      outcome="resolved", drift=False, tags=["temporary-access", "hr", "policy-consistent"],
      tickets=[
          T("Temporary Greenhouse Site Admin (30 days) - Nisha Pandey - campus pipeline configuration",
            "To close out the Campus Hiring Drive I need to restructure the campus job pipelines (new stages, scorecards, offer approval "
            "chain). This needs Site Admin in Greenhouse. Requesting 30 days, after which I'm happy to drop back to Recruiter. Manager: "
            "Rohit Sinha.",
            "Rohit Sinha (manager + Greenhouse Site Admin owner) approved 28-Apr. Elevated to Site Admin 28-Apr with end date 28-May on the "
            "ticket. 28-May: reverted to 'Recruiter' role as scheduled; Nisha confirmed configuration complete.",
            "Nisha Pandey", "Rohit Sinha", "2026-04-28", resolved="2026-05-28", group="HR Systems", approvers=["Rohit Sinha"]),
      ],
      emails=[
          M("Greenhouse Site Admin - temporary",
            [("Rohit Sinha", "Nisha Pandey", "2026-04-28T14:10",
              "Nisha - done, you're Site Admin until 28 May (ticket has the end date so IAM will nudge me). Please don't change the offer "
              "approval chain for non-campus jobs; Sunita signed that off separately.\n\nRohit"),
             ("Nisha Pandey", "Rohit Sinha", "2026-04-28T14:25", "Understood - campus jobs only. Thanks!\n\nNisha")]),
      ]),

    # ------------------------------------------------------------------ EVT-019
    E("EVT-019", "access_request", "raw_data_access_denied_alternative_provided", "2026-03-05",
      ["Yash Agrawal", "Manoj Venkatesh", "Suresh Pillai", "Manish Tiwari"], "Demand Generation",
      system="Snowflake Data Warehouse", policy="Snowflake Data Access Policy",
      summary="Yash Agrawal (Performance Marketing) asked for direct Snowflake access to raw product event tables for attribution analysis. "
              "Suresh Pillai declined raw access per the Snowflake policy (native SQL for non-engineering teams discouraged; raw schemas "
              "engineering-only) and had Manish Tiwari build a curated 'Marketing Attribution' Metabase collection instead, delivered in a week.",
      outcome="denied_with_alternative", drift=False, tags=["data-access", "denied", "policy-consistent", "alternative"],
      tickets=[
          T("Snowflake access to RAW.PRODUCT_EVENTS - Yash Agrawal (Performance Marketing)",
            "I want to join ad-click data with product sign-up and first-trip events to work out true CAC by channel. Requesting read access "
            "to RAW.PRODUCT_EVENTS and RAW.SIGNUPS in Snowflake plus a SQL client. Manager: Manoj Venkatesh (approved).",
            "Declined for raw schema access - RAW.* is engineering-only and RAW.SIGNUPS carries PII (Snowflake Data Access Policy 1 and "
            "2.3). Alternative agreed with Yash and Manoj: Data Engineering built the curated mart MARKETING_MART.ATTRIBUTION (channel, "
            "campaign, signup_date, first_trip_date, hashed account id) and a Metabase collection 'Marketing Attribution' with SQL access on "
            "that mart only. Delivered 12-Mar (Jira DATA-1121). Yash added to metabase-sql and snowflake-analyst (MARKETING_MART only).",
            "Yash Agrawal", "Suresh Pillai", "2026-03-05", resolved="2026-03-12", status="closed", group="Data Engineering",
            approvers=["Manoj Venkatesh"]),
      ],
      emails=[
          M("RE: Snowflake raw access request - alternative",
            [("Suresh Pillai", ["Yash Agrawal", "Manoj Venkatesh"], "2026-03-05T16:30",
              "Hi Yash, Manoj,\n\nI can't grant raw access here - RAW.* is limited to engineering roles and RAW.SIGNUPS has email and phone "
              "columns, which would need a PII sign-off we currently can't get. But the question is a good one and we should answer it "
              "properly. Proposal: Manish builds an attribution mart (channel, campaign, signup and first-trip dates, hashed account id) and "
              "exposes it in Metabase with SQL enabled for you. Should take about a week. OK?\n\nSuresh"),
             ("Manoj Venkatesh", ["Suresh Pillai", "Yash Agrawal"], "2026-03-05T17:05",
              "Works for us - as long as Yash can write his own SQL against it. Thanks Suresh.\n\nManoj"),
             ("Manish Tiwari", ["Yash Agrawal", "Suresh Pillai", "Manoj Venkatesh"], "2026-03-12T11:40",
              "MARKETING_MART.ATTRIBUTION is live and refreshed hourly; Metabase collection 'Marketing Attribution' is shared with Demand "
              "Gen. Column notes are on the Confluence page. Yash, you have SQL on that mart.\n\nManish")]),
      ],
      slack=[
          S("#eng-data", [
              ("Yash Agrawal", "2026-03-05T14:20", "Raised a request for raw Snowflake access for attribution work - hope that's the right place?"),
              ("Suresh Pillai", "2026-03-05T14:35", "Right place, but raw won't fly - replying on the ticket with an alternative. Short version: we'll build you a curated mart."),
              ("Manish Tiwari", "2026-03-12T11:45", "@Yash your attribution mart + Metabase collection are live."),
              ("Yash Agrawal", "2026-03-12T12:02", "This is actually better than what I asked for, thanks both."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-020
    E("EVT-020", "access_request", "shared_vault_after_credential_in_slack", "2026-05-06",
      ["Aakash Bhatia", "Amit Saxena", "Natasha D'Souza", "Kavya Reddy"], "Enterprise Sales",
      system="1Password Business", policy="Password & MFA Standard",
      summary="Aakash Bhatia posted the demo-tenant admin password in #sales-team. Amit Saxena rotated it within the hour per the Password "
              "& MFA Standard, and Natasha D'Souza requested a shared 1Password vault 'Sales-Demo' which IAM created the next day. "
              "Policy applied as written.",
      outcome="resolved", drift=False, tags=["security", "credentials", "policy-consistent"],
      tickets=[
          T("Shared 1Password vault 'Sales-Demo' for Enterprise Sales demo credentials",
            "Following today's incident where a demo tenant password was posted in Slack, please create a shared vault 'Sales-Demo' for the "
            "Enterprise Sales team holding the demo tenant admin, the demo driver app logins and the sandbox Chargebee portal. Owner: "
            "Natasha D'Souza. Members: Enterprise Sales team + Sales Ops (Megha, Arun).",
            "Vault 'Sales-Demo' created 07-May, owner Natasha D'Souza, members per request (10 users). Rotated demo tenant credentials "
            "stored by Amit Saxena. Slack message deleted by the author; reminder on the Password & MFA Standard posted in #sales-team.",
            "Natasha D'Souza", "Kavya Reddy", "2026-05-06", resolved="2026-05-07", group="IAM", category="secrets",
            approvers=["Natasha D'Souza"]),
      ],
      slack=[
          S("#sales-team", [
              ("Aakash Bhatia", "2026-05-06T11:02", "Anyone doing a demo today - the demo tenant admin login is demo-admin / AlgoWorks#Demo2026 (changed it yesterday)"),
              ("Amit Saxena", "2026-05-06T11:15", "@Aakash please delete that message right now - credentials never go in Slack (Password & MFA Standard 1.4). I'm rotating the demo admin password; it'll be in a 1Password shared vault within the hour."),
              ("Aakash Bhatia", "2026-05-06T11:16", "sorry! deleted"),
              ("Natasha D'Souza", "2026-05-06T11:25", "My fault for not setting up a vault when we got the demo tenant. Raising the request for a 'Sales-Demo' vault now - everyone will get access via 1Password, please stop keeping these in notes/Slack."),
              ("Amit Saxena", "2026-05-06T12:05", "Rotated. New credential is with Natasha until the vault exists."),
              ("Kavya Reddy", "2026-05-07T10:30", "Vault 'Sales-Demo' is live - everyone on the Enterprise Sales and Sales Ops lists should see it in 1Password now."),
          ]),
      ]),
]
