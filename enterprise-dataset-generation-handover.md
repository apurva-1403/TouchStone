# Enterprise Knowledge Bank — Synthetic Dataset Generation Handover

**Purpose:** This document defines the scale, generation order, schemas, and dependency rules for building a synthetic-but-relationally-realistic enterprise dataset. It is meant to be handed to whoever writes the generation scripts (or fed directly to an LLM as a system prompt for each generation stage).

**Core principle:** Every layer below is generated **only after** the layers above it exist, and every artifact in a lower layer must reference real IDs from the layers above it. Nothing is generated in isolation. If a generator can't cite a valid upstream ID, it doesn't generate that record.

---

## 0. Assumed scale (company size)

Assumed: a **mid-size company simulation, ~100 employees**, spread across 6 departments. This size is chosen deliberately:

- Large enough to produce genuine cross-department, cross-project relational complexity (an employee can be pulled into 2-3 projects, a policy can be owned by one department but affect another, teams can be multi-layered with real manager chains, etc.).
- Still small enough that the entity graph fits comfortably in JSON/a lightweight DB and can be manually spot-checked for consistency — 100 employees means ~18 teams and ~80 events, which is reviewable by two people in the time you have.
- Scales the downstream artifact counts (tickets, emails, Slack, docs) into the 500-650 range — enough to feel like genuine "enterprise volume" in a demo, and enough that naive retrieval will visibly struggle without your source-aware/rerank logic, which is a good thing to be able to show.

If more time is available later, every count below can be scaled up proportionally again. Do not scale up further before the pipeline works end-to-end at this size.

| Entity | Count (was @60) | Count (@100 employees) | Rationale |
|---|---|---|---|
| Departments | 6 | **6** | Kept the same — going wider than 6-7 departments adds org complexity without adding demo value. ~17 employees/department average now. |
| Employees | 60 | **100** | Target scale |
| Teams | 12 | **18** | 3 per department instead of 2 — needed so ~17 people/department splits into reviewable team sizes (~5-6 people/team) |
| Systems/Apps | 20 | **30** | More tool sprawl at this size is realistic (more teams → more team-owned internal tools) |
| Projects | 15 | **24** | ~1.3 projects per team |
| Policies/SOPs | 25 | **35** | Proportional increase, still covers IT/HR/Finance/Security/general process |
| Confluence/Wiki docs | 45 | **70** | 50 standalone (system/project/dept docs) + 20 event-referencing (meeting notes, decision logs) |
| Events (the connective layer) | 50 | **80** | Each event generates 2-4 downstream artifacts — this is your relational backbone |
| ServiceNow tickets | ~180 | **~280** | ~150 event-derived + ~130 baseline/noise tickets not tied to a curated event |
| Email threads | ~70 | **~110** | Derived from events |
| Slack conversations | ~90 | **~140** | Higher volume since Slack is high-frequency/low-effort; includes some pure noise/chatter channels |

---

## 1. Generation hierarchy (strict order — do not skip or parallelize across layers)

```
Layer 0: Departments
   ↓
Layer 1: Employees            (each references a department_id, manager_id)
   ↓
Layer 2: Teams                (each references department_id, member employee_ids)
   ↓
Layer 3: Systems/Apps         (each references owner team_id)
   ↓
Layer 4: Projects             (each references team_id, staffed employee_ids)
   ↓
Layer 5: Policies/SOPs        (each references owner department_id, related system_ids)
   ↓
Layer 6: Events               (the connective layer — each references specific
                                employee_ids, team_id, project_id/system_id/policy_id,
                                a date, and an "outcome")
   ↓
Layer 7: Derived artifacts     (generated FROM events, not independently)
          — ServiceNow tickets
          — Email threads
          — Slack conversations
          — Confluence docs (some are standalone, some are event-driven — see 7.4)
```

**Rule:** nothing in Layer 7 may invent a name, date, department, or system that doesn't already exist in Layers 0-6. This is the single most important rule for relational realism — violating it is what makes synthetic datasets feel like "isolated dummy documents" instead of one coherent organization.

---

## 2. Layer-by-layer schemas

### Layer 0 — Departments (generate first, purely scripted, no LLM needed)

```json
{
  "department_id": "DEPT-01",
  "name": "Engineering",
  "head_employee_id": null   // filled in after Layer 1 exists, patch step
}
```
Suggested 6: Engineering, IT/Infrastructure, Sales, HR, Finance, Marketing.

### Layer 1 — Employees (scripted generation, names can be LLM-assisted for realism, structure is not)

```json
{
  "employee_id": "EMP-014",
  "name": "Priya Shah",
  "department_id": "DEPT-01",
  "team_id": null,             // filled in Layer 2 patch step
  "role": "Senior Software Engineer",
  "manager_id": "EMP-003",     // must reference an existing employee_id, or null for dept heads
  "join_date": "2022-03-14",
  "status": "active",
  "location": "Bengaluru"
}
```

