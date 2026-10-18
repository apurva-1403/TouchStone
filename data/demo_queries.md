# Known-good demo queries

Each query has a verified multi-source answer in the dataset. `expected_drift_flag` / `expected_conflict_flag` say whether the 
knowledge bank *should* surface a policy-vs-practice gap or a contradictory-resolution warning. Queries where both are false are 
false-positive controls: the correct answer is a clean one.

## DQ-01: "How do I get access to Salesforce?"

- **Primary event:** EVT-050 (policy_drift) | **Policy:** Application Access Request Policy | **DRIFT expected**
- **Expected answer:** Ritika Sharma (new SDR) requested Salesforce access on her first day while her manager Natasha D'Souza was on leave for two weeks. The Application Access Request Policy says approvals must escalate to the Department Head (VP Sales) after 2 business days and IAM must never provision without recorded approval. In practice IAM approved and provisioned on day 6 after a Slack confirmation from Vinod Krishnamurthy (a different team's manager) - an undocumented '5-business-day SLA override' IAM has used since the SSO Phase 2 backlog. A second ticket (Sonal Mehra, June) shows the same pattern with a peer's confirmation.
- **Drift note:** POLICY (POL Application Access Request v3, s3.3/3.5): manager unavailable >2 business days -> escalate to Department Head; IAM must not provision without recorded approval. PRACTICE (Aug-2026, Jun-2026 tickets): IAM approves after 5 business days pending, on an informal Slack confirmation from any senior person on the requester's side, and documents it as 'SLA override'.
- **Evidence:** events EVT-050, EVT-071; policies POL-01; tickets RITM-22437, RITM-22027, RITM-22510, RITM-22313; emails EMAIL-0095, EMAIL-0097, EMAIL-0079, EMAIL-0082; slack SLACK-0266, SLACK-0208, SLACK-0243; docs DOC-0140

## DQ-02: "How long does a replacement laptop take?"

- **Primary event:** EVT-051 (policy_drift) | **Policy:** Laptop & Endpoint Provisioning SOP | **DRIFT expected**
- **Expected answer:** The Laptop SOP promises replacement devices within 5 business days from a buffer stock of 4+4. Since May 2026 the buffer has been empty and MacBook Pro lead time is 3-4 weeks; the Service Desk's actual practice is 'loaner on day one, standard device when stock arrives' (14 and 12 business days in these two cases). Rajesh Kumar proposed updating the SOP; not done.
- **Drift note:** POLICY (Laptop & Endpoint Provisioning SOP v4, s2.2-2.3): replacement device delivered within 5 business days; buffer stock of 4 MacBook Pros + 4 ThinkPads; loaner only when repair exceeds 2 days. PRACTICE (Jun-Jul 2026): buffer stock exhausted; loaner issued immediately by default; standard device in 12-14 business days. SOP not updated.
- **Evidence:** events EVT-051; policies POL-04; tickets RITM-22125, RITM-22161, RITM-22173; emails EMAIL-0069, EMAIL-0066; slack SLACK-0229; docs -

## DQ-03: "Do I need a change request (CHG) to deploy to production?"

- **Primary event:** EVT-052 (policy_drift) | **Policy:** Change Management Policy | **DRIFT expected**
- **Expected answer:** Engineers keep asking whether a production deployment needs a Change Request. The Change Management Policy (v2) says all production application deployments are Normal changes requiring a CHG and CAB approval. Since the ArgoCD go-live (Dec 2025), the operating rule is that a merged GitOps PR is the approval and CHGs are only for infrastructure - decided at CAB in September 2025 (EVT-042) but never written into the policy. Two CHGs were raised and cancelled in April and July.
- **Drift note:** POLICY (Change Management v2, s2/s3.1/s4): all production application deployments are Normal changes -> CHG + CAB approval. PRACTICE (since 1-Dec-2025): merged PR in algoworks-deploy is the approval for standard app deployments; CHG only for infra/network/identity/DB. Source of practice: CAB decision 2-Sep-2025 (EVT-042). Policy never updated.
- **Evidence:** events EVT-052, EVT-042, EVT-073; policies POL-09; tickets CHG-21840, CHG-22272, RITM-21845, CHG-20783, CHG-21750; emails EMAIL-0038, EMAIL-0001, EMAIL-0030; slack SLACK-0171, SLACK-0241, SLACK-0071, SLACK-0155; docs DOC-0089

