"""Layer 6/7 - Unresolved / contradictory-resolution events EVT-063..EVT-070.

Each event has two tickets about the same problem resolved differently (or not at all),
so the knowledge bank can be tested on conflict detection rather than policy drift.
"""
from events.dsl import E, T, M, S, D

EVENTS = [
    # ------------------------------------------------------------------ EVT-063
    E("EVT-063", "contradictory_resolution", "vpn_disconnects_two_fixes_no_root_cause", "2026-06-17",
      ["Payal Shah", "Nithin George", "Deepak Verma", "Shruti Joshi", "Lakshmi Narayanan", "Harsha Vardhan"], "IT Service Desk & Endpoint",
      system="GlobalProtect VPN", policy="Incident Management & Severity Classification SOP",
      summary="Two Finance users reported GlobalProtect dropping every ~30 minutes on home Wi-Fi. Ticket A (March, Payal Shah) was closed "
              "as 'reinstalled the client'; ticket B (June, Nithin George) was closed as 'disabled IPv6 on the Wi-Fi adapter'. Both users "
              "say it still happens intermittently; no root cause was found and the two resolutions contradict each other. Still recurring "
              "per an August Slack thread.",
      outcome="unresolved", drift=False, tags=["conflict", "vpn", "troubleshooting", "recurring", "demo"],
      demo={"query": "Has the VPN disconnecting every 30 minutes on Wi-Fi been solved before?", "expected_conflict": True},
      tickets=[
          T("VPN disconnects every ~30 minutes on home Wi-Fi - Payal Shah",
            "Since last week GlobalProtect drops roughly every half hour when I'm on my home Wi-Fi (Airtel fibre). It reconnects on its "
            "own but NetSuite sessions are lost each time. Doesn't happen on the office LAN or on my phone hotspot. macOS 15.3, GP 6.3.1.",
            "Uninstalled and reinstalled GlobalProtect 6.3.1 with a clean config (removed ~/Library/Application Support/PaloAltoNetworks); "
            "user reports stable for 2 hours after reinstall. Closing as resolved - reinstall fixed it. Reopen if it recurs.",
            "Payal Shah", "Deepak Verma", "2026-03-10", resolved="2026-03-10", group="IT Service Desk", kind="incident", category="vpn",
            priority="P3", work_notes="No packet capture taken. Resolution assumed from a 2-hour observation."),
          T("GlobalProtect drops connection every 25-30 min on Wi-Fi - Nithin George",
            "GlobalProtect disconnects every 25-30 minutes when working from home; reconnects but I lose my NetSuite and Metabase sessions. "
            "Started around May. Same laptop is fine in the office. Payal had this in March and IT reinstalled the client - I tried that "
            "myself, no change.",
            "Reinstall had no effect (user already tried). Checked GP logs: tunnel drops coincide with IPv6 router advertisements on the "
            "home network causing a default-route flap. Disabled IPv6 on the Wi-Fi adapter (networksetup -setv6off Wi-Fi). User stable for "
            "the rest of the day. Closing as resolved - IPv6 on the home router. Suggest users with the same symptom disable IPv6.",
            "Nithin George", "Shruti Joshi", "2026-06-17", resolved="2026-06-17", group="IT Service Desk", kind="incident", category="vpn",
            priority="P3", work_notes="Different fix from the March ticket; no confirmation beyond one day."),
      ],
      emails=[
          M("VPN drops - two tickets, two different fixes, still happening",
            [("Nithin George", ["Payal Shah", "IT-Helpdesk"], "2026-08-04T09:40",
              "Hi,\n\nPayal and I compared notes: her March ticket was closed as 'reinstall fixed it', mine in June as 'disable IPv6'. Both of "
              "us still get the 30-minute drop a couple of times a week (less often for me since the IPv6 change, but not zero). Could "
              "someone actually look at the root cause rather than closing on the first quiet afternoon? Happy to run a packet capture.\n\nNithin"),
             ("Lakshmi Narayanan", ["Nithin George", "Payal Shah", "IT-Helpdesk"], "2026-08-04T12:30",
              "Hi both - agreed this shouldn't have been closed twice with different answers. I'll take it from IAM's side: please both run "
              "the GP log collector the next time it drops and send me the timestamp. My current suspicion is the gateway's 30-minute "
              "rekey with certain home routers, which would explain the interval. Re-opening as a problem record rather than a new incident.\n\nLakshmi")]),
      ],
      slack=[
          S("#it-helpdesk", [
              ("Harsha Vardhan", "2026-08-03T10:15", "Does anyone else's VPN drop every half hour on home Wi-Fi? Mine's done it three times this morning."),
              ("Payal Shah", "2026-08-03T10:18", "Yes! IT reinstalled my client in March and said it was fixed. It wasn't really."),
              ("Nithin George", "2026-08-03T10:20", "Mine was 'fixed' in June by disabling IPv6. Better but still happens."),
              ("Deepak Verma", "2026-08-03T10:30", "Different fixes because different engineers - sorry. Can you all raise it under one ticket this time so we stop closing it in pieces?"),
              ("Lakshmi Narayanan", "2026-08-04T12:35", "Taking this as a problem record. Suspect the 30-min rekey; will confirm with logs."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-064
    E("EVT-064", "contradictory_resolution", "salesforce_report_export_two_causes", "2026-05-05",
      ["Sonal Mehra", "Arun Prasad", "Anjali Gupta", "Megha Patil", "Vinod Krishnamurthy"], "Sales Operations & Deal Desk",
      system="Salesforce CRM", policy="CRM Data Hygiene & Lead Ownership Policy",
      summary="Two Sales Ops users could not export Salesforce reports. Ticket A (Sonal Mehra, February) was resolved by the Service Desk as "
              "'cleared browser cache'; ticket B (Arun Prasad, May) was resolved by the Salesforce Administrator as 'user profile lacked the "
              "Export Reports permission - added'. The two tickets give different answers to the same question and the Service Desk's "
              "answer was probably coincidental.",
      outcome="resolved_inconsistently", drift=False, tags=["conflict", "salesforce", "permissions", "demo"],
      demo={"query": "Why can't I export reports from Salesforce?", "expected_conflict": True},
      tickets=[
          T("Cannot export Salesforce report - button greyed out - Sonal Mehra",
            "The 'Export' option on my pipeline reports is greyed out since yesterday. I need the weekly pipeline extract for Vinod.",
            "Cleared Chrome cache and cookies for salesforce.com and had the user log in again via Okta; export button available "
            "afterwards. Likely a cached Lightning component issue. Closed.",
            "Sonal Mehra", "Anjali Gupta", "2026-02-24", resolved="2026-02-24", group="IT Service Desk", kind="incident",
            category="application", priority="P3", work_notes="Salesforce permissions not checked by Service Desk."),
          T("Salesforce report export not available - Arun Prasad (Deal Desk)",
            "I can run reports but there's no Export option. Sonal had the same in Feb and IT cleared her cache - I tried that (and Firefox), "
            "no luck.",
            "Checked the user's profile: 'Deal Desk Analyst' profile does not include the 'Export Reports' permission (it was removed from "
            "the base Sales Ops profiles during the January licence/profile cleanup and only re-added to some users via permission set). "
            "Assigned permission set 'Report Export' to Arun. Note: Sonal's February issue was almost certainly the same - her export "
            "started working because Megha had bulk-assigned the permission set the same afternoon, not because of the cache clear. "
            "Service Desk should route Salesforce permission issues to Sales Ops.",
            "Arun Prasad", "Megha Patil", "2026-05-05", resolved="2026-05-05", group="Sales Ops", kind="incident", category="application",
            priority="P3"),
      ],
      emails=[
          M("Salesforce export issue - routing note",
            [("Megha Patil", ["Anjali Gupta", "Deepak Verma", "Vinod Krishnamurthy"], "2026-05-05T15:20",
              "Hi Service Desk,\n\nFYI on Arun's export ticket: it was a missing 'Export Reports' permission, not a browser issue - and I "
              "think Sonal's February one was the same thing (I bulk-assigned the permission set that afternoon, which is why her cache "
              "clear 'worked'). For anything Salesforce that isn't a login problem, could you route straight to the Sales Ops queue? It'll "
              "save everyone a round trip.\n\nMegha"),
             ("Anjali Gupta", ["Megha Patil", "Deepak Verma", "Vinod Krishnamurthy"], "2026-05-05T15:45",
              "Understood, will do. Sorry for the misdiagnosis - the cache clear looked like it fixed it.\n\nAnjali")]),
      ],
      slack=[
          S("#sales-ops", [
              ("Arun Prasad", "2026-05-05T10:30", "No Export option on my reports. Tried the cache thing from Sonal's ticket, nothing."),
              ("Sonal Mehra", "2026-05-05T10:32", "Mine came back after IT cleared my cache in Feb, weird."),
              ("Megha Patil", "2026-05-05T10:45", "It's a permission, not the cache - you don't have Export Reports on the Deal Desk profile. Fixing. Sonal, yours was the same, I just happened to fix it that day."),
              ("Arun Prasad", "2026-05-05T10:50", "Working now, thanks. So the Feb ticket is basically wrong?"),
              ("Megha Patil", "2026-05-05T10:52", "Right cause, wrong write-up. I've asked IT to route Salesforce stuff to us."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-065
    E("EVT-065", "contradictory_resolution", "okta_verify_push_two_fixes", "2026-07-01",
      ["Riya Sen", "Bhavana Shetty", "Kavya Reddy", "Deepak Verma", "Lakshmi Narayanan"], "Identity & Access Management",
      system="Okta SSO", policy="Password & MFA Standard",
      summary="Okta Verify push notifications not arriving: ticket A (Riya Sen, April) was fixed by re-enrolling Okta Verify; ticket B "
              "(Bhavana Shetty, July) was fixed by correcting the phone's automatic time setting. Both were closed as resolved with different "
              "root causes; the IT knowledge article still lists only 're-enrol', so the Service Desk keeps re-enrolling users for whom the "
              "time-sync fix would work.",
      outcome="resolved_inconsistently", drift=False, tags=["conflict", "okta", "mfa", "troubleshooting"],
      demo={"query": "Okta Verify push notifications are not arriving - what fixes it?", "expected_conflict": True},
      tickets=[
          T("Okta Verify push not arriving on phone - Riya Sen",
            "Since this morning I don't get the Okta Verify push when logging in. The app opens but there's no prompt; 'Enter code' works "
            "but it's slow. Android, Okta Verify updated last night.",
            "Removed the Okta Verify factor for the user in the Okta admin console and had the user re-enrol (scan QR). Push notifications "
            "working after re-enrolment. Closed.",
            "Riya Sen", "Kavya Reddy", "2026-04-14", resolved="2026-04-14", group="IAM", kind="incident", category="mfa", priority="P3"),
          T("No Okta Verify push prompts - Bhavana Shetty",
            "Okta Verify stopped sending push prompts on my iPhone about a week ago; I've been using the 6-digit code. Riya had the same "
            "and IAM re-enrolled her - can you do that for me?",
            "Before re-enrolling, checked the device: iPhone clock was 4 minutes off (automatic date & time disabled). Push challenges "
            "were expiring before the device accepted them. Enabled automatic time; push worked immediately, no re-enrolment needed. "
            "Note for KB: check device time sync before re-enrolling; the April re-enrolment probably worked only because re-enrolment "
            "re-syncs the factor.",
            "Bhavana Shetty", "Deepak Verma", "2026-07-01", resolved="2026-07-01", group="IT Service Desk", kind="incident", category="mfa",
            priority="P3"),
      ],
      slack=[
          S("#it-helpdesk", [
              ("Bhavana Shetty", "2026-07-01T11:05", "Okta Verify isn't sending push prompts again. Riya said IAM re-enrolled her for the same thing - can someone do mine?"),
              ("Deepak Verma", "2026-07-01T11:12", "Before we re-enrol - is 'Set Automatically' on for date & time on your phone? Saw this last week."),
              ("Bhavana Shetty", "2026-07-01T11:15", "It was off... turned it on and the push just arrived. Huh."),
              ("Deepak Verma", "2026-07-01T11:16", "That's the actual cause most of the time. Re-enrolment works by accident."),
              ("Kavya Reddy", "2026-07-01T11:25", "The KB article only says re-enrol. I'll add the time-sync check as step 1 - and Riya's April ticket should probably be annotated."),
              ("Lakshmi Narayanan", "2026-07-01T11:30", "Please do. Re-enrolling is 10 minutes of the user's time; the time check is 10 seconds."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-066
    E("EVT-066", "contradictory_resolution", "home_internet_reimbursement_two_decisions", "2026-06-12",
      ["Ethan Brooks", "Ishita Bose", "Ramesh Babu", "Alok Mishra", "Shalini Menon", "Manoj Venkatesh", "Meera Krishnan"],
      "Accounts Payable & Procurement", system="Zoho Expense", policy="Travel & Expense Reimbursement Policy",
      summary="Two remote employees claimed home internet. Ethan Brooks (March) was approved Rs 1,500/month by Ramesh Babu 'as a remote "
              "designation allowance'; Ishita Bose (June) was rejected by Alok Mishra because home internet is 'not in the policy'. The "
              "T&E policy is silent on home internet (only mobile bills are listed). Finance has not decided; both tickets remain as "
              "precedent and Ishita's appeal is open.",
      outcome="unresolved", drift=False, related_events=["EVT-056"], tags=["conflict", "expenses", "remote", "unresolved", "demo"],
      demo={"query": "Can remote employees claim home internet on expenses?", "expected_conflict": True},
      tickets=[
          T("Home internet reimbursement - remote employee (US) - Ethan Brooks",
            "As a fully remote employee I'd like to claim my home internet (USD 60/month, approx Rs 5,000). Manoj has approved on his side. "
            "The T&E policy lists mobile bills but doesn't mention internet.",
            "Approved at Rs 1,500/month (in line with the mobile-bill cap in T&E 3.2, treated as an equivalent connectivity allowance for "
            "designated remote roles) by Ramesh Babu 27-Mar with manager approval. Claim monthly under 'Connectivity'.",
            "Ethan Brooks", "Ramesh Babu", "2026-03-26", resolved="2026-03-27", group="Finance AP", category="expenses",
            approvers=["Manoj Venkatesh"], work_notes="Policy silent; approved by analogy to mobile cap."),
          T("Home broadband claim rejected - remote employee - Ishita Bose",
            "My broadband claim (Rs 1,199/month, Jio Fiber) was rejected as 'not a reimbursable category'. I'm a designated remote employee "
            "and Ethan in Marketing gets Rs 1,500/month for the same thing since March. Meera approved on her side. Please review.",
            "Rejected 12-Jun by Alok Mishra: home internet is not listed in the T&E policy (v5) and section 3.4 says unlisted items are not "
            "reimbursable without prior CFO approval. Appeal escalated to Shalini Menon 15-Jun; Shalini to raise with the CFO whether a "
            "remote connectivity allowance exists. No decision as of Sep-2026 - ticket OPEN.",
            "Ishita Bose", "Alok Mishra", "2026-06-12", status="open", group="Finance AP", category="expenses", approvers=["Meera Krishnan"],
            work_notes="Contradicts March approval for Ethan Brooks. Awaiting CFO decision."),
      ],
      emails=[
          M("Home internet claims - two different decisions",
            [("Ishita Bose", ["Alok Mishra", "Meera Krishnan"], "2026-06-12T16:10",
              "Hi Alok,\n\nMy broadband claim was rejected as not reimbursable, but Ethan Brooks (also designated remote) has been reimbursed "
              "Rs 1,500/month since March under the same policy. Either we both should or neither of us should - can Finance decide one "
              "way and tell remote employees?\n\nIshita"),
             ("Alok Mishra", ["Ishita Bose", "Meera Krishnan", "Shalini Menon"], "2026-06-15T10:20",
              "Hi Ishita,\n\nYou're right that it's inconsistent. The policy doesn't list home internet, and 3.4 says unlisted items need "
              "CFO pre-approval, which is why I rejected it; Ramesh approved Ethan's by analogy to the mobile cap. I've escalated to "
              "Shalini to get a proper answer rather than two analysts guessing.\n\nAlok"),
             ("Shalini Menon", ["Ishita Bose", "Alok Mishra", "Meera Krishnan", "Ramesh Babu"], "2026-06-16T12:00",
              "Thanks both. Position for now: Ethan's approval stands (we won't claw back a decision we made), Ishita's stays on hold, and "
              "I'll take 'remote connectivity allowance - yes/no, and how much' to Vivek for the T&E v6 draft. Until then no new home "
              "internet approvals please, Ramesh.\n\nShalini")]),
      ]),

    # ------------------------------------------------------------------ EVT-067
    E("EVT-067", "contradictory_resolution", "admin_console_access_granted_vs_denied", "2026-04-21",
      ["Preeti Nambiar", "Sameer Khan", "Rohan Mehta", "Nikhil Bhatt", "Kavya Reddy", "Anita Desai"], "Identity & Access Management",
      system="AlgoWorks Admin Console", policy="Privileged Access & Admin Console Policy",
      summary="Two Support Engineers requested AlgoWorks Admin Console read-only. Preeti Nambiar (January, policy v1) was granted it by Rohan "
              "Mehta with a manager attestation instead of the training; Sameer Khan (April, after policy v2 removed that option) was denied "
              "by Nikhil Bhatt pending the training and never re-requested. The same team therefore has one member with access obtained "
              "without training and another without access - and Kunal Shah's May request (EVT-003) shows the policy applied correctly.",
      outcome="unresolved", drift=False, related_events=["EVT-003"], tags=["conflict", "privileged-access", "admin-console", "demo"],
      demo={"query": "Can Customer Success get access to the AlgoWorks Admin Console?", "expected_conflict": True},
      tickets=[
          T("AlgoWorks Admin Console read-only - Preeti Nambiar (Support Engineer)",
            "Requesting console-readonly to look up tenant config and device status for Tier 1 tickets instead of pinging engineers. "
            "Manager: Anita Desai.",
            "Approved by Anita Desai 15-Jan and Rohan Mehta (Platform EM) 16-Jan. Training 'Handling Customer Data' not yet completed - "
            "Rohan accepted a manager attestation in lieu (permitted under Privileged Access policy v1). Added to console-readonly 16-Jan. "
            "Training to be completed within 30 days (not tracked).",
            "Preeti Nambiar", "Kavya Reddy", "2026-01-15", resolved="2026-01-16", group="IAM", approvers=["Anita Desai", "Rohan Mehta"],
            sensitivity="restricted", work_notes="Attestation route (v1). Training completion never verified."),
          T("AlgoWorks Admin Console read-only - Sameer Khan (TAM)",
            "Requesting console-readonly for enterprise account troubleshooting (same as Preeti has). Manager: Anita Desai.",
            "DENIED 22-Apr by Nikhil Bhatt: policy v2 (27-Apr draft, effective on publication) removes the attestation option; training "
            "'Handling Customer Data' must be completed first, no exceptions. Requester to complete training and re-raise. [No re-request "
            "as of Sep-2026; Sameer notes in Slack that he still handles enterprise escalations via Preeti's access.]",
            "Sameer Khan", "Nikhil Bhatt", "2026-04-21", resolved="2026-04-22", status="closed", group="IAM", approvers=["Anita Desai"],
            sensitivity="restricted", work_notes="Denied under v2 rules a week before v2 was published."),
      ],
      emails=[
          M("Admin Console access - inconsistent outcomes on the CS team",
            [("Anita Desai", ["Nikhil Bhatt", "Rohan Mehta"], "2026-04-23T09:30",
              "Nikhil, Rohan,\n\nSameer's console request was denied pending training, which I understand under the new version of the policy. "
              "But Preeti got the same access in January with just my attestation, and as far as I know she still hasn't done the course. "
              "So one of my Support Engineers has access without training and the other has training-pending and no access. Can we agree "
              "one rule for the team and apply it both ways?\n\nAnita"),
             ("Nikhil Bhatt", ["Anita Desai", "Rohan Mehta"], "2026-04-23T11:15",
              "Fair point. Rule from v2 onward: training first, no attestations - that's why Sameer was denied. For Preeti I'd rather not "
              "revoke mid-quarter; Rohan, can you make sure she completes the course before the Q2 review or she comes out at the review? "
              "Sameer just needs to do the 40-minute course and re-raise.\n\nNikhil"),
             ("Rohan Mehta", ["Anita Desai", "Nikhil Bhatt"], "2026-04-23T12:00",
              "Agreed - I'll chase Preeti. In hindsight the attestation route was a mistake; glad v2 removes it.\n\nRohan")],
            sensitivity="restricted"),
      ],
      slack=[
          S("#customer-success", [
              ("Sameer Khan", "2026-04-22T15:10", "My Admin Console request got denied - need to do the 'Handling Customer Data' course first. Preeti, did you have to do that?"),
              ("Preeti Nambiar", "2026-04-22T15:12", "No - Anita vouched for me in January and Rohan approved. I keep meaning to do the course."),
              ("Sameer Khan", "2026-04-22T15:14", "So same team, same role, different answer. Cool cool."),
              ("Anita Desai", "2026-04-22T15:30", "The rules changed in April (v2 of the policy). I'll sort this out with Nikhil and Rohan - meanwhile Sameer, do the course, it's 40 minutes."),
              ("Sameer Khan", "2026-06-10T10:05", "Still haven't found a slot for the course - Preeti's been looking things up for me. Will do it before the enterprise QBRs, promise."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-068
    E("EVT-068", "contradictory_resolution", "jira_project_creation_ownership", "2026-08-03",
      ["Ankit Chawla", "Manoj Venkatesh", "Shruti Joshi", "Deepak Verma", "Rohan Mehta", "Karthik Iyer"], "IT Service Desk & Endpoint",
      system="Jira", policy="Application Access Request Policy",
      summary="Two Marketing managers asked for a new Jira project. Ankit Chawla (May) got 'MKT' created by the Service Desk (Shruti Joshi) "
              "the same day; Manoj Venkatesh (August) was told by the Service Desk that Jira projects are created by Platform Backend and "
              "waited four days for Rohan Mehta. Jira is owned by Platform Backend per the Systems Directory, but the Service Desk still "
              "holds admin rights from before the ownership change - so the answer depends on who picks up the ticket.",
      outcome="resolved_inconsistently", drift=False, tags=["conflict", "jira", "ownership"],
      demo={"query": "How do I get a new Jira project created?", "expected_conflict": True},
      tickets=[
          T("New Jira project for Marketing content tracking (key: MKT)",
            "Per the new content approval SOP we're moving the content calendar from a spreadsheet to Jira. Please create a Jira project "
            "'Marketing Content' with key MKT, Kanban template, and add the Content & Brand and Demand Gen teams.",
            "Created Jira project MKT (Kanban, company-managed) and added groups mkt-brand and mkt-demandgen as project members; Ankit "
            "Chawla set as project lead. Done 15-May.",
            "Ankit Chawla", "Shruti Joshi", "2026-05-15", resolved="2026-05-15", group="IT Service Desk", category="jira",
            work_notes="Created by Service Desk using legacy Jira admin rights."),
          T("New Jira project for Demand Gen campaigns (key: DG)",
            "Need a separate Jira project 'Demand Gen Campaigns' (key DG) - MKT is getting crowded with website and content tickets. Same "
            "setup as MKT please.",
            "03-Aug (Deepak Verma): Jira is owned by Platform Backend per the Systems Directory; project creation requests go to Platform "
            "(Jira admins) - reassigned to Rohan Mehta / #eng-platform. 07-Aug: Rohan created project DG (Kanban) and added mkt-demandgen. "
            "Note from Rohan: Service Desk still has Jira admin from before the handover; either remove it or agree they can create "
            "projects - currently inconsistent.",
            "Manoj Venkatesh", "Rohan Mehta", "2026-08-03", resolved="2026-08-07", group="Platform Backend", category="jira",
            work_notes="Routed to Platform; 4-day wait. Same request type handled by Service Desk in May."),
      ],
      emails=[
          M("Who creates Jira projects? Two answers in three months",
            [("Manoj Venkatesh", ["Rajesh Kumar", "Rohan Mehta"], "2026-08-05T09:50",
              "Rajesh, Rohan,\n\nIn May Ankit asked the Service Desk for a Jira project and had it the same day. I asked last Monday and was "
              "told Jira projects are 'Platform Backend only' and to wait for Rohan. Four days later, still no project and my team is "
              "logging campaign tasks in a spreadsheet again. I don't mind who does it - but could you agree between you and put it on the "
              "Jira page in the Systems Directory?\n\nManoj"),
             ("Rohan Mehta", ["Manoj Venkatesh", "Rajesh Kumar"], "2026-08-05T13:30",
              "Manoj - creating DG now, sorry. Rajesh: Platform took Jira ownership in January but the Service Desk kept admin rights, so "
              "both of us can do it and each of us thinks the other should. Proposal: Service Desk creates projects from a standard template "
              "on request (it's a 5-minute task and you're staffed for tickets); Platform keeps schemes, workflows and integrations. I'll "
              "update the Systems Directory entry if you agree.\n\nRohan"),
             ("Rajesh Kumar", ["Rohan Mehta", "Manoj Venkatesh"], "2026-08-06T10:10",
              "Agree. Shruti will own it; please share the template. Until the directory is updated my team will keep routing to you, "
              "so let's do it this week.\n\nRajesh")]),
      ],
      slack=[
          S("#eng-platform", [
              ("Deepak Verma", "2026-08-03T11:40", "@Rohan Jira project request from Manoj (key DG) - reassigned to you since Platform owns Jira. Ticket in your queue."),
              ("Karthik Iyer", "2026-08-03T11:45", "Didn't the Service Desk create MKT for Ankit in May? Why is this one different?"),
              ("Deepak Verma", "2026-08-03T11:48", "Shruti did that one. The directory says Platform though, so I'm following the directory."),
              ("Rohan Mehta", "2026-08-07T09:20", "DG created. Rajesh and I have agreed the Service Desk creates projects from the template going forward; I'll fix the directory entry."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-069
    E("EVT-069", "contradictory_resolution", "snowflake_query_timeouts_two_answers", "2026-09-10",
      ["Harsha Vardhan", "Meenakshi Sundaram", "Ananya Chatterjee", "Manish Tiwari", "Suresh Pillai", "Ashwin Raman"],
      "Data & Analytics Engineering", system="Snowflake Data Warehouse", policy="Snowflake Data Access Policy",
      project="Snowflake Cost Optimization",
      summary="Two FP&A analysts hit 5-minute query timeouts on the same AOP cost-centre query after the warehouse restructure. Harsha "
              "Vardhan (June) had his warehouse bumped from S to M by Ananya Chatterjee; Meenakshi Sundaram (September) was told by Manish "
              "Tiwari to use the Metabase 'AOP Actuals' dashboard instead and the ticket closed 'won't fix'. FP&A now has one analyst on a "
              "bigger warehouse and one told there is no SQL path - unresolved.",
      outcome="unresolved", drift=False, related_events=["EVT-044"], tags=["conflict", "snowflake", "performance", "unresolved"],
      demo={"query": "My Snowflake query for FP&A times out after 5 minutes - what should I do?", "expected_conflict": True},
      tickets=[
          T("Snowflake query timeout (5 min) on WH_FIN - AOP actuals by cost centre - Harsha Vardhan",
            "Since the warehouse changes my monthly actuals-by-cost-centre query on FIN_MART times out at 5 minutes on WH_FIN. It used to "
            "take ~3 min on the old shared warehouse. Need it for the AOP baseline.",
            "WH_FIN was sized S in the restructure. Query plan shows a large join on FIN_MART.GL_LINES; raised WH_FIN to M for the FP&A "
            "role (resource monitor adjusted +200 credits/month with Nithin's OK). Query now 1m40s. Closed.",
            "Harsha Vardhan", "Ananya Chatterjee", "2026-06-22", resolved="2026-06-23", group="Data Engineering", kind="incident",
            category="performance", priority="P3", work_notes="Fix: bigger warehouse."),
          T("Snowflake query times out - AOP cost centre actuals - Meenakshi Sundaram (new FP&A analyst)",
            "Running the same query Harsha uses for AOP actuals (he shared it) and it times out after 5 minutes on WH_FIN. Harsha says his "
            "runs in under 2 min. I joined 7-Sep - am I on a different warehouse?",
            "User is on WH_FIN (S) via the FIN-FPA role bundle; Harsha's user was individually moved to WH_FIN_M in June. Per the cost "
            "optimisation decisions, we are not adding more users to the M warehouse for ad-hoc queries - the 'AOP Actuals by Cost Centre' "
            "Metabase dashboard (built July) serves this need without SQL. Advised to use the dashboard. Closing as WON'T FIX. If FP&A "
            "needs SQL at scale, Suresh and Ashwin to agree a warehouse budget.",
            "Meenakshi Sundaram", "Manish Tiwari", "2026-09-10", resolved="2026-09-11", status="closed", group="Data Engineering",
            kind="incident", category="performance", priority="P3", work_notes="Contradicts June resolution for Harsha."),
      ],
      emails=[
          M("FP&A Snowflake access - two analysts, two answers",
            [("Ashwin Raman", ["Suresh Pillai"], "2026-09-14T09:20",
              "Suresh,\n\nHarsha got a bigger warehouse in June for the AOP query; Meenakshi asked for the same thing last week and was told "
              "to use a dashboard instead. Both are on my team doing the same work. Which is FP&A's actual entitlement - SQL on a warehouse "
              "we pay for, or dashboards only? I'm fine either way as long as it's one answer.\n\nAshwin"),
             ("Suresh Pillai", ["Ashwin Raman"], "2026-09-14T11:40",
              "You're right that it's inconsistent - Ananya's June fix predates the cost decisions and Manish applied them literally. "
              "Proposal: FP&A gets WH_FIN at M during the AOP window (Aug-Dec) with a 600-credit budget Nithin owns, both analysts on it; "
              "from January it drops back to S and the dashboards are the primary path. If you agree I'll raise the CHG. Not yet decided.\n\nSuresh")]),
      ],
      slack=[
          S("#eng-data", [
              ("Meenakshi Sundaram", "2026-09-10T14:10", "Hi! My AOP actuals query times out at 5 min on WH_FIN. Harsha's identical query runs in 2 min - is there a setting I'm missing?"),
              ("Manish Tiwari", "2026-09-10T14:20", "Harsha's on WH_FIN_M from a June ticket. We're not adding people to M for ad-hoc SQL - the 'AOP Actuals by Cost Centre' dashboard in Metabase does what you need."),
              ("Harsha Vardhan", "2026-09-10T14:25", "The dashboard doesn't let me pivot by project code though, that's why I use SQL."),
              ("Ananya Chatterjee", "2026-09-10T14:30", "I moved Harsha before the cost decisions, so we're inconsistent here. @Suresh call?"),
              ("Suresh Pillai", "2026-09-10T15:05", "Let me talk to Ashwin about an FP&A warehouse budget for the AOP window. Until then Meenakshi, use the dashboard or have Harsha run the pivot."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-070
    E("EVT-070", "contradictory_resolution", "referral_bonus_timing_two_answers", "2026-07-14",
      ["Karthik Iyer", "Aditya Rao", "Rakesh Nair", "Fatima Sheikh", "Rohit Sinha", "Vijay Kumar"], "Talent Acquisition",
      system="Greenhouse ATS", policy="Employee Referral Bonus Policy",
      summary="Two engineers asked when their referral bonus would be paid. Rakesh Nair (February, HR Ops) said 'in the payroll after the "
              "referred employee completes 90 days'; Fatima Sheikh (July, HRBP) said 'after 6 months, in the following payroll cycle'. The "
              "policy was changed from 6 months to 90 days in April 2026 (v2), so Fatima's July answer follows the superseded v1 - and "
              "Aditya's bonus is now late. Payroll is still waiting for TA confirmation.",
      outcome="unresolved", drift=False, tags=["conflict", "referral", "hr", "payroll", "demo"],
      demo={"query": "When is the referral bonus paid?", "expected_conflict": True},
      tickets=[
          T("Referral bonus timing - Karthik Iyer (referred Daniel Fernandes' replacement hire, joined 12-Jan)",
            "I referred Arnav (SWE, joined 12 January) via Greenhouse. When is the referral bonus paid and how much for an engineering role?",
            "Per the Referral Bonus Policy (v2 draft, effective April - confirmed with Rohit Sinha): Rs 50,000 for Engineering roles, paid "
            "in the payroll cycle after the referred employee completes 90 days (i.e. April payroll if Arnav is active on 12-Apr). TA will "
            "confirm to Payroll. [Paid in April payroll - confirmed by Vijay Kumar 30-Apr.]",
            "Karthik Iyer", "Rakesh Nair", "2026-02-10", resolved="2026-02-10", group="HR Ops", category="hr-query"),
          T("Referral bonus not received - Aditya Rao (referred Ishaan Roy, joined 30-Jun)",
            "I referred Ishaan Roy (Employer Branding, joined 30 June). HR said the bonus is paid after the referred person completes 6 "
            "months - but Karthik got his after 3 months in April. Which is it, and when will mine be paid?",
            "14-Jul (Fatima Sheikh): bonus is paid after the referred employee completes 6 months of service, in the following payroll "
            "cycle - i.e. January 2027 payroll. Rs 25,000 for non-engineering roles. Closed. [Re-opened 22-Sep by Rohit Sinha: the policy "
            "changed to 90 days in April (v2); the answer above follows v1. Ishaan completes 90 days on 28-Sep; bonus should be in the "
            "October payroll. Awaiting Payroll confirmation - OPEN.]",
            "Aditya Rao", "Fatima Sheikh", "2026-07-14", status="open", group="HR Ops", category="hr-query",
            work_notes="Answered from superseded policy v1; contradicts February answer and current v2."),
      ],
      slack=[
          S("#people-ops", [
              ("Aditya Rao", "2026-09-21T10:10", "Referral bonus question - HR told me in July it's paid after 6 months, but Karthik got his after 90 days in April. Ishaan hits 90 days next week. Which rule applies?"),
              ("Rakesh Nair", "2026-09-21T10:20", "90 days - the policy went to v2 in April. Who told you 6 months?"),
              ("Aditya Rao", "2026-09-21T10:21", "Fatima, on the ticket in July."),
              ("Fatima Sheikh", "2026-09-21T10:35", "That was the rule when I last processed one - sorry, I missed the April change. Rohit, can you confirm and I'll re-open the ticket?"),
              ("Rohit Sinha", "2026-09-22T09:15", "Confirmed: 90 days, Rs 25,000, October payroll. Re-opening the ticket and telling Vijay. We need one owner for these questions - TA, not HR Ops or HRBPs."),
              ("Vijay Kumar", "2026-09-22T09:30", "Payroll will include it in October once TA sends the confirmation form. Nothing received yet."),
          ]),
      ]),
]