**Generation notes:**
- Build the manager hierarchy top-down in three tiers: generate 6 department heads first (manager_id = null), then ~18 team leads/managers reporting to heads (1 per team, since Layer 2 now has 18 teams), then the remaining ICs reporting to those managers. This avoids dangling manager references and gives you a realistic 3-tier org chart instead of a flat one.
- 100 employees ≈ 6 dept heads + 18 managers + 76 ICs is a reasonable split (roughly 4-5 ICs per manager, which is a believable span of control).
- Vary join_date across a 3-4 year range — this matters later for onboarding-related events and "policy existed before this employee joined" scenarios. With 100 employees you have enough volume to comfortably have 10-15 "recent joiners" (last 3 months) purely for onboarding-flow demo queries.

### Layer 2 — Teams (scripted, patches Layer 1)

```json
{
  "team_id": "TEAM-04",
  "name": "Platform Access & Identity",
  "department_id": "DEPT-02",
  "member_employee_ids": ["EMP-021", "EMP-022", "EMP-023"],
  "lead_employee_id": "EMP-021"
}
```
18 teams total (3 per department). After generating, patch each employee's `team_id` field. Suggested team size: 5-6 members each (18 teams × ~5.5 ≈ 100 employees, consistent with Layer 1).

### Layer 3 — Systems/Apps (scripted skeleton + LLM for descriptions)

```json
{
  "system_id": "SYS-07",
  "name": "Salesforce CRM",
  "owner_team_id": "TEAM-03",
  "category": "customer-facing" ,
  "access_request_process_summary": "Requires manager approval + IT Security provisioning",
  "criticality": "high"
}
```
30 systems — mix of customer-facing (CRM, support portal, billing), internal (HRMS, expense tool, VPN, ticketing system itself, intranet), and dev tooling (CI/CD, cloud console access, artifact registry, monitoring). At 18 teams, aim for most teams owning 1-2 systems, with a few shared/central systems (VPN, HRMS) owned by IT but used org-wide.

### Layer 4 — Projects (scripted skeleton + LLM for descriptions)

```json
{
  "project_id": "PROJ-09",
  "name": "Customer Portal Revamp",
  "team_id": "TEAM-03",
  "staffed_employee_ids": ["EMP-021", "EMP-034", "EMP-012"],
  "status": "in_progress",
  "start_date": "2024-02-01",
  "related_system_ids": ["SYS-07", "SYS-12"]
}
```
24 projects (~1.3 per team). Allow ~20-25% of employees to be staffed on 2 projects (cross-team collaboration realism) — at 100 employees that's roughly 20-25 people who show up in more than one project's `staffed_employee_ids`, which gives your retrieval layer genuine multi-hop paths to demonstrate ("who else worked on X" style queries).

### Layer 5 — Policies/SOPs (scripted skeleton + LLM for full document text)

```json
{
  "policy_id": "POL-11",
  "title": "Application Access Request Policy",
  "owner_department_id": "DEPT-02",
  "related_system_ids": ["SYS-07"],
  "version": "v3",
  "last_updated": "2023-01-15",
  "status": "active",
  "full_text": "<LLM-generated policy document text>"
}
```
35 policies. **Deliberately set `last_updated` dates 6-18 months in the past** for 30-40% of policies (roughly 10-14 of the 35) — this is what creates the "stale policy vs. current practice" gap your Events layer will exploit.

### Layer 6 — Events (the critical connective layer — generate with LLM assistance, but scripted structure)

This is the layer that makes everything else relationally coherent, and the one layer whose *count went up the most* relative to the smaller version of this plan (50 → 80). **Do not generate Layer 7 artifacts directly — always generate an Event first, then derive artifacts from it.**

```json
{
  "event_id": "EVT-023",
  "type": "access_request_escalation",
  "date": "2024-06-02",
  "involved_employee_ids": ["EMP-034", "EMP-021"],
  "team_id": "TEAM-03",
  "related_system_id": "SYS-07",
  "related_policy_id": "POL-11",
  "related_project_id": null,
  "summary": "EMP-034's manager (EMP-021) was on leave for 10 days; access request escalated to IT Security who approved directly after SLA breach, per undocumented escalation practice",
  "outcome": "resolved",
  "is_drift_scenario": true,
  "produces_artifacts": ["ticket", "email", "slack"]
}
```

**Event type distribution (80 events total):**

| Event type | Count | Notes |
|---|---|---|
| Access/onboarding requests | 20 | Core demo scenarios — access grants, exceptions, escalations. With 100 employees you can also stage several as "new joiner" onboarding bundles (one event covering VPN + HRMS + team tool access together), which reads as more realistic |
| Incident/troubleshooting | 16 | "Has this issue been solved before" queries |
| Project decisions/requirements changes | 13 | "How was this project implemented" queries |
| Policy-practice drift scenarios | 13 | Deliberately contradicts an existing Layer 5 policy |
| Unresolved/contradictory resolutions | 8 | Two tickets, same issue, different resolutions — tests conflict detection |
| Routine/no-conflict baseline events | 10 | Normal, boring, policy-matches-practice — needed so drift detection doesn't fire on everything (false positive control) |