## DQ-04: "Are we allowed to deploy to production on a Friday?"

- **Primary event:** EVT-053 (policy_drift) | **Policy:** Deployment & Release Process SOP | **DRIFT expected**
- **Expected answer:** On Friday 19-Jun Aditya Rao deployed a portal fix at 11:30. Meera Krishnan objected citing the Deployment & Release SOP (no Friday production deployments). Arjun Venkataraman confirmed the freeze was relaxed at the 12-Mar Engineering all-hands ('Friday deploys allowed before 14:00 IST if behind a feature flag or trivially reversible') - a decision recorded only in the all-hands notes and a Slack thread; the SOP (v3, Apr 2025) still states the freeze.
- **Drift note:** POLICY (Deployment & Release Process SOP v3, s1.2): no production deployments on Fridays. PRACTICE (since 12-Mar-2026 Engineering all-hands): Friday deploys permitted before 14:00 IST when feature-flagged or trivially reversible. Recorded in all-hands notes and Slack only; SOP not updated.
- **Evidence:** events EVT-053; policies POL-15; tickets RITM-22089; emails EMAIL-0061; slack SLACK-0214; docs DOC-0121

## DQ-05: "Who approves Snowflake PII access now that the DPO has left?"

- **Primary event:** EVT-054 (policy_drift) | **Policy:** Snowflake Data Access Policy | **DRIFT expected**
- **Expected answer:** Chitra Mohan (Email Marketing) was granted the snowflake-pii-reader role for customer contact data on the approval of Suresh Pillai alone. The Snowflake Data Access Policy requires written DPO sign-off for PII schemas, but the DPO left in February and was never replaced (EVT-005). Data Engineering's working rule since April: the Data Engineering Manager approves PII access with a purpose statement and a 6-month expiry. Repeated for Ravi Shankar's churn-model access in June.
- **Drift note:** POLICY (Snowflake Data Access v2, s2.2): PII-tagged schema access requires written DPO sign-off on the DATA ticket. PRACTICE (since Apr-2026): Data Engineering Manager approves alone with purpose + 6-month expiry, because the DPO role is vacant (EVT-005) and no interim was named.
- **Evidence:** events EVT-054, EVT-005, EVT-019; policies POL-18, POL-05; tickets RITM-21883, RITM-22137, RITM-21899, RITM-21525, RITM-21566, RITM-21567; emails EMAIL-0042, EMAIL-0043, EMAIL-0017, EMAIL-0019, EMAIL-0018; slack SLACK-0178, SLACK-0132, SLACK-0136; docs -

## DQ-06: "How many days a week do I need to be in the office?"

- **Primary event:** EVT-055 (policy_drift) | **Policy:** Hybrid Work Policy | **DRIFT expected**
- **Expected answer:** New joiner Tanvi Deshpande asked HR how many days she must be in the office. HR Ops (Ayesha Khan) answered per the Hybrid Work Policy: 3 days, Tue/Wed/Thu anchor days. Her manager Rohan Mehta said the team does 2 days (Tue/Thu) since leadership relaxed the rule in April. The HRBP confirmed the relaxation is real but the policy update is 'pending with the CPO'.
- **Drift note:** POLICY (Hybrid Work v2, s1.1-1.2): minimum 3 days/week in office, Tue/Wed/Thu anchor days. PRACTICE (since Apr-2026): 2 days/week with team discretion on which days, agreed verbally by leadership; HR Ops still quotes 3 days; policy not updated.
- **Evidence:** events EVT-055; policies POL-21; tickets RITM-22367, RITM-22388; emails EMAIL-0087; slack SLACK-0255; docs -

## DQ-07: "What is the deadline for submitting expense claims?"

