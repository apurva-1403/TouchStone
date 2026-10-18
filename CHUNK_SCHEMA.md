# Chunk Schema (shared contract: Person A ↔ Person B)

**Status:** v0.6 (2026-10-07), implemented in [app/ingest.py](app/ingest.py) and [app/agent.py](app/agent.py). Change it only by agreement; bump the version.
Code mirror: [app/schema.py](app/schema.py). Built index: `index/` (`chunks.jsonl`, `embeddings.npy`, `manifest.json`).

Person A's ingestion writes a list of `Chunk` objects. Person B's agent and UI read only these
fields. Until the real index exists, Person B can build against hand-written fixtures in this shape.

## 1. Chunk

```json
{
  "chunk_id": "POL-01#1",
  "record_id": "POL-01",
  "chunk_index": 1,
  "source_type": "policy",
  "source_system": "confluence",
  "title": "Application Access Request Policy — 3. Policy",
  "text": "Application Access Request Policy (v3, last updated 2025-05-12)\n**Owner:** Identity & Access Management ...\n\n## 3. Policy\n3.1 All application access must be requested through ServiceNow ...",
  "department_id": "DEPT-02",
  "sensitivity": "internal",
  "created_date": "2025-05-12",
  "last_updated": "2025-05-12",
  "last_referenced_date": "2026-08-27",
  "owner_employee_ids": ["EMP-010"],
  "owner_team_id": "TEAM-04",
  "event_id": null,
  "status": "active",
  "kind": "v3",
  "category": null,
  "participant_employee_ids": [],
  "confidential": false,
  "personal_data": false,
  "personal_data_category": null,
  "data_domain": "security",
  "confidential_reason": null,
  "referenced_ids": [],
  "related_policy_ids": [],
  "related_system_ids": ["SYS-10", "SYS-15", "SYS-04", "SYS-05", "SYS-07", "SYS-30", "SYS-17"],
  "signals": {
    "days_since_update": 500,  // 2025-05-12 → today 2026-09-24
    "owners_inactive": [],
    "inactive_people_mentioned": [],
    "open_update_request_ids": ["RITM-20559"],
    "later_mention_ids": ["DOC-0058", "DOC-0070", "POL-19", "RITM-20559"]
  }
}
```

| Field | Meaning / source |
|---|---|
| `chunk_id` | `<record_id>#<chunk_index>`. Stable across re-ingests. |
| `record_id` | `policy_id` / `ticket_id` / `thread_id` / `conversation_id` / `doc_id`. Used for citations. |
| `source_type` | `policy \| ticket \| email \| slack \| confluence` (from `metadata.source_type`). |
| `source_system` | `confluence \| servicenow \| outlook \| slack`. Drives the source icon in the UI. |
| `title` | Human title for the citation card (policy/doc title + section heading, ticket subject, email subject, `#channel` for Slack). |
| `text` | The chunk text that gets embedded. Prefixed with a record header (title, version/date, owner) so a chunk makes sense on its own. |
| `department_id` | `metadata.department`. Used for access filtering. |
| `sensitivity` | `public \| internal \| restricted`. Used for access filtering. |
| `created_date`, `last_updated`, `last_referenced_date` | ISO dates. For records with no `last_updated` field (ticket/email/slack), use the latest activity date (resolved date, last message). |
| `owner_employee_ids` | Who to route to: doc `author_employee_ids`; ticket assignee; email/Slack participants. Policies use `owner_team_id` → team lead. |
| `owner_team_id` | Policies only (`owner_team_id`). |
| `event_id` | Link to `events.json` when event-derived, else null. |
| `status` | Ticket `status`; `active` for policies/docs; null for email/Slack. |
| `kind` | Sub-type: ticket `ticket_type`, doc `doc_type`, Slack `channel`, policy `version`. |
| `category` | Tickets only: ServiceNow `category` (e.g. `vpn`, `hr-query`). Groups similar past cases (v0.4). |
| `participant_employee_ids` | Everyone involved: ticket requester/on-behalf-of/assignee/approvers, email and Slack participants, doc authors (v0.5). |
| `confidential`, `personal_data`, `confidential_reason` | See §4 (v0.5). |
| `personal_data_category`, `data_domain` | What kind of confidential data it is; role grants are per category/domain (v0.6). |
| `referenced_ids` | IDs mentioned in the record's text (EVT-* removed). Used for link expansion. |
| `related_policy_ids`, `related_system_ids` | From the record, **plus policy titles / system names detected in the text** (tickets and emails name policies by title, never by ID). |
| `signals` | **Derived at ingest from real fields only** (see §3). |

