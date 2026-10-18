# AlgoWorks — Synthetic Enterprise Knowledge Dataset

A relationally consistent, synthetic-but-realistic enterprise dataset for the GenAI Enterprise Knowledge Bank:
one fictional company (**AlgoWorks Pvt. Ltd.**, ~100 employees, a B2B fleet-management SaaS with offices in
Bengaluru, Pune, Hyderabad and Singapore) whose policies, tickets, emails, Slack threads and wiki pages all describe the
*same* people, systems and events — including 13 places where written policy has drifted from actual practice, 8
issues that were "solved" two different ways, and 10 boring-but-correct controls where policy and practice agree.

Built to the spec in [enterprise-dataset-generation-handover.md](enterprise-dataset-generation-handover.md).
Simulated "today" is **2026-09-24**. Everything is fictional; SaaS product names (Okta, Salesforce, …) are only the tools the
fictional company subscribes to.

## Regenerate / validate

Python 3.11+, standard library only, deterministic (seed `20260924`):

```bash
python generate/build.py
```

```bash
python generate/validate.py
```

`build.py` runs Layers 0→7 in strict order, resolves every by-name reference to an ID (a typo fails the build), assigns
artifact IDs, resolves cross-artifact placeholders, attaches the cross-cutting metadata, validates and writes `data/`.
`validate.py` re-checks `data/*.json` independently (foreign keys, counts, type distribution, metadata, people acting
only while employed, event↔artifact back-links).

## What's in `data/`

| File | Layer | Count | Notes |
|---|---|---|---|
| `departments.json` | 0 | 6 | Engineering, IT & Infrastructure, Sales, HR, Finance, Marketing |
| `employees.json` | 1 | 100 | 6 heads → 18 team leads → 76 ICs; 12 recent joiners (last 3 months); 1 exited (the DPO), 1 on leave |
| `teams.json` | 2 | 18 | 3 per department, 4–7 members |
| `systems.json` | 3 | 30 | customer-facing / internal / dev-tooling; owner team; access-request process summary |
| `projects.json` | 4 | 24 | 31 employees staffed on 2+ projects (multi-hop paths) |
| `policies.json` | 5 | 35 | full document text; **13 deliberately stale** (`is_stale_by_design`, last_updated 6–18 months ago) |
| `events.json` | 6 | 80 | the connective layer: 20 access / 16 incident / 13 project decision / 13 drift / 8 contradictory / 10 baseline |
| `tickets.json` | 7 | 281 | 148 event-derived + 133 routine noise; `INC-`/`RITM-`/`CHG-` prefixes by `ticket_type` |
| `emails.json` | 7 | 106 | all event-derived (threads of 1–5 messages) |
| `slack.json` | 7 | 141 | 84 event-derived + 57 chatter/noise |
| `confluence.json` | 7 | 70 | 50 standalone (system guides, project pages, process/team/reference pages) + 20 event-referencing (postmortems, ADRs, decision logs, meeting notes, runbooks) |
| `demo_queries.json` / `.md` | — | 27 | known-good queries with expected drift/conflict flags and evidence IDs |
| `manifest.json` | — | — | counts, distributions, validation summary |

## Schemas

All entities follow the handover schemas; extra fields are additive.

**Events** — `event_id, type, subtype, date, involved_employee_ids, team_id, related_system_id, related_policy_id,
related_project_id, summary, outcome, is_drift_scenario, drift_note, produces_artifacts, artifact_ids{tickets,emails,slack,docs},
related_event_ids, tags`. `drift_note` states the exact policy clause vs. observed practice for the 13 drift events.

**Tickets** — `ticket_id, ticket_type (request|incident|change), event_id|null, subject, description, resolution, status,
priority, category, requester_employee_id, requester_name, on_behalf_of_employee_id, assigned_to_employee_id, assigned_to_name,
assignment_group, approver_employee_ids, created_date, resolved_date, work_notes, department (name), referenced_ids, metadata`.

**Emails** — `thread_id, event_id, subject, participant_employee_ids, messages[{from_employee_id, from_name, to[], date, body}],
referenced_ids, metadata`. `to` entries are employee IDs or distribution lists (`IT-Access-Team`, `All-Company`, …).