- **Primary event:** EVT-056 (policy_drift) | **Policy:** Travel & Expense Reimbursement Policy | **DRIFT expected**
- **Expected answer:** Zoho Expense auto-rejected Aakash Bhatia's 45-day-old claim per the T&E policy's 30-day rule; Finance AP approved it on appeal because 'we accept up to 60 days now'. Separately, Gaurav Thakur's APAC per-diem claim at Rs 2,500/day was rejected by the Zoho rule (policy: Rs 2,000) and then approved because the per-diem was raised to Rs 2,500 in April by CFO email. Neither change is in the policy (v5, Nov 2025) or the Zoho rules.
- **Drift note:** POLICY (T&E v5, s1.2/s2.3): claims within 30 days, older claims rejected; domestic per-diem Rs 2,000/day. PRACTICE (2026): AP accepts claims up to 60 days on appeal; per-diem Rs 2,500 since Apr-2026 (CFO email). Zoho rules still enforce the old values, so claims are auto-rejected and manually approved.
- **Evidence:** events EVT-056, EVT-072, EVT-066; policies POL-26; tickets RITM-22103, RITM-22127, RITM-22141, RITM-21938, RITM-21675, RITM-22038, RITM-22058; emails EMAIL-0062, EMAIL-0063, EMAIL-0050, EMAIL-0049, EMAIL-0059, EMAIL-0026; slack SLACK-0218, SLACK-0186, SLACK-0207; docs DOC-0137

## DQ-08: "Who needs to approve a 25% discount?"

- **Primary event:** EVT-057 (policy_drift) | **Policy:** Discount Approval Matrix | **DRIFT expected**
- **Expected answer:** Two Deal Desk tickets show 27% and 24% discounts approved by the VP Sales alone. The Discount Approval Matrix (v3) requires the CFO for 20-30%. The CPQ workflow was configured in March to route 20-30% to VP Sales under a verbal Rahul/Vivek agreement with a weekly report (EVT-045); the matrix was never reissued, so the policy page and the CPQ system disagree.
- **Drift note:** POLICY (Discount Approval Matrix v3, s2): 20.01-30% discount requires CFO approval. PRACTICE (since Apr-2026 CPQ go-live): VP Sales approves 20-30%; CFO gets a weekly report. Codified in CPQ config and a project decision doc (EVT-045); policy not updated.
- **Evidence:** events EVT-057, EVT-045, EVT-080; policies POL-31; tickets RITM-22193, RITM-22467, RITM-22209, RITM-21902; emails EMAIL-0073, EMAIL-0072, EMAIL-0025, EMAIL-0044; slack SLACK-0232, SLACK-0150, SLACK-0182; docs DOC-0123

## DQ-09: "How do I renew my VPN access, and can contractors use the VPN?"

- **Primary event:** EVT-058 (policy_drift) | **Policy:** VPN & Remote Connectivity Policy | **DRIFT expected**
- **Expected answer:** Nithin George received a '90-day VPN expiry' reminder from an old ServiceNow schedule and asked how to renew; IAM told him employee VPN has been on 365-day automatic renewal via the Okta group since the SSO integration. Separately, a Pixelcraft contractor was given direct VPN via the vpn-contractors Okta group (per the June Contractor policy) although the VPN policy (v2, May 2025) still says contractors must use the jump host only. Two policies now conflict and the VPN policy is stale.
- **Drift note:** POLICY (VPN & Remote Connectivity v2, s2.3-2.4): VPN granted for 90 days, renewal by manager-approved request; contractors jump-host only. PRACTICE: employee VPN auto-renews for 365 days via Okta group (since Dec-2025); contractors get scoped VPN via the vpn-contractors group (per the newer Contractor & Guest Access Policy v2). VPN policy not updated; conflicts with the Contractor policy.
- **Evidence:** events EVT-058, EVT-004; policies POL-02, POL-13; tickets RITM-21984, RITM-22230, RITM-21992, RITM-22013, RITM-22016; emails EMAIL-0053, EMAIL-0057; slack SLACK-0200, SLACK-0205; docs -

## DQ-10: "What does a new joiner get automatically and what do I need to request as their manager?"