## 2. Chunking rules (per source)

| Source | Unit | Rule |
|---|---|---|
| policies (35) | section | Split `full_text` on `##` headings, pack to ~1600 chars; every chunk repeats the header (title, version, last updated, owner). |
| confluence (70) | section | Same as policies; oversized sections split on paragraphs. |
| tickets (281) | record | `subject + description + resolution + work_notes` → 1 chunk (split only if very long). |
| emails (106) | thread | Whole thread, with messages labelled `from/to/date`, → 1 chunk. |
| slack (141) | conversation | Whole conversation → 1 chunk. |

Result: 649 chunks from 633 records (47 policy, 74 confluence, 281 ticket, 106 email, 141 slack).

Embeddings: `gemini-embedding-2`, 768-d (Matryoshka-truncated, re-normalised), `RETRIEVAL_DOCUMENT` /
`RETRIEVAL_QUERY` task types, **one text per request** (the model merges a list into one vector).
Never use Chroma's default embedder, which is not a Google model.

## 3. What must NOT be used at runtime

These are the dataset's **answer key**. Using them in the product would be cheating, and judges
would see through a demo that only works because of them.

- `policies[].is_stale_by_design`
- `events[].is_drift_scenario`, `events[].drift_note`, `events[].type == "policy_drift"`
- the whole of `demo_queries.json` / `.md` (used only for tests)

Staleness and conflict have to be **inferred** from real signals. `signals` holds them:

| Signal | Derived from |
|---|---|
| `days_since_update` | `last_updated` vs simulated today (2026-09-24) |
| `owners_inactive` | owners whose `employees.status` is `exited` / `on_leave` |
| `inactive_people_mentioned` | inactive people named in the text, by full name or by a role title only they held (e.g. POL-18 → "Data Protection Officer" → EMP-021, exited) |
| `open_update_request_ids` | open / in-progress / on-hold tickets with category `policy-update` that name this record |
| `later_mention_ids` | records that mention/reference this one and are newer than its last update |

These are hints for the agent, not verdicts. On policies they flag 11 of the 13 stale-by-design
policies, with 1 false positive (POL-13).

**Retrieval does not use `event_id`** for linking. It groups exactly the evidence set of each scenario,
which a real enterprise wouldn't have, so using it would inflate results. Links come only from
text-derived references. `event_id` stays on chunks for tracing and evaluation.

## 4. Access control (v0.6, 2026-10-07; implemented in [app/access.py](app/access.py), policy POL-36)

Users sign in as an employee ([app/auth.py](app/auth.py)); the session holds only the `employee_id`. Each
employee has `access_roles` (from the HRIS, see `data/employees.json`); scope is recomputed server-side on
every request. Full rules: **POL-36 "Access Roles & Need-to-Know Standard"** (also indexed, so TouchStone
can explain them).

**Classification** (at ingest): not confidential / confidential **personal data** (`personal_data_category`:
pay, health_or_leave_reason, performance_or_disciplinary, exit_details, personal_contact_or_ids, other; found
by the Gemini check in [app/classify.py](app/classify.py)) / confidential **business** (labelled restricted;
`data_domain`: security, finance, hr, commercial, legal, general).

**Baseline:** employees and interns see everything non-confidential; contractors only non-confidential policies
and Confluence; anyone sees records they are involved in; restricted policies/Confluence are visible to the
owning department.

| Role | Adds |
|---|---|
| people_manager | confidential records involving their reporting line, except health/leave reasons and personal contact |
| department_head | business-confidential records of their department |
| executive | business-confidential company-wide, no personal data |
| hr_business_partner | all personal data for supported departments |
| hr_operations | leave/health, exit, contact data company-wide + HR business records |
| compensation_admin / payroll_admin | pay + performance / pay, company-wide |
| finance_controller / security_admin / legal_counsel | finance / security / legal + commercial business records |
| compliance_auditor | everything confidential; flagged in the audit log |

Every decision returns its rule (`access_basis`), shown on confidential citations and written to the audit log
([app/audit.py](app/audit.py)). Index on 2026-10-07: 1,897 records, 236 confidential (167 labelled restricted,
122 with personal data). Tests: `python -m scripts.test_access [--agent]` (58 checks + live agent checks).

