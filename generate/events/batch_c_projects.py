"""Layer 6/7 - Project decision / requirements-change events EVT-037..EVT-049 (with derived artifacts)."""
from events.dsl import E, T, M, S, D

EVENTS = [
    # ------------------------------------------------------------------ EVT-037
    E("EVT-037", "project_decision", "architecture_decision_record", "2026-01-20",
      ["Rohan Mehta", "Priya Shah", "Sneha Kulkarni", "Karthik Iyer", "Arjun Venkataraman", "Harish Gowda"], "Platform Backend",
      system="AlgoWorks Fleet Production Platform", policy="Code Review & Branch Protection Standard",
      project="AlgoWorks Fleet v4 API Platform Migration",
      summary="ADR-014: the v4 public API stays REST with OpenAPI-first contracts (generated clients and contract tests); gRPC is adopted "
              "only for internal service-to-service calls behind the gateway, phased after GA. Decided at the v4 architecture review on "
              "20-Jan-2026, approved by Arjun Venkataraman.",
      outcome="decided", drift=False, tags=["adr", "v4", "api", "architecture"],
      docs=[
          D("ADR-014: v4 public API protocol - REST/OpenAPI-first; gRPC internal only",
            "**Status:** Accepted (20 January 2026) | **Deciders:** Rohan Mehta, Sneha Kulkarni, Priya Shah, Arjun Venkataraman | **Project:** {{proj:AlgoWorks Fleet v4 API Platform Migration}}\n\n"
            "## Context\nThe v3 monolith exposes ~180 REST endpoints with inconsistent contracts and no machine-readable spec. Customers "
            "integrate with the API directly (34 enterprise customers have custom integrations). For v4 we needed to choose the external "
            "protocol and how strictly to manage contracts.\n\n"
            "## Options considered\n1. **REST + OpenAPI-first** (spec is the source of truth; server stubs, clients and contract tests generated).\n"
            "2. **gRPC externally with a REST transcoding gateway.**\n3. **GraphQL** for the portal with REST retained for integrations.\n\n"
            "## Decision\nOption 1 for the public API. gRPC is adopted **only** for internal service-to-service calls behind the gateway, "
            "phased in after GA. GraphQL is not pursued.\n\n"
            "## Rationale\n- Customer integrations are REST/JSON; a protocol change would reset the 12-month migration clock.\n"
            "- OpenAPI-first gives us contract tests in CI (blocking breaking changes) and generated SDKs for the portal and mobile apps.\n"
            "- gRPC's benefits (streaming, binary efficiency) matter most for telematics ingest, which is internal.\n\n"
            "## Consequences\n- `algoworks-api-v4` repo adopts spec-first workflow; PRs that change `openapi.yaml` require two approvals (data-pipeline rule extended).\n"
            "- Sneha Kulkarni owns the contract-test harness (PLAT-2150).\n- Gateway keeps v3 compatibility routes for 12 months from GA.\n- Revisit gRPC-external in Q2 2027 if a customer requires streaming.",
            doc_type="decision_record", space="ENG", created="2026-01-21", authors=["Rohan Mehta", "Sneha Kulkarni"],
            labels=["adr", "v4", "api"]),
      ],
      emails=[
          M("ADR-014 approved - v4 stays REST/OpenAPI-first",
            [("Rohan Mehta", ["Arjun Venkataraman", "Harish Gowda"], "2026-01-20T17:30",
              "Arjun,\n\nWe closed the protocol question at today's review: v4 public API remains REST with OpenAPI-first contracts; gRPC only "
              "internally after GA. Sneha's write-up is on Confluence as ADR-014. Main driver is the 34 customers with direct REST "
              "integrations - we don't want to restart their migration clock. Harish, FYI for the gateway sizing.\n\nRohan"),
             ("Arjun Venkataraman", ["Rohan Mehta", "Harish Gowda"], "2026-01-20T18:05",
              "Approved. Make the contract tests a required check before the first customer moves to v4.\n\nArjun")]),
      ],
      slack=[
          S("#proj-v4-migration", [
              ("Priya Shah", "2026-01-20T16:10", "Decision from the review: REST + OpenAPI-first for external, gRPC internal only post-GA. ADR going up tonight."),
              ("Karthik Iyer", "2026-01-20T16:12", "So the spec is the source of truth now - no more hand-editing handlers first?"),
              ("Sneha Kulkarni", "2026-01-20T16:15", "Correct. Spec PR -> generated stubs -> implement. I'm building the contract-test harness this sprint."),
              ("Daniel Fernandes", "2026-01-20T16:20", "Does that mean openapi.yaml changes need two reviewers?"),
              ("Rohan Mehta", "2026-01-20T16:22", "Yes, same as the data-pipeline rule. Adding it to CODEOWNERS."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-038
    E("EVT-038", "project_decision", "architecture_decision_record", "2025-11-10",
      ["Varun Chandra", "Nandini Rajan", "Siddharth Jain", "Sandeep Malhotra", "Vivek Anand", "Harish Gowda"],
      "Cloud Infrastructure & Security", system="AWS Production Account", policy="Change Management Policy",
      project="Multi-Region AWS Deployment",
      summary="ADR: the Singapore region is built as a warm standby (active-passive) with cross-region RDS replication and Route 53 "
              "failover, not active-active, because it meets the 30-minute RTO and APAC residency ask at ~40% of the cost. Approved by "
              "Sandeep Malhotra with CFO visibility on the ~USD 9k/month run-rate.",
      outcome="decided", drift=False, tags=["adr", "aws", "multi-region", "cost"],
      tickets=[
          T("Change: create ap-southeast-1 production baseline (VPC, EKS, RDS read replica, ArgoCD cluster registration)",
            "Stand up the Singapore warm-standby baseline per ADR-011: VPC and subnets via Terraform, EKS cluster, cross-region RDS read "
            "replica of prod-postgres, ArgoCD cluster registration (no apps synced yet). No customer traffic. Rollback: destroy via "
            "Terraform. Window: 24-Nov 20:00-24:00 IST.",
            "Approved at CAB 20-Nov (Thu). Implemented 24-Nov 20:10-23:15. Replica lag < 2s. No production impact. Closed successful.",
            "Nandini Rajan", "Varun Chandra", "2025-11-13", resolved="2025-11-25", group="Cloud Infrastructure", kind="change",
            category="infrastructure-change", priority="P3"),
      ],
      docs=[
          D("ADR-011: Multi-region topology - warm standby in ap-southeast-1 (active-passive)",
            "**Status:** Accepted (10 November 2025) | **Deciders:** Varun Chandra, Sandeep Malhotra; consulted Rohan Mehta, Vivek Anand | **Project:** {{proj:Multi-Region AWS Deployment}}\n\n"
            "## Context\nTwo APAC prospects (Singapore, Malaysia) require data residency in the region and a documented DR capability; our "
            "current RTO from a single-region loss is 'rebuild from backups' (~6 hours).\n\n"
            "## Options\n| Option | RTO | Monthly run-rate (est.) | Complexity |\n|---|---|---|---|\n"
            "| A. Backup/restore only (status quo) | ~6h | USD 0 | low |\n| B. **Warm standby (active-passive)**: replica DB, pre-built EKS, apps synced but scaled to zero, Route 53 failover | ~30 min | ~USD 9,000 | medium |\n"
            "| C. Active-active with global load balancing and multi-writer DB | ~0 | ~USD 22,000 | high (data consistency for telematics writes) |\n\n"
            "## Decision\n**Option B.** Singapore is a warm standby with cross-region RDS replication (async), EKS pre-provisioned, ArgoCD "
            "applications synced with replicas=0, and Route 53 health-check failover. Failover is a documented manual runbook (promote "
            "replica, scale apps, flip DNS) targeting 30 minutes.\n\n"
            "## Consequences\n- Meets residency by allowing APAC tenants to be pinned to the Singapore region in phase 2 (Q3 2026).\n"
            "- Monitoring must distinguish standby from active (see incident of May 2026 for what happens otherwise).\n- Quarterly failover drill required; first drill March 2026.\n- FP&A tracks the run-rate as a separate cost line.",
            doc_type="decision_record", space="IT", created="2025-11-11", authors=["Varun Chandra"], labels=["adr", "aws", "dr"]),
      ],
      emails=[
          M("Multi-region: recommending warm standby (approx USD 9k/month)",
            [("Varun Chandra", ["Sandeep Malhotra", "Vivek Anand"], "2025-11-10T15:40",
              "Sandeep, Vivek,\n\nFor the Singapore build we recommend a warm standby rather than active-active: ~30 minute RTO, satisfies the "
              "residency requirement for APAC tenants, and roughly USD 9k/month versus USD 22k for active-active - which would also mean "
              "solving multi-writer consistency for telematics, a 6+ month engineering problem. Details in ADR-011 on Confluence. Vivek, "
              "I'd like this as its own cost line in the FY27 plan.\n\nVarun"),
             ("Vivek Anand", ["Varun Chandra", "Sandeep Malhotra"], "2025-11-10T17:20",
              "Fine with 9k as a separate line. Please make sure the APAC pricing Rahul is building recovers it.\n\nVivek"),
             ("Sandeep Malhotra", ["Varun Chandra", "Vivek Anand"], "2025-11-11T09:00", "Approved. Go ahead with the CAB submission for the baseline.\n\nSandeep")]),
      ],
      slack=[
          S("#proj-multi-region", [
              ("Varun Chandra", "2025-11-11T09:15", "ADR-011 is approved: warm standby in Singapore. Nandini owns the Terraform baseline, Siddharth the ArgoCD cluster registration, Harish the failover runbook."),
              ("Siddharth Jain", "2025-11-11T09:20", "Apps synced with replicas=0 in the standby - so ArgoCD shows them 'healthy' but nothing runs. We'll need a clear label so nobody panics."),
              ("Harish Gowda", "2025-11-11T09:25", "And the monitors need to know it's a standby. Adding that to the runbook."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-039
    E("EVT-039", "project_decision", "requirements_change_scope_expansion", "2026-04-15",
      ["Meera Krishnan", "Aditya Rao", "Aakash Bhatia", "Natasha D'Souza", "Arjun Venkataraman", "Kavita Bhatnagar", "Kavya Reddy",
       "Varsha Pai", "Ishita Bose"],
      "Web & Mobile Frontend", system="AlgoWorks Fleet Customer Portal", policy="Application Access Request Policy",
      project="Customer Portal Revamp",
      summary="Scope change: after Meridian Logistics and two APAC prospects made SAML SSO with their own identity providers a condition of "
              "renewal/purchase, the Customer Portal Revamp added customer-IdP SSO. Meera Krishnan re-planned: launch moved from "
              "September to November 2026 (six weeks); IAM provisioned a test SAML IdP in Okta for development.",
      outcome="decided", drift=False, tags=["requirements-change", "portal", "sso", "timeline"],
      tickets=[
          T("Okta test tenant / SAML IdP for Customer Portal SSO development",
            "For the portal's new customer-IdP SSO feature we need a SAML identity provider to test against that behaves like a customer's "
            "Azure AD / Okta. Requesting a dedicated Okta preview org (or a SAML app in our dev Okta) with test users the frontend team "
            "controls. Manager approval: Meera Krishnan.",
            "Created a SAML 2.0 IdP configuration in the Okta developer org (algoworks-dev) with 5 test users and metadata shared via "
            "1Password vault 'Frontend-Dev'. Lakshmi added Aditya and Ishita as app admins. No production Okta changes.",
            "Aditya Rao", "Kavya Reddy", "2026-04-16", resolved="2026-04-20", group="IAM", approvers=["Meera Krishnan"]),
      ],
      docs=[
          D("Customer Portal Revamp - scope change decision: customer-IdP SAML SSO (15 April 2026)",
            "**Meeting:** Portal Revamp steering, 15 April 2026 | **Attendees:** Meera Krishnan (chair), Aditya Rao, Ishita Bose, Neha Agarwal, "
            "Varsha Pai, Natasha D'Souza, Aakash Bhatia, Arjun Venkataraman | **Project:** {{proj:Customer Portal Revamp}}\n\n"
            "## Request\nSales (Aakash Bhatia) reports that Meridian Logistics has made 'login with our Azure AD' a condition of their "
            "October renewal, and two APAC prospects (Singapore, Malaysia) asked the same in RFPs. Today portal users have AlgoWorks-managed "
            "passwords only.\n\n"
            "## Options\n1. Decline / defer to 2027 - risk to a Rs 3.2 crore renewal and two APAC deals.\n2. Add SAML SSO (SP-initiated, per-tenant IdP metadata, JIT user provisioning) to the revamp scope.\n3. Ship the revamp on time and add SSO as a fast-follow in Q4.\n\n"
            "## Decision\n**Option 2.** SAML SSO is in scope. Launch moves from **15 September to 2 November 2026** (6 weeks). JIT "
            "provisioning maps IdP groups to portal roles; SCIM deferred. IAM (Kavya Reddy) provides a test IdP. Sales will not commit "
            "SSO dates to customers beyond 'November' until the feature passes security review.\n\n"
            "## Actions\n- Meera: re-baseline the plan; communicate the date change to Marketing (v4 campaign alignment).\n"
            "- Aditya: technical design for SAML/JIT (review with Nikhil Bhatt for security).\n- Aakash/Natasha: confirm Meridian accepts November.\n- Varsha: update the launch messaging.",
            doc_type="meeting_notes", space="ENG", created="2026-04-15", authors=["Meera Krishnan"], labels=["portal", "sso", "scope-change"]),
      ],
      emails=[
          M("Meridian renewal - SSO with their Azure AD is now a hard requirement",
            [("Aakash Bhatia", ["Meera Krishnan", "Natasha D'Souza"], "2026-04-09T18:20",
              "Meera,\n\nMeridian's IT security team have added 'SSO with our Azure AD' as a condition of the October renewal (Rs 3.2 crore ARR). "
              "Two APAC RFPs ask for the same. Is there any way the portal revamp can include it? I know it's not in scope. Natasha is "
              "aware.\n\nAakash"),
             ("Meera Krishnan", ["Aakash Bhatia", "Natasha D'Souza"], "2026-04-10T09:45",
              "Not in scope today, and it's not small - SAML, per-tenant IdP config, JIT provisioning, security review. Rough estimate is six "
              "weeks of slip. Let's take it to the steering meeting on Wednesday with Arjun; I'd rather decide it properly than promise "
              "Meridian something.\n\nMeera")]),
          M("Portal revamp launch moves to 2 November - SSO added to scope",
            [("Meera Krishnan", ["Arjun Venkataraman", "Kavita Bhatnagar", "Sanya Kapadia"], "2026-04-15T17:10",
              "All,\n\nSteering decision today: customer-IdP SAML SSO is now in the portal revamp scope (renewal and APAC pipeline "
              "dependency). Launch moves from 15 September to 2 November. Notes on Confluence. Sanya/Kavita - this affects the v4 campaign "
              "sequencing; happy to talk through options.\n\nMeera"),
             ("Kavita Bhatnagar", ["Meera Krishnan", "Arjun Venkataraman", "Sanya Kapadia"], "2026-04-16T08:30",
              "Understood. Sanya will re-sequence - we may lead the campaign with the v4 API and follow with the portal.\n\nKavita")]),
      ],
      slack=[
          S("#proj-portal-revamp", [
              ("Meera Krishnan", "2026-04-15T16:30", "Decision: SAML SSO with customer IdPs is in scope. Launch is now 2 Nov. I know - but the alternative was losing Meridian."),
              ("Aditya Rao", "2026-04-15T16:33", "I'll draft the SAML/JIT design this week. Need a test IdP - raising a request with IAM."),
              ("Ishita Bose", "2026-04-15T16:35", "Per-tenant IdP metadata upload in the admin settings screen? That's a new screen."),
              ("Aditya Rao", "2026-04-15T16:36", "Yes, plus role mapping. Let's scope it together tomorrow."),
              ("Neha Agarwal", "2026-04-15T16:40", "Adding SSO scenarios to the regression plan. We'll need the test IdP for automation too."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-040
    E("EVT-040", "project_decision", "design_decision", "2025-09-22",
      ["Meera Krishnan", "Farhan Siddiqui", "Vikram Nair", "Karthik Iyer"], "Web & Mobile Frontend",
      system="AlgoWorks Fleet Driver Mobile App", policy="Feature Flag & Rollback Guidelines", project="Driver App Offline Mode",
      summary="Offline mode design decision: trip events are queued in a local SQLite store and synced in order; conflicts on the same "
              "trip are resolved last-write-wins by device timestamp, with server-side audit of overwritten values. Simpler than CRDT/merge "
              "and acceptable because drivers rarely edit the same trip from two devices.",
      outcome="decided", drift=False, tags=["design", "mobile", "offline", "conflict-resolution"],
      docs=[
          D("Driver App Offline Mode - design decision: local queue and last-write-wins conflict resolution",
            "**Date:** 22 September 2025 | **Authors:** Farhan Siddiqui, Vikram Nair | **Approved:** Meera Krishnan | **Project:** {{proj:Driver App Offline Mode}}\n\n"
            "## Problem\nDrivers lose connectivity in warehouses and rural routes; check-ins and proof-of-delivery captured offline must "
            "reach the platform reliably and in order, and conflicts must be resolved predictably.\n\n"
            "## Decision\n1. **Local queue:** SQLite (Room on Android, GRDB on iOS) event table with monotonically increasing sequence numbers per device.\n"
            "2. **Sync:** background job replays events in order over the v3 batch endpoint (v4 later); at-least-once with server-side idempotency key = deviceId + sequence.\n"
            "3. **Conflict resolution:** **last-write-wins by device timestamp** for the same trip field. The server keeps an audit row of "
            "the overwritten value (`trip_event_audit`) so support can see what was replaced.\n4. Photos (POD) are uploaded after events, with retry; the event references the photo by local id until upload completes.\n\n"
            "## Alternatives rejected\n- CRDT / field-level merge: correct but heavy; conflicts are rare (one driver per trip in 99.6% of trips).\n- Server-wins: loses legitimate offline edits.\n\n"
            "## Risks\n- Device clock skew -> server compares against receive time when skew > 5 minutes and flags the trip.\n- Large queues after long offline periods -> batch size 200, progress UI.\n\n"
            "Shipped in Driver App 3.5 (January 2026).",
            doc_type="decision_record", space="ENG", created="2025-09-23", authors=["Farhan Siddiqui", "Vikram Nair"],
            labels=["mobile", "offline", "design"]),
      ],
      slack=[
          S("#eng-frontend", [
              ("Farhan Siddiqui", "2025-09-22T15:05", "Offline mode design is agreed: local SQLite queue, in-order replay, last-write-wins on conflicts with a server audit row. Doc going up."),
              ("Karthik Iyer", "2025-09-22T15:10", "From the platform side: idempotency key = deviceId+sequence, and we'll add trip_event_audit. Clock skew check at 5 min."),
              ("Vikram Nair", "2025-09-22T15:12", "iOS side mirrors it with GRDB. POD photos upload after events."),
              ("Meera Krishnan", "2025-09-22T15:20", "Approved. Let's make sure support knows about the audit table - they'll get 'my delivery time changed' tickets."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-041
    E("EVT-041", "project_decision", "cutover_decision", "2025-10-27",
      ["Nikhil Bhatt", "Kavya Reddy", "Lakshmi Narayanan", "Megha Patil", "Rakesh Nair", "Sandeep Malhotra", "Rahul Kapoor",
       "Anita Desai", "Manoj Venkatesh", "Geeta Iyengar"],
      "Identity & Access Management", system="Okta SSO", policy="Password & MFA Standard", project="Okta SSO Rollout Phase 2",
      summary="SSO Phase 2 cutover decision: Salesforce, Zendesk, HubSpot and Darwinbox become SSO-only (local passwords disabled) on "
              "15-Dec-2025, app assignment moves to Okta groups, and Darwinbox drives Okta account creation. One exception: the shared "
              "Salesforce demo account stays local until a 1Password vault exists. Two CHGs implemented the cutover.",
      outcome="decided", drift=False, tags=["sso", "cutover", "okta", "decision"],
      tickets=[
          T("Change: Salesforce SSO-only cutover (disable local passwords, group-based assignment)",
            "Per the Phase 2 decision: enable 'SSO required' on the Salesforce org, disable password login for all users except the "
            "demo-admin integration user, move all user assignments from direct to Okta group 'salesforce-users'. Window 15-Dec 07:00-09:00 "
            "IST. Rollback: re-enable password login.",
            "Approved CAB 09-Dec (Tue). Implemented 15-Dec 07:10-08:20 by Megha Patil and Kavya Reddy. 11 users had direct assignments "
            "left; migrated. 3 users had no Okta account (former interns) - licences removed. Closed successful.",
            "Kavya Reddy", "Nikhil Bhatt", "2025-12-02", resolved="2025-12-15", group="IAM", kind="change", category="application-change",
            priority="P2"),
          T("Change: Zendesk, HubSpot, Darwinbox SSO-only cutover",
            "Per the Phase 2 decision: enforce SSO on Zendesk (agents), HubSpot and Darwinbox; disable local passwords; Okta groups "
            "zendesk-agents, hubspot-users, darwinbox-all. Darwinbox -> Okta provisioning (HR-driven) enabled. Window 15-Dec 09:00-12:00. "
            "Rollback: per app, re-enable local auth.",
            "Approved CAB 09-Dec. Implemented 15-Dec 09:05-11:40 (Lakshmi Narayanan, Rakesh Nair for Darwinbox). Darwinbox provisioning "
            "tested with 2 dummy joiners. HubSpot: 4 agency users without Okta accounts moved to sponsored contractor accounts. Closed successful.",
            "Lakshmi Narayanan", "Nikhil Bhatt", "2025-12-02", resolved="2025-12-15", group="IAM", kind="change",
            category="application-change", priority="P2"),
      ],
      docs=[
          D("Okta SSO Phase 2 - cutover decision log (27 October 2025)",
            "**Meeting:** SSO Phase 2 steering | **Chair:** Nikhil Bhatt | **Attendees:** Sandeep Malhotra, Kavya Reddy, Lakshmi Narayanan, "
            "Megha Patil (Sales Ops), Rakesh Nair (HR Ops), Anita Desai (CS), Manoj Venkatesh (Marketing) | **Project:** {{proj:Okta SSO Rollout Phase 2}}\n\n"
            "## Decisions\n1. **Cutover date: Monday 15 December 2025.** Salesforce, Zendesk, HubSpot and Darwinbox become SSO-only; local passwords disabled.\n"
            "2. **Group-based assignment.** All application assignments move from direct user assignment to Okta groups. (Note from Q2 2026 review: some Salesforce direct assignments survived - see {{doc:EVT-016#1}}.)\n"
            "3. **HR-driven provisioning.** Darwinbox creates the Okta account on Day -1; IT no longer creates accounts by hand.\n"
            "4. **Exception:** the shared Salesforce demo account (demo-admin) remains a local login until Sales has a shared 1Password vault. Owner: Vinod Krishnamurthy. (Vault created May 2026.)\n"
            "5. **Communication:** all-staff email 1 December; department heads brief teams; Service Desk extended hours on cutover day.\n\n"
            "## Risks discussed\n- Agency users in HubSpot without Okta accounts -> sponsored contractor accounts.\n- Recruiters using Darwinbox on mobile -> Okta Verify enrolment drive in November.\n\n"
            "## Actions\n- Kavya: CHG for Salesforce cutover. Lakshmi: CHG for Zendesk/HubSpot/Darwinbox.\n- Rakesh: Darwinbox provisioning test plan.\n- Nikhil: update the Password & MFA Standard after cutover (done, v3 June 2025 -> v4 May 2026).",
            doc_type="decision_log", space="IT", created="2025-10-27", authors=["Nikhil Bhatt"], labels=["sso", "okta", "cutover"],
            references=["{{doc:EVT-016#1}}"], related_events=["EVT-016"]),
      ],
      emails=[
          M("SSO cutover on 15 December - what changes for your teams",
            [("Nikhil Bhatt", ["Rahul Kapoor", "Anita Desai", "Manoj Venkatesh", "Geeta Iyengar", "Sandeep Malhotra"], "2025-10-28T10:30",
              "All,\n\nFollowing yesterday's steering meeting: on Monday 15 December, Salesforce, Zendesk, HubSpot and Darwinbox move to "
              "Okta-only login. Local passwords stop working that morning. What your teams need to do before then: make sure everyone has "
              "Okta Verify enrolled (IAM will chase stragglers), and tell us about any shared or agency logins so we can convert them to "
              "sponsored accounts. The only agreed exception is the Sales demo account.\n\nDetails and the decision log are on Confluence.\n\nNikhil"),
             ("Rahul Kapoor", ["Nikhil Bhatt", "Sandeep Malhotra"], "2025-10-28T12:15",
              "Thanks Nikhil. Vinod will send you the list of shared logins this week.\n\nRahul")]),
      ],
      slack=[
          S("#it-access-requests", [
              ("Kavya Reddy", "2025-10-28T09:40", "Heads-up: SSO Phase 2 cutover is 15 Dec. From then, please don't ask us to 'reset the Salesforce password' - there won't be one :slightly_smiling_face: Everything is Okta."),
              ("Megha Patil", "2025-10-28T09:45", "And Salesforce assignments will be via the salesforce-users Okta group. I'm migrating direct assignments in the sandbox first."),
              ("Rakesh Nair", "2025-10-28T09:50", "Darwinbox will create the Okta account for new joiners from December - HR Ops won't email IT for accounts anymore."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-042
    E("EVT-042", "project_decision", "process_decision_gitops_approvals", "2025-08-25",
      ["Varun Chandra", "Siddharth Jain", "Harish Gowda", "Rohan Mehta", "Sandeep Malhotra", "Arjun Venkataraman", "Nikhil Bhatt"],
      "Cloud Infrastructure & Security", system="ArgoCD Deployment Platform", policy="Change Management Policy",
      project="ArgoCD GitOps Migration",
      summary="GitOps process decision: from the ArgoCD go-live (1-Dec-2025), a reviewed and merged pull request to the algoworks-deploy "
              "environment repo is the approval record for standard application deployments; no CHG or CAB slot is needed. CAB is retained "
              "for infrastructure, network, identity and database changes. Approved at CAB on 2-Sep-2025. The Change Management Policy "
              "(v2, June 2025) was never updated to reflect this.",
      outcome="decided", drift=False, related_events=["EVT-052"], tags=["gitops", "change-management", "process", "decision"],
      tickets=[
          T("Change (process): GitOps PR approval replaces CAB for standard application deployments from ArgoCD go-live",
            "Proposal for CAB: with ArgoCD, every production application deployment is a merged PR in algoworks-deploy with a required "
            "CODEOWNER review and CI checks. We propose that from go-live (target 1-Dec-2025) this PR record is the change approval for "
            "'standard application deployments' (image tag / replica / feature-flag config changes to existing services). CAB continues "
            "to review: infrastructure (Terraform), network, Okta/identity, database schema/parameter changes, and new services. Emergency "
            "changes unchanged.",
            "Approved at CAB 02-Sep-2025 (Tue): Varun Chandra (chair), Nikhil Bhatt, Rohan Mehta, Rajesh Kumar. Effective from ArgoCD "
            "go-live 01-Dec-2025. Action: Varun to update the Change Management Policy to add the GitOps category (NOT DONE as of "
            "Sep-2026 - policy still at v2). Decision record: {{doc:EVT-042#1}}.",
            "Varun Chandra", "Varun Chandra", "2025-08-26", resolved="2025-09-02", group="Cloud Infrastructure", kind="change",
            category="process-change", priority="P3"),
      ],
      docs=[
          D("Decision: GitOps pull-request approval as the change record for application deployments",
            "**Date:** 25 August 2025 (proposed), 2 September 2025 (approved at CAB) | **Owner:** Varun Chandra | **Project:** {{proj:ArgoCD GitOps Migration}} | **CAB record:** {{ticket:EVT-042#1}}\n\n"
            "## Context\nUnder the Change Management Policy (v2) every production application deployment needs a CHG reviewed at the "
            "twice-weekly CAB. With Jenkins this was tolerable (2-3 deploys/week). ArgoCD enables 10-20 deploys/day; CAB would become the "
            "bottleneck and CHG records would be rubber-stamped.\n\n"
            "## Decision\nFrom ArgoCD go-live (1 December 2025):\n"
            "- **Standard application deployment** = a change to an existing service's image tag, replica count, resource limits, or feature-flag config in `algoworks-deploy`. "
            "Approval = merged PR with required CODEOWNER review and green CI. **No CHG, no CAB.** ArgoCD's sync history plus the PR is the audit trail.\n"
            "- **Still CAB / CHG:** Terraform/infrastructure, network and firewall, Okta and identity configuration, database schema or parameter changes, new services or new external endpoints, anything touching secrets management.\n"
            "- **Emergency changes:** unchanged (verbal approval by Cloud Infra Lead, retrospective CHG).\n\n"
            "## Open question (raised at CAB, not resolved)\nWhether config-only changes with high blast radius (connection pools, timeouts, rate limits) should carry a `high-risk-config` label requiring an extra reviewer. Revisit after 3 months. (See the March 2026 postmortem, action item 3.)\n\n"
            "## Follow-ups\n- Update the Change Management Policy with a 'GitOps standard deployment' category - **owner Varun Chandra, due October 2025.**\n- Engineering onboarding guide to explain what does and doesn't need a CHG.",
            doc_type="decision_record", space="IT", created="2025-09-02", authors=["Varun Chandra"],
            references=["{{ticket:EVT-042#1}}"], labels=["gitops", "change-management", "decision"]),
      ],
      emails=[
          M("CAB decision: app deployments via GitOps PR from December",
            [("Varun Chandra", ["Sandeep Malhotra", "Arjun Venkataraman"], "2025-09-02T16:45",
              "Sandeep, Arjun,\n\nCAB approved the GitOps proposal today: from the ArgoCD go-live, a reviewed PR in algoworks-deploy is the "
              "change approval for standard application deployments; CAB keeps infra, network, identity, DB and new services. Record and "
              "reasoning on Confluence. I'll update the Change Management Policy with the new category before go-live.\n\nVarun"),
             ("Arjun Venkataraman", ["Varun Chandra", "Sandeep Malhotra"], "2025-09-02T17:30",
              "Good outcome. Please make the policy update visible - engineers read the policy, not CAB minutes.\n\nArjun"),
             ("Sandeep Malhotra", ["Varun Chandra", "Arjun Venkataraman"], "2025-09-03T08:50", "Agreed on both counts.\n\nSandeep")]),
      ],
      slack=[
          S("#devops-sre", [
              ("Varun Chandra", "2025-09-02T16:20", "CAB approved: from ArgoCD go-live (1 Dec), standard app deploys = merged PR in algoworks-deploy. No CHG. Infra/network/identity/DB still go to CAB."),
              ("Siddharth Jain", "2025-09-02T16:22", ":tada: finally"),
              ("Harish Gowda", "2025-09-02T16:25", "What counts as 'standard'? Image tag and replicas obviously. Config maps?"),
              ("Varun Chandra", "2025-09-02T16:30", "Config for an existing service, yes. New service or anything in algoworks-infra (Terraform) = CAB. I'll write it up properly."),
              ("Rohan Mehta", "2025-09-02T16:35", "Please put it in the policy too, not just Confluence - people will ask 'do I need a CHG' forever otherwise."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-043
    E("EVT-043", "project_decision", "requirements_change_catalog_routing", "2026-05-19",
      ["Rajesh Kumar", "Shruti Joshi", "Deepak Verma", "Kavya Reddy", "Nikhil Bhatt", "Megha Patil"], "IT Service Desk & Endpoint",
      system="ServiceNow ITSM", policy="Application Access Request Policy", project="ServiceNow Self-Service Catalog",
      summary="Self-Service Catalog design decision: application-access catalog items route approval to the line manager (from Darwinbox) "
              "and then to the system owner's team from the Systems Directory table, replacing free-text incidents. Wave 1 covers "
              "Salesforce, Zendesk, HubSpot, Metabase and GitHub; go-live 8-Jun-2026.",
      outcome="decided", drift=False, tags=["servicenow", "catalog", "routing", "decision"],
      tickets=[
          T("Publish access-request catalog items - wave 1 (Salesforce, Zendesk, HubSpot, Metabase, GitHub)",
            "Per the catalog design decision: publish five 'Request Access' catalog items with two-step approval (line manager from "
            "Darwinbox sync, then owning-team approver from the Systems Directory), assignment to the IAM queue for Okta group changes, "
            "and a sub-task to the system administrator for in-app role assignment. Go-live target 08-Jun.",
            "Items built by Shruti Joshi; approver mapping table loaded from the Systems Directory (owner team lead as approver for admin "
            "roles). UAT with Megha Patil (Salesforce) and Anita Desai (Zendesk) 01-05 Jun. Published 08-Jun 09:00. Free-text 'access' "
            "incidents now redirect to the catalog. Wave 2 (VPN, shared mailbox, laptop, software) planned for August.",
            "Rajesh Kumar", "Shruti Joshi", "2026-05-19", resolved="2026-06-08", group="IT Service Desk", category="itsm-configuration"),
      ],
      docs=[
          D("ServiceNow Self-Service Catalog - access request routing design (decision, 19 May 2026)",
            "**Project:** {{proj:ServiceNow Self-Service Catalog}} | **Decided by:** Rajesh Kumar, Nikhil Bhatt | **Built by:** Shruti Joshi\n\n"
            "## Problem\n60% of 'access' tickets arrive as free-text incidents with no approver named, so IAM chases approvals by Slack. "
            "The Application Access Request Policy requires a recorded line-manager approval and, for admin roles, the owning team lead.\n\n"
            "## Design\n1. One catalog item per application (wave 1: Salesforce, Zendesk, HubSpot, Metabase, GitHub; wave 2: VPN, shared mailbox, laptop, software install, contractor account).\n"
            "2. **Approval step 1:** line manager, auto-populated from the Darwinbox -> ServiceNow user sync. If the manager has a Darwinbox delegate set, the delegate is used. *Escalation when the manager is unavailable follows the policy (Department Head); the catalog does not auto-approve.*\n"
            "3. **Approval step 2 (admin roles only):** owning team lead from the Systems Directory mapping table (`u_system_owner`).\n"
            "4. **Fulfilment:** RITM assigned to IAM for the Okta group; sub-task to the system administrator for in-app role.\n"
            "5. Training prerequisites (e.g. Admin Console) are a checkbox the requester attests and IAM verifies.\n\n"
            "## Decisions\n- Do not build auto-approval on SLA breach (discussed and rejected: not in policy).\n- Role bundles from the Darwinbox onboarding automation remain separate from the catalog; new joiners still use catalog items for anything outside their bundle.\n\n"
            "## Metrics\nTarget: 80% of access requests via catalog by September 2026; median time-to-approve under 2 business days.",
            doc_type="decision_record", space="IT", created="2026-05-20", authors=["Rajesh Kumar", "Shruti Joshi"],
            labels=["servicenow", "catalog", "access-requests"]),
      ],
      slack=[
          S("#it-helpdesk", [
              ("Rajesh Kumar", "2026-05-19T15:00", "Catalog design is signed off. Wave 1 access items (Salesforce, Zendesk, HubSpot, Metabase, GitHub) go live 8 June with manager + owner approvals wired in."),
              ("Deepak Verma", "2026-05-19T15:04", "Can we make the free-text 'I need access to X' incidents auto-redirect? Half my queue is that."),
              ("Shruti Joshi", "2026-05-19T15:06", "Yes - a UI policy will suggest the catalog item when someone types 'access' in a new incident."),
              ("Kavya Reddy", "2026-05-19T15:10", "One ask: the approver field must come from Darwinbox, not whoever the requester types. We've had people put a peer as 'manager'."),
              ("Shruti Joshi", "2026-05-19T15:12", "Locked to the synced manager field. Delegates honoured if set in Darwinbox."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-044
    E("EVT-044", "project_decision", "cost_controls_decision", "2026-06-16",
      ["Suresh Pillai", "Ananya Chatterjee", "Divya Menon", "Nithin George", "Ashwin Raman", "Manish Tiwari"], "Data & Analytics Engineering",
      system="Snowflake Data Warehouse", policy="Change Management Policy", project="Snowflake Cost Optimization",
      summary="Snowflake cost decisions: one warehouse per consuming team (ENG, SALES, FIN, MKT, DBT) with 60-second auto-suspend, "
              "Metabase pinned to XS with a 5-minute timeout, a monthly credit budget per warehouse owned by FP&A with alerts at 80%, and "
              "a dbt model-pruning pass. Implemented via a CHG on 23-Jun; June spend down 31% vs January.",
      outcome="decided", drift=False, related_events=["EVT-027"], tags=["snowflake", "cost", "finops", "decision"],
      tickets=[
          T("Change: Snowflake warehouse restructure (per-team warehouses, auto-suspend, resource monitors)",
            "Per the cost optimisation decisions: create warehouses WH_ENG (M), WH_DBT (M), WH_SALES (S), WH_FIN (S), WH_MKT (XS) with "
            "60s auto-suspend; drop the shared L warehouse; bind Metabase to WH_MKT/WH_SALES by collection; resource monitors per warehouse "
            "with FP&A notification at 80% and suspend at 100%. Window 23-Jun 06:00-08:00 (before dbt run). Rollback: recreate shared L.",
            "Approved CAB 18-Jun (Thu). Implemented 23-Jun 06:05-07:30 by Ananya Chatterjee. Metabase collections re-pointed by Manish. "
            "One dbt model needed the M warehouse (fixed). Closed successful. Monthly review with FP&A set for the first Monday.",
            "Ananya Chatterjee", "Varun Chandra", "2026-06-16", resolved="2026-06-23", group="Data Engineering", kind="change",
            category="application-change", priority="P3"),
      ],
      docs=[
          D("Snowflake Cost Optimization - decisions and cost model (16 June 2026)",
            "**Project:** {{proj:Snowflake Cost Optimization}} | **Owner:** Suresh Pillai | **FP&A partner:** Nithin George | **Trigger:** January 2026 credit overrun ({{ticket:EVT-027#1}})\n\n"
            "## Decisions\n| # | Decision | Owner |\n|---|---|---|\n"
            "| 1 | One warehouse per consuming team: WH_ENG, WH_DBT, WH_SALES, WH_FIN, WH_MKT. Shared L warehouse retired. | Ananya |\n"
            "| 2 | Auto-suspend 60 seconds on all warehouses; auto-resume on. | Ananya |\n"
            "| 3 | Metabase bound to XS/S warehouses by collection, statement timeout 5 minutes, no scheduled refresh under 1 hour without Data Eng review. | Manish |\n"
            "| 4 | Resource monitors per warehouse with a monthly credit budget **owned by FP&A** (Nithin); notify at 80%, suspend at 100%. | Nithin |\n"
            "| 5 | dbt model pruning: 41 unused models removed; incremental strategy for the 6 largest. | Divya |\n"
            "| 6 | Monthly cost review, first Monday, Data Eng + FP&A. | Suresh |\n\n"
            "## Budget\nBaseline (Jan 2026): ~6,900 credits. Target: 4,500 credits/month by September. June actual: 4,760 (-31%).\n\n"
            "## Notes\nChanges to warehouse sizes or monitors are Normal changes (CAB) since they affect production data pipelines.",
            doc_type="decision_record", space="ENG", created="2026-06-16", authors=["Suresh Pillai"],
            references=["{{ticket:EVT-027#1}}"], labels=["snowflake", "cost", "finops"]),
      ],
      emails=[
          M("Snowflake cost plan - decisions and budget ownership",
            [("Suresh Pillai", ["Ashwin Raman", "Nithin George"], "2026-06-16T17:00",
              "Ashwin, Nithin,\n\nDecisions from today are on Confluence. The one that needs your sign-off: FP&A owns the monthly credit budget "
              "per warehouse (Nithin as named owner), with the resource monitors notifying you at 80%. Target is 4,500 credits/month by "
              "September, from 6,900 in January. CHG goes to Thursday's CAB.\n\nSuresh"),
             ("Ashwin Raman", ["Suresh Pillai", "Nithin George"], "2026-06-17T09:10",
              "Signed off. Nithin will add the credit line to the monthly SaaS review pack.\n\nAshwin")]),
      ],
      slack=[
          S("#eng-data", [
              ("Suresh Pillai", "2026-06-16T16:30", "Cost decisions locked: per-team warehouses, 60s auto-suspend, Metabase on XS with a 5-min timeout, FP&A-owned budgets. CHG for Thursday."),
              ("Divya Menon", "2026-06-16T16:33", "41 dead dbt models found, PR up to remove them."),
              ("Manish Tiwari", "2026-06-16T16:35", "Repointing Metabase collections after the CHG. Sales dashboards go to WH_SALES."),
              ("Ananya Chatterjee", "2026-06-23T07:35", "Restructure done. Shared L warehouse is gone - if your query is slow, tell me which warehouse before asking for a bigger one."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-045
    E("EVT-045", "project_decision", "workflow_configuration_decision", "2026-03-23",
      ["Vinod Krishnamurthy", "Megha Patil", "Arun Prasad", "Rahul Kapoor", "Vivek Anand", "Natasha D'Souza", "Anusha Rao"],
      "Sales Operations & Deal Desk", system="Salesforce CRM", policy="Discount Approval Matrix", project="Salesforce CPQ Implementation",
      summary="CPQ discount approval workflow configured with VP Sales approving 20-30% discounts (CFO only above 30%), based on a verbal "
              "agreement between Rahul Kapoor and Vivek Anand in February 2026. This differs from the Discount Approval Matrix (v3, Oct "
              "2025), which the project decision log acknowledges but the policy was never updated. Codified the drift later seen in EVT-057.",
      outcome="decided", drift=False, related_events=["EVT-057"], tags=["cpq", "discount", "workflow", "decision", "policy-gap"],
      docs=[
          D("Salesforce CPQ - discount approval workflow configuration (decision, 23 March 2026)",
            "**Project:** {{proj:Salesforce CPQ Implementation}} | **Decided by:** Vinod Krishnamurthy with Rahul Kapoor | **Configured by:** Megha Patil | **Deal Desk:** Arun Prasad\n\n"
            "## Approval steps configured in CPQ (Advanced Approvals)\n| Discount | Approver in CPQ |\n|---|---|\n"
            "| 0-10% | Auto-approved (AE) |\n| 10.01-20% | Enterprise Sales Manager / Head of Customer Success (renewals) |\n"
            "| **20.01-30%** | **VP Sales** |\n| Above 30% | CEO (CFO notified) |\n\n"
            "## Note on the Discount Approval Matrix\nThe published matrix ({{pol:Discount Approval Matrix}}, v3 Oct 2025) lists the **CFO** "
            "as approver for 20-30%. Rahul Kapoor and Vivek Anand agreed in February 2026 (verbal, in the Q4 pipeline review) that VP Sales "
            "approves up to 30% to shorten cycle times for APAC deals, with the CFO receiving a weekly report of all approvals above 20%. "
            "**Action: Vinod to get the matrix updated to v4** - not yet done at the time of writing.\n\n"
            "## Other configuration\n- Every discount above 10% still creates a Deal Desk ticket automatically (ServiceNow integration).\n"
            "- Multi-year TCV basis; free months counted as discount.\n- Chargebee subscription created only from an approved CPQ quote (existing rule retained).\n\n"
            "## Go-live\nPilot with Enterprise Sales from 6 April 2026; all teams 4 May 2026.",
            doc_type="decision_record", space="SALES", created="2026-03-24", authors=["Vinod Krishnamurthy", "Megha Patil"],
            labels=["cpq", "deal-desk", "discounts"]),
      ],
      emails=[
          M("CPQ approval matrix - confirming the 20-30% step",
            [("Vinod Krishnamurthy", ["Rahul Kapoor", "Vivek Anand"], "2026-03-23T14:20",
              "Rahul, Vivek,\n\nBefore Megha builds the CPQ approval steps I want to confirm in writing what you agreed in the February pipeline "
              "review: VP Sales approves discounts of 20-30% (CFO only above 30%, with a weekly report to Vivek of everything above 20%). "
              "The published matrix still says CFO for 20-30% - I'll raise a policy update once you both confirm.\n\nVinod"),
             ("Rahul Kapoor", ["Vinod Krishnamurthy", "Vivek Anand"], "2026-03-23T15:05", "Confirmed from my side.\n\nRahul"),
             ("Vivek Anand", ["Vinod Krishnamurthy", "Rahul Kapoor"], "2026-03-24T08:40",
              "Confirmed, with the weekly report. Please do update the matrix so Finance and Sales are reading the same document.\n\nVivek")]),
      ],
      slack=[
          S("#sales-ops", [
              ("Megha Patil", "2026-03-24T10:15", "CPQ approval chain is configured: AE to 10%, Sales Manager to 20%, VP Sales to 30%, CEO above. Pilot with Enterprise from 6 April."),
              ("Arun Prasad", "2026-03-24T10:18", "Deal Desk tickets still auto-create above 10%, right? I need them for the weekly report to Vivek."),
              ("Megha Patil", "2026-03-24T10:19", "Yes, unchanged."),
              ("Natasha D'Souza", "2026-03-24T10:25", "The published matrix on Confluence still says CFO for 20-30 - my AEs will ask. Is v4 coming?"),
              ("Vinod Krishnamurthy", "2026-03-24T10:30", "Rahul and Vivek have both confirmed by email; I'll raise the policy update with Sales Ops governance. Until then the CPQ chain is the operating rule."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-046
    E("EVT-046", "project_decision", "role_bundle_mapping", "2026-07-21",
      ["Geeta Iyengar", "Rakesh Nair", "Kavya Reddy", "Shruti Joshi", "Swati Kulkarni"], "People Operations",
      system="Darwinbox HRMS", policy="Employee Onboarding SOP", project="Darwinbox Onboarding Workflow Automation",
      summary="Post-project enhancement: HR Ops and IAM published the first written table of role-based application bundles that the "
              "Darwinbox-to-Okta automation applies to new joiners (ENG-PLATFORM, ENG-FRONTEND, CS-SUPPORT, FIN-AP, MKT-PMM, ...). The "
              "table was incomplete (e.g. no Metabase in SALES-OPS-ANALYST) and the Onboarding SOP still describes manual per-app requests.",
      outcome="decided", drift=False, related_events=["EVT-059"], tags=["onboarding", "role-bundles", "okta", "documentation"],
      docs=[
          D("Role-based application bundles for new joiners (v1, July 2026)",
            "**Owner:** People Operations (Rakesh Nair) with IAM (Kavya Reddy) | **Project:** {{proj:Darwinbox Onboarding Workflow Automation}} | **Status:** v1 - incomplete, being extended\n\n"
            "Since the onboarding automation went live (May 2026), Darwinbox sends the new joiner's role code to Okta, and Okta applies a "
            "**bundle** of group memberships on Day -1 in addition to the default bundle (M365, Slack, Confluence, Darwinbox, Zoho Expense, LearnHub). "
            "Anything not in the bundle is requested through the ServiceNow catalog by the manager.\n\n"
            "| Role code (Darwinbox) | Bundle contents (Okta groups) |\n|---|---|\n"
            "| ENG-PLATFORM | github-engineering, jira-users, datadog-standard, aws-sandbox-developers |\n"
            "| ENG-FRONTEND | github-engineering, jira-users, datadog-standard |\n"
            "| ENG-DATA | github-engineering, jira-users, snowflake-analyst (curated), metabase-viewer |\n"
            "| IT-SERVICEDESK | servicenow-fulfiller-it, intune-admin-readonly, jira-users |\n"
            "| IT-IAM | okta-helpdesk-admin, servicenow-fulfiller-it, 1password-admin |\n"
            "| CS-SUPPORT | zendesk-light-agent, jira-sup, confluence-cs |\n"
            "| SALES-AE | salesforce-users, hubspot-sales-starter |\n"
            "| SALES-OPS-ANALYST | salesforce-users, servicenow-fulfiller-salesops |\n"
            "| HR-OPS | darwinbox-hr-admin, servicenow-fulfiller-hr, greenhouse-interviewer |\n"
            "| FIN-AP | servicenow-fulfiller-finance, zoho-finance-admin |\n"
            "| FIN-FPA | servicenow-fulfiller-finance, metabase-viewer |\n"
            "| MKT-PMM | confluence-mkt, jira-mkt |\n"
            "| MKT-DEMANDGEN | hubspot-marketing, confluence-mkt, jira-mkt |\n\n"
            "**Not covered yet:** MKT-BRAND, HR-TA, HR-LD, FIN-PAYROLL, IT-CLOUD, SALES-CS-MANAGER. Licence-based apps (NetSuite, Zendesk full agent, Salesforce for non-Sales) are never in a bundle.\n\n"
            "_Note: the Employee Onboarding SOP (v3, Aug 2025) still says the manager raises a separate request for every application on Day 1. HR Ops to update the SOP._",
            doc_type="reference", space="HR", created="2026-07-21", authors=["Rakesh Nair", "Kavya Reddy"],
            labels=["onboarding", "role-bundles", "okta"]),
      ],
      emails=[
          M("Role bundle table published - please review your department's rows",
            [("Geeta Iyengar", ["Kavya Reddy", "Swati Kulkarni", "Rakesh Nair"], "2026-07-21T16:10",
              "All,\n\nRakesh and Kavya have written down the role bundles the onboarding automation applies - until today this lived in "
              "Okta group rules only, and managers kept asking what their new joiners 'automatically' get. It's on the HR space. It's "
              "incomplete: several roles have no bundle yet, and the SOP still describes the old manual process. Swati, could you review "
              "the Engineering and IT rows with the team leads? I'll get the SOP updated once the table is stable.\n\nGeeta"),
             ("Kavya Reddy", ["Geeta Iyengar", "Swati Kulkarni", "Rakesh Nair"], "2026-07-22T09:30",
              "One caveat: bundles only cover group-based apps. Anything licence-based (NetSuite, full Zendesk seats) still needs a request, "
              "which is where most of the 'my new joiner is missing X' tickets come from.\n\nKavya")]),
      ],
      slack=[
          S("#people-ops", [
              ("Rakesh Nair", "2026-07-21T16:30", "Role bundle table is up on the HR space - first time it's written down anywhere. If your department's row is wrong, tell me before I put it in the SOP."),
              ("Ayesha Khan", "2026-07-21T16:35", "This will save me ten questions a week. Does SALES-OPS-ANALYST really not include Metabase? Sonal's whole job is dashboards."),
              ("Rakesh Nair", "2026-07-21T16:40", "That's what's configured in Okta today. Kavya can add it if Vinod confirms."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-047
    E("EVT-047", "project_decision", "integration_design_decision", "2026-06-09",
      ["Shalini Menon", "Alok Mishra", "Kritika Jain", "Payal Shah", "Manish Tiwari", "Ashwin Raman"], "Accounts Payable & Procurement",
      system="Zoho Expense", policy="Month-End Close Checklist", project="Zoho Expense to NetSuite Integration",
      summary="Integration design decision: post one summarised journal per day per cost centre and GST bucket from Zoho Expense to "
              "NetSuite (not one line per expense), keeping expense-level detail in Zoho with a drill-back link. Chosen for NetSuite "
              "performance and audit simplicity; the first version's retry logic later caused the August duplicate-journal incident.",
      outcome="decided", drift=False, related_events=["EVT-035"], tags=["integration", "netsuite", "zoho", "design"],
      docs=[
          D("Zoho Expense -> NetSuite integration: posting design decision (9 June 2026)",
            "**Project:** {{proj:Zoho Expense to NetSuite Integration}} | **Decided by:** Shalini Menon, Ashwin Raman | **Built by:** Manish Tiwari (Data Eng, embedded) with Payal Shah\n\n"
            "## Decision\nPost **one summarised journal entry per day**, with lines grouped by cost centre x expense category x GST rate, "
            "instead of one journal line per expense claim. Expense-level detail stays in Zoho Expense; each NetSuite journal carries a "
            "`zoho_batch_id` and a drill-back URL for auditors.\n\n"
            "## Why\n- ~1,100 expense lines/month would make NetSuite journals unwieldy and slow the close.\n- Auditors have accepted summarised posting with drill-back (confirmed with the statutory auditors 2 June).\n- Reimbursement payouts remain in Keka payroll; NetSuite needs the accrual, not the individual claim.\n\n"
            "## Mechanics\n- Daily at 02:00 IST the integration pulls approved claims since the last batch, aggregates, and posts via NetSuite REST (custom record `ZohoBatchLog` records batch id, totals, status).\n- Reversals in Zoho generate a negative line in the next batch.\n- Failure -> alert to #finance and retry next run. *(Retry behaviour revised after the August 2026 duplicate incident: idempotency key required - see {{ticket:EVT-035#1}}.)*\n\n"
            "## Go-live\nParallel run June (manual upload continues); automated posting only from 1 July 2026.",
            doc_type="decision_record", space="FIN", created="2026-06-10", authors=["Shalini Menon", "Manish Tiwari"],
            references=["{{ticket:EVT-035#1}}"], labels=["integration", "netsuite", "zoho"]),
      ],
      emails=[
          M("Zoho-NetSuite posting design - summarised daily journals",
            [("Shalini Menon", "Ashwin Raman", "2026-06-09T16:20",
              "Ashwin - we've agreed the posting design with Manish: one summarised journal per day grouped by cost centre, category and GST "
              "rate, detail stays in Zoho with a drill-back link. The auditors are fine with it. Parallel run in June, automated from 1 July. "
              "Doc on the Finance space.\n\nShalini"),
             ("Ashwin Raman", "Shalini Menon", "2026-06-09T17:00",
              "Good. Please make sure the cost-centre mapping matches the AOP structure so we don't remap in October.\n\nAshwin")]),
      ]),

    # ------------------------------------------------------------------ EVT-048
    E("EVT-048", "project_decision", "technology_and_vendor_decision", "2026-05-26",
      ["Ankit Chawla", "Omar Farooq", "Ishita Bose", "Aparna Das", "Kavita Bhatnagar", "Nikhil Bhatt", "Kritika Jain"],
      "Content & Brand", system="Corporate Website CMS", policy="Software Procurement & SaaS Approval Policy",
      project="Website Redesign & CMS Migration",
      summary="Website stack decision: headless WordPress (content) + Next.js front-end hosted on Vercel, with HubSpot forms embedded. "
              "Vercel is a new vendor (~Rs 6.2 lakh/year), so Security review and Procurement onboarding were flagged as prerequisites - "
              "the procurement step later happened with a single quote (EVT-062).",
      outcome="decided", drift=False, related_events=["EVT-062"], tags=["website", "vendor", "decision", "procurement"],
      docs=[
          D("Website Redesign - stack decision: headless WordPress + Next.js on Vercel (26 May 2026)",
            "**Project:** {{proj:Website Redesign & CMS Migration}} | **Decided by:** Ankit Chawla, Kavita Bhatnagar; consulted Ishita Bose (Frontend), Nikhil Bhatt (Security)\n\n"
            "## Decision\n- Content stays in WordPress (editors keep their workflow) exposed via WPGraphQL - **headless**.\n"
            "- New front-end in Next.js built by Pixelcraft Studio with Ishita Bose reviewing; design system tokens shared with the product portal.\n"
            "- Hosting on **Vercel** (Pro plan, ~USD 7,500/year => ~Rs 6.2 lakh) for preview deployments and edge caching. WordPress stays on the existing WP Engine plan.\n"
            "- HubSpot forms and chat embedded; no separate form vendor.\n\n"
            "## Prerequisites flagged\n1. **Security review** of Vercel (SSO, data handled: none beyond public content and form submissions routed to HubSpot) - Nikhil Bhatt. Completed 4 June: approved, SAML SSO enabled on the Vercel team.\n"
            "2. **Procurement:** Vercel is a new vendor above Rs 5 lakh/year - Vendor Onboarding SOP applies (quotes, vendor form, DPA). Owner: Ankit with Kritika Jain. *Target: before production launch.*\n"
            "3. Contractor accounts for Pixelcraft on Vercel via SSO (sponsored, 90-day) - done under {{ticket:EVT-004#1}}.\n\n"
            "## Timeline\nStaging on Vercel preview from June; production cutover aligned to the v4 launch (originally 15 Sep, now 6 Oct 2026).",
            doc_type="decision_record", space="MKT", created="2026-05-27", authors=["Ankit Chawla"],
            references=["{{ticket:EVT-004#1}}"], related_events=["EVT-004"], labels=["website", "vercel", "vendor"]),
      ],
      emails=[
          M("Website stack decision - Vercel hosting (new vendor)",
            [("Ankit Chawla", ["Kavita Bhatnagar", "Nikhil Bhatt", "Kritika Jain"], "2026-05-26T17:40",
              "Kavita, Nikhil, Kritika,\n\nWe've settled the website stack: headless WordPress + Next.js on Vercel. Vercel is new to us and "
              "will be about Rs 6.2 lakh/year, so: Nikhil, could you do the security review (they support SAML SSO; only public content and "
              "form posts that go straight to HubSpot)? Kritika, I'll raise the purchase request - I understand new vendors over 5 lakh need "
              "the full onboarding. Decision doc on the Marketing space.\n\nAnkit"),
             ("Nikhil Bhatt", ["Ankit Chawla", "Kavita Bhatnagar", "Kritika Jain"], "2026-05-27T10:15",
              "Will review this week. If SSO is enforced and no PII lands on Vercel it should be straightforward.\n\nNikhil"),
             ("Kritika Jain", ["Ankit Chawla", "Kavita Bhatnagar", "Nikhil Bhatt"], "2026-05-27T11:00",
              "Thanks Ankit. Send me the vendor form and quotes when you have them; the PO needs Kavita + Shalini + Vivek at that value.\n\nKritika")]),
      ],
      slack=[
          S("#marketing", [
              ("Ankit Chawla", "2026-05-26T17:20", "Website stack decided: headless WordPress + Next.js, hosted on Vercel. Pixelcraft starts the build next week; Ishita is our technical reviewer."),
              ("Omar Farooq", "2026-05-26T17:22", "Design tokens from the portal design system? That'd keep brand consistent."),
              ("Ishita Bose", "2026-05-26T17:25", "Yes, same tokens package. I'll set up the repo and the Vercel preview flow."),
              ("Aparna Das", "2026-05-26T17:30", "HubSpot forms embed - I'll prepare the form IDs and tracking config."),
              ("Kavita Bhatnagar", "2026-05-26T17:45", "Great. Ankit, please keep procurement moving in parallel - I don't want hosting to block the launch."),
          ]),
      ]),

    # ------------------------------------------------------------------ EVT-049
    E("EVT-049", "project_decision", "requirements_change_launch_date", "2026-08-12",
      ["Sanya Kapadia", "Varsha Pai", "Rohini Pathak", "Kavita Bhatnagar", "Rahul Kapoor", "Arjun Venkataraman", "Rohan Mehta", "Nikita Bansal"],
      "Product Marketing", system="HubSpot Marketing Hub", policy="Marketing Content Approval & Publishing SOP",
      project="AlgoWorks Fleet v4 Launch Campaign",
      summary="v4 launch campaign date moved from 15 September to 6 October 2026 after Engineering re-baselined v4 GA (contract-test "
              "coverage and the March outage follow-ups). Marketing re-sequenced: webinar series and analyst briefings shift three weeks; "
              "website cutover aligned to the new date.",
      outcome="decided", drift=False, related_events=["EVT-021", "EVT-039"], tags=["launch", "timeline", "campaign", "requirements-change"],
      docs=[
          D("v4 Launch Campaign - re-plan for 6 October launch (12 August 2026)",
            "**Project:** {{proj:AlgoWorks Fleet v4 Launch Campaign}} | **Meeting:** Launch readiness, 12 August 2026 | **Attendees:** Sanya Kapadia (chair), Varsha Pai, Rohini Pathak, Nikita Bansal, Kabir Mehrotra, Rohan Mehta (Eng), Kavita Bhatnagar, Rahul Kapoor\n\n"
            "## Change\nEngineering GA for the v4 API moves from 15 September to **6 October 2026** (Rohan Mehta): contract-test coverage "
            "for the 34 customer integrations is at 70% and the load-testing action from the March postmortem needs another cycle. "
            "The campaign launch date moves with it.\n\n"
            "## Re-sequenced plan\n| Item | Old date | New date | Owner |\n|---|---|---|---|\n"
            "| Launch day (press, website hero, email) | 15 Sep | 6 Oct | Sanya |\n| Customer webinar series (3) | 17 Sep - 1 Oct | 8 Oct - 22 Oct | Varsha |\n"
            "| Analyst briefings | 10-12 Sep | 1-2 Oct | Rohini |\n| Sales enablement deck & battlecards | 8 Sep | 29 Sep | Varsha / Imran |\n"
            "| Launch video | 12 Sep | 2 Oct | Nikita |\n| Social campaign | 15 Sep | 6 Oct | Kabir |\n| New website cutover (Vercel) | 15 Sep | 6 Oct | Ankit |\n\n"
            "## Risks\n- Portal revamp launches 2 November; messaging must not imply the new portal ships with v4.\n- Diwali week (starting 8 Nov) limits post-launch follow-up windows.\n\n"
            "## Approvals\nKavita Bhatnagar and Rahul Kapoor approved the re-plan; Arjun Venkataraman confirmed the 6 October GA.",
            doc_type="meeting_notes", space="MKT", created="2026-08-12", authors=["Sanya Kapadia"], labels=["launch", "v4", "campaign"]),
      ],
      emails=[
          M("v4 launch date: 6 October (was 15 September)",
            [("Rohan Mehta", ["Sanya Kapadia", "Arjun Venkataraman", "Kavita Bhatnagar"], "2026-08-10T18:30",
              "Sanya, Kavita,\n\nWe need to move v4 GA to 6 October. Contract tests cover 70% of customer integrations and I won't ship "
              "without the load-test cycle we committed to after March. Sorry for the late notice - I'd rather tell you now than slip in "
              "September.\n\nRohan"),
             ("Sanya Kapadia", ["Rohan Mehta", "Arjun Venkataraman", "Kavita Bhatnagar"], "2026-08-11T09:20",
              "Understood. We'll re-plan on Wednesday - webinars and analyst briefings shift three weeks; the website cutover follows the "
              "launch. I'll need the new date confirmed by Arjun before we tell the analysts.\n\nSanya"),
             ("Arjun Venkataraman", ["Sanya Kapadia", "Rohan Mehta", "Kavita Bhatnagar"], "2026-08-11T10:05", "6 October is confirmed.\n\nArjun")]),
          M("Re-planned launch timeline - approved",
            [("Sanya Kapadia", ["Kavita Bhatnagar", "Rahul Kapoor"], "2026-08-12T16:45",
              "Kavita, Rahul - the re-planned timeline for the 6 October launch is on Confluence (v4 Launch Campaign space). Key change for "
              "Sales: enablement deck and battlecards land 29 September, webinars 8-22 October. Please confirm you're fine with analyst "
              "briefings on 1-2 October.\n\nSanya"),
             ("Rahul Kapoor", ["Sanya Kapadia", "Kavita Bhatnagar"], "2026-08-12T17:30", "Fine by me. Natasha will block the AEs for enablement on the 29th.\n\nRahul"),
             ("Kavita Bhatnagar", ["Sanya Kapadia", "Rahul Kapoor"], "2026-08-12T18:00", "Approved.\n\nKavita")]),
      ],
      slack=[
          S("#product-marketing", [
              ("Sanya Kapadia", "2026-08-12T15:30", "Launch is now 6 October. Re-planned timeline is on Confluence - everything shifts ~3 weeks. Please update your Jira MKT issues today."),
              ("Nikita Bansal", "2026-08-12T15:33", "Launch video moves to 2 Oct then - gives us time for the second customer interview."),
              ("Rohini Pathak", "2026-08-12T15:35", "Rebooking the analyst briefings for 1-2 Oct."),
              ("Varsha Pai", "2026-08-12T15:40", "Webinars 8/15/22 Oct. I'll update the HubSpot landing pages and hold the send."),
          ]),
      ]),
]