- **Primary event:** EVT-059 (policy_drift) | **Policy:** Employee Onboarding SOP | **DRIFT expected**
- **Expected answer:** Dhruv Malik (Revenue Analyst) started 10-Aug with Salesforce and Slack auto-provisioned by the SALES-OPS-ANALYST role bundle but no Metabase - his main tool. His manager Vinod Krishnamurthy, following the Onboarding SOP, expected to raise every application request on Day 1 and was confused about what the bundle covers. The SOP (v3, Aug 2025) describes HR emailing IT 5 days ahead and managers requesting each app; practice since May 2026 is Darwinbox-triggered tickets 10 days ahead and role bundles, documented only in a July reference page.
- **Drift note:** POLICY (Employee Onboarding SOP v3, s1/s2.2): HR emails IT 5 business days before start; manager raises a separate request for every application on Day 1; nothing provisioned automatically by role. PRACTICE (since May-2026): Darwinbox auto-creates the ticket 10 business days ahead and Okta applies role bundles; managers request only what the bundle misses. SOP not updated.
- **Evidence:** events EVT-059, EVT-046, EVT-001; policies POL-19; tickets RITM-22399, RITM-22406, RITM-22250, RITM-22344, RITM-22345; emails EMAIL-0090, EMAIL-0078, EMAIL-0084; slack SLACK-0260, SLACK-0239, SLACK-0248, SLACK-0252; docs DOC-0138

## DQ-11: "Can I get work email on my personal phone?"

- **Primary event:** EVT-060 (policy_drift) | **Policy:** BYOD & Mobile Device Policy | **DRIFT expected**
- **Expected answer:** The BYOD policy (v1, Jun 2025) prohibits personal phones from accessing corporate email and says mobile access requires a company-issued device. In practice the Service Desk routinely enrols personal iPhones/Androids with Intune app-protection (MAM) for Outlook and Teams - two tickets in April and June show it as a standard, no-approval request. The policy's own rationale ('MAM not adopted pending licence review') is out of date since the Intune P2 licences arrived in early 2026.
- **Drift note:** POLICY (BYOD & Mobile Device v1, s1.1-1.2): personal mobile devices may not access corporate email/Slack; company-issued Intune-managed phones only; exceptions need Head of IT approval for 30 days. PRACTICE (since ~Feb-2026): Service Desk enrols personal phones with Intune MAM (app protection) for Outlook/Teams on request, no approval. Policy not updated.
- **Evidence:** events EVT-060; policies POL-12; tickets RITM-21732, RITM-22044, RITM-21741; emails EMAIL-0028; slack SLACK-0153; docs -

## DQ-12: "What is the L&D reimbursement limit and do I need pre-approval?"

- **Primary event:** EVT-061 (policy_drift) | **Policy:** Learning & Development Reimbursement Policy | **DRIFT expected**
- **Expected answer:** Divya Menon claimed Rs 32,000 for an AWS certification without pre-approval; L&D approved it. The L&D Reimbursement Policy (v2, Dec 2025) caps claims at Rs 25,000/year and says claims without pre-approval are not reimbursed. Since the FY27 budget (April 2026) L&D has applied a Rs 40,000 cap for certifications and waives pre-approval when the certification is passed; Harish Gowda's Rs 28,000 CKA claim in May was handled the same way. Policy not updated.
- **Drift note:** POLICY (L&D Reimbursement v2, s1/s2.2): Rs 25,000 annual cap; pre-approval mandatory, no reimbursement without it. PRACTICE (since Apr-2026 FY27 budget): Rs 40,000 cap for certifications; pre-approval waived if the certification is passed. Applied in May and July 2026; policy not updated.
- **Evidence:** events EVT-061; policies POL-24; tickets RITM-22295, RITM-21874, RITM-22310; emails EMAIL-0080, EMAIL-0081; slack SLACK-0242; docs -

## DQ-13: "Do I need three quotes to buy a new SaaS tool?"

