"""Layer 6/7 - Incident & troubleshooting events EVT-021..EVT-028 (with derived artifacts)."""
from events.dsl import E, T, M, S, D

EVENTS = [
    # ------------------------------------------------------------------ EVT-021
    E("EVT-021", "incident", "sev1_api_outage_after_deploy", "2026-03-17",
      ["Harish Gowda", "Varun Chandra", "Rohan Mehta", "Priya Shah", "Karthik Iyer", "Anita Desai", "Preeti Nambiar", "Kunal Shah",
       "Sanya Kapadia", "Arjun Venkataraman"],
      "Platform Backend", system="AlgoWorks Fleet Production Platform", policy="Incident Management & Severity Classification SOP",
      project="AlgoWorks Fleet v4 API Platform Migration",
      summary="Sev1: AlgoWorks Fleet API returned 5xx for ~60% of requests for 47 minutes (14:05-14:52 IST) after v4 API gateway 4.2.0 "
              "changed the PgBouncer pool size from 200 to 50 per pod, exhausting RDS connections under production concurrency. Rolled back "
              "via ArgoCD. 38 customers affected; driver app check-ins queued offline and synced afterwards. Postmortem published; actions: "
              "staging load test, config-change checklist, connection-pool alert.",
      outcome="resolved", drift=False, related_events=["EVT-008"], tags=["sev1", "outage", "v4", "rollback", "postmortem"],
      tickets=[
          T("SEV1 - AlgoWorks Fleet API 5xx errors / platform degraded (17-Mar-2026 14:05-14:52 IST)",
            "PagerDuty alert 'API 5xx rate > 5%' fired at 14:12 IST, 7 minutes after ArgoCD synced algoworks-api-gateway 4.2.0 to production. "
            "Error rate reached 61%; RDS connection count flat at the pool ceiling; p95 latency > 8s. Customer portal and driver app "
            "check-ins failing. Incident declared Sev1 at 14:18 by Varun Chandra (IC). Scribe: Karthik Iyer.",
            "14:25 correlated with 4.2.0 deploy (PR #2231 changed PgBouncer default_pool_size 200 -> 50 per pod as part of the v4 "
            "connection-management work; staging did not reproduce at its lower concurrency). 14:40 rollback to 4.1.7 initiated via ArgoCD "
            "(app rollback to previous revision). 14:52 error rate < 1%, RDS connections normal. 15:00 incident resolved; status page "
            "updated; Customer Success sent customer comms at 15:30. Retrospective emergency CHG raised. Postmortem: "
            "{{doc:EVT-021#1}}. Follow-up: Kinesis consumer lag caused by the rollback handled under {{ticket:EVT-008#1}}.",
            "Harish Gowda", "Varun Chandra", "2026-03-17", resolved="2026-03-17", group="Cloud Infrastructure", kind="incident",
            category="major-incident", priority="P1"),
          T("Customer report: Meridian Logistics - API timeouts and driver app cannot check in (17-Mar)",
            "Zendesk #48213: Meridian Logistics (enterprise, 1,200 vehicles) reports all API calls timing out since ~14:10 and drivers "
            "unable to check in. Their dispatch board is blank. P1 in Zendesk. Linking to the platform incident.",
            "Linked to {{ticket:EVT-021#1}}. Service restored 14:52; confirmed with customer at 15:10 that dispatch board recovered and "
            "queued driver check-ins synced. Customer comms and RCA summary sent 18-Mar. Zendesk ticket closed 19-Mar.",
            "Preeti Nambiar", "Preeti Nambiar", "2026-03-17", resolved="2026-03-19", group="Customer Support", kind="incident",
            category="customer-incident", priority="P1"),
          T("Customer report: SwiftHaul and 6 mid-market accounts - portal 'Something went wrong' errors (17-Mar)",
            "Multiple mid-market customers (SwiftHaul, Ganga Freight, Nimbus Couriers + 4 others) emailed their CSM about portal errors "
            "between 14:10 and 14:50. Raising one ticket to track comms; individual Zendesk tickets linked.",
            "Linked to {{ticket:EVT-021#1}}. All accounts confirmed recovered by 15:30. Standard incident comms template sent to all 38 "
            "affected accounts from Customer Success on 17-Mar 15:30; RCA summary on 18-Mar.",
            "Kunal Shah", "Kunal Shah", "2026-03-17", resolved="2026-03-18", group="Customer Success", kind="incident",
            category="customer-incident", priority="P2"),
          T("Emergency change (retrospective): rollback algoworks-api-gateway 4.2.0 -> 4.1.7 via ArgoCD",
            "Retrospective CHG per Change Management Policy 3.4 for the emergency rollback executed 17-Mar 14:40 during the Sev1. Approved "
            "verbally by Varun Chandra (IC). Rollback restored the 4.1.7 revision; no data changes.",
            "Reviewed at CAB 19-Mar (Thu): accepted. Note recorded that the original 4.2.0 deployment went through GitOps PR approval and "
            "not a CHG, per the ArgoCD process; CAB discussed whether config-only changes to pool sizes should require a CHG - no decision.",
            "Harish Gowda", "Varun Chandra", "2026-03-17", resolved="2026-03-19", group="Cloud Infrastructure", kind="change",
            category="emergency-change", priority="P1"),
      ],
      emails=[
          M("[RESOLVED] Sev1 - AlgoWorks Fleet API outage 17-Mar 14:05-14:52 IST",
            [("Varun Chandra", "Eng-All", "2026-03-17T15:20",
              "All,\n\nSummary of today's Sev1:\n- Impact: ~60% of API requests failed for 47 minutes (14:05-14:52 IST). Customer portal "
              "errors; driver app check-ins queued offline and have since synced. 38 customers affected.\n- Cause: algoworks-api-gateway 4.2.0 "
              "reduced the PgBouncer pool size per pod (200 -> 50). Under production concurrency this exhausted connections. Staging did not "
              "reproduce.\n- Fix: rolled back to 4.1.7 via ArgoCD at 14:40; recovered 14:52.\n- Next: postmortem by Friday (Rohan owns), "
              "customer comms from CS at 15:30.\n\nThanks to Harish, Priya and Karthik for a fast rollback.\n\nVarun"),
             ("Arjun Venkataraman", "Eng-All", "2026-03-17T16:02",
              "Thanks Varun and team. Two things I want in the postmortem: why our staging load profile didn't catch this, and whether "
              "pool-size changes should be flagged as high-risk in PR review. Blameless, but let's learn it properly.\n\nArjun")]),
          M("Customer comms draft - 17-Mar API incident",
            [("Anita Desai", ["Sanya Kapadia", "Kavita Bhatnagar"], "2026-03-17T15:05",
              "Sanya, Kavita - per the incident SOP, please review the wording below before we send to the 38 affected accounts (target "
              "15:30):\n\n'Between 14:05 and 14:52 IST today the AlgoWorks Fleet API and portal experienced elevated errors following a "
              "platform update. The update was rolled back and service is fully restored. Driver app activity recorded during this "
              "window has synced automatically. We will share a root-cause summary within 24 hours. We apologise for the disruption.'\n\nAnita"),
             ("Sanya Kapadia", ["Anita Desai", "Kavita Bhatnagar"], "2026-03-17T15:18",
              "Looks good - one change: 'following a platform update' -> 'following a scheduled platform update' reads as more controlled. "
              "Approved from Marketing.\n\nSanya"),
             ("Anita Desai", ["Sanya Kapadia", "Kavita Bhatnagar"], "2026-03-17T15:32", "Sent with that change. RCA summary tomorrow.\n\nAnita")]),
      ],
      slack=[
          S("#incidents", [
              ("Harish Gowda", "2026-03-17T14:14", "!incident API 5xx rate at 22% and climbing, started ~14:07. Looking."),
              ("Varun Chandra", "2026-03-17T14:18", "Declaring Sev1. I'm IC. @Karthik can you scribe? @Anita heads-up for customer comms."),
              ("Priya Shah", "2026-03-17T14:24", "4.2.0 went out at 14:05 - that's the PR with the PgBouncer pool change (#2231). RDS connections are pinned at the ceiling. Strongly suspect that."),
              ("Rohan Mehta", "2026-03-17T14:31", "Agree. Recommend rollback to 4.1.7 now, investigate after."),
              ("Varun Chandra", "2026-03-17T14:39", "Go for rollback. Harish, ArgoCD rollback on algoworks-api-gateway."),
              ("Harish Gowda", "2026-03-17T14:41", "Rollback syncing."),
              ("Harish Gowda", "2026-03-17T14:53", "Error rate 0.8%, connections back to normal. Watching."),
              ("Varun Chandra", "2026-03-17T15:00", "Resolved. 47 minutes. Postmortem by Friday, Rohan owns. Status page updated."),
              ("Anita Desai", "2026-03-17T15:33", "Customer comms sent to 38 accounts."),
          ]),
          S("#eng-platform", [
              ("Karthik Iyer", "2026-03-17T16:40", "For the postmortem: staging runs ~40 concurrent API sessions vs ~900 in prod at 2pm. 50 connections/pod x 6 pods = 300 was never going to hold. We need a load profile in staging that's at least 50% of prod peak."),
              ("Priya Shah", "2026-03-17T16:45", "Also - the pool change was buried in a 40-file PR. Should we require pool/limit/timeout config changes to be separate PRs with a 'high-risk-config' label?"),
              ("Rohan Mehta", "2026-03-17T16:50", "Both go in the action items. Draft postmortem tomorrow, review Thursday."),
              ("Sneha Kulkarni", "2026-03-18T09:10", "Adding: we had no alert on RDS connection utilisation. Datadog monitor at 80% should have paged before users noticed."),
          ]),
      ],
      docs=[
          D("Postmortem: 17 March 2026 - AlgoWorks Fleet API outage (Sev1)",
            "**Status:** Final | **Author:** Rohan Mehta | **Reviewers:** Varun Chandra, Arjun Venkataraman | **Incident ticket:** {{ticket:EVT-021#1}}\n\n"
            "## Summary\nOn 17 March 2026 between 14:05 and 14:52 IST, approximately 60% of requests to the AlgoWorks Fleet API failed with 5xx "
            "errors. The customer portal showed errors and driver app check-ins were queued offline. 38 customers were affected. The cause "
            "was a configuration change in algoworks-api-gateway 4.2.0 that reduced the PgBouncer pool size per pod from 200 to 50; under "
            "production concurrency this exhausted available connections to RDS. Service was restored by rolling back to 4.1.7 via ArgoCD.\n\n"
            "## Timeline (IST)\n- 14:05 ArgoCD syncs algoworks-api-gateway 4.2.0 (merged PR #2231, GitOps approval by Priya Shah and Sneha Kulkarni).\n"
            "- 14:07 First 5xx errors; RDS connection count reaches pool ceiling.\n- 14:12 PagerDuty alert 'API 5xx rate > 5%'.\n"
            "- 14:18 Sev1 declared, IC Varun Chandra.\n- 14:24 Correlation with 4.2.0 pool-size change.\n- 14:40 Rollback initiated.\n"
            "- 14:52 Error rate below 1%.\n- 15:00 Resolved. 15:30 Customer comms sent.\n- 19-Mar Kinesis consumer lag from the rollback cleared ({{ticket:EVT-008#1}}).\n\n"
            "## Root cause\nPR #2231 (v4 connection-management work) changed `default_pool_size` from 200 to 50 per pod to reduce idle "
            "connections, based on staging measurements. Staging runs ~40 concurrent sessions versus ~900 at production peak. The change "
            "was one of 40 files in the PR and was not called out in the description.\n\n"
            "## What went well\n- Correlation to the deploy in under 20 minutes; rollback in 35.\n- ArgoCD rollback worked first time.\n- Customer comms within 30 minutes of resolution.\n\n"
            "## What went badly\n- No alert on RDS connection utilisation.\n- Staging load profile is not representative.\n- High-risk config change hidden in a large PR.\n\n"
            "## Action items\n| # | Action | Owner | Due | Jira |\n|---|---|---|---|---|\n"
            "| 1 | Datadog monitor: RDS connections > 80% of max pages Platform on-call | Sneha Kulkarni | 24-Mar | PLAT-2201 |\n"
            "| 2 | Staging load test at >= 50% of prod peak as a required check for gateway deploys | Karthik Iyer | 30-Apr | PLAT-2205 |\n"
            "| 3 | PR label `high-risk-config` required for pool/limit/timeout changes; must be a separate PR | Priya Shah | 31-Mar | PLAT-2206 |\n"
            "| 4 | Dead-letter path for poison Kinesis records | Harish Gowda | 30-Apr | PLAT-2210 |\n"
            "| 5 | CAB to decide whether config-only production changes need a CHG in addition to GitOps approval | Varun Chandra | 15-Apr | - |\n\n"
            "_Blameless postmortem per the Incident Management & Severity Classification SOP._",
            doc_type="postmortem", space="ENG", created="2026-03-20", authors=["Rohan Mehta"],
            references=["{{ticket:EVT-021#1}}", "{{ticket:EVT-008#1}}"], related_events=["EVT-008"],
            labels=["postmortem", "sev1", "v4-migration"]),
      ]),

    # ------------------------------------------------------------------ EVT-022
    E("EVT-022", "incident", "integration_failure_secret_rotation", "2026-05-27",
      ["Anusha Rao", "Deepa Subramanian", "Daniel Fernandes", "Sanjay Dutta", "Nithin George"], "Billing, Payroll & Compliance",
      system="Chargebee Billing", policy="Incident Management & Severity Classification SOP", project="Chargebee Revenue Recognition Automation",
      summary="Chargebee-to-NetSuite invoice sync silently failed for three days (24-27 May) after Sanjay Dutta rotated the Chargebee "
              "webhook signing secret during a compliance review without updating the integration service. Anusha Rao noticed the AR "
              "mismatch; Daniel Fernandes updated the secret and replayed 312 webhooks. Action: secret rotation checklist.",
      outcome="resolved", drift=False, tags=["integration", "billing", "secret-rotation", "sev3"],
      tickets=[
          T("Chargebee invoices not appearing in NetSuite since 24-May (webhook failures)",
            "AR aging in NetSuite is short by Rs 41 lakh vs Chargebee for invoices dated 24-27 May. The chargebee-sync service dashboard in "
            "Datadog shows 100% webhook signature failures since 24-May 03:10. Nothing changed on our side that I know of. Need this fixed "
            "before the month-end BD-1 reconciliation.",
            "Cause: Chargebee webhook signing secret was rotated on 22-May (Sanjay Dutta, as part of the SOC 2 credential-rotation "
            "evidence) and the new secret was not updated in the chargebee-sync service's AWS Secrets Manager entry, so all webhooks were "
            "rejected from the first delivery attempt after rotation (24-May 03:10). Daniel Fernandes updated the secret 27-May 15:40 and "
            "replayed 312 failed webhooks from the Chargebee event log; AR reconciled to the rupee by 28-May 11:00. Actions: (1) Datadog "
            "monitor on webhook signature failures > 10/hour paging Platform on-call (PLAT-2318); (2) added 'update dependent integrations' "
            "step to the Finance systems credential-rotation checklist.",
            "Anusha Rao", "Daniel Fernandes", "2026-05-27", resolved="2026-05-28", group="Platform Backend", kind="incident",
            category="integration", priority="P2"),
      ],
      emails=[
          M("Chargebee -> NetSuite sync gap 24-27 May - root cause",
            [("Daniel Fernandes", ["Anusha Rao", "Deepa Subramanian", "Sanjay Dutta"], "2026-05-27T17:05",
              "Hi all,\n\nFound it. The webhook signing secret in Chargebee was rotated on 22 May; our sync service still had the old one in "
              "Secrets Manager, so every webhook since Sunday 03:10 failed signature validation and was dropped (Chargebee retries for 24h "
              "then gives up). I've updated the secret and replayed the 312 events from the Chargebee log - invoices are flowing again and "
              "I'll confirm the AR total tomorrow morning.\n\nSanjay - not a blame thing, the rotation was the right call for SOC 2; we just "
              "didn't have the dependency written down anywhere. I've added it to the rotation checklist and we're adding an alert.\n\nDaniel"),
             ("Sanjay Dutta", ["Daniel Fernandes", "Anusha Rao", "Deepa Subramanian"], "2026-05-27T17:30",
              "Apologies - I rotated it from the Chargebee admin console and assumed the integration read it from Chargebee. I'll route "
              "future rotations through a ticket to Platform first.\n\nSanjay"),
             ("Deepa Subramanian", ["Daniel Fernandes", "Anusha Rao", "Sanjay Dutta"], "2026-05-28T11:20",
              "AR reconciles this morning, thank you Daniel. Adding this to the revenue automation project risk log - the new pipeline must "
              "alert on any sync gap rather than fail silently.\n\nDeepa")]),
      ],
      slack=[
          S("#finance", [
              ("Anusha Rao", "2026-05-27T10:15", "Anyone touched the Chargebee integration? NetSuite AR is missing ~Rs 41L of invoices from the weekend onward."),
              ("Nithin George", "2026-05-27T10:20", "Not me. Datadog chargebee-sync dashboard shows signature failures since Sunday 3am."),
              ("Anusha Rao", "2026-05-27T10:22", "Raising an INC to Platform."),
              ("Daniel Fernandes", "2026-05-27T15:45", "Secret was rotated on the Chargebee side on Friday. Fixed and replaying now - you should see invoices land over the next hour."),
              ("Anusha Rao", "2026-05-28T11:05", "Reconciled. Thanks Daniel!"),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-023
    E("EVT-023", "incident", "sso_misconfiguration_login_loop", "2026-07-15",
      ["Kavya Reddy", "Anita Desai", "Preeti Nambiar", "Kunal Shah", "Lakshmi Narayanan", "Nikhil Bhatt"], "Identity & Access Management",
      system="Zendesk Support Desk", policy="Change Management Policy",
      summary="All Zendesk agents were stuck in an Okta login loop for ~2 hours (10:40-12:35 IST) after Kavya Reddy changed the Zendesk SAML "
              "NameID format while tidying app settings from the Q2 review. Rolled back by Lakshmi Narayanan. Sev2 for internal system. "
              "Lesson: Okta app configuration changes need a CHG (they are in scope of the Change Management Policy) - this one had none.",
      outcome="resolved", drift=False, related_events=["EVT-016"], tags=["sso", "zendesk", "sev2", "config-change"],
      tickets=[
          T("SEV2 - Zendesk agents cannot log in (Okta login loop) - 15-Jul 10:40-12:35 IST",
            "All Zendesk agents (34 users) are bounced back to Okta after authenticating - infinite loop. Started ~10:40. Customer tickets "
            "are queuing; P1 SLA at risk for two enterprise tickets. No Zendesk status-page issue.",
            "Cause: at 10:32 the Zendesk SAML app in Okta was changed from NameID format 'EmailAddress' to 'Persistent' during cleanup of app "
            "settings (follow-up from the Q2 access review). Zendesk maps users by email, so every assertion failed to match and Zendesk "
            "re-initiated login. Lakshmi Narayanan reverted the setting at 12:30; logins recovered 12:35. No CHG was raised for the change; "
            "reminder issued that Okta app config changes are Normal changes under the Change Management Policy. Zendesk P1 SLAs met via "
            "phone handling. Action: Okta admin console change-log review weekly (Nikhil).",
            "Anita Desai", "Lakshmi Narayanan", "2026-07-15", resolved="2026-07-15", group="IAM", kind="incident",
            category="major-incident", priority="P2"),
          T("Cannot log in to Zendesk - keeps redirecting to Okta",
            "Since about 10:40 I authenticate in Okta, get sent to Zendesk, and immediately get sent back to Okta. Tried Chrome incognito "
            "and Edge. Others on the team have the same.",
            "Duplicate of {{ticket:EVT-023#1}} (Okta SAML config change). Resolved 12:35 after rollback. Closed.",
            "Preeti Nambiar", "Deepak Verma", "2026-07-15", resolved="2026-07-15", group="IT Service Desk", kind="incident",
            category="login", priority="P2"),
          T("Zendesk login loop - Kunal Shah",
            "Same as Preeti's - Zendesk bounces between Okta and Zendesk. I have a customer QBR at 2pm and need the ticket history.",
            "Linked to {{ticket:EVT-023#1}}. Resolved 12:35. Closed.",
            "Kunal Shah", "Deepak Verma", "2026-07-15", resolved="2026-07-15", group="IT Service Desk", kind="incident",
            category="login", priority="P3"),
      ],
      slack=[
          S("#incidents", [
              ("Anita Desai", "2026-07-15T10:52", "!incident Zendesk login loop for every agent since ~10:40. Customers are queuing. @Nikhil @Kavya"),
              ("Kavya Reddy", "2026-07-15T10:58", "Looking. I was in the Zendesk app settings in Okta this morning cleaning up from the Q2 review, checking if it's related."),
              ("Nikhil Bhatt", "2026-07-15T11:05", "Sev2 (internal critical system down for a whole team). Lakshmi, please pair with Kavya. Anita - phones for the two enterprise P1s until this is back."),
              ("Lakshmi Narayanan", "2026-07-15T12:31", "Found it - NameID format was switched from EmailAddress to Persistent at 10:32. Reverted. Try again in a minute."),
              ("Preeti Nambiar", "2026-07-15T12:36", "I'm in."),
              ("Nikhil Bhatt", "2026-07-15T12:40", "Resolved. Kavya, no blame, but Okta app config changes are Normal changes under the change policy - please raise a CHG for anything in app settings from now on, even 'cleanup'."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-024
    E("EVT-024", "incident", "hrms_payroll_sync_mapping", "2026-02-04",
      ["Vijay Kumar", "Deepa Subramanian", "Rakesh Nair", "Geeta Iyengar", "Anjali Gupta", "Kunal Shah"], "Billing, Payroll & Compliance",
      system="Darwinbox HRMS", policy="Incident Management & Severity Classification SOP",
      summary="January payslips were missing in Darwinbox for all 12 Pune employees after a Keka upgrade changed the legal-entity code used "
              "by the Keka-to-Darwinbox payslip push. Vijay Kumar fixed the mapping with Keka support; payslips appeared on 6-Feb. HR Ops "
              "fielded a dozen queries in two days.",
      outcome="resolved", drift=False, tags=["payroll", "hrms", "sync", "pune"],
      tickets=[
          T("January payslips not visible in Darwinbox for Pune employees",
            "Multiple Pune employees report their January payslip is missing in Darwinbox (Bengaluru and Hyderabad are fine). Salary was "
            "credited on 31-Jan. Raising on behalf of the Pune team; Anjali and Kunal have raised individual tickets.",
            "Cause: Keka release 2026.1 (deployed 28-Jan) changed the legal entity identifier for 'AlgoWorks - Pune (Branch)' from "
            "KT-PUN to KT-PUNE-BR; the payslip export to Darwinbox filters on entity code and silently skipped Pune. Vijay Kumar worked with "
            "Keka support (case #KS-88121) to remap the code and re-ran the January push on 06-Feb 10:00. All 12 Pune payslips now visible. "
            "Added a post-payroll check: Darwinbox payslip count = Keka headcount per entity.",
            "Rakesh Nair", "Vijay Kumar", "2026-02-04", resolved="2026-02-06", group="Payroll", kind="incident", category="hr-systems",
            priority="P3", sensitivity="restricted"),
          T("My January payslip is not showing in Darwinbox",
            "Salary came in on the 31st but there's no January payslip under Documents in Darwinbox. I need it for a home loan application "
            "this week.",
            "Linked to {{ticket:EVT-024#1}}. Payslips restored 06-Feb. Sent a signed PDF copy on 05-Feb as an interim for the loan application.",
            "Anjali Gupta", "Vijay Kumar", "2026-02-04", resolved="2026-02-06", group="Payroll", kind="incident", category="hr-systems",
            priority="P3", sensitivity="restricted"),
          T("January payslip missing - Pune",
            "No January payslip in Darwinbox. December is there.",
            "Linked to {{ticket:EVT-024#1}}. Resolved 06-Feb.",
            "Kunal Shah", "Vijay Kumar", "2026-02-04", resolved="2026-02-06", group="Payroll", kind="incident", category="hr-systems",
            priority="P4", sensitivity="restricted"),
      ],
      emails=[
          M("Pune payslips - root cause and fix",
            [("Vijay Kumar", ["Deepa Subramanian", "Geeta Iyengar"], "2026-02-05T18:10",
              "Deepa, Geeta,\n\nRoot cause of the missing Pune payslips: Keka's 28-Jan release renamed our Pune branch entity code, and the "
              "Darwinbox push filters on that code. Keka support have remapped it; I'll re-run the January push tomorrow morning and verify "
              "all 12. For anyone who needs a payslip urgently before then I'm sending signed PDFs.\n\nI've also added a check to the "
              "post-payroll checklist so we catch a count mismatch before employees do.\n\nVijay"),
             ("Geeta Iyengar", ["Vijay Kumar", "Deepa Subramanian"], "2026-02-05T18:30",
              "Thanks Vijay. HR Ops has had 11 queries on this; I'll post an update in #people-ops once you confirm tomorrow.\n\nGeeta")],
            sensitivity="restricted"),
      ],
      slack=[
          S("#people-ops", [
              ("Rakesh Nair", "2026-02-04T11:20", "Heads up - getting several 'January payslip missing' queries, all from Pune. Raising with Payroll."),
              ("Swati Kulkarni", "2026-02-04T11:22", "Two more from the Pune engineers on my side as well. Bengaluru folks seem fine."),
              ("Vijay Kumar", "2026-02-04T14:05", "Confirmed Pune-only. Looks like a Keka entity code change from last week's upgrade. Working with Keka support."),
              ("Geeta Iyengar", "2026-02-06T10:30", "Pune payslips are back in Darwinbox as of this morning. Please close out any open queries."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-025
    E("EVT-025", "incident", "ci_runners_disk_full", "2026-06-11",
      ["Siddharth Jain", "Karthik Iyer", "Varun Chandra", "Daniel Fernandes"], "Cloud Infrastructure & Security",
      system="GitHub Enterprise", policy="Incident Management & Severity Classification SOP",
      summary="All four self-hosted GitHub Actions runners went offline for 3 hours (09:20-12:25) because the Docker layer cache filled the "
              "root volume. CI blocked for every team. Siddharth Jain pruned the cache, then shipped a CHG adding a nightly prune and a "
              "Datadog disk alert; runbook updated.",
      outcome="resolved", drift=False, tags=["ci", "github-actions", "disk", "runbook"],
      tickets=[
          T("GitHub Actions self-hosted runners offline - all CI jobs queued (11-Jun 09:20)",
            "All four self-hosted runners (runner-prod-1..4) show offline in the org settings since ~09:20. Every workflow is queued; the "
            "v4 release branch can't build. GitHub-hosted runners aren't an option for the jobs that need VPC access.",
            "Cause: root volume (100 GB) on all runner instances at 100% - Docker image layer cache had grown since the runner AMI was "
            "rebuilt in April without the prune cron. Runner agent crashes when it can't write its work directory. Fix: `docker system "
            "prune -af` on each runner (freed 60-70 GB), agents restarted 12:20, queue drained by 12:25. Permanent fix via "
            "{{ticket:EVT-025#2}}: nightly prune + Datadog disk alert at 80%. Runbook updated: {{doc:EVT-025#1}}.",
            "Karthik Iyer", "Siddharth Jain", "2026-06-11", resolved="2026-06-11", group="Cloud Infrastructure", kind="incident",
            category="ci-cd", priority="P2"),
          T("Change: GitHub Actions runner AMI - add nightly docker prune cron and disk alert",
            "Add a systemd timer to the runner AMI that runs `docker system prune -af --filter until=48h` nightly, and a Datadog monitor "
            "on root volume usage > 80% paging Cloud on-call. Rebuild AMI and roll the four runners one at a time outside working hours. "
            "Rollback: previous AMI ID retained.",
            "Approved at CAB 16-Jun (Tue). Implemented 17-Jun 20:00-21:30; runners rolled one at a time with no queued-job impact. Monitor "
            "'runner-disk-usage' live. Closed successful.",
            "Siddharth Jain", "Varun Chandra", "2026-06-11", resolved="2026-06-17", group="Cloud Infrastructure", kind="change",
            category="infrastructure-change", priority="P3"),
      ],
      slack=[
          S("#devops-sre", [
              ("Karthik Iyer", "2026-06-11T09:35", "All self-hosted runners are offline - is someone on it? v4 release build is stuck."),
              ("Siddharth Jain", "2026-06-11T09:41", "On it. Disks are full on all four - docker cache. Pruning now."),
              ("Daniel Fernandes", "2026-06-11T09:43", "Didn't we have a prune cron on these?"),
              ("Siddharth Jain", "2026-06-11T09:50", "We did on the old AMI; the April rebuild dropped it. My bad - I'll bake it into the AMI properly this time and add a disk alert."),
              ("Siddharth Jain", "2026-06-11T12:26", "Runners are back and the queue's drained. CHG for the permanent fix going to Tuesday's CAB."),
              ("Varun Chandra", "2026-06-11T12:30", "Thanks. Please add the prune + alert to the runner runbook so the next AMI rebuild doesn't lose it."),
          ]),
      ],
      docs=[
          D("Runbook: GitHub Actions self-hosted runners",
            "**Owner:** Cloud Infrastructure & Security | **Last updated:** 12 June 2026 (Siddharth Jain) | **Related:** {{ticket:EVT-025#1}}, {{ticket:EVT-025#2}}\n\n"
            "## Overview\nFour self-hosted runners (runner-prod-1..4, c6i.2xlarge, ap-south-1) execute workflows that need VPC access "
            "(integration tests against staging RDS, ECR pushes, ArgoCD promotion). GitHub-hosted runners are used for everything else.\n\n"
            "## Health checks\n- Org settings > Actions > Runners: all four should be Idle/Active.\n- Datadog dashboard 'CI Runners': queue depth, disk usage, agent status.\n- Alert `runner-disk-usage` pages Cloud on-call at 80% root volume.\n\n"
            "## Known failure modes\n| Symptom | Cause | Fix |\n|---|---|---|\n"
            "| All runners offline, agent log 'no space left on device' | Docker layer cache fills the 100 GB root volume (June 2026 incident) | `sudo docker system prune -af`, then `sudo systemctl restart actions.runner.*`. Nightly prune timer should prevent this - check `systemctl list-timers` |\n"
            "| Single runner offline after reboot | Agent not registered after instance replacement | Re-run the registration script from the AMI user-data; token from the org settings |\n"
            "| Jobs queued but runners idle | Label mismatch in workflow `runs-on` | Compare labels in workflow vs runner settings |\n\n"
            "## AMI rebuild checklist\n1. Base on the latest Ubuntu 24.04 golden image.\n2. Include: Docker, runner agent, Datadog agent, **nightly prune timer (`docker-prune.timer`)**, CloudWatch agent.\n"
            "3. Bake, test on runner-prod-4 first, then roll the others one at a time outside working hours.\n4. Update the AMI ID in `algoworks-infra/ci/runners.tf` via PR; keep the previous AMI ID for rollback.\n\n"
            "## Escalation\nCloud on-call (PagerDuty schedule 'Cloud Infrastructure'), then Varun Chandra.",
            doc_type="runbook", space="IT", created="2026-06-12", authors=["Siddharth Jain"],
            references=["{{ticket:EVT-025#1}}", "{{ticket:EVT-025#2}}"], labels=["runbook", "ci", "github-actions"]),
      ]),

    # ------------------------------------------------------------------ EVT-026
    E("EVT-026", "incident", "mobile_release_crash_hotfix", "2026-08-20",
      ["Farhan Siddiqui", "Meera Krishnan", "Neha Agarwal", "Preeti Nambiar", "Anita Desai", "Sanya Kapadia"], "Web & Mobile Frontend",
      system="AlgoWorks Fleet Driver Mobile App", policy="Deployment & Release Process SOP",
      summary="Driver App 3.8.0 crashed on launch on Android 15 devices during the 10% staged rollout (20-Aug). Farhan Siddiqui halted the "
              "rollout within 40 minutes, shipped hotfix 3.8.1 (edge-to-edge inset handling) the same evening, and staged rollout resumed "
              "next day. ~1,100 drivers affected for up to 6 hours; customer comms handled by CS.",
      outcome="resolved", drift=False, tags=["mobile", "android", "hotfix", "release"],
      tickets=[
          T("Driver App 3.8.0 crashes on launch - Android 15 (staged rollout 10%)",
            "Zendesk has 14 tickets since 09:00 from drivers on Android 15 (Pixel 8, Samsung S24) saying the app closes immediately on "
            "launch after updating this morning. Android 14 and iOS are fine. Raising as P2 - affected drivers can't check in.",
            "Cause: 3.8.0 targets API 35, which enforces edge-to-edge; the trip-list screen's inset handling threw a NullPointerException "
            "on Android 15 only. Not caught because the CI device farm has no Android 15 device (Neha adding one). Farhan halted the Play "
            "staged rollout at 09:42 (10% -> 0 new installs). Hotfix 3.8.1 built 15:30, internal track 16:00, expedited Play review 18:40, "
            "released to the same 10% cohort 19:15; crash-free rate back to 99.8%. Full rollout resumed 21-Aug. Skipped the 48-hour "
            "internal-track soak for the hotfix per the release SOP emergency clause (Meera approved).",
            "Preeti Nambiar", "Farhan Siddiqui", "2026-08-20", resolved="2026-08-21", group="Frontend & Mobile", kind="incident",
            category="mobile-release", priority="P2"),
          T("Customer comms tracking - Driver App 3.8.0 Android 15 crash",
            "Tracking comms to the 9 accounts with affected Android 15 drivers (approx 1,100 devices). Template: acknowledge, workaround "
            "(uninstall update / use web check-in), ETA for fix.",
            "Comms sent 10:30 with workaround; follow-up at 19:30 confirming 3.8.1 available. All 9 accounts confirmed recovery by 21-Aug noon. Closed.",
            "Anita Desai", "Kunal Shah", "2026-08-20", resolved="2026-08-21", group="Customer Success", kind="incident",
            category="customer-incident", priority="P2"),
      ],
      emails=[
          M("Driver App 3.8.0 - Android 15 crash - hotfix status",
            [("Meera Krishnan", ["Anita Desai", "Sanya Kapadia"], "2026-08-20T10:05",
              "Anita, Sanya - heads-up on the Driver App crash on Android 15 (only ~10% of drivers got 3.8.0 before we halted). Farhan has the "
              "cause; hotfix 3.8.1 targeted for this evening. Workaround for affected drivers: uninstall the update or use web check-in. "
              "We'll skip the 48-hour soak for the hotfix given it's a one-line fix with a clear repro - I'm approving that under the release "
              "SOP's emergency clause. Will update by 16:00.\n\nMeera"),
             ("Anita Desai", ["Meera Krishnan", "Sanya Kapadia"], "2026-08-20T10:20",
              "Thanks Meera. Comms with the workaround going out to the 9 affected accounts at 10:30.\n\nAnita"),
             ("Meera Krishnan", ["Anita Desai", "Sanya Kapadia"], "2026-08-20T19:20",
              "3.8.1 is live on Play for the affected cohort; crash-free rate recovered. Full rollout resumes tomorrow.\n\nMeera")]),
      ],
      slack=[
          S("#eng-frontend", [
              ("Farhan Siddiqui", "2026-08-20T09:38", "3.8.0 is crashing on launch on Android 15 - NPE in TripListFragment inset handling. Halting the rollout now."),
              ("Meera Krishnan", "2026-08-20T09:40", "Do it. How long for a fix?"),
              ("Farhan Siddiqui", "2026-08-20T09:55", "Fix is small - WindowInsets null on API 35 before the view is attached. Build by 15:00, then Play review."),
              ("Neha Agarwal", "2026-08-20T10:02", "Device farm has no Android 15 device, that's why regression missed it. Adding a Pixel 8 on 15 today."),
              ("Vikram Nair", "2026-08-20T10:05", "iOS unaffected, confirmed on the 3.8.0 build."),
              ("Farhan Siddiqui", "2026-08-20T19:16", "3.8.1 released to the 10% cohort. Crashlytics looks clean."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-027
    E("EVT-027", "incident", "cloud_cost_overrun_runaway_query", "2026-01-29",
      ["Suresh Pillai", "Ananya Chatterjee", "Sonal Mehra", "Ashwin Raman", "Nithin George"], "Data & Analytics Engineering",
      system="Snowflake Data Warehouse", policy="Incident Management & Severity Classification SOP", project="Snowflake Cost Optimization",
      summary="Snowflake's January credit budget was blown by 29-Jan: a Metabase dashboard built by Sonal Mehra had a cartesian join and was "
              "scheduled hourly on the shared L warehouse, burning ~2,400 credits (~USD 7,200) in 9 days. Suresh Pillai killed it and "
              "capped Metabase to an XS warehouse; the incident kicked off the Snowflake Cost Optimization project.",
      outcome="resolved", drift=False, tags=["snowflake", "cost", "metabase", "finops"],
      tickets=[
          T("Snowflake monthly credit budget exceeded on 29-Jan (runaway Metabase query)",
            "Snowflake resource monitor 'monthly-budget' hit 100% at 06:10 on 29-Jan and suspended the L warehouse, which broke the morning "
            "dbt run. Investigating what consumed ~2,400 more credits than forecast.",
            "Cause: Metabase question 'Pipeline by region x rep' (created 20-Jan by Sonal Mehra) joined OPPORTUNITIES to ACTIVITIES without a "
            "key, producing ~1.8bn rows; it was set to refresh hourly and ran on the shared L warehouse. Killed the query and disabled the "
            "schedule 07:30; raised the monitor to unblock dbt for the remaining 2 days with Ashwin's OK. Fixed the question with Sonal. "
            "Controls: Metabase now bound to an XS warehouse with 5-minute statement timeout; per-team warehouses and a monthly credit "
            "budget owned by FP&A to follow under the cost optimisation project.",
            "Suresh Pillai", "Ananya Chatterjee", "2026-01-29", resolved="2026-01-30", group="Data Engineering", kind="incident",
            category="cost", priority="P2"),
      ],
      emails=[
          M("Snowflake January overspend - cause and controls",
            [("Suresh Pillai", ["Ashwin Raman", "Nithin George"], "2026-01-29T12:40",
              "Ashwin, Nithin,\n\nWe've exceeded the January Snowflake budget by roughly USD 7,200. One Metabase dashboard with a bad join was "
              "refreshing hourly on the large warehouse for nine days. It's killed and fixed. Controls going in today: Metabase pinned to an "
              "XS warehouse with a 5-minute timeout, and auto-suspend dropped to 60 seconds.\n\nI'd like to propose a proper cost project "
              "for Q2 - per-team warehouses and a credit budget FP&A owns. Can we discuss in the SaaS spend review?\n\nSuresh"),
             ("Ashwin Raman", ["Suresh Pillai", "Nithin George"], "2026-01-29T14:05",
              "Yes - and I'd like Nithin on that project from our side. For now, please keep the resource monitor at the raised level only "
              "until month-end and drop it back on 1 Feb.\n\nAshwin")]),
      ],
      slack=[
          S("#eng-data", [
              ("Ananya Chatterjee", "2026-01-29T06:45", "dbt morning run failed - the L warehouse is suspended by the resource monitor. We've burned the whole month's budget?!"),
              ("Suresh Pillai", "2026-01-29T07:10", "Looking at query history. One Metabase question is at the top by a mile - 2,400 credits over 9 days. Killing it."),
              ("Suresh Pillai", "2026-01-29T07:35", "It's a cartesian join in a Sales Ops dashboard, scheduled hourly. Schedule disabled. @Sonal can we pair on the join after standup?"),
              ("Sonal Mehra", "2026-01-29T09:02", "Oh no - yes, sorry. I didn't realise the refresh ran on the big warehouse."),
              ("Suresh Pillai", "2026-01-29T09:05", "Not your fault, we let Metabase use the L warehouse. Pinning it to XS with a timeout today."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-028
    E("EVT-028", "incident", "vendor_outage_identity_provider", "2025-11-18",
      ["Nikhil Bhatt", "Sandeep Malhotra", "Lakshmi Narayanan", "Deepak Verma", "Anjali Gupta", "Rajesh Kumar", "Aakash Bhatia",
       "Payal Shah", "Riya Sen", "Farhan Siddiqui", "Bhavana Shetty"],
      "Identity & Access Management", system="Okta SSO", policy="Incident Management & Severity Classification SOP",
      summary="Okta's ap-1 cell had a vendor-side outage from 09:40 to 10:20 IST on 18-Nov-2025; nobody could log in to any SSO app "
              "(Slack, M365, ServiceNow included). The Service Desk logged user reports by phone, IAM used the break-glass local admin only "
              "to confirm Okta health, and communication went via the office WhatsApp group per the vendor-outage runbook. No data impact.",
      outcome="resolved", drift=False, tags=["okta", "vendor-outage", "sev2", "runbook"],
      tickets=[
          T("SEV2 - Okta login failures for all users (vendor outage) 18-Nov-2025 09:40-10:20 IST",
            "From 09:40 all Okta logins fail with 'Service unavailable'. Slack, Microsoft 365, ServiceNow, Salesforce, GitHub all "
            "unreachable for anyone not already signed in. Okta status page shows a degradation in the ap-1 cell. Logged after the fact "
            "(ServiceNow itself was behind Okta).",
            "Vendor outage (Okta incident OKTA-2025-1118, ap-1 cell, 09:38-10:19 IST). Actions taken per the 'Okta outage' runbook: (1) "
            "confirmed Okta admin console unreachable, break-glass local admin used only to verify tenant health; (2) comms via office "
            "WhatsApp group and floor announcements; (3) Service Desk logged phone reports on behalf of users (5 tickets linked); (4) no "
            "changes made. Recovered 10:20; existing sessions were unaffected throughout. Post-incident note sent to all staff by Sandeep.",
            "Nikhil Bhatt", "Nikhil Bhatt", "2025-11-18", resolved="2025-11-18", group="IAM", kind="incident",
            category="major-incident", priority="P2"),
          T("Cannot log in to Slack or email - Okta error (logged by Service Desk on behalf of user)",
            "User called the Service Desk at 09:48: Okta shows 'Service unavailable' when trying to open Slack and Outlook on a fresh laptop "
            "restart. Logged on behalf of Aakash Bhatia.",
            "Linked to {{ticket:EVT-028#1}} (Okta vendor outage). Resolved 10:20; user confirmed login.",
            "Deepak Verma", "Deepak Verma", "2025-11-18", resolved="2025-11-18", group="IT Service Desk", kind="incident",
            category="login", priority="P3", on_behalf_of="Aakash Bhatia"),
          T("Okta not working - can't get into NetSuite (logged by Service Desk)",
            "Payal Shah called at 09:52 - Okta login page returns an error; needs NetSuite for a bank payment run due 11:00.",
            "Linked to {{ticket:EVT-028#1}}. Advised no workaround (NetSuite is SSO-only since Phase 2). Resolved 10:20; payment run completed 10:45.",
            "Deepak Verma", "Deepak Verma", "2025-11-18", resolved="2025-11-18", group="IT Service Desk", kind="incident",
            category="login", priority="P3", on_behalf_of="Payal Shah"),
          T("Okta 'Service unavailable' - remote employee (logged by Service Desk)",
            "Riya Sen (remote) messaged the Service Desk on WhatsApp at 09:55 - cannot open Slack, Outlook or Confluence.",
            "Linked to {{ticket:EVT-028#1}}. Resolved 10:20.",
            "Anjali Gupta", "Anjali Gupta", "2025-11-18", resolved="2025-11-18", group="IT Service Desk", kind="incident",
            category="login", priority="P4", on_behalf_of="Riya Sen"),
          T("Okta down - can't access GitHub (logged by Service Desk)",
            "Farhan Siddiqui (Hyderabad) called at 10:01 - GitHub SSO login failing, release build blocked.",
            "Linked to {{ticket:EVT-028#1}}. Resolved 10:20.",
            "Anjali Gupta", "Anjali Gupta", "2025-11-18", resolved="2025-11-18", group="IT Service Desk", kind="incident",
            category="login", priority="P4", on_behalf_of="Farhan Siddiqui"),
          T("Greenhouse and Outlook login errors - Okta (logged by Service Desk)",
            "Bhavana Shetty called at 10:05 - cannot log in to Greenhouse to send interview invites; Outlook also failing.",
            "Linked to {{ticket:EVT-028#1}}. Resolved 10:20.",
            "Deepak Verma", "Deepak Verma", "2025-11-18", resolved="2025-11-18", group="IT Service Desk", kind="incident",
            category="login", priority="P4", on_behalf_of="Bhavana Shetty"),
      ],
      emails=[
          M("Okta outage this morning (09:40-10:20) - what happened",
            [("Sandeep Malhotra", "All-Company", "2025-11-18T12:30",
              "All,\n\nBetween 09:40 and 10:20 this morning Okta - our login provider - had a service outage in its Asia-Pacific region. During "
              "that window nobody could sign in to Slack, email, ServiceNow or other apps unless they were already signed in. Okta has "
              "confirmed the cause was on their side; no AlgoWorks systems or data were affected, and no action is needed from you.\n\n"
              "Because our ticketing system is behind Okta too, the Service Desk took reports by phone and WhatsApp. If you are not in the "
              "office WhatsApp group, please ask your team lead to add you - it is our fallback channel for exactly this situation.\n\nSandeep\n"
              "Head of IT & Infrastructure")]),
      ],
      slack=[
          S("#incidents", [
              ("Nikhil Bhatt", "2025-11-18T10:24", "Okta is back (vendor outage in ap-1, 09:38-10:19). If you were already logged in you probably didn't notice. Service Desk is closing the phone-logged tickets."),
              ("Rajesh Kumar", "2025-11-18T10:26", "We logged 5 user reports by phone/WhatsApp. Reminder to everyone: during an Okta outage the WhatsApp group is the channel, since Slack is behind Okta."),
              ("Lakshmi Narayanan", "2025-11-18T10:30", "Break-glass admin was used only to check tenant health, logged in the sealed vault record per the MFA standard. No config touched."),
              ("Sandeep Malhotra", "2025-11-18T10:35", "Thanks all. I'll send an all-company note at lunch."),
          ]),
      ]),
]