## 5. Agent response (`POST /api/chat` → UI), v0.5

Request: `{"question": "...", "history": [{"question", "answer"}]}` (last 4 turns used); requires a session cookie from `POST /api/login {"employee_id", "password"}`. Other endpoints: `GET /api/me`, `GET /api/directory` (login picker), `POST /api/logout`.

```json
{
  "answer": "markdown with [1][2] citation markers",
  "citations": [{"n": 1, "chunk_id": "POL-18#0", "record_id": "POL-18", "title": "...", "source_system": "confluence", "date": "2025-07-21"}],
  "conflicts": [{"kind": "policy_vs_practice", "summary": "POL-18 requires DPO sign-off; since Apr 2026 the Data Eng Manager approves", "record_ids": ["POL-18", "DOC-0032"], "current_view": "DOC-0032"}],
  "staleness": [{"record_id": "POL-18", "reason": "names people no longer active: Pradeep Chauhan (exited); open update request RITM-20349; last updated 2025-07-21 (430 days ago)"}],
  "fallback": {"needed": false, "contact_employee_id": "EMP-016", "contact_name": "Suresh Pillai", "contact_role": "Data Engineering Manager", "reason": "..."},
  "access_note": "8 restricted record(s) relevant to this question are not available to your role. To request access, contact ...",
  "trace": [{"tool": "search_docs", "args": {"query": "..."}, "summary": "8 results, 6 linked, 8 restricted withheld"}],
  "meta": {"model": "gemini-3.8-flash", "user_id": "EMP-046", "confidence": "high", "latency_s": 14.2, "model_calls": 4,
           "input_tokens": 26975, "output_tokens": 699, "dropped_citations": [],
           "model_call_secs": [1.9, 3.4, 5.9, 3.0], "tool_secs": 2.3, "cached": false}
}
```

`trace[]` items also carry `secs` (time inside that tool). `meta.cached` is true when the answer came from the
per-instance answer cache (same single-turn question + role asked before).

`conflicts[].kind`: `policy_vs_practice` (written rule vs what happens), `conflicting_resolutions` (same problem or
request, different outcomes), `source_vs_source` (two official documents disagree).

Guarantees enforced in code, not left to the model:
- every citation points to a record a tool returned **for this role** (others are dropped and listed in `meta.dropped_citations`);
- cited policies/docs with signals (inactive people, open update requests) always get a `staleness` entry;
- `fallback.contact_employee_id` is always an active employee (inactive ones are re-routed up the manager chain);
- `access_note` appears whenever restricted records were withheld from this role's search.

## 6. Retrieval (implemented: [app/retrieval.py](app/retrieval.py))

`retriever().search(query, role, k=8)` → `SearchResult`:
1. Hybrid scoring over all chunks: Gemini cosine + BM25, fused with reciprocal rank fusion (k=60).
2. **Role filter before ranking output**; best chunk per record; 2 of the k slots reserved for policies.
3. `related`: linked records of the hits. Open `policy-update` requests against retrieved
   policies come first, then text-derived links by score.
4. `withheld_count` / `withheld_contacts`: restricted records that would have ranked, reported only
   as a count plus the owning department's head. No text or titles are exposed.

5. `case_groups` (v0.4): each retrieved ticket grouped with similar past tickets: same `category`, embedding
   cosine ≥ 0.88, and both among the 40 records most relevant to the query. `app/cases.py` then asks
   `gemini-3.5-flash-lite` whether each group is the same issue and whether it was handled the same way
   (8 s budget). `search_docs` returns these as `similar_past_cases` so the agent can report
   `conflicting_resolutions` without having to notice the pattern itself.

HTTP: `POST /api/search {"query", "role", "k"}`. Eval: `python -m scripts.eval_retrieval [-v]`.

Baseline (27 demo queries, role exec, k=8):

| | governing policy in top-k | practice evidence in top 5 | evidence recall@k | recall incl. related |
|---|---|---|---|---|
| BM25 only | 67% | 93% | 0.54 | 0.63 |
| Hybrid + policy slots | **93%** | **96%** | **0.60** | **0.70** |

Known gap: DQ-01/DQ-22 (Salesforce/HubSpot access) are crowded out by many routine access tickets;
reaching the drift evidence takes a second hop (policy → update request → cited tickets), which the
agent does with a follow-up tool call.