- **Primary event:** EVT-062 (policy_drift) | **Policy:** Vendor Onboarding & Payment Terms SOP | **DRIFT expected**
- **Expected answer:** Vercel (new vendor, Rs 6.2 lakh/year) was onboarded with a single quote and Net-30 terms. The Vendor Onboarding SOP requires three quotes above Rs 5 lakh 'equally for SaaS and hosting' with CFO-approved single-source justification, and Net-45 unless the CFO approves shorter terms. Procurement has been treating SaaS subscriptions as exempt from the three-quote rule and accepting vendors' Net-30 for anything under Rs 10 lakh since early 2026 - neither is written down.
- **Drift note:** POLICY (Vendor Onboarding & Payment Terms SOP v2, s2.1/s3.1-3.2): three quotes for any new vendor above Rs 5 lakh including SaaS/hosting; Net-45 standard, Net-30 only with CFO approval. PRACTICE (2026): SaaS subscriptions processed on one quote as an 'informal SaaS exemption'; Net-30 accepted under Rs 10 lakh without CFO approval.
- **Evidence:** events EVT-062, EVT-048, EVT-078; policies POL-29, POL-07; tickets RITM-22419, RITM-22494, RITM-21496; emails EMAIL-0092, EMAIL-0093, EMAIL-0051, EMAIL-0016; slack SLACK-0272, SLACK-0192, SLACK-0130; docs DOC-0129

## DQ-14: "Has the VPN disconnecting every 30 minutes on Wi-Fi been solved before?"

- **Primary event:** EVT-063 (contradictory_resolution) | **Policy:** Incident Management & Severity Classification SOP | **CONFLICT expected**
- **Expected answer:** Two Finance users reported GlobalProtect dropping every ~30 minutes on home Wi-Fi. Ticket A (March, Payal Shah) was closed as 'reinstalled the client'; ticket B (June, Nithin George) was closed as 'disabled IPv6 on the Wi-Fi adapter'. Both users say it still happens intermittently; no root cause was found and the two resolutions contradict each other. Still recurring per an August Slack thread.
- **Evidence:** events EVT-063; policies POL-08; tickets INC-21595, INC-22069, INC-22356; emails EMAIL-0085; slack SLACK-0249; docs -

## DQ-15: "Why can't I export reports from Salesforce?"

- **Primary event:** EVT-064 (contradictory_resolution) | **Policy:** CRM Data Hygiene & Lead Ownership Policy | **CONFLICT expected**
- **Expected answer:** Two Sales Ops users could not export Salesforce reports. Ticket A (Sonal Mehra, February) was resolved by the Service Desk as 'cleared browser cache'; ticket B (Arun Prasad, May) was resolved by the Salesforce Administrator as 'user profile lacked the Export Reports permission - added'. The two tickets give different answers to the same question and the Service Desk's answer was probably coincidental.
- **Evidence:** events EVT-064; policies POL-32; tickets INC-21530, INC-21851, RITM-21852; emails EMAIL-0039; slack SLACK-0172; docs -

## DQ-16: "Okta Verify push notifications are not arriving - what fixes it?"

- **Primary event:** EVT-065 (contradictory_resolution) | **Policy:** Password & MFA Standard | **CONFLICT expected**
- **Expected answer:** Okta Verify push notifications not arriving: ticket A (Riya Sen, April) was fixed by re-enrolling Okta Verify; ticket B (Bhavana Shetty, July) was fixed by correcting the phone's automatic time setting. Both were closed as resolved with different root causes; the IT knowledge article still lists only 're-enrol', so the Service Desk keeps re-enrolling users for whom the time-sync fix would work.
- **Evidence:** events EVT-065; policies POL-03; tickets INC-21768, INC-22142, RITM-22144; emails EMAIL-0068; slack SLACK-0225; docs -

## DQ-17: "Can remote employees claim home internet on expenses?"

- **Primary event:** EVT-066 (contradictory_resolution) | **Policy:** Travel & Expense Reimbursement Policy | **CONFLICT expected**
- **Expected answer:** Two remote employees claimed home internet. Ethan Brooks (March) was approved Rs 1,500/month by Ramesh Babu 'as a remote designation allowance'; Ishita Bose (June) was rejected by Alok Mishra because home internet is 'not in the policy'. The T&E policy is silent on home internet (only mobile bills are listed). Finance has not decided; both tickets remain as precedent and Ishita's appeal is open.
- **Evidence:** events EVT-066, EVT-056; policies POL-26; tickets RITM-21675, RITM-22038, RITM-22058, RITM-22103, RITM-22127, RITM-22141; emails EMAIL-0059, EMAIL-0026, EMAIL-0062, EMAIL-0063; slack SLACK-0207, SLACK-0218; docs DOC-0137