**Why the baseline/no-conflict category matters:** if every single query surfaces a "conflict," judges will suspect the conflict-detection is hardcoded or trivial. Having ~15% clean, boring, policy-matches-practice events lets you demo that the system correctly does *not* flag drift when there isn't any — this is a strong technical-merit signal.

### Layer 7 — Derived artifacts (generated FROM each event, using shared event context)

For each event with `produces_artifacts`, generate the corresponding source-formatted documents. Each generation call is given the **full event JSON as context**, plus the relevant upstream entity details (employee names/roles, system name, policy text if referenced), so names/dates/outcomes stay consistent.

**7.1 ServiceNow ticket schema:**
```json
{
  "ticket_id": "INC-04521",
  "event_id": "EVT-023",
  "subject": "...",
  "description": "...",
  "resolution": "...",
  "status": "resolved",
  "requester_employee_id": "EMP-034",
  "assigned_to_employee_id": "EMP-055",
  "created_date": "2024-06-02",
  "department": "Engineering"
}
```
Plus ~130 additional baseline/noise tickets not tied to a specific "interesting" event — routine password resets, laptop requests, standard onboarding checklist items, etc. — for volume and to make retrieval actually have to work (not every query should have an obviously-matching curated ticket). Combined with the ~150 event-derived tickets, this lands you at the ~280 total from the scale table above.

**7.2 Email thread schema:**
```json
{
  "thread_id": "EMAIL-0044",
  "event_id": "EVT-023",
  "subject": "Re: Re: access request stuck",
  "messages": [
    {"from_employee_id": "EMP-021", "to": "IT-Access-Team", "date": "2024-06-02T09:14", "body": "..."},
    {"from_employee_id": "EMP-055", "to": "EMP-021", "date": "2024-06-02T11:02", "body": "..."}
  ]
}
```

**7.3 Slack conversation schema:**
```json
{
  "conversation_id": "SLACK-0091",
  "event_id": "EVT-023",
  "channel": "#it-access-escalation",
  "messages": [
    {"employee_id": "EMP-034", "text": "...", "ts": "2024-06-01T10:15"},
    {"employee_id": "EMP-021", "text": "...", "ts": "2024-06-01T10:20"}
  ]
}
```

**7.4 Confluence/wiki docs — two sub-types:**
- **Standalone docs (~30 of the 45):** generated directly from Layer 3/4/5 entities (project design docs, system runbooks, department process pages) — not event-driven, these represent the "official" documentation layer.
- **Event-referencing docs (~15 of the 45):** meeting notes or decision logs that reference a specific event_id (e.g., "Notes from Access Policy Review — discussed INC-04521 and INC-04890 as examples of needed process update"). These are what create multi-hop traceability (doc → references ticket → references employee → references policy).

---

## 3. Cross-cutting metadata (apply to every Layer 7 artifact regardless of type)

Every artifact, no matter the source, must carry these fields for the retrieval/access-control layer built later:

```json
{
  "source_type": "policy | ticket | email | slack | confluence",
  "source_system": "confluence | servicenow | outlook | slack",
  "department": "<department_id>",
  "sensitivity": "public | internal | restricted",
  "created_date": "...",
  "last_referenced_date": "..."
}
```

---

## 4. Practical generation sequence (maps to your build calendar)

1. **Script Layers 0-2** (departments, employees, teams) — pure code, deterministic, ~half a day. Use a name-list + role-list + simple random assignment with manager-hierarchy constraints. At 100 employees / 18 teams this is still trivially fast to run and re-run.
2. **Script Layer 3-5 skeletons** (30 systems, 24 projects, 35 policies — IDs and relationships only) — pure code, half a day.
3. **LLM pass over Layer 3-5 to generate descriptive text** (system descriptions, project summaries, full policy documents) — one LLM call per record (~89 calls total), context = the skeleton JSON. Half to full day, fully batchable.
4. **Design the 80 Layer 6 events by hand (structure only, not prose)** — this is still the one part worth real human thought, since it defines what your demo can actually show. Budget a full day (up from half a day at 50 events) to write these 80 event skeletons deliberately, especially the 13 drift scenarios and 8 contradictory ones — those ~21 events are what your differentiator feature depends on, so don't rush them just because the total count went up.
5. **LLM pass generating Layer 7 artifacts per event** — for each event, 2-4 LLM calls (one per artifact type), each given the event JSON + relevant upstream context. At 80 events this is roughly 240-280 LLM calls, plus the baseline noise tickets/Slack chatter. Budget 1-1.5 days including spot-checking — fully batchable/scriptable, so this is compute time more than human time.
6. **Spot-check 15-20% of generated artifacts** (roughly 90-110 records at this scale) for name/date/fact consistency against the source event — fix or regenerate outliers.

---

## 5. What "done" looks like before you move to the ingestion pipeline

- [ ] All Layer 0-5 entities generated and internally consistent (every foreign key resolves)
- [ ] 80 events written, with the type distribution above respected (especially the ~12-13% no-conflict baseline)
- [ ] All Layer 7 artifacts generated, each tagged with `event_id` where applicable and full cross-cutting metadata
- [ ] At least 5-6 "known good" demo queries identified in advance, each with a verified correct multi-source answer you can check your system's output against