**Slack** — `conversation_id, event_id|null, channel, channel_type, participant_employee_ids, messages[{employee_id, name, text, ts}],
referenced_ids, metadata`. Mentions appear as `@FirstName` in text.

**Confluence** — `doc_id, event_id|null, title, space, doc_type, body (markdown), author_employee_ids, created_date, last_updated,
labels, related_event_ids, related_system_ids, related_project_ids, related_policy_ids, referenced_ids, metadata`.

**Cross-cutting `metadata`** on every ticket, email, Slack conversation, doc *and policy*:
`source_type (policy|ticket|email|slack|confluence), source_system (confluence|servicenow|outlook|slack), department (department_id),
sensitivity (public|internal|restricted), created_date, last_referenced_date`.
`last_referenced_date` is bumped whenever another artifact (or event) cites the record — so a stale policy shows
`last_updated: 2025-05-12` next to `last_referenced_date: 2026-08-27`.

`referenced_ids` lists every ID (ticket, doc, event, policy, project, system) that appears in the record's text — the
multi-hop graph (doc → ticket → policy → event) without parsing prose.

## The drift map (what the knowledge bank should catch)

| Event | Stale policy (last updated) | Policy says | Practice shows |
|---|---|---|---|
| EVT-050 | POL-01 Application Access Request (May 2025) | manager unavailable → Department Head; IAM never provisions without approval | IAM approves after 5 business days on an informal Slack confirmation |
| EVT-051 | POL-04 Laptop & Endpoint SOP (Aug 2025) | replacement in 5 business days, 4+4 buffer stock | buffer empty; loaner day 1, real device in 12–14 business days |
| EVT-052 | POL-09 Change Management (Jun 2025) | every app deployment needs a CHG + CAB | merged GitOps PR is the approval since Dec 2025 (CAB decision EVT-042 never written into policy) |
| EVT-053 | POL-15 Deployment & Release SOP (Apr 2025) | no Friday deployments | Fridays before 14:00 IST if flagged (all-hands decision, notes only) |
| EVT-054 | POL-18 Snowflake Data Access (Jul 2025) | PII access needs DPO sign-off | DPO left Feb 2026 (EVT-005); Data Eng Manager approves alone |
| EVT-055 | POL-21 Hybrid Work (Sep 2025) | 3 days/week, Tue/Wed/Thu anchors | 2 days at team discretion since April; HR Ops still quotes 3 |
| EVT-056 | POL-26 Travel & Expense (Nov 2025) | 30-day window, Rs 2,000 per diem | 60 days accepted on appeal; Rs 2,500 per diem; Zoho still auto-rejects |
| EVT-057 | POL-31 Discount Approval Matrix (Oct 2025) | 20–30% → CFO | VP Sales approves in CPQ (codified in project doc EVT-045) |
| EVT-058 | POL-02 VPN & Remote Connectivity (May 2025) | 90-day access, contractors jump-host only | 365-day auto-renewal; contractors on `vpn-contractors` group per the newer Contractor policy (policy-vs-policy conflict) |
| EVT-059 | POL-19 Employee Onboarding SOP (Aug 2025) | HR emails IT 5 days ahead; manager requests every app | Darwinbox auto-ticket 10 days ahead; Okta role bundles (documented only in a July page) |
| EVT-060 | POL-12 BYOD & Mobile Device (Jun 2025) | no personal phones on email | Service Desk enrols personal phones with Intune MAM as standard |
| EVT-061 | POL-24 L&D Reimbursement (Dec 2025) | Rs 25,000 cap; pre-approval mandatory | Rs 40,000 for certifications; pre-approval waived if passed |
| EVT-062 | POL-29 Vendor Onboarding SOP (Jan 2026) | 3 quotes above Rs 5 lakh incl. SaaS; Net-45 | single quote "SaaS exemption"; Net-30 under Rs 10 lakh |

Each drift event also spawned an open **policy-update request ticket** (category `policy-update`), so "is anyone fixing this?"
is answerable too. The 22 non-stale policies are consistent with practice; the 10 `routine_baseline` events (EVT-071–080) are
the false-positive controls where the correct answer is "no drift".