## DQ-18: "Can Customer Success get access to the AlgoWorks Admin Console?"

- **Primary event:** EVT-067 (contradictory_resolution) | **Policy:** Privileged Access & Admin Console Policy | **CONFLICT expected**
- **Expected answer:** Two Support Engineers requested AlgoWorks Admin Console read-only. Preeti Nambiar (January, policy v1) was granted it by Rohan Mehta with a manager attestation instead of the training; Sameer Khan (April, after policy v2 removed that option) was denied by Nikhil Bhatt pending the training and never re-requested. The same team therefore has one member with access obtained without training and another without access - and Kunal Shah's May request (EVT-003) shows the policy applied correctly.
- **Evidence:** events EVT-067, EVT-003; policies POL-11; tickets RITM-21368, RITM-21799, RITM-22145, RITM-21908; emails EMAIL-0035, EMAIL-0007, EMAIL-0046, EMAIL-0045; slack SLACK-0165, SLACK-0183; docs -

## DQ-19: "How do I get a new Jira project created?"

- **Primary event:** EVT-068 (contradictory_resolution) | **Policy:** Application Access Request Policy | **CONFLICT expected**
- **Expected answer:** Two Marketing managers asked for a new Jira project. Ankit Chawla (May) got 'MKT' created by the Service Desk (Shruti Joshi) the same day; Manoj Venkatesh (August) was told by the Service Desk that Jira projects are created by Platform Backend and waited four days for Rohan Mehta. Jira is owned by Platform Backend per the Systems Directory, but the Service Desk still holds admin rights from before the ownership change - so the answer depends on who picks up the ticket.
- **Evidence:** events EVT-068; policies POL-01; tickets RITM-21911, RITM-22348, RITM-22380; emails EMAIL-0086; slack SLACK-0250; docs -

## DQ-20: "My Snowflake query for FP&A times out after 5 minutes - what should I do?"

- **Primary event:** EVT-069 (contradictory_resolution) | **Policy:** Snowflake Data Access Policy | **CONFLICT expected**
- **Expected answer:** Two FP&A analysts hit 5-minute query timeouts on the same AOP cost-centre query after the warehouse restructure. Harsha Vardhan (June) had his warehouse bumped from S to M by Ananya Chatterjee; Meenakshi Sundaram (September) was told by Manish Tiwari to use the Metabase 'AOP Actuals' dashboard instead and the ticket closed 'won't fix'. FP&A now has one analyst on a bigger warehouse and one told there is no SQL path - unresolved.
- **Evidence:** events EVT-069, EVT-044; policies POL-18, POL-09; tickets INC-22090, INC-22584, CHG-22055; emails EMAIL-0105, EMAIL-0060; slack SLACK-0283, SLACK-0209; docs DOC-0135

## DQ-21: "When is the referral bonus paid?"

- **Primary event:** EVT-070 (contradictory_resolution) | **Policy:** Employee Referral Bonus Policy | **CONFLICT expected**
- **Expected answer:** Two engineers asked when their referral bonus would be paid. Rakesh Nair (February, HR Ops) said 'in the payroll after the referred employee completes 90 days'; Fatima Sheikh (July, HRBP) said 'after 6 months, in the following payroll cycle'. The policy was changed from 6 months to 90 days in April 2026 (v2), so Fatima's July answer follows the superseded v1 - and Aditya's bonus is now late. Payroll is still waiting for TA confirmation.
- **Evidence:** events EVT-070; policies POL-23; tickets RITM-21460, RITM-22210, RITM-22634; emails -; slack SLACK-0291; docs -

## DQ-22: "How do I get access to HubSpot?"

- **Primary event:** EVT-071 (routine_baseline) | **Policy:** Application Access Request Policy | **clean - no flag expected**
- **Expected answer:** Kabir Mehrotra (new Social Media Manager) requested HubSpot access on his second day. Line manager Ankit Chawla approved within the hour; IAM added the Okta group and Aparna Das assigned the permission set the same day - well inside the 3-business-day fulfilment SLA. Exactly what the Application Access Request Policy describes.
- **Evidence:** events EVT-071, EVT-050; policies POL-01; tickets RITM-22313, RITM-22437, RITM-22027, RITM-22510; emails EMAIL-0079, EMAIL-0082, EMAIL-0095, EMAIL-0097; slack SLACK-0243, SLACK-0266, SLACK-0208; docs DOC-0140

