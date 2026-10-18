"""Layer 6/7 - Incident & troubleshooting events EVT-029..EVT-036 (with derived artifacts)."""
from events.dsl import E, T, M, S, D

EVENTS = [
    # ------------------------------------------------------------------ EVT-029
    E("EVT-029", "incident", "phishing_campaign_executive_impersonation", "2026-04-22",
      ["Amit Saxena", "Nikhil Bhatt", "Alok Mishra", "Riya Sen", "Bhavana Shetty", "Vivek Anand", "Kavya Reddy", "Sandeep Malhotra"],
      "Identity & Access Management", system="Microsoft 365", policy="Password & MFA Standard",
      project="Security Awareness & Phishing Simulation Program",
      summary="A phishing campaign impersonating the CFO ('urgent vendor payment - reply with the bank change form') hit 61 mailboxes on "
              "22-Apr. Three employees clicked the link; Alok Mishra entered his Okta password on the fake page. Amit Saxena revoked "
              "sessions and reset the credential within 25 minutes; MFA prevented account takeover. No funds moved. The incident launched "
              "the Security Awareness & Phishing Simulation Program.",
      outcome="resolved", drift=False, tags=["phishing", "security-incident", "cfo-impersonation", "mfa"],
      tickets=[
          T("SECURITY INCIDENT - Phishing campaign impersonating CFO (22-Apr-2026)",
            "At 09:12 a phishing email from 'Vivek Anand <vivek.anand@algoworks-finance.com>' with subject 'URGENT: vendor bank change - "
            "action needed before 11am' reached 61 mailboxes (mostly Finance, HR and Marketing). Link goes to a fake Okta login page. "
            "Reported by Bhavana Shetty via the report-phish button at 09:20. Defender flagged 3 clicks.",
            "09:25 sender domain blocked at the mail gateway; all 61 copies purged from mailboxes via Defender. Clicks: Riya Sen (closed the "
            "page), Bhavana Shetty (reported it), Alok Mishra (entered Okta password on the fake page at 09:31, no MFA prompt completed). "
            "09:37 Alok's Okta sessions revoked, password reset, Okta Verify re-enrolled ({{ticket:EVT-029#2}}); mailbox rules and "
            "forwarding checked - clean. MFA (number matching) blocked the attacker's login attempt at 09:34 from a Nigerian IP. No "
            "financial transactions attempted in NetSuite; AP informed. Lookalike domain reported to registrar. Follow-up: security "
            "awareness refresh and quarterly phishing simulations (project kicked off 16-Mar, prioritised).",
            "Amit Saxena", "Amit Saxena", "2026-04-22", resolved="2026-04-23", group="Security", kind="incident",
            category="security-incident", priority="P1", sensitivity="restricted"),
          T("Credential reset after phishing click - Alok Mishra",
            "User entered Okta credentials on a phishing page at 09:31 (see security incident). Reset required.",
            "Sessions revoked 09:37, password reset via video-verified call with the Service Desk, Okta Verify re-enrolled on the user's "
            "phone, 1Password master password rotated by user. Confirmed no unexpected sign-ins in Okta system log. User completed the "
            "Security Awareness refresher 23-Apr.",
            "Amit Saxena", "Kavya Reddy", "2026-04-22", resolved="2026-04-22", group="IAM", kind="incident", category="security-incident",
            priority="P1", on_behalf_of="Alok Mishra", sensitivity="restricted"),
      ],
      emails=[
          M("[Security] Phishing email impersonating the CFO - do not respond",
            [("Amit Saxena", "All-Company", "2026-04-22T09:50",
              "All,\n\nThis morning some of you received an email that appears to be from Vivek Anand with the subject 'URGENT: vendor bank "
              "change - action needed before 11am'. It is a phishing attempt from a lookalike domain (algoworks-finance.com). We have "
              "removed it from mailboxes and blocked the sender.\n\nIf you clicked the link or entered your password, please call the Service "
              "Desk now (ext. 200) - you will not be in trouble. Reminder: AlgoWorks will never ask for passwords or bank-detail changes by "
              "email; vendor bank changes go through Finance AP with a call-back check.\n\nUse the 'Report Phish' button in Outlook for anything "
              "suspicious.\n\nAmit Saxena\nSecurity Engineer"),
             ("Vivek Anand", "All-Company", "2026-04-22T10:15",
              "To be clear: that email did not come from me, and I will never send payment instructions by email. Thank you Bhavana for "
              "reporting it quickly.\n\nVivek")]),
      ],
      slack=[
          S("#security", [
              ("Amit Saxena", "2026-04-22T09:22", "Phish in progress - CFO impersonation, fake Okta page, 61 recipients. Blocking domain and purging now."),
              ("Nikhil Bhatt", "2026-04-22T09:24", "Treat as P1. Pull the Defender click report and check Okta system log for any successful auth from new IPs."),
              ("Amit Saxena", "2026-04-22T09:36", "One credential entered (Alok, Finance AP). Attacker tried to log in at 09:34 - number-matching MFA blocked it. Revoking sessions and resetting."),
              ("Kavya Reddy", "2026-04-22T09:41", "Reset done, Okta Verify re-enrolled. Mailbox rules clean."),
              ("Sandeep Malhotra", "2026-04-22T09:45", "Good. All-company note from Amit, and let's move the awareness programme up the list - this was targeted at Finance the week before a payment run."),
          ], private=True, sensitivity="restricted"),
      ]),

    # ------------------------------------------------------------------ EVT-030
    E("EVT-030", "incident", "certificate_expiry_vpn", "2026-06-03",
      ["Lakshmi Narayanan", "Nikhil Bhatt", "Ishita Bose", "Riya Sen", "Siddharth Jain", "Deepak Verma", "Varun Chandra"],
      "Identity & Access Management", system="GlobalProtect VPN", policy="Incident Management & Severity Classification SOP",
      summary="The GlobalProtect portal TLS certificate expired at midnight on 3-Jun; every remote user got a certificate error from 08:00 "
              "until Lakshmi Narayanan installed the renewed certificate at 09:35. Nobody owned the renewal reminder after the 2025 gateway "
              "migration. A runbook with a renewal calendar and a Datadog certificate-expiry check was created.",
      outcome="resolved", drift=False, tags=["vpn", "certificate", "sev2", "runbook"],
      tickets=[
          T("SEV2 - GlobalProtect VPN connection failures for all remote users (certificate expired) 03-Jun 08:00-09:35",
            "Remote and WFH users report GlobalProtect fails with 'Portal certificate is invalid' since this morning. Office users on LAN "
            "unaffected. Three user tickets so far.",
            "Cause: the public TLS certificate on vpn.algoworks.io expired 03-Jun 00:00 IST. It was issued in June 2025 during the "
            "gateway migration and the renewal reminder was in the previous engineer's personal calendar. Renewed via the corporate CA "
            "portal 09:10, installed on both gateways 09:35, connections recovered. Actions: certificate inventory on the IT Runbooks page "
            "with renewal dates; Datadog synthetic check for certificate expiry < 30 days on all public endpoints (done 04-Jun); runbook "
            "{{doc:EVT-030#1}}.",
            "Deepak Verma", "Lakshmi Narayanan", "2026-06-03", resolved="2026-06-03", group="IAM", kind="incident",
            category="major-incident", priority="P2"),
          T("VPN won't connect - 'Portal certificate is invalid'",
            "Working remotely today. GlobalProtect shows a red certificate error and won't connect. Restarted laptop, same. I can't reach "
            "the Admin Console or Metabase.",
            "Linked to {{ticket:EVT-030#1}} - portal certificate expired. Fixed 09:35; user confirmed connection.",
            "Ishita Bose", "Deepak Verma", "2026-06-03", resolved="2026-06-03", group="IT Service Desk", kind="incident", category="vpn",
            priority="P3"),
          T("GlobalProtect certificate error this morning",
            "Can't connect to VPN from home since 8am, certificate invalid error. Need Confluence restricted space for the brand guidelines draft.",
            "Linked to {{ticket:EVT-030#1}}. Resolved 09:35.",
            "Riya Sen", "Anjali Gupta", "2026-06-03", resolved="2026-06-03", group="IT Service Desk", kind="incident", category="vpn",
            priority="P4"),
          T("VPN cert expired? GlobalProtect refusing to connect (Pune WFH)",
            "Certificate on vpn.algoworks.io shows expired 03-Jun 00:00 in the browser. Flagging in case nobody's seen it yet.",
            "Confirmed - linked to {{ticket:EVT-030#1}}. Thanks for the precise report. Resolved 09:35.",
            "Siddharth Jain", "Lakshmi Narayanan", "2026-06-03", resolved="2026-06-03", group="IAM", kind="incident", category="vpn",
            priority="P3"),
      ],
      slack=[
          S("#it-helpdesk", [
              ("Ishita Bose", "2026-06-03T08:12", "VPN is refusing to connect this morning - 'portal certificate is invalid'. Anyone else?"),
              ("Riya Sen", "2026-06-03T08:14", "Same here"),
              ("Siddharth Jain", "2026-06-03T08:20", "The cert on vpn.algoworks.io expired at midnight. @Lakshmi @Nikhil"),
              ("Lakshmi Narayanan", "2026-06-03T08:31", "On it. Renewing now - it's a CA-issued cert so about an hour."),
              ("Deepak Verma", "2026-06-03T08:35", "Raised the INC and linking your tickets. Office LAN users are fine, so if you're near an office you can come in meanwhile."),
              ("Lakshmi Narayanan", "2026-06-03T09:36", "New cert installed on both gateways. Quit and reopen GlobalProtect."),
              ("Ishita Bose", "2026-06-03T09:40", "Connected, thanks!"),
              ("Nikhil Bhatt", "2026-06-03T09:50", "Post-incident: we'll put a certificate inventory with renewal dates on the IT Runbooks page and add an expiry check in Datadog. This shouldn't rely on someone's calendar."),
          ]),
      ],
      docs=[
          D("Runbook: GlobalProtect VPN - certificate renewal and outage response",
            "**Owner:** Identity & Access Management | **Created:** 4 June 2026 (Lakshmi Narayanan) after {{ticket:EVT-030#1}}\n\n"
            "## Certificate inventory\n| Endpoint | Issuer | Expires | Renewal owner | Monitoring |\n|---|---|---|---|---|\n"
            "| vpn.algoworks.io (portal + gateways) | DigiCert (corporate CA account) | 3 June 2027 | IAM (Lakshmi Narayanan, backup Nikhil Bhatt) | Datadog synthetic `cert-expiry-vpn` alerts at 30 and 7 days |\n"
            "| GlobalProtect gateway-sg (Singapore) | same | 3 June 2027 | IAM | same |\n\n"
            "## Renewal procedure (allow 2 hours, do it 30 days early)\n1. Generate CSR on the primary gateway (Device > Certificate Management > Generate).\n"
            "2. Submit the CSR in the DigiCert portal (credentials in 1Password vault 'IAM-Infra').\n3. Import the issued certificate and chain on **both** gateways; set as the portal and gateway SSL/TLS profile certificate.\n"
            "4. Commit; verify with `openssl s_client -connect vpn.algoworks.io:443` and a test connection from an external network.\n5. Update the expiry date in this table and in the IT change calendar.\n\n"
            "## If the certificate has already expired\n- Symptom: all remote users see 'Portal certificate is invalid'. Office LAN users are unaffected.\n"
            "- Declare Sev2 (internal critical system down for all remote staff). Post in #it-helpdesk and #incidents.\n- Follow the renewal procedure; an expedited reissue takes ~45 minutes.\n"
            "- Interim: office attendance, or hotspot to a colleague on LAN is *not* a workaround; there is no VPN bypass for the Admin Console or Metabase.\n\n"
            "## History\n- 3 June 2026: certificate expired; 95-minute outage for remote users. Root cause: renewal reminder lived in a former engineer's calendar after the 2025 gateway migration.",
            doc_type="runbook", space="IT", created="2026-06-04", authors=["Lakshmi Narayanan"],
            references=["{{ticket:EVT-030#1}}"], labels=["runbook", "vpn", "certificates"]),
      ]),

    # ------------------------------------------------------------------ EVT-031
    E("EVT-031", "incident", "mdm_enrollment_token_expiry", "2026-09-09",
      ["Mohammed Irfan", "Rajesh Kumar", "Meenakshi Sundaram", "Deepak Verma", "Ashwin Raman"], "IT Service Desk & Endpoint",
      system="Microsoft Intune", policy="Laptop & Endpoint Provisioning SOP",
      summary="New MacBooks could not enrol in Intune from 8-Sep because the Apple Business Manager MDM server token had expired. "
              "Discovered when Meenakshi Sundaram's Day-2 laptop provisioning failed; Mohammed Irfan renewed the token on 9-Sep. Two "
              "laptops delayed by a day; expiry added to the certificate/token inventory.",
      outcome="resolved", drift=False, related_events=["EVT-030"], tags=["intune", "abm", "token", "endpoint"],
      tickets=[
          T("Intune enrollment failing for new MacBooks - ABM token expired",
            "Two MacBook Pros for this week's joiners fail Automated Device Enrollment with 'MDM server unavailable' at setup. Same on a "
            "re-imaged loaner. Windows enrollment is fine. Started 08-Sep.",
            "Cause: Apple Business Manager MDM server token for the Intune connector expired 08-Sep 02:00 (annual). Renewed the token in "
            "ABM and uploaded to Intune 09-Sep 11:20; enrollment succeeded on all three devices by 12:00. Added ABM token (expires "
            "09-Sep-2027) and the Apple Push certificate (expires 14-Nov-2026) to the IT certificate & token inventory created after the "
            "June VPN incident, with Datadog calendar reminders at 30/7 days.",
            "Mohammed Irfan", "Mohammed Irfan", "2026-09-09", resolved="2026-09-09", group="IT Service Desk", kind="incident",
            category="endpoint", priority="P3"),
          T("Laptop not ready on Day 2 - Meenakshi Sundaram (FP&A, started 07-Sep)",
            "Meenakshi started on Monday; her MacBook Air is stuck at the setup assistant with an MDM error and she is working from a "
            "loaner ThinkPad. Please prioritise - she needs NetSuite and the FP&A Excel models which are on the Mac build.",
            "Linked to {{ticket:EVT-031#1}} (ABM token). MacBook Air KT-LT-0425 enrolled 09-Sep 12:00, apps pushed, handed over 14:30. "
            "Loaner returned. Note: Day-1 laptop was a ThinkPad loaner, so the Day-1 checklist was met; the Mac was a role-standard swap.",
            "Ashwin Raman", "Deepak Verma", "2026-09-08", resolved="2026-09-09", group="IT Service Desk", category="laptop",
            priority="P3", on_behalf_of="Meenakshi Sundaram"),
      ],
      slack=[
          S("#it-helpdesk", [
              ("Deepak Verma", "2026-09-08T15:10", "@Mohammed the MacBooks for this week's joiners won't get past setup - 'MDM server unavailable'. Third device now."),
              ("Mohammed Irfan", "2026-09-08T15:25", "Windows is enrolling fine so it's Apple-side. Checking the ABM connector."),
              ("Mohammed Irfan", "2026-09-09T11:25", "ABM MDM token expired yesterday. Renewed and re-uploaded; try the setup again."),
              ("Deepak Verma", "2026-09-09T12:02", "All three enrolled. Meenakshi gets her Mac this afternoon."),
              ("Rajesh Kumar", "2026-09-09T12:10", "Add the ABM token and the APNs cert to the inventory page from the VPN incident please - same failure pattern."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-032
    E("EVT-032", "incident", "crm_sync_duplicate_leads_regression", "2026-07-29",
      ["Aparna Das", "Megha Patil", "Manoj Venkatesh", "Vinod Krishnamurthy", "Wei Lin Tan"], "Demand Generation",
      system="HubSpot Marketing Hub", policy="CRM Data Hygiene & Lead Ownership Policy", project="HubSpot-Salesforce Lead Sync Cleanup",
      summary="Duplicate leads reappeared in Salesforce (about 430 in 3 days) after a HubSpot workflow that had been disabled during the "
              "sync cleanup was re-enabled by mistake during the April connector mapping fix. Aparna Das and Megha Patil disabled the "
              "workflow, merged duplicates, and added a monitor - and the new CRM hygiene policy now requires a Jira ticket for mapping changes.",
      outcome="resolved", drift=False, related_events=["EVT-007"], tags=["crm", "hubspot", "salesforce", "duplicates", "regression"],
      tickets=[
          T("Duplicate leads being created in Salesforce from HubSpot again (approx 430 since 26-Jul)",
            "SDRs report duplicate leads for the same contact: one from the web form and one from the HubSpot 'Re-sync APAC contacts' "
            "workflow. Round-robin is assigning both, so two SDRs are calling the same person. This is the issue we fixed in January.",
            "Cause: the HubSpot workflow 'Re-sync APAC contacts' (disabled during the January cleanup) was re-enabled on 10-Apr as a side "
            "effect of the connector mapping change made under {{ticket:EVT-007#1}} - the workflow was re-published when the mapping was "
            "saved. It creates a new lead when 'Lead Source' changes. Disabled again 29-Jul 14:00; Megha merged 431 duplicates using the "
            "Salesforce duplicate rule report by 31-Jul; SDR ownership corrected. Added a HubSpot workflow-change alert to Marketing Ops and "
            "a weekly duplicate-lead report. Per CRM hygiene policy v2, mapping changes now require a Jira ticket and sandbox test.",
            "Wei Lin Tan", "Aparna Das", "2026-07-29", resolved="2026-07-31", group="Marketing Ops", kind="incident",
            category="crm", priority="P3"),
      ],
      emails=[
          M("Duplicate leads - regression from April mapping change",
            [("Manoj Venkatesh", ["Vinod Krishnamurthy", "Aparna Das", "Megha Patil"], "2026-07-29T16:40",
              "Vinod,\n\nThe duplicate leads are back - about 430 over three days. Cause is embarrassing: the APAC re-sync workflow we disabled "
              "in January got re-published when the connector mapping was changed in April. It's off again and Megha is merging. Two "
              "changes: Aparna gets an alert on any HubSpot workflow status change, and we'll enforce the Jira-ticket-plus-sandbox rule "
              "from the hygiene policy for every mapping change, including ours.\n\nManoj"),
             ("Vinod Krishnamurthy", ["Manoj Venkatesh", "Aparna Das", "Megha Patil"], "2026-07-29T17:15",
              "Thanks for the straight answer. SDRs have been double-calling prospects; Megha, please send the corrected ownership list to "
              "Natasha tonight so nobody calls the same person twice tomorrow.\n\nVinod")]),
      ],
      slack=[
          S("#sales-ops", [
              ("Wei Lin Tan", "2026-07-29T10:05", "Getting duplicate leads again - same contact twice, one from web form and one 'APAC re-sync'. Two of us called the same logistics manager yesterday :grimacing:"),
              ("Megha Patil", "2026-07-29T10:12", "Looking at the duplicate report. ~430 since Sunday. @Aparna is the APAC re-sync workflow on? It should have been disabled in Jan."),
              ("Aparna Das", "2026-07-29T10:40", "It's on. Re-published on 10-Apr - the day we changed the connector mapping. Disabling now."),
              ("Megha Patil", "2026-07-31T16:20", "All 431 merged, ownership fixed. Weekly dupe report is set up."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-033
    E("EVT-033", "incident", "alert_storm_misconfigured_monitors", "2026-05-08",
      ["Nandini Rajan", "Harish Gowda", "Varun Chandra", "Abhishek Yadav"], "Cloud Infrastructure & Security",
      system="Datadog Monitoring", policy="On-Call & Escalation Policy", project="Multi-Region AWS Deployment",
      summary="Enabling the Singapore standby environment's monitors with production thresholds generated ~340 PagerDuty alerts in two "
              "hours on 8-May (the standby runs at near-zero traffic, so every 'low throughput' monitor fired). Nandini Rajan muted the "
              "region and rebuilt the monitors with per-region thresholds. Led to the alert-hygiene rule in the On-Call policy v2.",
      outcome="resolved", drift=False, tags=["datadog", "alert-storm", "multi-region", "on-call"],
      tickets=[
          T("Datadog alert storm - ~340 PagerDuty alerts from ap-southeast-1 standby monitors (08-May 11:00-13:00)",
            "Since the multi-region monitors were enabled at 11:00, PagerDuty has paged Cloud on-call continuously - 'low request rate', "
            "'consumer lag zero', 'no deploys in 24h' for every service in the Singapore standby. Abhishek (on-call) is drowning; real "
            "alerts would be missed.",
            "Cause: monitors for ap-southeast-1 were cloned from ap-south-1 with production thresholds; the standby serves no live "
            "traffic, so throughput-based monitors fired for every service. Muted the `region:ap-southeast-1` scope 13:05, deleted the "
            "cloned monitors, and rebuilt with per-region thresholds (standby: health-check and replication-lag monitors only). PagerDuty "
            "incidents bulk-resolved. Follow-ups: alert review at the weekly SRE sync; On-Call policy updated with the 'page > 3 times/week "
            "without action = review' rule.",
            "Abhishek Yadav", "Nandini Rajan", "2026-05-08", resolved="2026-05-08", group="Cloud Infrastructure", kind="incident",
            category="monitoring", priority="P3"),
      ],
      slack=[
          S("#devops-sre", [
              ("Abhishek Yadav", "2026-05-08T11:40", "I've had 90 pages in 40 minutes, all Singapore standby. Is this the multi-region monitor rollout?"),
              ("Nandini Rajan", "2026-05-08T11:44", "Yes - sorry. Cloned the Mumbai monitors and the thresholds make no sense for a zero-traffic standby. Muting the region now."),
              ("Harish Gowda", "2026-05-08T11:50", "Standby should only have health + replication lag monitors. Everything throughput-based is noise until failover."),
              ("Varun Chandra", "2026-05-08T12:05", "Agreed. Nandini - rebuild with a standby monitor set. Abhishek, take the afternoon off pager, Harish covers."),
              ("Nandini Rajan", "2026-05-08T13:10", "Region muted, cloned monitors deleted, standby set (12 monitors) live. PagerDuty cleaned up."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-034
    E("EVT-034", "incident", "vendor_outage_chat", "2026-02-19",
      ["Rajesh Kumar", "Deepak Verma", "Shruti Joshi", "Ankit Chawla", "Arun Prasad", "Sandeep Malhotra"], "IT Service Desk & Endpoint",
      system="Slack", policy="Incident Management & Severity Classification SOP",
      summary="Slack had a global vendor outage from 13:10 to 15:20 IST on 19-Feb-2026 (messages failing to send, channels not loading). "
              "Per the vendor-outage runbook the fallback was Outlook and Microsoft Teams; the Service Desk emailed all staff. Two user "
              "tickets logged. No AlgoWorks-side cause.",
      outcome="resolved", drift=False, tags=["slack", "vendor-outage", "fallback"],
      tickets=[
          T("Slack outage (vendor) - messages not sending, channels not loading - 19-Feb 13:10-15:20 IST",
            "Slack desktop and mobile show 'Trouble connecting' and messages fail to send for everyone since ~13:10. status.slack.com "
            "confirms a global incident. Raising to track comms.",
            "Vendor incident (Slack status: 'Users may be unable to send messages', 13:02-15:18 IST). Fallback per runbook: all-staff email "
            "at 13:30 directing urgent comms to Microsoft Teams chat and phone; #incidents mirror in Teams 'IT-Incidents' channel. "
            "Recovered 15:20. No action required on our side; 2 user tickets linked.",
            "Rajesh Kumar", "Rajesh Kumar", "2026-02-19", resolved="2026-02-19", group="IT Service Desk", kind="incident",
            category="vendor-outage", priority="P3"),
          T("Slack not loading - is it just me?",
            "Slack desktop app stuck on 'Trouble connecting'. Reinstalled, no change. Web version also not loading.",
            "Linked to {{ticket:EVT-034#1}} - Slack vendor outage. Resolved 15:20.",
            "Ankit Chawla", "Deepak Verma", "2026-02-19", resolved="2026-02-19", group="IT Service Desk", kind="incident",
            category="collaboration", priority="P4"),
          T("Slack messages failing to send (Deal Desk)",
            "Can't send in #deal-desk - every message errors. I have three discount approvals waiting on Slack threads.",
            "Linked to {{ticket:EVT-034#1}}. Advised to use Teams/email for approvals during the outage (approvals must be recorded on the "
            "Deal Desk ticket anyway). Resolved 15:20.",
            "Arun Prasad", "Shruti Joshi", "2026-02-19", resolved="2026-02-19", group="IT Service Desk", kind="incident",
            category="collaboration", priority="P4"),
      ],
      emails=[
          M("Slack outage - use Teams or email until further notice",
            [("Rajesh Kumar", "All-Company", "2026-02-19T13:30",
              "All,\n\nSlack is having a global outage (confirmed on status.slack.com) since about 13:10. This is on Slack's side and there is "
              "nothing to fix on your laptop. Until it recovers:\n- Urgent messages: Microsoft Teams chat or phone.\n- Incidents: the 'IT-Incidents' "
              "channel in Teams.\n- Approvals: email, so there is a record.\n\nWe'll send an all-clear when Slack is back.\n\nRajesh Kumar\nIT Service Desk"),
             ("Rajesh Kumar", "All-Company", "2026-02-19T15:25", "All-clear - Slack has recovered as of 15:20. Thanks for your patience.\n\nRajesh")]),
      ]),

    # ------------------------------------------------------------------ EVT-035
    E("EVT-035", "incident", "integration_duplicate_journals_month_end", "2026-08-06",
      ["Alok Mishra", "Shalini Menon", "Manish Tiwari", "Payal Shah", "Kritika Jain", "Ashwin Raman", "Vivek Anand"],
      "Accounts Payable & Procurement", system="NetSuite ERP", policy="Month-End Close Checklist",
      project="Zoho Expense to NetSuite Integration",
      summary="During the July close (BD+2, 6-Aug), Alok Mishra found duplicate expense journals in NetSuite for 3 and 4 August: the new "
              "Zoho-NetSuite integration re-posted batches when NetSuite timed out. Manish Tiwari added idempotency keys and Payal Shah "
              "reversed 2 duplicate journals; close slipped by one day. The Month-End Close Checklist v6 added a duplicate check.",
      outcome="resolved", drift=False, tags=["netsuite", "zoho", "integration", "month-end", "duplicates"],
      tickets=[
          T("Duplicate expense journal entries in NetSuite from Zoho integration (03-Aug and 04-Aug batches)",
            "During BD+2 expense journal review the 03-Aug and 04-Aug daily batches from Zoho Expense appear twice each in NetSuite "
            "(Rs 2.14 lakh doubled). Journal IDs differ, amounts identical. Blocking the July close.",
            "Cause: the integration's retry logic re-posts the whole batch when NetSuite's REST endpoint times out (>30s) even though "
            "NetSuite had accepted the first request. Both nights had a NetSuite maintenance window overlapping the 02:00 post. Fix: "
            "idempotency key (batch date + hash) checked against a NetSuite custom record before posting; deployed 07-Aug via "
            "{{ticket:EVT-035#2}}. Payal reversed the two duplicate journals 06-Aug 17:00; close resumed 07-Aug (one day slip, CFO informed). "
            "Checklist updated: BD+2 duplicate check.",
            "Alok Mishra", "Manish Tiwari", "2026-08-06", resolved="2026-08-07", group="Finance Systems", kind="incident",
            category="integration", priority="P2", sensitivity="restricted"),
          T("Change: Zoho-NetSuite integration - idempotent batch posting (hotfix)",
            "Deploy integration v0.9.3 adding an idempotency check (batch date + payload hash stored in NetSuite custom record "
            "'ZohoBatchLog') before posting expense journals, and moving the daily post to 04:00 to avoid the NetSuite maintenance window. "
            "Rollback: revert to v0.9.2 image. Emergency-ish: needed before the close resumes.",
            "Approved by Varun Chandra (chair) out-of-cycle 07-Aug 09:30 given close impact; reviewed at CAB 11-Aug. Deployed 07-Aug 10:15 "
            "via ArgoCD (finance-integrations app). Verified no duplicate on the 07-Aug and 08-Aug batches. Closed successful.",
            "Manish Tiwari", "Varun Chandra", "2026-08-06", resolved="2026-08-11", group="Cloud Infrastructure", kind="change",
            category="application-change", priority="P2"),
      ],
      emails=[
          M("July close - one day delay (Zoho integration duplicates)",
            [("Shalini Menon", ["Ashwin Raman", "Vivek Anand"], "2026-08-06T15:30",
              "Ashwin, Vivek,\n\nWe found duplicate expense journals for 3 and 4 August from the new Zoho integration (retry re-posted after a "
              "NetSuite timeout). Payal is reversing the duplicates this afternoon and Manish has a fix going in tomorrow morning. Net effect: "
              "the July close slips one day - BD+6 lock on Friday instead of Thursday. Amounts are small (Rs 2.14 lakh) and fully "
              "identified.\n\nShalini"),
             ("Vivek Anand", ["Shalini Menon", "Ashwin Raman"], "2026-08-06T16:05",
              "Fine, one day is acceptable. Please add a duplicate check to the close checklist so this is caught at BD+2 every month, not "
              "by luck.\n\nVivek"),
             ("Ashwin Raman", ["Shalini Menon", "Vivek Anand"], "2026-08-06T16:20", "Adding it to v6 of the checklist now.\n\nAshwin")],
            sensitivity="restricted"),
      ],
      slack=[
          S("#finance", [
              ("Alok Mishra", "2026-08-06T11:10", "The Zoho expense journals for 3-Aug and 4-Aug are in NetSuite twice. Different journal IDs, same lines. @Manish @Payal"),
              ("Manish Tiwari", "2026-08-06T11:25", "Checking the integration logs. Both nights show a NetSuite timeout then a retry - I bet NetSuite accepted the first one."),
              ("Payal Shah", "2026-08-06T11:30", "I'll reverse the duplicates once you confirm which journal IDs are the retries."),
              ("Manish Tiwari", "2026-08-06T14:40", "Confirmed: JE-118204 and JE-118231 are the retries. Fix is an idempotency key; CHG raised for tomorrow morning."),
              ("Payal Shah", "2026-08-06T17:05", "Reversed. Close resumes tomorrow after the fix is in."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-036
    E("EVT-036", "incident", "office_network_outage", "2026-03-31",
      ["Deepak Verma", "Shruti Joshi", "Rajesh Kumar", "Aditya Rao", "Nisha Pandey", "Ashwin Raman"], "IT Service Desk & Endpoint",
      system="Microsoft 365", policy="Change Management Policy",
      summary="Wi-Fi on floor 3 of the Bengaluru office dropped for ~2.5 hours on 31-Mar after the wireless controller auto-installed a "
              "firmware update overnight that broke the floor-3 access point group. Shruti Joshi rolled the firmware back; auto-update was "
              "disabled and firmware updates now go through a CHG.",
      outcome="resolved", drift=False, tags=["office", "wifi", "network", "firmware"],
      tickets=[
          T("Bengaluru office floor 3 Wi-Fi down since ~09:00 (31-Mar)",
            "All of floor 3 (Engineering, Finance) cannot connect to AlgoWorks-Corp Wi-Fi - SSID visible but authentication fails. Floors "
            "2 and 4 fine. Wired desks work. Approx 40 people affected; several joined calls from the cafe on floor 2.",
            "Cause: the wireless controller auto-installed firmware 8.10.3 at 02:30; the update reset the RADIUS profile on the "
            "floor-3 AP group (a known issue per the vendor's release notes). Shruti rolled the controller back to 8.9.8 at 11:20 and "
            "re-applied the profile; floor 3 recovered 11:35. Controller auto-update disabled; firmware updates will be raised as Normal "
            "changes with a CAB slot and tested on the floor-4 AP group first.",
            "Aditya Rao", "Shruti Joshi", "2026-03-31", resolved="2026-03-31", group="IT Service Desk", kind="incident",
            category="network", priority="P2"),
          T("Wi-Fi authentication failing - floor 3, Talent Acquisition desks",
            "Can't get onto AlgoWorks-Corp on my laptop or phone; interview candidates in Room Heron also can't join the guest network? "
            "(Guest seems fine actually, just corp.)",
            "Linked to {{ticket:EVT-036#1}}. Guest SSID confirmed unaffected. Resolved 11:35.",
            "Nisha Pandey", "Deepak Verma", "2026-03-31", resolved="2026-03-31", group="IT Service Desk", kind="incident",
            category="network", priority="P3"),
          T("No Wi-Fi on floor 3 - FP&A",
            "Floor 3 corp Wi-Fi not working for my whole team. Using a wired dock for now but the two analysts don't have docks.",
            "Linked to {{ticket:EVT-036#1}}. Two spare docks issued from stock at 10:00 as interim. Resolved 11:35; docks retained for the team.",
            "Ashwin Raman", "Deepak Verma", "2026-03-31", resolved="2026-03-31", group="IT Service Desk", kind="incident",
            category="network", priority="P3"),
      ],
      slack=[
          S("#bengaluru-office", [
              ("Aditya Rao", "2026-03-31T09:12", "Floor 3 Wi-Fi is down for everyone near us - anyone else?"),
              ("Karthik Iyer", "2026-03-31T09:13", "Same, whole floor I think"),
              ("Deepak Verma", "2026-03-31T09:20", "We're on it - floors 2 and 4 are fine, it's the floor-3 AP group. Wired docks work if you have one; spares at the Service Desk."),
              ("Shruti Joshi", "2026-03-31T10:05", "Controller took a firmware update overnight and it's broken the RADIUS profile for floor 3. Rolling back, ~1 hour."),
              ("Shruti Joshi", "2026-03-31T11:37", "Floor 3 is back. Sorry all - auto-update is now off and firmware goes through change management from here."),
              ("Nisha Pandey", "2026-03-31T11:40", "Confirmed working, thanks Shruti!"),
          ]),
      ]),
]