**Contradictory resolutions (EVT-063–070):** two tickets, same problem, different answers — VPN 30-minute drops
(reinstall vs. disable IPv6, still recurring), Salesforce export (cache vs. permission), Okta Verify push (re-enrol vs. phone
time sync), home-internet claims (approved vs. rejected), Admin Console for CS (granted on attestation vs. denied pending
training), Jira project creation (Service Desk vs. Platform), FP&A Snowflake timeouts (bigger warehouse vs. "won't fix"),
referral bonus timing (90 days vs. 6 months).

## Demo queries

[data/demo_queries.md](data/demo_queries.md) lists 27 queries with the expected answer, whether a drift or conflict flag is
expected, and the evidence IDs. A good demo set of eight:

1. "How do I get access to Salesforce?" — DRIFT (EVT-050 vs. POL-01; baseline EVT-071 shows the clean path)
2. "Do I need a change request (CHG) to deploy to production?" — DRIFT (EVT-052/EVT-042 vs. POL-09; EVT-073 shows infra CHGs still work)
3. "What is the deadline for submitting expense claims?" — DRIFT (EVT-056 vs. POL-26; EVT-072 clean)
4. "Who approves Snowflake PII access now that the DPO has left?" — DRIFT, multi-hop (EVT-054 ← EVT-005 ← POL-18)
5. "Has the VPN disconnecting every 30 minutes on Wi-Fi been solved before?" — CONFLICT (EVT-063)
6. "Can Customer Success get access to the AlgoWorks Admin Console?" — CONFLICT (EVT-067) with a clean counter-example (EVT-003)
7. "How many leave days can I carry forward?" — CLEAN (EVT-075; POL-20 is current)
8. "What caused the March API outage and how was it fixed?" — CLEAN multi-source (EVT-021: INC + postmortem doc + Slack + email)

## How it was built (and how to extend it)

```
generate/
  common.py                 paths, seed, date helpers, Registry (name -> ID resolution with typo suggestions)
  layer0_departments.py … layer5_policies.py   scripted layers; policy full text hand-written
  events/dsl.py             E/T/M/S/D constructors; placeholders {{ticket:EVT-050#1}}, {{doc:…}}, {{pol:Title}}, {{proj:Name}}
  events/batch_*.py         the 80 hand-designed events with their derived artifacts, written by name
  events/augment.py         follow-up tickets/docs/threads + generated approval-nudge emails
  layer7_noise.py           133 routine tickets and 57 chatter threads from seeded templates
  layer7_standalone_docs.py 50 official docs (system guides, project pages, process/team/reference pages)
  build.py / validate.py
```

Design rules that keep it coherent:

- **Nothing in Layer 7 is written against a name that doesn't exist upstream.** Artifacts are authored with employee, system,
  policy and project *names*; the build resolves them and refuses to continue on a miss.
- **People only act while employed.** The validator rejects any ticket, message or doc dated before the person's `join_date`
  or after their `exit_date` (this caught three errors during generation).
- **Drift events must point at a stale policy and postdate its `last_updated`.**
- **Official docs disagree with each other on purpose** where that is realistic: the Engineering onboarding guide and the
  ArgoCD system guide state the GitOps rule that the Change Management Policy lacks; the Deal Desk page mirrors CPQ, not the
  published matrix; the role-bundle page contradicts the Onboarding SOP.
- Ticket numbers increase with `created_date` across event and noise tickets; email/Slack/doc IDs are sequential by date.

To add an event: append an `E(...)` bundle to a batch file (or a new one listed in `events/__init__.py`), keep the type
distribution in `EXPECTED_TYPE_COUNTS` in sync, and run the build. To scale up, raise the template counts in
`layer7_noise.py` or add batches — the validator's targets are in `build.validate()`.

## Known limitations

- Prose is English, IST-centric and written from an Indian mid-size SaaS perspective by design.
- Approval-nudge email threads (24) and the noise tickets/chatter are template-generated; everything event-specific is hand-written.
- Slack mentions are rendered as `@FirstName` rather than Slack's `<@Uxxxx>` export format.
- Ticket departments follow the requester (an HR-raised onboarding ticket is tagged HR even when it is about an engineer).