## DQ-23: "How do I submit a travel expense claim?"

- **Primary event:** EVT-072 (routine_baseline) | **Policy:** Travel & Expense Reimbursement Policy | **clean - no flag expected**
- **Expected answer:** Anita Desai's Mumbai customer-visit claim (submitted 9 days after travel, itemised receipts for every item over Rs 500, hotel under the metro cap, per-diem claimed without meal receipts) was approved by her manager and by Finance AP in two days. A textbook claim under the T&E policy - no exceptions needed.
- **Evidence:** events EVT-072, EVT-056; policies POL-26; tickets RITM-21938, RITM-22103, RITM-22127, RITM-22141; emails EMAIL-0050, EMAIL-0049, EMAIL-0062, EMAIL-0063; slack SLACK-0186, SLACK-0218; docs DOC-0137

## DQ-24: "How do I get an infrastructure change approved?"

- **Primary event:** EVT-073 (routine_baseline) | **Policy:** Change Management Policy | **clean - no flag expected**
- **Expected answer:** RDS production instance resize (db.r6g.2xlarge to 4xlarge) raised as a Normal change with rollback plan, reviewed and approved at the Thursday CAB, implemented in the approved window with the outcome recorded next day. Infrastructure changes still follow the Change Management Policy exactly as written.
- **Evidence:** events EVT-073, EVT-052; policies POL-09; tickets CHG-21750, CHG-21840, CHG-22272, RITM-21845; emails EMAIL-0030, EMAIL-0038; slack SLACK-0155, SLACK-0171, SLACK-0241; docs -

## DQ-25: "How many leave days can I carry forward to next year?"

- **Primary event:** EVT-075 (routine_baseline) | **Policy:** Leave & Time-Off Policy | **clean - no flag expected**
- **Expected answer:** Bhavana Shetty asked how many privilege-leave days carry forward and how much notice a 5-day leave needs. HR Ops answered from the Leave & Time-Off Policy v4 (12 days carry forward; notice of twice the duration; Department Head for >10 days) and Darwinbox enforced the same rules. No gap between policy and practice.
- **Evidence:** events EVT-075; policies POL-20; tickets RITM-22512; emails EMAIL-0100; slack SLACK-0275; docs -

## DQ-26: "What approvals do I need to buy a new SaaS tool under 5 lakh?"

- **Primary event:** EVT-078 (routine_baseline) | **Policy:** Software Procurement & SaaS Approval Policy | **clean - no flag expected**
- **Expected answer:** Marketing bought 5 Figma Professional seats (Rs 1.8 lakh/year): under Rs 5 lakh, so Department Head approval, a Security review (SSO supported) and a Procurement PO - no competitive quotes required. Processed in 5 business days exactly as the SaaS Approval and Purchase Order policies describe.
- **Evidence:** events EVT-078, EVT-062; policies POL-07, POL-29; tickets RITM-21496, RITM-22419, RITM-22494; emails EMAIL-0016, EMAIL-0092, EMAIL-0093; slack SLACK-0130, SLACK-0272; docs -

## DQ-27: "Who approves a 15% discount?"

- **Primary event:** EVT-080 (routine_baseline) | **Policy:** Discount Approval Matrix | **clean - no flag expected**
- **Expected answer:** Aakash Bhatia requested a 15% discount for a mid-market renewal. Under both the published Discount Approval Matrix and the CPQ configuration, 10-20% is the Sales Manager's call; Natasha D'Souza approved in CPQ and on the Deal Desk ticket the same afternoon. No policy question arises at this discount level.
- **Evidence:** events EVT-080, EVT-057; policies POL-31; tickets RITM-21902, RITM-22193, RITM-22467, RITM-22209; emails EMAIL-0044, EMAIL-0073, EMAIL-0072; slack SLACK-0182, SLACK-0232; docs -
