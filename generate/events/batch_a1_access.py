"""Layer 6/7 - Access & onboarding events EVT-001..EVT-010 (with derived artifacts)."""
from events.dsl import E, T, M, S, D

EVENTS = [
    # ------------------------------------------------------------------ EVT-001
    E("EVT-001", "access_request", "new_joiner_onboarding_bundle", "2026-08-03",
      ["Tanvi Deshpande", "Rohan Mehta", "Rakesh Nair", "Deepak Verma", "Kavya Reddy", "Nandini Rajan", "Varun Chandra"],
      "Platform Backend", system="GitHub Enterprise", policy="Employee Onboarding SOP", project="AlgoWorks Fleet v4 API Platform Migration",
      summary="New joiner Tanvi Deshpande (Software Engineer, Platform Backend) onboarded on 2026-08-03. Darwinbox auto-created the "
              "onboarding ticket 10 business days ahead; default bundle and laptop were ready on Day 1. Rohan Mehta raised GitHub and "
              "AWS access on Day 1; GitHub was same-day, AWS read-only took 3 days because the Identity Center assignment waited for "
              "Varun Chandra's approval while he was at the Mumbai data-centre visit.",
      outcome="resolved", drift=False, tags=["onboarding", "new-joiner", "engineering"],
      tickets=[
          T("Onboarding: Tanvi Deshpande - Software Engineer, Platform Backend (start 03-Aug-2026)",
            "Auto-created from Darwinbox pre-boarding workflow.\nNew joiner: Tanvi Deshpande\nRole: Software Engineer\n"
            "Team: Platform Backend (manager: Rohan Mehta)\nLocation: Bengaluru\nStart date: 2026-08-03\n"
            "Default bundle required: Okta, Microsoft 365, Slack, Confluence, Darwinbox self-service, Zoho Expense, LearnHub.\n"
            "Laptop: MacBook Pro 14\" (Engineering standard). Role bundle: ENG-PLATFORM.",
            "Okta account created 31-Jul (Day -1) via Darwinbox sync; role bundle ENG-PLATFORM applied (Slack, Confluence, Jira, "
            "GitHub Okta group, Datadog read). MacBook Pro asset KT-LT-0412 enrolled in Intune and handed over 03-Aug 09:45. "
            "Induction completed with HR. Ticket closed after Day-1 checklist sign-off by Rohan Mehta.",
            "Rakesh Nair", "Deepak Verma", "2026-07-20", resolved="2026-08-03", group="IT Service Desk",
            category="onboarding", on_behalf_of="Tanvi Deshpande"),
          T("GitHub Enterprise access for Tanvi Deshpande (algoworks-platform repos)",
            "Please add Tanvi Deshpande (new SWE on my team, started today) to the GitHub org and to the platform-backend GitHub team so "
            "she can pick up the v4 migration tickets. She is already in the ENG-PLATFORM Okta bundle so the SSO side should be done.",
            "Confirmed Tanvi is in Okta group github-engineering (via role bundle). Added to GitHub team @algoworks-tech/platform-backend "
            "with write on algoworks-api-v4, algoworks-core and read on algoworks-deploy. Rohan Mehta approval recorded.",
            "Rohan Mehta", "Kavya Reddy", "2026-08-03", resolved="2026-08-03", group="IAM", approvers=["Rohan Mehta"]),
          T("AWS sandbox + production read-only access for Tanvi Deshpande",
            "Requesting AWS access for Tanvi Deshpande (Platform Backend): full developer access in the sandbox account and "
            "ProdReadOnly in the production account per the Production Access policy. Needed for v4 migration debugging.",
            "Sandbox: added to Identity Center group aws-sandbox-developers on 03-Aug. Production ProdReadOnly permission set requires "
            "Cloud Infrastructure Lead approval - Varun Chandra was at the Mumbai DC visit 03-05 Aug and approved on 06-Aug morning; "
            "assignment completed the same day. Note for future: approvals can be delegated to Harish Gowda when Varun is travelling.",
            "Rohan Mehta", "Nandini Rajan", "2026-08-03", resolved="2026-08-06", group="Cloud Infrastructure",
            approvers=["Rohan Mehta", "Varun Chandra"]),
      ],
      emails=[
          M("Welcome to Platform Backend - your first week",
            [("Rohan Mehta", "Tanvi Deshpande", "2026-08-03T08:12",
              "Hi Tanvi,\n\nWelcome to AlgoWorks! Your laptop and accounts should be ready when you get in - Deepak from IT will hand over the "
              "MacBook at 9:30 and HR induction runs until 11.\n\nA few things for week one:\n- I've raised your GitHub and AWS access; "
              "GitHub should land today, AWS may take a couple of days.\n- Priya is your onboarding buddy; she'll walk you through the "
              "v4 migration repo and our local dev setup.\n- Please complete the Security Awareness and Code of Conduct modules in LearnHub "
              "in the first two weeks.\n- Team sync is Tue/Thu 10:30 in Meeting Room Falcon.\n\nRohan"),
             ("Tanvi Deshpande", "Rohan Mehta", "2026-08-03T13:40",
              "Thanks Rohan! Laptop's set up and I'm in GitHub already. AWS console says no permission sets assigned yet - I'll wait. "
              "Priya has given me the v4 onboarding doc.\n\nTanvi"),
             ("Rohan Mehta", "Tanvi Deshpande", "2026-08-06T10:05",
              "AWS is sorted now - Varun approved this morning. You should see ProdReadOnly and the sandbox account in the access portal. "
              "Shout if not.\n\nRohan")]),
      ],
      slack=[
          S("#new-joiners", [
              ("Rakesh Nair", "2026-08-03T09:05", "Please welcome Tanvi Deshpande who joins Platform Backend today as a Software Engineer! :tada:"),
              ("Priya Shah", "2026-08-03T09:07", "Welcome Tanvi! I'm your buddy - ping me anytime."),
              ("Tanvi Deshpande", "2026-08-03T09:31", "Thank you all! Excited to be here."),
              ("Karthik Iyer", "2026-08-03T09:33", "welcome! the chai machine on floor 3 is the good one"),
          ]),
          S("#eng-platform", [
              ("Tanvi Deshpande", "2026-08-04T11:20", "Quick q - the AWS access portal shows my sandbox account but nothing for prod. Is that expected on day 2?"),
              ("Nandini Rajan", "2026-08-04T11:24", "Yes - ProdReadOnly needs Varun's approval on the ticket and he's at the Mumbai DC till Wed. Sandbox is done. I'll push it as soon as he's back."),
              ("Rohan Mehta", "2026-08-04T11:26", "Fine for now, you can do everything you need in sandbox this week."),
              ("Nandini Rajan", "2026-08-06T09:50", "@Tanvi prod read-only is assigned now."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-002
    E("EVT-002", "access_request", "standard_data_access", "2026-07-21",
      ["Pooja Hegde", "Suresh Pillai", "Ananya Chatterjee"], "Data & Analytics Engineering",
      system="Snowflake Data Warehouse", policy="Snowflake Data Access Policy", project="Unified Customer 360 Dashboard",
      summary="Pooja Hegde (new Data Analyst) requested curated Snowflake access and Metabase on her second day. Handled exactly per the "
              "Snowflake Data Access Policy: Jira DATA ticket, Data Engineering Manager approval, snowflake-analyst role granted next day. "
              "No PII schemas requested.",
      outcome="resolved", drift=False, tags=["data-access", "new-joiner", "policy-consistent"],
      tickets=[
          T("Snowflake (curated marts) + Metabase access - Pooja Hegde",
            "Hi, I joined the Data team yesterday as a Data Analyst and will be working on the Customer 360 dashboard. I need read access "
            "to the curated Snowflake marts (CORE_MART, SALES_MART, SUPPORT_MART) and a Metabase login with native query. I don't need "
            "any PII schemas. Suresh has approved verbally; I've also raised DATA-1187 in Jira as the wiki says.",
            "Linked to Jira DATA-1187 (approved by Suresh Pillai 21-Jul). Added Pooja to Okta groups snowflake-analyst and metabase-sql. "
            "Snowflake role ANALYST_RO grants read on CORE_MART, SALES_MART, SUPPORT_MART. No pii-reader requested. "
            "Confirmed login works on 22-Jul.",
            "Pooja Hegde", "Ananya Chatterjee", "2026-07-21", resolved="2026-07-22", group="Data Engineering",
            approvers=["Suresh Pillai"]),
      ],
      slack=[
          S("#eng-data", [
              ("Pooja Hegde", "2026-07-21T10:02", "Hi team! What's the right way to get Snowflake access? I see a ServiceNow form and also a mention of a Jira DATA ticket in the wiki."),
              ("Ananya Chatterjee", "2026-07-21T10:06", "Both, sort of :slightly_smiling_face: Raise the DATA ticket (type 'Data access request') - that's where Suresh approves. The ServiceNow one just tracks the Okta group change; I'll link them."),
              ("Suresh Pillai", "2026-07-21T10:15", "Approved DATA-1187. Curated marts only for now; we'll talk about PII if Customer 360 needs it, that has a separate sign-off."),
              ("Ananya Chatterjee", "2026-07-22T09:40", "@Pooja you're in - role ANALYST_RO. Metabase link is on the Data team page (needs VPN)."),
              ("Pooja Hegde", "2026-07-22T09:52", "Working, thank you!"),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-003
    E("EVT-003", "access_request", "privileged_access_with_training_gate", "2026-05-14",
      ["Kunal Shah", "Anita Desai", "Rohan Mehta", "Kavya Reddy", "Preeti Nambiar"], "Customer Success & Support",
      system="AlgoWorks Admin Console", policy="Privileged Access & Admin Console Policy",
      summary="Kunal Shah (CSM) requested read-only AlgoWorks Admin Console access. IAM put the request on hold because he had not "
              "completed the 'Handling Customer Data' course; he completed it on 18-May, Anita Desai and Rohan Mehta approved, and IAM "
              "granted console-readonly on 20-May. Followed the policy as written. (Contrast: EVT-067, where the same access was handled "
              "inconsistently for two Support Engineers.)",
      outcome="resolved", drift=False, related_events=["EVT-067"], tags=["privileged-access", "policy-consistent", "admin-console"],
      tickets=[
          T("AlgoWorks Admin Console read-only access - Kunal Shah (Customer Success)",
            "I manage 14 enterprise accounts and keep having to ask Support Engineers to look up tenant configuration (feature flags, "
            "device counts, subscription state) for QBR prep. Requesting console-readonly so I can self-serve. Manager: Anita Desai.",
            "On hold 14-May: LearnHub shows 'Handling Customer Data' not completed (required by the Privileged Access policy section 3.1). "
            "Requester completed the course 18-May (certificate attached). Approvals: Anita Desai (manager) 18-May, Rohan Mehta (system "
            "owner, Platform EM) 19-May. Added to Okta group console-readonly 20-May. Reminder: quarterly review by Platform EM.",
            "Kunal Shah", "Kavya Reddy", "2026-05-14", resolved="2026-05-20", group="IAM",
            approvers=["Anita Desai", "Rohan Mehta"], sensitivity="restricted"),
      ],
      emails=[
          M("RE: Admin Console access request - training prerequisite",
            [("Kavya Reddy", ["Kunal Shah", "Anita Desai"], "2026-05-14T15:22",
              "Hi Kunal,\n\nI've picked up your Admin Console request. Before I can grant console-readonly, the Privileged Access & Admin "
              "Console Policy (v2, April 2026) requires completion of the 'Handling Customer Data' course in LearnHub within the last 12 "
              "months - LearnHub shows it as not started for you. It takes about 40 minutes. Once it shows complete I'll route the "
              "approvals to Anita and to Rohan Mehta (Platform EM, system owner).\n\nSorry for the extra step - v2 removed the option "
              "for a manager attestation instead of the training.\n\nKavya\nIAM Analyst"),
             ("Kunal Shah", ["Kavya Reddy", "Anita Desai"], "2026-05-18T11:48",
              "Done - certificate attached. Thanks for the clear explanation. Anita, could you approve on the ticket?\n\nKunal"),
             ("Anita Desai", ["Kunal Shah", "Kavya Reddy"], "2026-05-18T12:30", "Approved on the ticket. Thanks both.\n\nAnita"),
             ("Kavya Reddy", ["Kunal Shah", "Anita Desai"], "2026-05-20T09:58",
              "Rohan approved yesterday evening; you're now in console-readonly. Login is via Okta tile 'Admin Console' (VPN required).\n\nKavya")]),
      ],
      slack=[
          S("#customer-success", [
              ("Kunal Shah", "2026-05-14T16:05", "FYI my Admin Console request got put on hold because I haven't done the 'Handling Customer Data' training. Apparently mandatory since April."),
              ("Preeti Nambiar", "2026-05-14T16:09", "Huh, I got console-readonly in January and nobody asked me for training. Maybe it's new."),
              ("Anita Desai", "2026-05-14T16:15", "It is new-ish (policy v2 came out end of April). Everyone on the team who needs console should do the course anyway - it's 40 min. Preeti, please do it too so we're covered at the next review."),
              ("Sameer Khan", "2026-05-14T16:20", "Mine got denied in April pending the same training and I still haven't found time. Doing it this week."),
              ("Kunal Shah", "2026-05-20T10:12", "Access came through today. Course -> manager approval -> Rohan approval -> IAM. About a week end to end."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-004
    E("EVT-004", "access_request", "contractor_sponsored_accounts", "2026-06-08",
      ["Ankit Chawla", "Kavya Reddy", "Deepak Verma", "Omar Farooq"], "Content & Brand",
      system="Corporate Website CMS", policy="Contractor & Guest Access Policy", project="Website Redesign & CMS Migration",
      summary="Ankit Chawla sponsored two Pixelcraft Studio (agency) contractor accounts for the website redesign: ext- Okta accounts with "
              "90-day expiry, WordPress editor role, and a Slack Connect channel. Processed under the new Contractor & Guest Access Policy "
              "(v2, effective 1 June 2026).",
      outcome="resolved", drift=False, tags=["contractor", "marketing", "policy-consistent"],
      tickets=[
          T("Contractor accounts (x2) - Pixelcraft Studio - Website Redesign project",
            "Sponsoring two contractor accounts for our design agency Pixelcraft Studio for the Website Redesign & CMS Migration project:\n"
            "1. Neha Prabhu (art director)\n2. Sameer Lobo (front-end developer)\nApplications needed: WordPress CMS (editor role on the "
            "staging site), Confluence (MKT space only), Slack Connect channel. No VPN needed. MSA ref: KT-MSA-2026-014, NDA signed. "
            "Engagement runs to end of October 2026, so please set expiry accordingly or I'll extend.",
            "Created ext-neha.prabhu and ext-sameer.lobo in Okta with 90-day expiry (expires 08-Sep-2026; sponsor reminder set for "
            "29-Aug). Assigned apps: WordPress staging (editor - configured by Ankit), Confluence MKT space. Sponsor attestation on endpoint "
            "baseline recorded. No VPN group assigned. Slack Connect handled on the linked request.",
            "Ankit Chawla", "Kavya Reddy", "2026-06-08", resolved="2026-06-10", group="IAM", category="contractor-access",
            approvers=["Ankit Chawla"]),
          T("Slack Connect shared channel with Pixelcraft Studio (#ext-pixelcraft)",
            "Please create a Slack Connect channel #ext-pixelcraft shared with pixelcraftstudio.slack.com for the website redesign. "
            "Members from our side: Ankit Chawla, Omar Farooq, Riya Sen, Shreya Ghosh, Ishita Bose, Aparna Das.",
            "Channel #ext-pixelcraft created and Slack Connect invite sent to Pixelcraft admin; accepted 09-Jun. Channel set to "
            "'external' with file-sharing restricted to AlgoWorks-side members. Requested members added.",
            "Ankit Chawla", "Deepak Verma", "2026-06-08", resolved="2026-06-09", group="IT Service Desk", category="collaboration"),
      ],
      emails=[
          M("Pixelcraft contractor accounts - expiry and extension",
            [("Kavya Reddy", "Ankit Chawla", "2026-06-10T14:05",
              "Hi Ankit,\n\nBoth Pixelcraft accounts are live (details on the ticket). Two things to note under the new contractor policy:\n"
              "1. Accounts expire on 8 September (90 days). You'll get a reminder 10 days before; extension is a one-click approval on the "
              "ticket, in 90-day blocks.\n2. If they ever need VPN (e.g. for the Admin Console or Metabase) that's a separate request and a "
              "security review - please don't share your own credentials.\n\nKavya"),
             ("Ankit Chawla", "Kavya Reddy", "2026-06-10T15:11",
              "Perfect, thanks Kavya. They only need the WordPress staging site and Confluence, no VPN. I'll extend in late August.\n\nAnkit")]),
      ]),

    # ------------------------------------------------------------------ EVT-005
    E("EVT-005", "access_request", "offboarding_with_unowned_approval_role", "2026-02-27",
      ["Pradeep Chauhan", "Nikhil Bhatt", "Kavya Reddy", "Rakesh Nair", "Sandeep Malhotra", "Sunita Raghavan", "Suresh Pillai"],
      "Identity & Access Management", system="Okta SSO", policy="Employee Offboarding & Access Revocation SOP",
      summary="Pradeep Chauhan (Data Protection Officer & Compliance Lead) left on 27-Feb-2026. Access revocation ran on time, but his "
              "role as DPO sign-off for Snowflake PII access and data-protection reviews was never formally reassigned: the follow-up "
              "ticket was put on hold pending a hiring decision and is still open. This is the root cause of the later Snowflake PII "
              "approval drift (EVT-054) and prompted section 3 of the Offboarding SOP v3.",
      outcome="partially_resolved", drift=False, related_events=["EVT-054"], tags=["offboarding", "dpo", "ownership-gap"],
      tickets=[
          T("Offboarding: Pradeep Chauhan - LWD 27-Feb-2026",
            "Auto-created from Darwinbox exit workflow. Employee: Pradeep Chauhan, Data Protection Officer & Compliance Lead, IAM team. "
            "Last working day 27-Feb-2026 (exit date on record 28-Feb). Manager: Nikhil Bhatt. Voluntary resignation. Please process "
            "access revocation and asset return per the Offboarding SOP.",
            "Okta disabled 27-Feb 18:00; sessions revoked; mail forwarded to Nikhil Bhatt for 30 days. 28-Feb: removed from all Okta groups "
            "(incl. snowflake-admin, console-admin), GitHub org, AWS Identity Center; Slack deactivated; 1Password vault 'Security-Compliance' "
            "ownership moved to Nikhil. Laptop KT-LT-0233 returned 27-Feb and wiped 02-Mar. NOTE: Pradeep was the named approver on the "
            "Jira DATA 'DPO sign-off' step and owner of the Data Protection review queue - manager to confirm reassignment (see linked ticket).",
            "Rakesh Nair", "Kavya Reddy", "2026-02-20", resolved="2026-03-02", group="IAM", category="offboarding",
            on_behalf_of="Pradeep Chauhan", sensitivity="restricted"),
          T("Reassign Data Protection Officer responsibilities (DPO sign-off on DATA tickets, DP reviews)",
            "Following Pradeep Chauhan's exit on 27-Feb we have no named DPO. Open items that referenced him as approver: (1) the DPO "
            "sign-off step on Jira DATA access requests for PII schemas (Snowflake Data Access Policy 2.2); (2) Data Protection review of "
            "new data uses (Data Classification standard); (3) the semi-annual pii-reader access review due April. Need a decision on "
            "interim owner and whether we hire a replacement or split the role.",
            "03-Mar: Sandeep Malhotra - interim: Nikhil Bhatt covers security compliance items and vendor questionnaires. Data-protection "
            "sign-offs on DATA tickets: no interim named; leadership to decide by end of March whether to backfill. 15-Apr: still pending "
            "budget discussion for FY27. Ticket placed ON HOLD. (No further update as of Sep-2026.)",
            "Nikhil Bhatt", "Sandeep Malhotra", "2026-03-03", status="on_hold", group="IT Leadership", category="governance",
            sensitivity="restricted", priority="P2"),
      ],
      emails=[
          M("DPO coverage after Pradeep's exit",
            [("Nikhil Bhatt", ["Sandeep Malhotra", "Sunita Raghavan"], "2026-03-02T09:40",
              "Sandeep, Sunita,\n\nPradeep's access is fully revoked as of Friday. The gap I want to flag: he was the DPO named in three "
              "policies (Snowflake Data Access, Data Classification, and by reference the Offboarding SOP). Concretely, the Snowflake policy "
              "says PII schema access needs written DPO sign-off on the DATA ticket. Suresh's team has two such requests queued right now.\n\n"
              "Options: (a) I cover it as an interim, (b) Suresh approves PII access himself until we backfill, (c) hold all PII requests. "
              "I'd prefer (a) with a hard 3-month limit and a backfill req.\n\nNikhil"),
             ("Sandeep Malhotra", ["Nikhil Bhatt", "Sunita Raghavan"], "2026-03-03T11:15",
              "Nikhil - take the security compliance and vendor questionnaire items as interim. On the data-protection sign-offs I don't want "
              "to formalise an interim until we know whether Finance approves a backfill in the FY27 plan; let's revisit end of March. "
              "Please log a ticket so it doesn't get lost.\n\nSandeep"),
             ("Sunita Raghavan", ["Sandeep Malhotra", "Nikhil Bhatt"], "2026-03-03T12:02",
              "Agree with Sandeep. From the HR side I'll add a checklist item to the exit process so ownership of approval roles is captured "
              "before LWD - this shouldn't have been discovered after the fact.\n\nSunita")],
            sensitivity="restricted"),
      ],
      slack=[
          S("#security", [
              ("Nikhil Bhatt", "2026-03-02T10:05", "Reminder: Pradeep's last day was Friday. I've taken over the Security-Compliance vault and the vendor questionnaire queue. The DPO sign-off question for Snowflake PII requests is with Sandeep - until we hear back, please don't approve pii-reader requests."),
              ("Suresh Pillai", "2026-03-02T10:20", "Noted. I have DATA-1102 (Marketing) and DATA-1109 (CS) waiting on that step. Will tell them it's on hold."),
              ("Amit Saxena", "2026-03-02T10:22", "Do we have his Jira filters/queue transferred? The 'DP Review' board was under his account."),
              ("Kavya Reddy", "2026-03-02T10:30", "Board ownership moved to Nikhil yesterday, filters too."),
          ], private=True, sensitivity="restricted"),
      ]),

    # ------------------------------------------------------------------ EVT-006
    E("EVT-006", "access_request", "new_joiner_onboarding_bundle", "2026-08-24",
      ["Zara Ahmed", "Shalini Menon", "Rakesh Nair", "Deepak Verma", "Payal Shah", "Ramesh Babu", "Kavya Reddy"],
      "Accounts Payable & Procurement", system="NetSuite ERP", policy="Employee Onboarding SOP",
      summary="Zara Ahmed (Procurement Associate) joined 24-Aug-2026. Default bundle was ready; NetSuite access took 4 days because no "
              "licence was free - Payal Shah reassigned a licence flagged as unused in the Q2 access review (EVT-016). Zoho Expense "
              "finance-admin role granted next day.",
      outcome="resolved", drift=False, related_events=["EVT-016"], tags=["onboarding", "new-joiner", "finance", "licence"],
      tickets=[
          T("Onboarding: Zara Ahmed - Procurement Associate (start 24-Aug-2026)",
            "Auto-created from Darwinbox pre-boarding workflow.\nNew joiner: Zara Ahmed\nRole: Procurement Associate\nTeam: Accounts "
            "Payable & Procurement (manager: Shalini Menon)\nLocation: Bengaluru\nStart date: 2026-08-24\nDefault bundle + role bundle "
            "FIN-AP. Laptop: ThinkPad T14.",
            "Okta/M365/Slack/Confluence/Darwinbox/Zoho/LearnHub provisioned 21-Aug. ThinkPad KT-LT-0421 handed over 24-Aug 09:40. "
            "Role bundle FIN-AP applied (ServiceNow Finance-queue fulfiller, Zoho Expense). NetSuite is not in the bundle (licence-based) - "
            "separate request raised by manager.",
            "Rakesh Nair", "Deepak Verma", "2026-08-10", resolved="2026-08-24", group="IT Service Desk", category="onboarding",
            on_behalf_of="Zara Ahmed"),
          T("NetSuite access (Procurement role) - Zara Ahmed",
            "Zara Ahmed joined my team today as Procurement Associate. She needs the NetSuite 'Purchasing - Procurement' role to raise POs "
            "and create vendor records. Approved by me as manager.",
            "No free NetSuite full-user licence on 24-Aug (32/32 in use). Cross-checked the Q2 access review list: Sonal Mehra (Sales Ops) "
            "had not logged in since March and confirmed she no longer needs it; licence released 27-Aug and reassigned. Role "
            "'Purchasing - Procurement' assigned 28-Aug; Zara confirmed login. Raised a note to FP&A to add 3 licences in the FY27 renewal.",
            "Shalini Menon", "Payal Shah", "2026-08-24", resolved="2026-08-28", group="Finance Systems", approvers=["Shalini Menon"],
            on_behalf_of="Zara Ahmed"),
          T("Zoho Expense finance-admin role - Zara Ahmed",
            "Please give Zara Ahmed the Finance Admin role in Zoho Expense so she can help with the AP approval queue and vendor bill "
            "uploads. Manager approval: Shalini Menon.",
            "Role 'Finance Admin' assigned in Zoho Expense on 25-Aug; added to the AP approval group. Shalini's approval on ticket.",
            "Shalini Menon", "Ramesh Babu", "2026-08-24", resolved="2026-08-25", group="Finance Systems", approvers=["Shalini Menon"],
            on_behalf_of="Zara Ahmed"),
      ],
      emails=[
          M("NetSuite licence for Zara",
            [("Shalini Menon", "Payal Shah", "2026-08-24T14:20",
              "Hi Payal, I've raised the NetSuite request for Zara (new Procurement Associate). Can we get her in this week? She's shadowing "
              "Kritika on POs from Wednesday.\n\nShalini"),
             ("Payal Shah", "Shalini Menon", "2026-08-24T16:02",
              "Hi Shalini - we're at 32 of 32 full-user licences. Two options: buy an add-on licence (Rs 38,000/yr, needs Ashwin + Vivek) or "
              "reclaim one. Kavya's Q2 access review flagged two NetSuite users with no login since March; I'm checking with them today.\n\nPayal"),
             ("Payal Shah", "Shalini Menon", "2026-08-27T17:30",
              "Sonal confirmed she doesn't need hers (she uses the Metabase finance dashboards now). Releasing it and assigning Zara tomorrow "
              "morning. I've also asked Ashwin to add 3 licences in the FY27 renewal so this doesn't keep happening.\n\nPayal"),
             ("Shalini Menon", "Payal Shah", "2026-08-28T10:10", "She's in. Thanks for chasing it, Payal.\n\nShalini")]),
      ],
      slack=[
          S("#finance", [
              ("Shalini Menon", "2026-08-24T09:55", "Welcome Zara Ahmed to the AP & Procurement team! Zara starts on POs and vendor onboarding with Kritika this week."),
              ("Kritika Jain", "2026-08-24T09:58", "Welcome Zara! :wave:"),
              ("Zara Ahmed", "2026-08-24T10:20", "Thanks everyone, happy to be here."),
              ("Kritika Jain", "2026-08-26T11:40", "@Zara until your NetSuite comes through you can raise the PO drafts in the ServiceNow purchase-request form and I'll key them in."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-007
    E("EVT-007", "access_request", "cross_department_admin_role", "2026-04-09",
      ["Megha Patil", "Vinod Krishnamurthy", "Manoj Venkatesh", "Aparna Das"], "Sales Operations & Deal Desk",
      system="HubSpot Marketing Hub", policy="Application Access Request Policy", project="HubSpot-Salesforce Lead Sync Cleanup",
      summary="Megha Patil (Salesforce Administrator) requested HubSpot super-admin to fix a connector field mapping. Admin roles need the "
              "requester's manager (Vinod) and the owning team's lead (Manoj Venkatesh); both approved within a day and Aparna Das granted "
              "it. Cross-department, by the book.",
      outcome="resolved", drift=False, tags=["cross-department", "admin-role", "policy-consistent"],
      tickets=[
          T("HubSpot super-admin access - Megha Patil (Salesforce Admin) - connector mapping fix",
            "The HubSpot-Salesforce connector is writing 'Lead Source' into the wrong Salesforce field again for the APAC campaign forms. "
            "I can fix it from the Salesforce side only partially; the mapping lives in HubSpot settings which need super-admin. Requesting "
            "super-admin (or at minimum 'Settings > Integrations' admin) for HubSpot. Manager: Vinod Krishnamurthy.",
            "Approvals: Vinod Krishnamurthy (manager) 09-Apr, Manoj Venkatesh (HubSpot owning team lead) 10-Apr - required for admin roles "
            "per Access Request Policy 3.7. Aparna Das (Marketing Ops, HubSpot super-admin) granted super-admin 10-Apr. Per the CRM hygiene "
            "policy, mapping changes to be tested in sandbox and logged in Jira first.",
            "Megha Patil", "Aparna Das", "2026-04-09", resolved="2026-04-10", group="Marketing Ops",
            approvers=["Vinod Krishnamurthy", "Manoj Venkatesh"]),
      ],
      slack=[
          S("#demand-gen", [
              ("Megha Patil", "2026-04-09T11:30", "@Aparna the APAC form leads are landing with Lead Source = 'Web' instead of 'Campaign - APAC'. I think it's the connector mapping on your side - can I get admin to look?"),
              ("Aparna Das", "2026-04-09T11:36", "Yes, raise the access request and tag Manoj as approver too (admin roles need the owning team lead). I'll grant as soon as both are in."),
              ("Manoj Venkatesh", "2026-04-09T12:01", "Approved. Megha - please make the change in the HubSpot sandbox first and drop the Jira ID here, per the sync cleanup runbook."),
              ("Megha Patil", "2026-04-10T10:15", "Got admin, thanks. Jira MKT-233 raised for the mapping change; sandbox test this afternoon."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-008
    E("EVT-008", "access_request", "break_glass_elevated_access", "2026-03-19",
      ["Harish Gowda", "Varun Chandra", "Rohan Mehta"], "Cloud Infrastructure & Security",
      system="AWS Production Account", policy="Production Access & Break-Glass Policy", project="AlgoWorks Fleet v4 API Platform Migration",
      summary="Two days after the March API outage, Harish Gowda needed ProdOperator to clear a stuck Kinesis consumer. Requested via the "
              "'Production elevated access' item, approved by Varun Chandra, 8-hour session (policy v1 at the time), post-hoc review "
              "recorded, and a retrospective emergency CHG raised the next day. Policy-consistent break-glass.",
      outcome="resolved", drift=False, related_events=["EVT-021"], tags=["break-glass", "aws", "policy-consistent"],
      tickets=[
          T("Production elevated access (ProdOperator) - Harish Gowda - Kinesis consumer lag",
            "Requesting ProdOperator for the production account. Telematics ingest consumer group 'telemetry-v4-consumer' has 2.1M records "
            "of lag since the 17-Mar rollback; the consumer is stuck on a poison shard and needs a checkpoint reset which is not possible "
            "via ArgoCD. Estimated 2 hours. Reference: {{ticket:EVT-021#1}}.",
            "Approved by Varun Chandra 19-Mar 10:12 (Cloud Infra Lead). ProdOperator permission set activated 10:20 for 8 hours (session "
            "actually closed 12:05). Actions: reset checkpoint for shard 0007, restarted consumer deployment. Post-hoc review by Varun "
            "20-Mar: CloudTrail actions match the ticket; no findings. Retrospective emergency CHG raised (linked).",
            "Harish Gowda", "Varun Chandra", "2026-03-19", resolved="2026-03-20", group="Cloud Infrastructure",
            approvers=["Varun Chandra"], category="privileged-access", priority="P2", sensitivity="restricted"),
          T("Emergency change (retrospective): Kinesis consumer checkpoint reset - telemetry-v4-consumer",
            "Retrospective CHG per Change Management Policy 3.4. On 19-Mar 10:20-12:05 the checkpoint for shard 0007 of "
            "telemetry-v4-consumer was reset and the consumer deployment restarted to clear a poison record causing 2.1M lag after the "
            "17-Mar rollback. Approved verbally by Varun Chandra before implementation. Risk: possible duplicate processing of ~400 events "
            "(idempotent writes, verified).",
            "Reviewed at CAB 24-Mar (Tue). Accepted as emergency change; action item to add a dead-letter path for poison records (Jira "
            "PLAT-2210). Closed successful.",
            "Harish Gowda", "Varun Chandra", "2026-03-20", resolved="2026-03-24", group="Cloud Infrastructure", kind="change",
            category="emergency-change", priority="P2"),
      ],
      emails=[
          M("Approved: ProdOperator session for Kinesis fix (19-Mar)",
            [("Varun Chandra", ["Harish Gowda", "Rohan Mehta"], "2026-03-19T10:12",
              "Harish - approved on the ticket, session is yours. Keep it to the checkpoint reset and the restart; anything else we discuss "
              "first. Rohan, FYI as this touches the v4 consumer.\n\nVarun"),
             ("Harish Gowda", ["Varun Chandra", "Rohan Mehta"], "2026-03-19T12:10",
              "Done and session closed. Lag is draining at ~40k/min, should be caught up by 13:00. Notes on the ticket; I'll raise the "
              "retrospective CHG tomorrow morning.\n\nHarish"),
             ("Varun Chandra", ["Harish Gowda", "Rohan Mehta"], "2026-03-20T09:30",
              "Post-hoc review done - CloudTrail lines up with the ticket. Thanks for the clean write-up.\n\nVarun")],
            sensitivity="restricted"),
      ],
      slack=[
          S("#devops-sre", [
              ("Harish Gowda", "2026-03-19T09:55", "telemetry-v4-consumer is stuck on a poison record on shard 0007, lag 2.1M and climbing. Need ProdOperator to reset the checkpoint - raising the elevated access request now. @Varun"),
              ("Varun Chandra", "2026-03-19T10:11", "Approving. Post in here when the session's closed."),
              ("Harish Gowda", "2026-03-19T12:06", "Session closed. Checkpoint reset + consumer restart, lag draining."),
              ("Rohan Mehta", "2026-03-19T12:15", "Thanks Harish. Adding a DLQ for poison records to the v4 backlog so this isn't a break-glass next time."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-009
    E("EVT-009", "access_request", "vpn_remote_employee_timezone", "2026-06-25",
      ["Ethan Brooks", "Manoj Venkatesh", "Kavya Reddy", "Lakshmi Narayanan"], "Demand Generation",
      system="GlobalProtect VPN", policy="VPN & Remote Connectivity Policy",
      summary="Ethan Brooks (Growth Analyst, remote US) requested VPN to reach Metabase. Approval and group assignment were quick, but "
              "connection failures caused by his home router's MTU took three days to diagnose across the 12.5-hour time difference. "
              "Resolved by Lakshmi Narayanan with a client-side MTU change; runbook updated.",
      outcome="resolved", drift=False, tags=["vpn", "remote", "troubleshooting"],
      tickets=[
          T("VPN access - Ethan Brooks (remote, US) - for Metabase dashboards",
            "I need VPN access to reach Metabase for the growth dashboards (currently asking Aparna to export screenshots, which is silly). "
            "I'm US-based remote (Denver, MT). Manager: Manoj Venkatesh.",
            "Manoj approved 25-Jun 19:40 IST. Added to vpn-employees 26-Jun 09:15 IST. 26-Jun: user reports 'connection established then "
            "drops after ~20s' - GlobalProtect logs show tunnel negotiation OK then fragmentation errors. 27-30 Jun: troubleshooting over "
            "email due to time zone (user's morning = our night). Root cause: home router MTU 1500 with PPPoE overhead; set client MTU to "
            "1380 via GlobalProtect portal config for the 'remote-us' gateway. Confirmed working 30-Jun. Runbook 'GlobalProtect - remote "
            "user troubleshooting' updated with the MTU step.",
            "Ethan Brooks", "Lakshmi Narayanan", "2026-06-25", resolved="2026-06-30", group="IAM", approvers=["Manoj Venkatesh"]),
      ],
      emails=[
          M("RE: VPN connects then drops - Ethan Brooks",
            [("Ethan Brooks", "IT-Access-Team", "2026-06-26T20:15",
              "Hi - thanks for adding me to VPN. It connects, shows 'Connected' for about 20 seconds, then drops and reconnects in a loop. "
              "Metabase never loads. I'm on macOS 15, GlobalProtect 6.3, home fibre. Happy to jump on a call but I'm 12.5 hours behind "
              "you - I can do 7am my time (7:30pm IST).\n\nEthan"),
             ("Lakshmi Narayanan", "Ethan Brooks", "2026-06-27T09:20",
              "Hi Ethan, I've picked this up. Could you send the GlobalProtect logs (Settings > Troubleshooting > Collect Logs) and the "
              "output of `ping -D -s 1400 10.20.0.1` while connected? That'll tell us if it's a fragmentation issue, which the 20-second "
              "pattern suggests.\n\nLakshmi"),
             ("Ethan Brooks", "Lakshmi Narayanan", "2026-06-27T19:50",
              "Logs attached. The 1400-byte ping fails ('Message too long'), 1300 works.\n\nEthan"),
             ("Lakshmi Narayanan", "Ethan Brooks", "2026-06-30T09:05",
              "That confirms it - your router is eating large packets (PPPoE overhead). I've pushed an MTU of 1380 to the remote-us gateway "
              "profile; please quit and reopen GlobalProtect and try again. I'm around till 7pm IST if you want to test early.\n\nLakshmi"),
             ("Ethan Brooks", "Lakshmi Narayanan", "2026-06-30T19:35", "Stable for 20 minutes now and Metabase loads. Thank you!\n\nEthan")]),
      ]),

    # ------------------------------------------------------------------ EVT-010
    E("EVT-010", "access_request", "restricted_finance_system_access", "2026-05-20",
      ["Manish Tiwari", "Suresh Pillai", "Ashwin Raman", "Vivek Anand", "Payal Shah"], "Financial Planning & Analysis",
      system="NetSuite ERP", policy="Application Access Request Policy", project="FY27 Annual Operating Plan",
      summary="Manish Tiwari (Analytics Engineer) was embedded with FP&A for the FY27 plan and needed NetSuite read-only. Non-Finance access "
              "requires FP&A Manager approval plus CFO sign-off; Ashwin approved same day, Vivek signed off two days later, Payal granted a "
              "reporting-only role. Restricted access, quarterly review noted.",
      outcome="resolved", drift=False, tags=["restricted", "finance", "cross-team", "policy-consistent"],
      tickets=[
          T("NetSuite read-only (reporting) access - Manish Tiwari (Data Eng, embedded with FP&A)",
            "I'm supporting the FY27 AOP model and the Zoho-NetSuite integration testing. I need read-only access to NetSuite saved "
            "searches and GL reports (no transaction entry). Managers: Suresh Pillai (line) and Ashwin Raman (project). Access can be "
            "time-boxed to end of December 2026.",
            "Approvals: Suresh Pillai (line manager) 20-May, Ashwin Raman (FP&A Manager, system owner) 20-May, Vivek Anand (CFO sign-off "
            "required for non-Finance NetSuite access) 22-May. Assigned custom role 'Reporting - Read Only' (no PII on employee records, "
            "no AP/AR entry). End date 31-Dec-2026 set on the ticket; included in the quarterly NetSuite access review.",
            "Manish Tiwari", "Payal Shah", "2026-05-20", resolved="2026-05-22", group="Finance Systems",
            approvers=["Suresh Pillai", "Ashwin Raman", "Vivek Anand"], sensitivity="restricted"),
      ],
      emails=[
          M("CFO sign-off needed: NetSuite read-only for Manish Tiwari (AOP support)",
            [("Ashwin Raman", "Vivek Anand", "2026-05-20T15:45",
              "Vivek - Manish from Data Engineering is building the driver-based revenue model for the FY27 AOP with us and needs read-only "
              "NetSuite (saved searches, GL reports). Per the access rules for non-Finance users I need your sign-off on the ticket. "
              "Time-boxed to 31 December.\n\nAshwin"),
             ("Vivek Anand", "Ashwin Raman", "2026-05-22T08:20",
              "Approved on the ticket. Please make sure the role excludes payroll journals and employee records.\n\nVivek"),
             ("Ashwin Raman", "Vivek Anand", "2026-05-22T09:02", "It does - Payal built a reporting-only role for exactly this. Thanks.\n\nAshwin")],
            sensitivity="restricted"),
      ],
      slack=[
          S("#finance", [
              ("Manish Tiwari", "2026-05-22T11:10", "NetSuite access is through, thanks Payal/Ashwin. I'll start pulling the FY26 actuals by cost centre for the AOP baseline."),
              ("Payal Shah", "2026-05-22T11:12", "The saved search 'AOP - Actuals by CC' is shared with you. Ping me if the GL mapping looks off."),
          ]),
      ]),
]
