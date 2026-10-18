"""Layer 6/7 - Policy-practice drift events EVT-050..EVT-062 (with derived artifacts).

Every event here contradicts a specific clause of a deliberately stale Layer 5 policy.
`drift_note` states the policy clause vs. the observed practice so the demo answers can be verified.
"""
from events.dsl import E, T, M, S, D

EVENTS = [
    # ------------------------------------------------------------------ EVT-050  (D1: access approval when manager unavailable)
    E("EVT-050", "policy_drift", "access_approval_sla_override", "2026-08-25",
      ["Ritika Sharma", "Natasha D'Souza", "Kavya Reddy", "Vinod Krishnamurthy", "Nikhil Bhatt", "Sonal Mehra", "Megha Patil", "Rahul Kapoor"],
      "Identity & Access Management", system="Salesforce CRM", policy="Application Access Request Policy",
      summary="Ritika Sharma (new SDR) requested Salesforce access on her first day while her manager Natasha D'Souza was on leave for two "
              "weeks. The Application Access Request Policy says approvals must escalate to the Department Head (VP Sales) after 2 business "
              "days and IAM must never provision without recorded approval. In practice IAM approved and provisioned on day 6 after a Slack "
              "confirmation from Vinod Krishnamurthy (a different team's manager) - an undocumented '5-business-day SLA override' IAM has "
              "used since the SSO Phase 2 backlog. A second ticket (Sonal Mehra, June) shows the same pattern with a peer's confirmation.",
      outcome="resolved", drift=True,
      drift_note="POLICY (POL Application Access Request v3, s3.3/3.5): manager unavailable >2 business days -> escalate to Department Head; "
                 "IAM must not provision without recorded approval. PRACTICE (Aug-2026, Jun-2026 tickets): IAM approves after 5 business days "
                 "pending, on an informal Slack confirmation from any senior person on the requester's side, and documents it as 'SLA override'.",
      related_events=["EVT-071"], tags=["drift", "access", "salesforce", "approval", "demo"],
      demo={"query": "How do I get access to Salesforce?", "expected_drift": True},
      tickets=[
          T("Salesforce access (SDR) - Ritika Sharma",
            "Hi, I started today as an SDR on the Enterprise Sales team and need Salesforce (SDR profile, APAC lead queue). My manager "
            "Natasha D'Souza is on leave until 28 August; I don't know who else can approve. Thanks!",
            "17-Aug: approval routed to Natasha D'Souza (on leave until 28-Aug, no delegate set in Darwinbox). 19-Aug: requester chased in "
            "#it-access-requests. 24-Aug: 5 business days pending - SLA override applied per IAM practice: confirmation from Vinod "
            "Krishnamurthy (Sales Ops Manager) in Slack thread that Ritika is a confirmed SDR hire. 25-Aug: added to Okta group "
            "salesforce-users; Megha Patil assigned SDR profile + APAC queue. Natasha to acknowledge on return (acknowledged 31-Aug).",
            "Ritika Sharma", "Kavya Reddy", "2026-08-17", resolved="2026-08-25", group="IAM", approvers=["Vinod Krishnamurthy"],
            work_notes="Manager on leave; no delegate. 5-day SLA override used. Policy says escalate to Dept Head (Rahul Kapoor) - not done."),
          T("Metabase viewer access - Sonal Mehra (Sales Ops)",
            "Need Metabase viewer access for the new Customer 360 collection (I'm on the project). Manager: Vinod Krishnamurthy - he is on "
            "leave 8-19 June, so it may sit for a bit.",
            "10-Jun: approval pending with Vinod (on leave). 17-Jun: 5 business days pending - SLA override: Megha Patil (Salesforce Admin, "
            "same team) confirmed in Slack that Sonal is on the Customer 360 project. Added to metabase-viewer 17-Jun. Vinod acknowledged "
            "on return 22-Jun.",
            "Sonal Mehra", "Kavya Reddy", "2026-06-10", resolved="2026-06-17", group="IAM", approvers=["Megha Patil"],
            work_notes="Override confirmation from a peer, not a manager or Dept Head."),
      ],
      emails=[
          M("RE: Salesforce access request stuck - manager on leave",
            [("Ritika Sharma", "IT-Access-Team", "2026-08-21T10:05",
              "Hi team,\n\nMy Salesforce request has been waiting since Monday because Natasha is on leave until the 28th. I can't work the "
              "lead queue without it. Is there someone else who can approve? Rahul Kapoor is the VP but I don't want to bother him for a "
              "login.\n\nRitika"),
             ("Kavya Reddy", "Ritika Sharma", "2026-08-21T11:30",
              "Hi Ritika,\n\nNo problem - this happens a lot with leave. Our practice is: if a request has been waiting on an unavailable "
              "manager for 5 business days, we approve it ourselves with a quick confirmation from someone senior on your side that you're "
              "who the ticket says you are (your team's ops manager is fine). Yours hits 5 days on Monday; I've already asked Vinod in "
              "Slack. If you need it sooner, Rahul approving on the ticket would do it today.\n\nKavya\nIAM Analyst"),
             ("Ritika Sharma", "Kavya Reddy", "2026-08-21T11:45", "Monday is fine, thank you!\n\nRitika")]),
          M("SLA override on access requests - we need to fix the policy or the practice",
            [("Nikhil Bhatt", "Kavya Reddy", "2026-08-26T09:15",
              "Kavya,\n\nI saw the notes on Ritika's and Sonal's tickets. I know we've been doing the 5-day override since the Phase 2 backlog "
              "last December - and honestly it keeps the queue moving - but the Access Request Policy still says 'escalate to Department "
              "Head' and 'IAM must not provision without recorded approval'. If the auditors sample either ticket we have a finding: "
              "approval by a peer, not in the chain.\n\nTwo options: (1) we stop and start escalating to Dept Heads, which they will hate; "
              "(2) we write the override into the policy properly (5 business days, confirmation from the requester's Dept Head *or* a "
              "manager in the same department, logged on the ticket). I prefer (2) and I'll take it to Sandeep. Until then, please at least "
              "get confirmation from a manager in the same department, not a peer.\n\nNikhil"),
             ("Kavya Reddy", "Nikhil Bhatt", "2026-08-26T09:50",
              "Agreed on (2). For the record, since January we've applied the override 14 times; 11 confirmations were from a manager in the "
              "requester's department, 3 from peers (all Sales Ops). I'll add the same-department-manager rule to the queue checklist "
              "today.\n\nKavya")],
            sensitivity="restricted"),
      ],
      slack=[
          S("#it-access-requests", [
              ("Ritika Sharma", "2026-08-19T14:20", "Hi! My Salesforce request from Monday is still 'awaiting approval' - my manager Natasha is on leave till the 28th. Is there a way around this? :pray:"),
              ("Kavya Reddy", "2026-08-19T14:35", "Hi Ritika - it'll hit our 5-day mark on Monday and we'll push it through then with a confirmation from your side. @Vinod can you confirm Ritika is the new SDR on Natasha's team?"),
              ("Vinod Krishnamurthy", "2026-08-19T15:02", "Confirmed - Ritika joined 17-Aug as SDR, Enterprise Sales, reporting to Natasha. :+1:"),
              ("Kavya Reddy", "2026-08-25T09:40", "@Ritika done - you're in the Salesforce group, Megha is setting up your SDR profile now."),
              ("Megha Patil", "2026-08-25T10:15", "Profile + APAC queue assigned. Welcome!"),
              ("Ritika Sharma", "2026-08-25T10:20", "Thank you both!"),
          ]),
          S("#sales-ops", [
              ("Sonal Mehra", "2026-06-15T11:00", "My Metabase request is stuck with Vinod on leave. Anyone know the trick?"),
              ("Megha Patil", "2026-06-15T11:05", "IAM will approve it after 5 working days if someone confirms you're legit. I'll do it when Kavya asks."),
              ("Kavya Reddy", "2026-06-17T09:30", "@Megha can you confirm Sonal is on the Customer 360 project? Then I can close this out."),
              ("Megha Patil", "2026-06-17T09:32", "Yes she is."),
              ("Kavya Reddy", "2026-06-17T09:45", "@Sonal you're in."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-051  (D2: laptop delivery SLA)
    E("EVT-051", "policy_drift", "laptop_delivery_sla_and_loaners", "2026-07-06",
      ["Aditya Rao", "Nithin George", "Mohammed Irfan", "Deepak Verma", "Rajesh Kumar", "Sandeep Malhotra", "Meera Krishnan", "Ashwin Raman"],
      "IT Service Desk & Endpoint", system="Microsoft Intune", policy="Laptop & Endpoint Provisioning SOP",
      summary="The Laptop SOP promises replacement devices within 5 business days from a buffer stock of 4+4. Since May 2026 the buffer has "
              "been empty and MacBook Pro lead time is 3-4 weeks; the Service Desk's actual practice is 'loaner on day one, standard "
              "device when stock arrives' (14 and 12 business days in these two cases). Rajesh Kumar proposed updating the SOP; not done.",
      outcome="resolved", drift=True,
      drift_note="POLICY (Laptop & Endpoint Provisioning SOP v4, s2.2-2.3): replacement device delivered within 5 business days; buffer stock "
                 "of 4 MacBook Pros + 4 ThinkPads; loaner only when repair exceeds 2 days. PRACTICE (Jun-Jul 2026): buffer stock exhausted; "
                 "loaner issued immediately by default; standard device in 12-14 business days. SOP not updated.",
      tags=["drift", "laptop", "sla", "endpoint"],
      demo={"query": "How long does a replacement laptop take?", "expected_drift": True},
      tickets=[
          T("Laptop replacement - swollen battery - Aditya Rao (MacBook Pro 14\", 2023)",
            "My MacBook Pro's trackpad is lifting - looks like a swollen battery. Apple support says don't use it. I need a replacement; "
            "I'm on the portal revamp and can't be without a machine. Manager: Meera Krishnan.",
            "29-Jun: device KT-LT-0198 collected for safety; loaner MacBook Air (KT-LN-004) issued same day. Replacement MacBook Pro 14\" "
            "not in stock (buffer stock 0 since May; vendor lead time 3-4 weeks for M-series). Ordered 29-Jun on PO KT-PO-26-0612. Delivered "
            "17-Jul (14 business days), enrolled and handed over 17-Jul 15:00; loaner returned. Note: SOP 5-day target not met - stock issue.",
            "Aditya Rao", "Mohammed Irfan", "2026-06-29", resolved="2026-07-17", group="IT Service Desk", category="laptop",
            approvers=["Meera Krishnan"], work_notes="Loaner-first practice. Buffer stock empty. Vendor lead time 3-4 weeks."),
          T("Laptop refresh (4-year cycle) - Nithin George (ThinkPad T14 Gen 2)",
            "My ThinkPad is 4 years old this month and the battery lasts under an hour. Requesting the standard refresh. Manager: Ashwin Raman.",
            "06-Jul: approved by Ashwin. No ThinkPad T14 in buffer stock; ordered on PO KT-PO-26-0631 (Lenovo lead time ~2 weeks). Loaner "
            "ThinkPad (KT-LN-011) issued 07-Jul. New device delivered 22-Jul (12 business days), provisioned and handed over 22-Jul; loaner "
            "returned. Old device wiped 24-Jul.",
            "Nithin George", "Deepak Verma", "2026-07-06", resolved="2026-07-22", group="IT Service Desk", category="laptop",
            approvers=["Ashwin Raman"]),
      ],
      emails=[
          M("Laptop stock and the 5-day SLA - proposal to update the SOP",
            [("Mohammed Irfan", "Rajesh Kumar", "2026-07-03T16:20",
              "Rajesh,\n\nWe have zero MacBook Pros and one ThinkPad in buffer stock, and Apple's lead time for the 14\" M-series is 3-4 weeks. "
              "Every replacement since May has been loaner-first and 2-3 weeks for the real device. The SOP still says 5 business days and a "
              "4+4 buffer. Either we get budget to rebuild the buffer (about Rs 9 lakh) or we change the SOP to say what we actually do.\n\nMohammed"),
             ("Rajesh Kumar", ["Sandeep Malhotra"], "2026-07-06T10:05",
              "Sandeep - forwarding Mohammed's note. Reality since May: loaner on day one, standard device in 2-3 weeks. The SOP promises 5 "
              "days. I'd like to (a) ask Finance for Rs 9 lakh to rebuild the buffer in the FY27 plan and (b) update the SOP now to "
              "'loaner within 1 business day; standard device within 15 business days' so we stop setting expectations we can't meet.\n\nRajesh"),
             ("Sandeep Malhotra", ["Rajesh Kumar"], "2026-07-06T14:30",
              "Put the buffer in the AOP request. On the SOP - draft the change and send it to me; let's not publish a 15-day SLA until we "
              "know whether the buffer gets funded.\n\nSandeep")]),
      ],
      slack=[
          S("#it-helpdesk", [
              ("Aditya Rao", "2026-07-08T11:40", "Any update on my MacBook replacement? The Air is fine but I can't run the full portal build on 8GB. Ticket says 'awaiting stock'."),
              ("Mohammed Irfan", "2026-07-08T11:48", "Sorry Aditya - no Pros in stock and Apple is quoting 3-4 weeks. Realistically week of 14-Jul. I know the wiki says 5 days; we haven't had buffer stock since May."),
              ("Meera Krishnan", "2026-07-08T11:55", "Is there a way to get a loaner Pro instead of an Air? Two of my team are in the same boat."),
              ("Mohammed Irfan", "2026-07-08T12:00", "All loaner Pros are out. If the FY27 buffer request goes through this stops happening."),
              ("Aditya Rao", "2026-07-17T15:10", "Got the new machine, thanks Mohammed. 14 working days for the record :sweat_smile:"),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-052  (D3: CHG for app deployments)
    E("EVT-052", "policy_drift", "change_request_not_required_for_gitops_deploys", "2026-04-30",
      ["Karthik Iyer", "Daniel Fernandes", "Varun Chandra", "Rohan Mehta", "Siddharth Jain", "Harish Gowda"], "Cloud Infrastructure & Security",
      system="ArgoCD Deployment Platform", policy="Change Management Policy", project="AlgoWorks Fleet v4 API Platform Migration",
      summary="Engineers keep asking whether a production deployment needs a Change Request. The Change Management Policy (v2) says all "
              "production application deployments are Normal changes requiring a CHG and CAB approval. Since the ArgoCD go-live (Dec 2025), "
              "the operating rule is that a merged GitOps PR is the approval and CHGs are only for infrastructure - decided at CAB in "
              "September 2025 (EVT-042) but never written into the policy. Two CHGs were raised and cancelled in April and July.",
      outcome="resolved", drift=True,
      drift_note="POLICY (Change Management v2, s2/s3.1/s4): all production application deployments are Normal changes -> CHG + CAB approval. "
                 "PRACTICE (since 1-Dec-2025): merged PR in algoworks-deploy is the approval for standard app deployments; CHG only for infra/network/identity/DB. "
                 "Source of practice: CAB decision 2-Sep-2025 (EVT-042). Policy never updated.",
      related_events=["EVT-042", "EVT-073"], tags=["drift", "change-management", "gitops", "demo"],
      demo={"query": "Do I need a change request (CHG) to deploy to production?", "expected_drift": True},
      tickets=[
          T("Change: deploy algoworks-api-v4 1.3.0 to production (v4 rate-limiting tier)",
            "Raising a CHG for the production deployment of algoworks-api-v4 1.3.0 (adds the rate-limiting tier) as per the Change "
            "Management Policy - deployments are Normal changes. Planned window: Tue 05-May 11:00 IST. Rollback: ArgoCD rollback to 1.2.4. "
            "PR algoworks-deploy#918 approved by Priya Shah.",
            "CANCELLED by Varun Chandra 30-Apr: 'Not required. Standard application deployments via ArgoCD are approved by the merged "
            "algoworks-deploy PR (CAB decision Sep-2025). CHGs are for infra/network/identity/DB changes only. Please deploy via the PR.' "
            "Deployed 05-May 11:05 via PR #918.",
            "Karthik Iyer", "Varun Chandra", "2026-04-30", resolved="2026-04-30", status="cancelled", group="Cloud Infrastructure",
            kind="change", category="application-change", priority="P3",
            work_notes="Requester followed the written policy; cancelled per unwritten practice."),
          T("Change: production deployment of telemetry-ingest 2.8 (new Kinesis DLQ)",
            "Per the Change Management Policy, requesting CAB approval for deploying telemetry-ingest 2.8 which adds the dead-letter queue "
            "for poison records (postmortem action PLAT-2210). Window Thu 30-Jul 10:00. Rollback via ArgoCD.",
            "CANCELLED by Siddharth Jain 23-Jul: 'App deploys don't need a CHG - merged PR in algoworks-deploy is the approval. The DLQ "
            "itself (new SQS queue) IS infra - that part was covered by CHG raised by Harish for the Terraform change last week. Deploy the "
            "app via the PR.' Deployed 30-Jul via algoworks-deploy#1041.",
            "Daniel Fernandes", "Siddharth Jain", "2026-07-23", resolved="2026-07-23", status="cancelled", group="Cloud Infrastructure",
            kind="change", category="application-change", priority="P3"),
      ],
      emails=[
          M("Do app deploys need a CHG? The policy and CAB disagree",
            [("Karthik Iyer", ["Varun Chandra", "Rohan Mehta"], "2026-04-30T15:40",
              "Varun, Rohan,\n\nI raised a CHG for the 1.3.0 deploy because the Change Management Policy on Confluence (v2) explicitly says "
              "'all production application deployments' are Normal changes needing CAB. Varun cancelled it saying app deploys are covered "
              "by the GitOps PR. I'm fine either way, but the written policy says the opposite of what we do, and new joiners (Tanvi starts "
              "in August, plus the campus hires) will read the policy. Can we get it updated?\n\nKarthik"),
             ("Varun Chandra", ["Karthik Iyer", "Rohan Mehta"], "2026-04-30T16:25",
              "You're right, and it's on me - the CAB decision from September says I'd update the policy and I never did. Operating rule "
              "since 1 Dec: merged algoworks-deploy PR = approval for standard app deployments; CHG for Terraform/network/Okta/DB/new services. "
              "I'll draft v3 of the policy with a 'GitOps standard deployment' category this month.\n\nVarun"),
             ("Rohan Mehta", ["Varun Chandra", "Karthik Iyer"], "2026-04-30T16:40",
              "Please do - I've answered this question in Slack at least five times. I'll add it to the engineering onboarding guide in "
              "the meantime.\n\nRohan")]),
      ],
      slack=[
          S("#devops-sre", [
              ("Karthik Iyer", "2026-04-30T14:50", "Quick check before Tuesday's CAB - I've raised a CHG for the 1.3.0 prod deploy. Is that the right process? The policy page says yes."),
              ("Varun Chandra", "2026-04-30T14:58", "No CHG needed for app deploys - the merged algoworks-deploy PR is the approval. That's been the rule since ArgoCD went live in December. Cancelling it."),
              ("Karthik Iyer", "2026-04-30T15:01", "The Change Management Policy (v2, June 2025) says 'all production application deployments' need CAB though. Which one wins?"),
              ("Harish Gowda", "2026-04-30T15:03", "The CAB decision from Sep 2025 wins in practice. The policy just never got updated."),
              ("Varun Chandra", "2026-04-30T15:05", "Correct, and that's my miss. Policy update coming."),
          ]),
          S("#devops-sre", [
              ("Daniel Fernandes", "2026-07-23T10:10", "Raised a CHG for the telemetry-ingest 2.8 deploy (DLQ). Do I need to present at CAB tomorrow?"),
              ("Siddharth Jain", "2026-07-23T10:15", "Nope - app deploy = PR approval. The SQS queue Harish added via Terraform last week was the CHG-worthy bit and that's done. Cancelling yours; just merge the deploy PR in the window."),
              ("Daniel Fernandes", "2026-07-23T10:17", "Got it. The policy page really should say that :upside_down_face:"),
              ("Rohan Mehta", "2026-07-23T10:20", "It's in the eng onboarding guide now at least. Varun's v3 is still 'in draft'."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-053  (D4: Friday deployments)
    E("EVT-053", "policy_drift", "friday_deploy_freeze_relaxed", "2026-06-19",
      ["Meera Krishnan", "Aditya Rao", "Arjun Venkataraman", "Rohan Mehta", "Priya Shah", "Neha Agarwal"], "Web & Mobile Frontend",
      system="AlgoWorks Fleet Customer Portal", policy="Deployment & Release Process SOP", project="Customer Portal Revamp",
      summary="On Friday 19-Jun Aditya Rao deployed a portal fix at 11:30. Meera Krishnan objected citing the Deployment & Release SOP "
              "(no Friday production deployments). Arjun Venkataraman confirmed the freeze was relaxed at the 12-Mar Engineering all-hands "
              "('Friday deploys allowed before 14:00 IST if behind a feature flag or trivially reversible') - a decision recorded only in "
              "the all-hands notes and a Slack thread; the SOP (v3, Apr 2025) still states the freeze.",
      outcome="resolved", drift=True,
      drift_note="POLICY (Deployment & Release Process SOP v3, s1.2): no production deployments on Fridays. PRACTICE (since 12-Mar-2026 "
                 "Engineering all-hands): Friday deploys permitted before 14:00 IST when feature-flagged or trivially reversible. "
                 "Recorded in all-hands notes and Slack only; SOP not updated.",
      tags=["drift", "deployment", "friday", "release"],
      demo={"query": "Are we allowed to deploy to production on a Friday?", "expected_drift": True},
      emails=[
          M("Friday deploys - what is the actual rule?",
            [("Meera Krishnan", ["Arjun Venkataraman", "Rohan Mehta"], "2026-06-19T12:10",
              "Arjun, Rohan,\n\nAditya shipped the portal export fix to production at 11:30 today (Friday). I asked him to hold and he said "
              "Friday deploys are fine before 2pm since March. The Deployment & Release SOP on Confluence says no Friday deploys, full "
              "stop. I don't mind either rule, but I need to know which one to hold my team to.\n\nMeera"),
             ("Arjun Venkataraman", ["Meera Krishnan", "Rohan Mehta"], "2026-06-19T12:45",
              "Aditya's right - at the 12 March all-hands we relaxed it: Friday deploys allowed before 14:00 IST if the change is behind a "
              "flag or trivially reversible, and the deployer stays online until 16:00. It's in the all-hands notes. The SOP wasn't updated, "
              "which is a fair complaint. Rohan, can Platform own an SOP v4 that reflects the ArgoCD world and the Friday rule?\n\nArjun"),
             ("Rohan Mehta", ["Arjun Venkataraman", "Meera Krishnan"], "2026-06-19T13:20",
              "Will do - I'll fold in the CHG/GitOps clarification at the same time since that's the other question I get weekly.\n\nRohan")]),
      ],
      slack=[
          S("#eng-platform", [
              ("Aditya Rao", "2026-06-19T11:32", "Portal export fix (PR #1207) is in prod, behind the `portal-export-v2` flag. Enabled for internal tenants only for now."),
              ("Meera Krishnan", "2026-06-19T11:40", "It's Friday - the release SOP says no Friday deploys. Please hold flag rollouts until Monday at least."),
              ("Aditya Rao", "2026-06-19T11:42", "Since the March all-hands Friday deploys are OK before 2pm if flagged. I'm online till 4."),
              ("Priya Shah", "2026-06-19T11:45", "Confirming - Arjun announced it on 12 March. Notes are in the ENG space. The SOP page is just old."),
              ("Meera Krishnan", "2026-06-19T11:50", "Then someone please update the SOP, because I've been telling my team no Fridays for three months. :expressionless:"),
              ("Neha Agarwal", "2026-06-19T11:55", "QA perspective: flagged + internal-only on a Friday is fine. Full rollout Monday please."),
              ("Arjun Venkataraman", "2026-06-19T12:50", "Meera's right that the doc is wrong. Rohan owns SOP v4. Until then: Fridays before 14:00, flagged or reversible, stay online till 16:00."),
          ]),
      ],
      docs=[
          D("Engineering All-Hands - 12 March 2026 - notes",
            "**Date:** 12 March 2026 | **Host:** Arjun Venkataraman | **Notes:** Priya Shah\n\n"
            "## Agenda\n1. Q1 delivery review (v4 migration, multi-region, portal revamp)\n2. On-call and release process changes\n3. Hiring update (campus hires)\n4. Q&A\n\n"
            "## 2. Release process changes (Arjun)\n- With ArgoCD rollbacks taking under 2 minutes and most new work behind feature flags, "
            "the blanket Friday deployment freeze is **relaxed**: **Friday production deployments are allowed before 14:00 IST provided the "
            "change is behind a feature flag or is trivially reversible, and the deploying engineer remains online until 16:00.** "
            "Month-end billing freeze (last two business days) stays.\n- Standard app deployments continue to go through the algoworks-deploy PR; no CHG.\n"
            "- Rohan Mehta to update the Deployment & Release Process SOP. *(Not done as of the June 2026 discussion.)*\n\n"
            "## 3. Hiring\n8 graduate engineers from the campus drive start July-September; buddies needed - see Swati.\n\n"
            "## 4. Q&A\n- Q: Does the Friday rule apply to mobile releases? A: No - Play/TestFlight staged rollouts follow their own 48-hour soak rule.\n"
            "- Q: What about hotfixes on Friday afternoon? A: Emergency changes as today: on-call lead approval, retrospective review.",
            doc_type="meeting_notes", space="ENG", created="2026-03-12", authors=["Priya Shah"], labels=["all-hands", "release-process"]),
      ]),

    # ------------------------------------------------------------------ EVT-054  (D5: PII access without DPO)
    E("EVT-054", "policy_drift", "pii_access_approved_without_dpo", "2026-05-12",
      ["Chitra Mohan", "Manoj Venkatesh", "Suresh Pillai", "Ananya Chatterjee", "Ravi Shankar", "Nikhil Bhatt"], "Data & Analytics Engineering",
      system="Snowflake Data Warehouse", policy="Snowflake Data Access Policy", project="Unified Customer 360 Dashboard",
      summary="Chitra Mohan (Email Marketing) was granted the snowflake-pii-reader role for customer contact data on the approval of "
              "Suresh Pillai alone. The Snowflake Data Access Policy requires written DPO sign-off for PII schemas, but the DPO left in "
              "February and was never replaced (EVT-005). Data Engineering's working rule since April: the Data Engineering Manager approves "
              "PII access with a purpose statement and a 6-month expiry. Repeated for Ravi Shankar's churn-model access in June.",
      outcome="resolved", drift=True,
      drift_note="POLICY (Snowflake Data Access v2, s2.2): PII-tagged schema access requires written DPO sign-off on the DATA ticket. "
                 "PRACTICE (since Apr-2026): Data Engineering Manager approves alone with purpose + 6-month expiry, because the DPO role is vacant "
                 "(EVT-005) and no interim was named.",
      related_events=["EVT-005", "EVT-019"], tags=["drift", "pii", "snowflake", "dpo", "demo"],
      demo={"query": "Who approves Snowflake PII access now that the DPO has left?", "expected_drift": True},
      tickets=[
          T("Snowflake PII schema access (customer contacts) - Chitra Mohan - lifecycle email segmentation",
            "For the customer lifecycle email programme I need CORE_PII.CUSTOMER_CONTACTS (email, name, role, account) joined to usage "
            "marts, to build segments in HubSpot. Jira DATA-1198 raised; manager Manoj Venkatesh approved. I understand this needs a DPO "
            "sign-off - who is that now?",
            "DATA-1198 approved by Suresh Pillai 12-May with purpose ('lifecycle segmentation; export limited to hashed id + segment "
            "label to HubSpot') and expiry 12-Nov-2026 recorded on the ticket. DPO sign-off step: N/A - role vacant since Feb-2026, no "
            "interim (see {{ticket:EVT-005#2}}); Data Eng Manager approval used per current Data team practice. Added to "
            "snowflake-pii-reader 13-May.",
            "Chitra Mohan", "Ananya Chatterjee", "2026-05-12", resolved="2026-05-13", group="Data Engineering", approvers=["Manoj Venkatesh", "Suresh Pillai"],
            sensitivity="restricted", work_notes="DPO step skipped - vacant role."),
          T("Snowflake PII access - Ravi Shankar - churn model features (driver + account contacts)",
            "The churn model needs account-level contact tenure and driver identity features from CORE_PII. Jira DATA-1233. Manager: "
            "Suresh Pillai.",
            "Approved by Suresh Pillai 30-Jun (line manager and Data Eng Manager) with purpose and expiry 31-Dec-2026. DPO sign-off: not "
            "available (vacant). Added to snowflake-pii-reader 01-Jul. Flagged for the Q3 access review.",
            "Ravi Shankar", "Ananya Chatterjee", "2026-06-30", resolved="2026-07-01", group="Data Engineering", approvers=["Suresh Pillai"],
            sensitivity="restricted"),
      ],
      emails=[
          M("RE: DPO sign-off for PII access - who approves now?",
            [("Chitra Mohan", ["Suresh Pillai", "Manoj Venkatesh"], "2026-05-11T15:20",
              "Hi Suresh,\n\nThe Snowflake Data Access Policy says PII schema access needs written sign-off from the Data Protection Officer "
              "on the DATA ticket. I can't find a DPO in the org chart - Pradeep Chauhan left in February. Who should I ask?\n\nChitra"),
             ("Suresh Pillai", ["Chitra Mohan", "Manoj Venkatesh"], "2026-05-12T09:40",
              "Hi Chitra,\n\nThere isn't one at the moment - the role wasn't backfilled and IT leadership hasn't named an interim for "
              "data-protection sign-offs. What the Data team has been doing since April: I approve PII access myself, on the condition that "
              "the ticket states the purpose and what leaves Snowflake, and the access expires in 6 months. It's not what the policy says, "
              "and Nikhil knows we're doing it. Your ticket is approved on that basis; Ananya will add you today.\n\nSuresh"),
             ("Manoj Venkatesh", ["Suresh Pillai", "Chitra Mohan"], "2026-05-12T10:05", "Thanks Suresh. Chitra, only hashed ids and segment labels go to HubSpot - nothing else.\n\nManoj")],
            sensitivity="restricted"),
      ],
      slack=[
          S("#eng-data", [
              ("Ananya Chatterjee", "2026-05-12T10:30", "@Suresh DATA-1198 (Chitra, PII contacts) - the DPO sign-off field is empty. Do we still hold these?"),
              ("Suresh Pillai", "2026-05-12T10:35", "No - we agreed in April: I approve with purpose + 6-month expiry until someone is named DPO. Add her, note it on the ticket."),
              ("Ananya Chatterjee", "2026-05-12T10:36", "OK. That's the third one since April. Should we tell Nikhil the count?"),
              ("Suresh Pillai", "2026-05-12T10:40", "He knows; the ownership ticket is still on hold with Sandeep. I'll raise it again at the IT sync."),
              ("Nikhil Bhatt", "2026-05-12T11:15", "Seen. I'd rather you approve with an expiry than block Marketing indefinitely, but the policy needs a v3 that names an interim. Chasing Sandeep."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-055  (D6: hybrid work days)
    E("EVT-055", "policy_drift", "hybrid_work_office_days", "2026-08-05",
      ["Tanvi Deshpande", "Ayesha Khan", "Rohan Mehta", "Swati Kulkarni", "Priya Shah", "Sunita Raghavan"], "People Operations",
      system="Darwinbox HRMS", policy="Hybrid Work Policy",
      summary="New joiner Tanvi Deshpande asked HR how many days she must be in the office. HR Ops (Ayesha Khan) answered per the Hybrid "
              "Work Policy: 3 days, Tue/Wed/Thu anchor days. Her manager Rohan Mehta said the team does 2 days (Tue/Thu) since leadership "
              "relaxed the rule in April. The HRBP confirmed the relaxation is real but the policy update is 'pending with the CPO'.",
      outcome="resolved", drift=True,
      drift_note="POLICY (Hybrid Work v2, s1.1-1.2): minimum 3 days/week in office, Tue/Wed/Thu anchor days. PRACTICE (since Apr-2026): "
                 "2 days/week with team discretion on which days, agreed verbally by leadership; HR Ops still quotes 3 days; policy not updated.",
      tags=["drift", "hybrid-work", "hr", "new-joiner", "demo"],
      demo={"query": "How many days a week do I need to be in the office?", "expected_drift": True},
      tickets=[
          T("HR query: required office days per week for a new joiner (Engineering, Bengaluru)",
            "Hi HR, I joined Platform Backend on 3 August. During induction I was told 3 days a week (Tue/Wed/Thu) in office, but my team "
            "seems to come in Tuesdays and Thursdays only. Which is correct? I want to plan my commute/lease.",
            "Answered per the Hybrid Work Policy (v2): office-based employees are expected in a minimum of 3 days per week, with Tuesday, "
            "Wednesday and Thursday as anchor days. Attendance is reviewed monthly via the badge integration. Any exception is via your "
            "HRBP (Swati Kulkarni). Ticket closed. [Later note from HRBP 07-Aug: see email - leadership relaxed to 2 days in April; policy "
            "update pending.]",
            "Tanvi Deshpande", "Ayesha Khan", "2026-08-05", resolved="2026-08-05", group="HR Ops", category="hr-query",
            work_notes="Answer given from the written policy; contradicted by HRBP two days later."),
      ],
      emails=[
          M("RE: Office days - policy vs what teams are doing",
            [("Rohan Mehta", ["Swati Kulkarni"], "2026-08-06T09:30",
              "Swati,\n\nTanvi asked HR about office days and was told 3 days with Tue/Wed/Thu anchors. I've been running the team on 2 days "
              "(Tue/Thu) since April, when Arjun said leadership had agreed to relax it to 2 days with team discretion. Which is it? I don't "
              "want my new joiner getting a different answer from HR than from me.\n\nRohan"),
             ("Swati Kulkarni", ["Rohan Mehta", "Ayesha Khan"], "2026-08-07T11:10",
              "Rohan,\n\nYou're not wrong - in the April leadership meeting the CPO agreed to move to 2 days/week with team-chosen days, "
              "and Department Heads were told to apply it. The Hybrid Work Policy on Confluence was supposed to go to v3 but it's still with "
              "Sunita for sign-off, so HR Ops is answering from v2 (3 days). Ayesha - for now, please add a line to any hybrid-work answer "
              "that 'current practice is 2 days at team discretion pending the policy update'. I'll chase Sunita.\n\nSwati"),
             ("Ayesha Khan", ["Swati Kulkarni", "Rohan Mehta"], "2026-08-07T11:25",
              "Will do. I answered three of these last month from the policy page - I'll go back to those people.\n\nAyesha")]),
      ],
      slack=[
          S("#eng-platform", [
              ("Tanvi Deshpande", "2026-08-05T13:10", "Silly question - HR says 3 days in office (Tue/Wed/Thu) but I've only seen everyone here Tue and Thu. What does the team actually do?"),
              ("Rohan Mehta", "2026-08-05T13:14", "2 days, Tue and Thu. Leadership relaxed it to 2 days in April; the policy page hasn't caught up. If HR pushes back send them to me."),
              ("Priya Shah", "2026-08-05T13:16", "Yeah the 3-day thing is from last year. Most of Engineering is on 2."),
              ("Karthik Iyer", "2026-08-05T13:18", "Finance still does 3 I think. Depends on the department head."),
              ("Tanvi Deshpande", "2026-08-05T13:20", "Got it, thanks! Tue/Thu it is."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-056  (D7: expense submission window & per-diem)
    E("EVT-056", "policy_drift", "expense_window_and_per_diem", "2026-06-24",
      ["Aakash Bhatia", "Gaurav Thakur", "Ramesh Babu", "Alok Mishra", "Shalini Menon", "Natasha D'Souza"], "Accounts Payable & Procurement",
      system="Zoho Expense", policy="Travel & Expense Reimbursement Policy",
      summary="Zoho Expense auto-rejected Aakash Bhatia's 45-day-old claim per the T&E policy's 30-day rule; Finance AP approved it on "
              "appeal because 'we accept up to 60 days now'. Separately, Gaurav Thakur's APAC per-diem claim at Rs 2,500/day was rejected "
              "by the Zoho rule (policy: Rs 2,000) and then approved because the per-diem was raised to Rs 2,500 in April by CFO email. "
              "Neither change is in the policy (v5, Nov 2025) or the Zoho rules.",
      outcome="resolved", drift=True,
      drift_note="POLICY (T&E v5, s1.2/s2.3): claims within 30 days, older claims rejected; domestic per-diem Rs 2,000/day. PRACTICE (2026): "
                 "AP accepts claims up to 60 days on appeal; per-diem Rs 2,500 since Apr-2026 (CFO email). Zoho rules still enforce the old values, "
                 "so claims are auto-rejected and manually approved.",
      related_events=["EVT-072", "EVT-066"], tags=["drift", "expenses", "finance", "demo"],
      demo={"query": "What is the deadline for submitting expense claims?", "expected_drift": True},
      tickets=[
          T("Expense claim auto-rejected as 'older than 30 days' - Aakash Bhatia - Chennai customer visit (May)",
            "Zoho rejected my Chennai trip claim (Rs 18,640, expenses dated 8-10 May) saying it's more than 30 days old. I was on the "
            "Meridian renewal and then on leave. Can this be approved? Natasha has approved it on her side.",
            "Claim is 45 days from expense date. Per current AP practice we accept claims up to 60 days with manager approval - the 30-day "
            "rule in Zoho reflects the policy text but Finance has been allowing 60 days since the FY26 year-end. Manually approved by "
            "Ramesh Babu 25-Jun; included in the July payroll reimbursement run. Suggest Finance update either the policy or the Zoho "
            "rule so claims stop auto-rejecting.",
            "Aakash Bhatia", "Ramesh Babu", "2026-06-24", resolved="2026-06-25", group="Finance AP", category="expenses",
            approvers=["Natasha D'Souza"], work_notes="30-day rule overridden; 60-day practice."),
          T("Per-diem claim rejected - Rs 2,500/day exceeds policy limit - Gaurav Thakur (Kuala Lumpur + Bengaluru trip)",
            "My per-diem for the Bengaluru leg (4 days) at Rs 2,500/day was rejected by Zoho: 'exceeds domestic per diem Rs 2,000'. Natasha "
            "told the team in April that the rate is now Rs 2,500. Which is right?",
            "The domestic per-diem was raised to Rs 2,500/day effective 1-Apr-2026 by CFO email (FY27 budget note) but the T&E policy (v5) "
            "and the Zoho per-diem rule were not updated. Approved manually at Rs 2,500 x 4 by Alok Mishra 30-Jun. Raised with Shalini to "
            "update the Zoho rule.",
            "Gaurav Thakur", "Alok Mishra", "2026-06-29", resolved="2026-06-30", group="Finance AP", category="expenses",
            approvers=["Natasha D'Souza"]),
      ],
      emails=[
          M("RE: Expense rejected - 30 days?",
            [("Aakash Bhatia", "Finance-AP", "2026-06-24T10:20",
              "Hi Finance,\n\nZoho has auto-rejected my Chennai claim as over 30 days. The policy page does say 30 days, but Natasha said "
              "Finance accepts up to 60 now. Could someone confirm and approve? Receipts are all attached.\n\nAakash"),
             ("Ramesh Babu", "Aakash Bhatia", "2026-06-25T09:35",
              "Hi Aakash,\n\nApproved manually - you're within the 60 days we've been accepting since year-end. The Zoho rule is still set to "
              "30 because the policy hasn't been reissued; I've asked Shalini whether we change the rule or the policy. It'll be in the "
              "July reimbursement run.\n\nRamesh"),
             ("Shalini Menon", ["Ramesh Babu", "Alok Mishra"], "2026-06-30T17:40",
              "Both of you - I've now seen the 30-day override and the Rs 2,500 per-diem override in the same week. We're operating two rules "
              "that aren't written anywhere except Vivek's April email and our own habit. I'll draft T&E v6 (60 days, Rs 2,500 domestic per "
              "diem, Rs 1,000 receipt threshold to match the Zoho config) for Vivek. Until it's published, keep approving on appeal and note "
              "the reason on the claim.\n\nShalini")]),
      ],
      slack=[
          S("#expenses-help", [
              ("Aakash Bhatia", "2026-06-24T10:05", "Zoho rejected my claim for being over 30 days. Is that really enforced? Natasha said 60."),
              ("Alok Mishra", "2026-06-24T10:12", "The system says 30, we say 60 :) raise a ticket and we'll approve it manually."),
              ("Gaurav Thakur", "2026-06-24T10:15", "Related - my per diem got bounced for being Rs 2,500 instead of 2,000. Same thing?"),
              ("Alok Mishra", "2026-06-24T10:18", "Yes. 2,500 is the rate since April but Zoho still has 2,000. Ticket please, sorry."),
              ("Simran Kaur", "2026-06-24T10:25", "So the policy page is wrong on both? Good to know before my Mumbai trip."),
              ("Ramesh Babu", "2026-06-24T10:30", "Policy page is behind, yes. We're getting it updated."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-057  (D8: discount approvals)
    E("EVT-057", "policy_drift", "discount_approval_matrix_vp_sales", "2026-07-10",
      ["Gaurav Thakur", "Simran Kaur", "Arun Prasad", "Rahul Kapoor", "Vivek Anand", "Vinod Krishnamurthy"], "Sales Operations & Deal Desk",
      system="Salesforce CRM", policy="Discount Approval Matrix", project="Salesforce CPQ Implementation",
      summary="Two Deal Desk tickets show 27% and 24% discounts approved by the VP Sales alone. The Discount Approval Matrix (v3) requires "
              "the CFO for 20-30%. The CPQ workflow was configured in March to route 20-30% to VP Sales under a verbal Rahul/Vivek agreement "
              "with a weekly report (EVT-045); the matrix was never reissued, so the policy page and the CPQ system disagree.",
      outcome="resolved", drift=True,
      drift_note="POLICY (Discount Approval Matrix v3, s2): 20.01-30% discount requires CFO approval. PRACTICE (since Apr-2026 CPQ go-live): "
                 "VP Sales approves 20-30%; CFO gets a weekly report. Codified in CPQ config and a project decision doc (EVT-045); policy not updated.",
      related_events=["EVT-045", "EVT-080"], tags=["drift", "discount", "deal-desk", "cpq", "demo"],
      demo={"query": "Who needs to approve a 25% discount?", "expected_drift": True},
      tickets=[
          T("Deal Desk: 27% discount - Sunway Logistics (Singapore) - 3-year, 400 vehicles",
            "Requesting approval for a 27% discount on TCV for Sunway Logistics (Singapore), 3-year term, 400 vehicles, competitive "
            "situation vs Cartrack. Business case attached; opportunity SF-00891. Per the matrix this is a CFO approval - routing via CPQ.",
            "CPQ routed the approval to VP Sales (20-30% step). Approved by Rahul Kapoor 10-Jul 16:40 on the opportunity and on this ticket. "
            "Included in the weekly >20% discount report to the CFO (w/e 12-Jul). Note: the published Discount Approval Matrix (v3) lists the "
            "CFO for 20-30%; CPQ is configured per the Feb-2026 Rahul/Vivek agreement. Quote sent 11-Jul.",
            "Gaurav Thakur", "Arun Prasad", "2026-07-10", resolved="2026-07-10", group="Deal Desk", category="deal-desk",
            approvers=["Rahul Kapoor"], work_notes="Matrix says CFO; CPQ routes to VP Sales."),
          T("Deal Desk: 24% discount - Ganga Freight renewal + expansion (2-year)",
            "24% discount on the 2-year renewal with 150-vehicle expansion for Ganga Freight. Retention risk (they trialled a competitor). "
            "Opportunity SF-00934.",
            "Approved by Rahul Kapoor 21-Aug via CPQ (VP Sales step). Weekly report to CFO w/e 23-Aug. Quote sent 21-Aug; Chargebee "
            "subscription updated from the approved quote.",
            "Simran Kaur", "Arun Prasad", "2026-08-21", resolved="2026-08-21", group="Deal Desk", category="deal-desk",
            approvers=["Rahul Kapoor"]),
      ],
      emails=[
          M("Discount approvals above 20% - matrix vs CPQ",
            [("Arun Prasad", ["Vinod Krishnamurthy", "Rahul Kapoor"], "2026-07-13T10:10",
              "Vinod, Rahul,\n\nGaurav's 27% Sunway deal went to Rahul via CPQ on Friday and is approved. Gaurav had written 'CFO approval' "
              "on the ticket because that's what the matrix on Confluence says, and he asked me which is right. I answered 'CPQ is the "
              "operating rule', but I'm uneasy putting that in writing on every ticket. Can we get the matrix reissued as v4? Vivek asked for "
              "that in March as well.\n\nArun"),
             ("Rahul Kapoor", ["Arun Prasad", "Vinod Krishnamurthy"], "2026-07-13T11:30",
              "Vinod, please get v4 out - this is the third time it's come up. The weekly report to Vivek is going, so Finance has visibility; "
              "the document is just stale.\n\nRahul"),
             ("Vinod Krishnamurthy", ["Rahul Kapoor", "Arun Prasad", "Vivek Anand"], "2026-07-13T12:15",
              "Drafting v4 this week: AE to 10%, Sales Manager to 20%, VP Sales to 30% with weekly CFO report, CEO above 30%. Vivek, you'll get "
              "it for sign-off by Friday.\n\nVinod")]),
      ],
      slack=[
          S("#deal-desk", [
              ("Gaurav Thakur", "2026-07-10T14:05", "Sunway 27% is in CPQ. The matrix says CFO for 20-30 but CPQ sent it to Rahul? Just checking I haven't misconfigured the quote."),
              ("Arun Prasad", "2026-07-10T14:10", "CPQ is right - VP Sales approves up to 30% since April, the CFO gets a weekly report. The Confluence matrix is out of date."),
              ("Gaurav Thakur", "2026-07-10T14:12", "OK. It'd be nice if the matrix said so, I nearly emailed Vivek directly."),
              ("Rahul Kapoor", "2026-07-10T16:41", "Approved. Good deal - go close it."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-058  (D9: VPN expiry and contractor VPN)
    E("EVT-058", "policy_drift", "vpn_renewal_and_contractor_group", "2026-05-29",
      ["Nithin George", "Kavya Reddy", "Lakshmi Narayanan", "Ankit Chawla", "Nikhil Bhatt", "Amit Saxena"], "Identity & Access Management",
      system="GlobalProtect VPN", policy="VPN & Remote Connectivity Policy",
      summary="Nithin George received a '90-day VPN expiry' reminder from an old ServiceNow schedule and asked how to renew; IAM told him "
              "employee VPN has been on 365-day automatic renewal via the Okta group since the SSO integration. Separately, a Pixelcraft "
              "contractor was given direct VPN via the vpn-contractors Okta group (per the June Contractor policy) although the VPN policy "
              "(v2, May 2025) still says contractors must use the jump host only. Two policies now conflict and the VPN policy is stale.",
      outcome="resolved", drift=True,
      drift_note="POLICY (VPN & Remote Connectivity v2, s2.3-2.4): VPN granted for 90 days, renewal by manager-approved request; contractors "
                 "jump-host only. PRACTICE: employee VPN auto-renews for 365 days via Okta group (since Dec-2025); contractors get scoped VPN via the "
                 "vpn-contractors group (per the newer Contractor & Guest Access Policy v2). VPN policy not updated; conflicts with the Contractor policy.",
      related_events=["EVT-004"], tags=["drift", "vpn", "contractor", "policy-conflict"],
      demo={"query": "How do I renew my VPN access, and can contractors use the VPN?", "expected_drift": True},
      tickets=[
          T("VPN access expiring in 10 days - how do I renew? - Nithin George",
            "I got an automated email saying my GlobalProtect access expires on 8-Jun (90 days) and to submit a renewal request with "
            "manager approval per the VPN policy. I can't find a 'VPN renewal' item in the catalog. What do I do?",
            "No action needed. Employee VPN is granted via the Okta group vpn-employees which has been on a 365-day auto-renewal cycle "
            "since the Okta integration in December 2025 - the 90-day expiry reminder is from a legacy ServiceNow scheduled job that "
            "predates the integration (disabled 29-May). Your access is valid until 15-Dec-2026 and will renew automatically while you "
            "are an active employee. The VPN policy page still describes the 90-day process - flagged to Nikhil for update.",
            "Nithin George", "Kavya Reddy", "2026-05-29", resolved="2026-05-29", group="IAM", category="vpn",
            work_notes="Legacy 90-day reminder job disabled. Policy says 90 days + renewal request; practice is 365-day auto."),
          T("Contractor VPN access - ext-sameer.lobo (Pixelcraft) - Metabase embed testing for website",
            "Our Pixelcraft developer needs to test the Metabase public-embed component on the new website against our Metabase instance, "
            "which is VPN-only. Requesting VPN for ext-sameer.lobo for 30 days, scoped to the Metabase subnet. Sponsor: Ankit Chawla.",
            "Security review by Amit Saxena 16-Jul: scope limited to 10.20.8.0/24 (Metabase), 30 days, sponsor attestation on endpoint "
            "baseline received. Added to Okta group vpn-contractors with the Metabase-only split-tunnel profile 17-Jul; expiry 16-Aug. Per "
            "the Contractor & Guest Access Policy v2 (June 2026). Note: the VPN policy (v2) still says jump-host only for contractors - "
            "the Contractor policy is newer and takes precedence per IAM.",
            "Ankit Chawla", "Lakshmi Narayanan", "2026-07-15", resolved="2026-07-17", group="IAM", category="contractor-access",
            approvers=["Ankit Chawla", "Amit Saxena"], work_notes="Conflict: VPN policy v2 (jump host) vs Contractor policy v2 (vpn-contractors group)."),
      ],
      slack=[
          S("#it-access-requests", [
              ("Nithin George", "2026-05-29T09:20", "Got an email saying my VPN expires in 10 days and I need to raise a renewal with manager approval. There's no renewal item in the catalog?"),
              ("Kavya Reddy", "2026-05-29T09:30", "Ignore it - that's a leftover scheduled job from before the Okta integration. Employee VPN renews yearly on its own now. I'm killing the job."),
              ("Nithin George", "2026-05-29T09:32", "The VPN policy page says 90 days though?"),
              ("Kavya Reddy", "2026-05-29T09:35", "It does. It's from May last year. @Nikhil another one for the policy backlog."),
              ("Nikhil Bhatt", "2026-05-29T09:50", "Noted. VPN policy v3 needs: 365-day employee renewal, and the contractor section aligned with the new Contractor policy (vpn-contractors group instead of jump host)."),
              ("Lakshmi Narayanan", "2026-07-17T11:20", "Related: first contractor on the vpn-contractors group went live today (Pixelcraft, Metabase subnet only). Jump host is effectively retired."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-059  (D10: onboarding role bundles vs manual requests)
    E("EVT-059", "policy_drift", "onboarding_role_bundles_vs_sop", "2026-08-11",
      ["Dhruv Malik", "Vinod Krishnamurthy", "Kavya Reddy", "Geeta Iyengar", "Rakesh Nair", "Megha Patil"], "People Operations",
      system="Okta SSO", policy="Employee Onboarding SOP", project="Darwinbox Onboarding Workflow Automation",
      summary="Dhruv Malik (Revenue Analyst) started 10-Aug with Salesforce and Slack auto-provisioned by the SALES-OPS-ANALYST role bundle "
              "but no Metabase - his main tool. His manager Vinod Krishnamurthy, following the Onboarding SOP, expected to raise every "
              "application request on Day 1 and was confused about what the bundle covers. The SOP (v3, Aug 2025) describes HR emailing "
              "IT 5 days ahead and managers requesting each app; practice since May 2026 is Darwinbox-triggered tickets 10 days ahead and "
              "role bundles, documented only in a July reference page.",
      outcome="resolved", drift=True,
      drift_note="POLICY (Employee Onboarding SOP v3, s1/s2.2): HR emails IT 5 business days before start; manager raises a separate request "
                 "for every application on Day 1; nothing provisioned automatically by role. PRACTICE (since May-2026): Darwinbox auto-creates the "
                 "ticket 10 business days ahead and Okta applies role bundles; managers request only what the bundle misses. SOP not updated.",
      related_events=["EVT-046", "EVT-001"], tags=["drift", "onboarding", "role-bundles", "demo"],
      demo={"query": "What does a new joiner get automatically and what do I need to request as their manager?", "expected_drift": True},
      tickets=[
          T("Metabase access missing for new joiner Dhruv Malik (Revenue Analyst) - what is in the SALES-OPS-ANALYST bundle?",
            "Dhruv started yesterday. He got Salesforce and the ServiceNow Sales Ops queue automatically, but not Metabase, which is 80% "
            "of his job. The onboarding SOP says I should raise a request per application on Day 1 - do I still do that for everything, "
            "or only for what the bundle doesn't include? And what does the bundle include? I couldn't find it written anywhere.",
            "The SALES-OPS-ANALYST role bundle (see the July 'Role-based application bundles' page on the HR space) contains "
            "salesforce-users and servicenow-fulfiller-salesops only - Metabase was never added. Added Dhruv to metabase-viewer 11-Aug "
            "(Vinod's approval on this ticket) and, with Vinod's confirmation, added metabase-viewer to the SALES-OPS-ANALYST bundle for "
            "future joiners. Managers only need to request what the bundle does not cover; the Onboarding SOP (v3) still describes the "
            "old per-application process and HR Ops is updating it.",
            "Vinod Krishnamurthy", "Kavya Reddy", "2026-08-11", resolved="2026-08-11", group="IAM", category="onboarding",
            approvers=["Vinod Krishnamurthy"], on_behalf_of="Dhruv Malik", work_notes="Bundle gap fixed; SOP outdated."),
      ],
      emails=[
          M("Onboarding SOP vs role bundles - which process do managers follow?",
            [("Vinod Krishnamurthy", ["Geeta Iyengar", "Rakesh Nair"], "2026-08-11T12:20",
              "Geeta, Rakesh,\n\nFor Dhruv's onboarding I followed the Employee Onboarding SOP: waited for Day 1 and prepared to raise "
              "requests for Salesforce, Metabase, Slack and the Sales Ops queue. Half of that appeared on its own (bundle), half didn't "
              "(Metabase). Nothing in the SOP mentions bundles, and HR didn't email IT - a ticket just appeared from Darwinbox two weeks "
              "before. Can the SOP be updated so managers know what's automatic and what isn't? I only found the bundle table because "
              "Kavya linked it.\n\nVinod"),
             ("Geeta Iyengar", ["Vinod Krishnamurthy", "Rakesh Nair"], "2026-08-11T15:05",
              "Vinod - fair. The automation went live in May and the bundle table only got written in July; the SOP is still the 2025 "
              "version. Rakesh is drafting v4 (Darwinbox-triggered ticket at start-10 days, role bundles, managers request only the "
              "exceptions, licence-based apps always manual). Target end of August. Meanwhile the July bundle page is the reference.\n\nGeeta")]),
      ],
      slack=[
          S("#sales-ops", [
              ("Dhruv Malik", "2026-08-11T09:45", "Morning! I have Salesforce but no Metabase - is that something I request or does it come later?"),
              ("Megha Patil", "2026-08-11T09:50", "Should've been automatic honestly - Sonal had to ask for it too. @Vinod can you raise it? Kavya will need your approval."),
              ("Vinod Krishnamurthy", "2026-08-11T10:05", "Raised. Also asked IAM what the bundle actually includes because the SOP says I should be requesting *everything* on Day 1 and clearly I'm not."),
              ("Kavya Reddy", "2026-08-11T11:30", "@Dhruv you're in Metabase. @Vinod I've added Metabase to the SALES-OPS-ANALYST bundle so the next hire gets it on day one. Bundle table is on the HR space - the SOP is the old process."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-060  (D11: BYOD)
    E("EVT-060", "policy_drift", "byod_personal_phone_email", "2026-04-02",
      ["Simran Kaur", "Kunal Shah", "Mohammed Irfan", "Deepak Verma", "Rajesh Kumar"], "IT Service Desk & Endpoint",
      system="Microsoft Intune", policy="BYOD & Mobile Device Policy",
      summary="The BYOD policy (v1, Jun 2025) prohibits personal phones from accessing corporate email and says mobile access requires a "
              "company-issued device. In practice the Service Desk routinely enrols personal iPhones/Androids with Intune app-protection "
              "(MAM) for Outlook and Teams - two tickets in April and June show it as a standard, no-approval request. The policy's own "
              "rationale ('MAM not adopted pending licence review') is out of date since the Intune P2 licences arrived in early 2026.",
      outcome="resolved", drift=True,
      drift_note="POLICY (BYOD & Mobile Device v1, s1.1-1.2): personal mobile devices may not access corporate email/Slack; company-issued "
                 "Intune-managed phones only; exceptions need Head of IT approval for 30 days. PRACTICE (since ~Feb-2026): Service Desk enrols personal "
                 "phones with Intune MAM (app protection) for Outlook/Teams on request, no approval. Policy not updated.",
      tags=["drift", "byod", "intune", "mobile"],
      demo={"query": "Can I get work email on my personal phone?", "expected_drift": True},
      tickets=[
          T("Outlook on personal iPhone - Simran Kaur (Enterprise AE)",
            "I'm travelling to customers 3 days a week and need email and calendar on my phone. The BYOD page says personal phones aren't "
            "allowed and I'd need a company phone - is that still true? I don't really want to carry two phones.",
            "Enrolled the user's personal iPhone via the Intune Company Portal with the MAM (app protection) policy: Outlook and Teams "
            "only, managed apps encrypted, PIN required, no data to unmanaged apps, selective wipe available. No full-device management. "
            "This is the standard approach for personal phones since the Intune P2 licences arrived in Feb-2026; no approval required. "
            "The BYOD policy page still reflects the 2025 'no personal devices' position - flagged to Rajesh for update.",
            "Simran Kaur", "Mohammed Irfan", "2026-04-02", resolved="2026-04-02", group="IT Service Desk", category="mobile",
            work_notes="MAM enrolment standard practice; policy says prohibited."),
          T("Work email on personal Android phone - Kunal Shah (CSM)",
            "Please set up Outlook on my personal Samsung so I can see customer emails when I'm at client sites in Pune.",
            "MAM enrolment via Company Portal completed remotely with Kunal on a call 15-Jun (Outlook + Teams, app-protection policy). "
            "Standard request, no approval needed.",
            "Kunal Shah", "Deepak Verma", "2026-06-15", resolved="2026-06-15", group="IT Service Desk", category="mobile"),
      ],
      slack=[
          S("#it-helpdesk", [
              ("Simran Kaur", "2026-04-02T09:40", "Is it true I can't have work email on my personal phone? The BYOD policy says company phone only, but half of Sales has Outlook on their own phones."),
              ("Mohammed Irfan", "2026-04-02T09:48", "You can - we enrol personal phones with Intune app protection (just Outlook/Teams, no control over the rest of your phone). Raise a ticket and I'll do it today. That policy page predates the licences we got in Feb."),
              ("Rajesh Kumar", "2026-04-02T09:55", "Correct. The BYOD policy needs a v2 - it's been on my list since the P2 licences landed. MAM enrolment is the standard for personal phones; company phones are for on-call and leadership only."),
              ("Simran Kaur", "2026-04-02T10:00", "Great, ticket raised. Thanks!"),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-061  (D12: L&D cap and pre-approval)
    E("EVT-061", "policy_drift", "ld_reimbursement_cap_and_preapproval", "2026-07-27",
      ["Divya Menon", "Harish Gowda", "Tarun Bhargava", "Madhavi Srinivasan", "Suresh Pillai", "Varun Chandra"], "Learning & Development",
      system="LearnHub LMS", policy="Learning & Development Reimbursement Policy",
      summary="Divya Menon claimed Rs 32,000 for an AWS certification without pre-approval; L&D approved it. The L&D Reimbursement Policy "
              "(v2, Dec 2025) caps claims at Rs 25,000/year and says claims without pre-approval are not reimbursed. Since the FY27 budget "
              "(April 2026) L&D has applied a Rs 40,000 cap for certifications and waives pre-approval when the certification is passed; "
              "Harish Gowda's Rs 28,000 CKA claim in May was handled the same way. Policy not updated.",
      outcome="resolved", drift=True,
      drift_note="POLICY (L&D Reimbursement v2, s1/s2.2): Rs 25,000 annual cap; pre-approval mandatory, no reimbursement without it. "
                 "PRACTICE (since Apr-2026 FY27 budget): Rs 40,000 cap for certifications; pre-approval waived if the certification is passed. "
                 "Applied in May and July 2026; policy not updated.",
      tags=["drift", "learning", "reimbursement", "hr"],
      demo={"query": "What is the L&D reimbursement limit and do I need pre-approval?", "expected_drift": True},
      tickets=[
          T("L&D reimbursement - AWS Certified Solutions Architect (Rs 32,000) - Divya Menon - no pre-approval",
            "Submitting my AWS SA Professional exam + course (Rs 32,000, passed 20-Jul, certificate attached) in Zoho under L&D. I didn't "
            "raise a pre-approval in LearnHub - I only decided to sit it during the Snowflake cost project. Suresh is fine with it. I know "
            "the policy says Rs 25,000 and pre-approval; is any of it claimable?",
            "Approved in full (Rs 32,000) by Tarun Bhargava 28-Jul. FY27 L&D budget raised the certification cap to Rs 40,000 (Madhavi's "
            "April budget note); pre-approval is waived where the certification is passed and the manager confirms relevance (Suresh "
            "confirmed). The policy page (v2) still shows Rs 25,000 and mandatory pre-approval - update pending with Madhavi.",
            "Divya Menon", "Tarun Bhargava", "2026-07-27", resolved="2026-07-28", group="L&D", category="learning",
            approvers=["Suresh Pillai", "Tarun Bhargava"], work_notes="Cap and pre-approval rules overridden per FY27 practice."),
          T("L&D reimbursement - CKA certification (Rs 28,000) - Harish Gowda",
            "CKA exam + course, passed 8-May. Certificate attached. Manager Varun approved on Slack. No LearnHub pre-approval raised.",
            "Approved Rs 28,000 by Tarun Bhargava 12-May under the FY27 certification cap (Rs 40,000); pre-approval waived (passed, "
            "manager-confirmed relevance to the multi-region project).",
            "Harish Gowda", "Tarun Bhargava", "2026-05-11", resolved="2026-05-12", group="L&D", category="learning",
            approvers=["Varun Chandra", "Tarun Bhargava"]),
      ],
      emails=[
          M("RE: AWS certification reimbursement without pre-approval",
            [("Divya Menon", ["Tarun Bhargava"], "2026-07-27T11:15",
              "Hi Tarun,\n\nI've submitted Rs 32,000 for my AWS SA Pro exam and prep course. I didn't do the LearnHub pre-approval - sorry, I "
              "decided to sit it mid-project. The policy page says Rs 25,000 cap and no reimbursement without pre-approval, so I'll "
              "understand if it's partly rejected.\n\nDivya"),
             ("Tarun Bhargava", ["Divya Menon", "Madhavi Srinivasan"], "2026-07-28T10:00",
              "Hi Divya,\n\nApproved in full. Since April the certification cap is Rs 40,000 (FY27 budget) and we don't insist on pre-approval "
              "when the exam is passed and your manager confirms it's relevant - Suresh did. The policy page is the December version; "
              "Madhavi has the v3 draft. Congrats on the cert.\n\nTarun"),
             ("Madhavi Srinivasan", ["Tarun Bhargava", "Divya Menon"], "2026-07-28T10:40",
              "Congrats Divya. Tarun - v3 is with Sunita; I'll push for it before the October review cycle so people stop reading Rs 25,000.\n\nMadhavi")]),
      ],
      slack=[
          S("#learning", [
              ("Divya Menon", "2026-07-27T11:30", "Question - is the L&D cap still Rs 25,000? And is pre-approval strictly required? I've got a Rs 32k cert claim with no pre-approval :grimacing:"),
              ("Harish Gowda", "2026-07-27T11:35", "I claimed Rs 28k for CKA in May with no pre-approval and it went through. Tarun said the cap is 40k for certs now."),
              ("Tarun Bhargava", "2026-07-27T11:50", "Correct - 40k for certifications since the FY27 budget, and we waive pre-approval if you've passed and your manager confirms it's relevant. The policy page is out of date, v3 is coming."),
              ("Dev Patel", "2026-07-27T11:55", "Adding a banner to the policy page pointing to this thread until v3 is out."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-062  (D13: vendor onboarding quotes and terms)
    E("EVT-062", "policy_drift", "vendor_quotes_exemption_and_net30", "2026-08-14",
      ["Ankit Chawla", "Kritika Jain", "Shalini Menon", "Vivek Anand", "Kavita Bhatnagar", "Zara Ahmed"], "Accounts Payable & Procurement",
      system="NetSuite ERP", policy="Vendor Onboarding & Payment Terms SOP", project="Website Redesign & CMS Migration",
      summary="Vercel (new vendor, Rs 6.2 lakh/year) was onboarded with a single quote and Net-30 terms. The Vendor Onboarding SOP requires "
              "three quotes above Rs 5 lakh 'equally for SaaS and hosting' with CFO-approved single-source justification, and Net-45 unless "
              "the CFO approves shorter terms. Procurement has been treating SaaS subscriptions as exempt from the three-quote rule and "
              "accepting vendors' Net-30 for anything under Rs 10 lakh since early 2026 - neither is written down.",
      outcome="resolved", drift=True,
      drift_note="POLICY (Vendor Onboarding & Payment Terms SOP v2, s2.1/s3.1-3.2): three quotes for any new vendor above Rs 5 lakh including "
                 "SaaS/hosting; Net-45 standard, Net-30 only with CFO approval. PRACTICE (2026): SaaS subscriptions processed on one quote as an "
                 "'informal SaaS exemption'; Net-30 accepted under Rs 10 lakh without CFO approval.",
      related_events=["EVT-048", "EVT-078"], tags=["drift", "procurement", "vendor", "finance"],
      demo={"query": "Do I need three quotes to buy a new SaaS tool?", "expected_drift": True},
      tickets=[
          T("Purchase request: Vercel Pro hosting (new vendor) - Rs 6,20,000/year - Website Redesign",
            "Requesting onboarding of Vercel Inc. as a vendor and a PO for the Pro plan (annual, USD 7,500 = approx Rs 6.2 lakh) for "
            "hosting the new website. Quote attached (one - Vercel is the platform the site is built on, there is no equivalent). Security "
            "review completed by Nikhil Bhatt 4-Jun. Vendor terms: Net-30. Budget: Marketing website line. Approvers: Kavita Bhatnagar, "
            "Shalini Menon, Vivek Anand.",
            "Vendor form, W-8BEN-E and DPA collected; bank details verified by call-back 18-Aug. Three-quote requirement: treated as SaaS "
            "subscription exemption (single-platform, no equivalent) per current Procurement practice - single-source justification note "
            "added to the ticket, not routed to the CFO as a separate approval. Payment terms Net-30 accepted (vendor standard; under the "
            "Rs 10 lakh threshold Procurement has been accepting Net-30 without CFO sign-off). PO KT-PO-26-0844 raised 19-Aug; approvals "
            "Kavita 15-Aug, Shalini 18-Aug, Vivek 19-Aug (PO approval, not a terms/quotes exception). Vendor active in NetSuite 19-Aug.",
            "Ankit Chawla", "Kritika Jain", "2026-08-14", resolved="2026-08-19", group="Procurement", category="purchase-request",
            approvers=["Kavita Bhatnagar", "Shalini Menon", "Vivek Anand"],
            work_notes="Single quote (SaaS exemption practice); Net-30 without CFO terms approval."),
      ],
      emails=[
          M("Vercel vendor onboarding - quotes and payment terms",
            [("Ankit Chawla", "Kritika Jain", "2026-08-14T10:30",
              "Hi Kritika,\n\nVercel purchase request is in. I only have the one quote - it's the platform the agency built on, there isn't a "
              "like-for-like alternative without rebuilding. The SOP says three quotes above 5 lakh 'including SaaS and hosting'; do I need "
              "to do something for that? Also Vercel's terms are Net-30.\n\nAnkit"),
             ("Kritika Jain", "Ankit Chawla", "2026-08-14T14:05",
              "Hi Ankit,\n\nFor SaaS subscriptions we've generally not been enforcing the three quotes this year - there's rarely a real "
              "alternative and the SaaS approval policy already covers the security and budget checks. I'll add a single-source note to the "
              "ticket. Net-30 is fine at this size; we accept vendor-standard terms under 10 lakh. I'll need Kavita, Shalini and Vivek on "
              "the PO since it's over 5 lakh.\n\nKritika"),
             ("Shalini Menon", ["Kritika Jain", "Zara Ahmed"], "2026-08-25T16:20",
              "Kritika, Zara - I approved the Vercel PO last week, but note for both of you (Zara, as you learn the process): the SOP (v2, "
              "January) says three quotes for SaaS and hosting with a CFO-approved single-source justification, and Net-45 unless Vivek "
              "approves. We have been doing neither for SaaS since about February. If Vivek is comfortable with a SaaS exemption and a "
              "Net-30 threshold we should write it into v3; if not, we need to go back to the SOP. I'll raise it with him at the month-end "
              "review.\n\nShalini")]),
      ],
      slack=[
          S("#finance", [
              ("Zara Ahmed", "2026-08-25T11:10", "Learning question from last week's Vercel PR - the vendor SOP says three quotes above 5L for SaaS too, but it was processed on one. Is there an exemption list somewhere?"),
              ("Kritika Jain", "2026-08-25T11:20", "No list - it's been our working practice for SaaS this year (Zendesk seats, Figma, now Vercel). Single-platform tools don't really have three quotes. Shalini's aware and it's going to Vivek."),
              ("Alok Mishra", "2026-08-25T11:25", "Also Net-30 - the SOP says 45 unless CFO. We've accepted 30 on most small SaaS."),
              ("Shalini Menon", "2026-08-25T16:30", "All true, and it needs to be either written down or stopped. On the agenda for the close review with Vivek."),
          ]),
      ]),
]
