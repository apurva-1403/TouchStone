# Project Handover: Enterprise Knowledge Management Assistant (TouchStone)

**Prepared for:** the engineering team (handover)
**Team size:** 2 people
**Timeline:** Sep 26, 2026 → Oct 18, 2026 (22 days)
**Status:** Day 2: retrieval + agent loop live on Cloud Run (M1–M5 done); next: differentiators (see Section 11)

---

## 1. Context — Why This Project Exists

This is a submission for a Gen AI hackathon. The hackathon has hard platform constraints
(see Section 4) that dictate our tech stack regardless of what would otherwise be
"best." Read Section 4 before making any architecture decisions — using the wrong
model provider or deployment target disqualifies the submission regardless of how good
the idea is.

---

## 2. Problem Statement

Most enterprise organizations have vast amounts of internal knowledge flowing between
teams and departments every day — HR policies, engineering runbooks, sales pricing,
legal/compliance rules, meeting decisions, Slack threads. This knowledge is largely
**siloed**: it lives in disconnected tools (Confluence, Google Drive, Slack, Notion,
email), and transferring it between teams currently relies on manual processes (asking
around, waiting for a meeting, searching multiple wikis by hand).

This creates three concrete failure modes we are targeting, not just "search is slow":

1. **Contradiction, not just fragmentation.** Multiple documents on the same topic
   often disagree (an old policy vs. a new one, an outdated pricing sheet still being
   referenced), and there's no way for an employee to know which is authoritative.
2. **Silent staleness.** Docs go out of date (owner left the company, system migrated,
   process changed) but nothing flags that the document is unreliable — it's just
   sitting there looking as valid as anything else.
3. **No fallback when the answer isn't in the docs at all.** Most Q&A-over-docs tools
   either hallucinate an answer or say "I don't know" with no path forward. Neither
   helps a real employee get unblocked.

Generic "chatbot over your documents" (naive RAG) does not solve any of these three
problems — it will happily retrieve the wrong (outdated) doc and answer confidently.
**This is the gap we are building for.**

---

## 3. Goal / What We're Building

An **enterprise knowledge assistant** that:

1. Answers employee questions by retrieving from a (simulated) multi-source internal
   knowledge base.
2. **Detects and surfaces conflicts** between documents (different dates, different
   authors, contradictory content on the same topic) instead of confidently picking one.
3. **Flags staleness/unreliable sources** (orphaned owner, explicitly-marked-outdated
   content) rather than presenting them as equally trustworthy.
4. **Falls back gracefully** when there's no confident answer — routing the user to the
   actual document owner (from metadata) instead of hallucinating.
5. **Respects role-based access** — a demo with 3 simulated roles (e.g., Engineer, HR/
   People Ops, Legal/Exec) shows the same question returning different, correctly
   scoped answers.

**One-line pitch:** *"Most knowledge management AI answers questions. Ours knows what
it doesn't know, who to trust, and who can see what."*

This is deliberately **not** trying to be a full production connector platform. Scope
is intentionally narrow: one ingested dataset, one retrieval pipeline, one agent, a
clean demo of the four behaviors above. Do not scope-creep into building real OAuth
connectors to live Slack/Drive/Confluence — the dataset is synthetic and mocked by design.

---

## 4. Hackathon Constraints (HARD REQUIREMENTS — do not deviate)

- **Model requirement:** Must use **Gemini or Gemma models**, or an approved agentic
  platform: **Agent Builder / Vertex AI Agent Platform, Antigravity, or AI Studio**.
  → All of the shipped product's model calls must go through Gemini/Gemma on Google Cloud.
- **Deployment requirement:** Must deploy on **Google Cloud**, via **Cloud Run** or
  **Firebase**. No other hosting counts for judging.
- **Submission package must include:**
  1. A proposal deck
  2. A working prototype (deployed, per above)
  3. A 3-minute demo video
- **Judging weights:**
  - 40% — Technical / Gen AI merit
  - 25% — Problem alignment / impact
  - 25% — Innovation
  - 10% — UX
- **Deadline:** Prototype submission **October 18, 2026**.

### Implication for architecture
- Model layer: **Gemini API** (via AI Studio for prototyping / Vertex AI for
  production-grade calls) for the main reasoning/agent loop. Consider **Gemma**
  (open-weight, smaller) for a secondary lightweight task (e.g., a fast reranker or a
  PII/sensitivity classifier) to demonstrate deliberate multi-model use — this is a
  technical-merit differentiator, not a requirement.
- Agent orchestration: evaluate **Vertex AI Agent Builder** or **Antigravity** early
  (day 2–3 spike) as a possible replacement for a hand-rolled Gemini function-calling
  loop. Judges are explicitly pointing us toward these platforms, so using one well
  could score higher on technical merit than a raw custom loop — but only adopt it if
  it doesn't slow down building our actual differentiators (conflict detection,
  fallback routing). Don't force it if it fights us.
- Vector/retrieval layer: Chroma (or similar) running inside the Cloud Run container is
  fine for hackathon scale. If time allows, Vertex AI Vector Search or Firestore vector
  search would look more "cloud-native," but this is a nice-to-have, not required.
- Deployment: containerize backend (FastAPI/Flask) → **Cloud Run**. Frontend →
  **Firebase Hosting**, or serve both from a single Cloud Run service to minimize
  moving parts for a 2-person team. Firebase Auth can be used to make the 3 demo roles
  feel real rather than hardcoded, if time allows.

---

## 5. What Already Exists

### 5.1 Synthetic dataset (already generated, ready to ingest)
refer to data_README.md for the details of data

---

## 6. Architecture (Target)

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (chat UI, role switcher, citation display,     │
│  conflict callouts)  →  Firebase Hosting                 │
└───────────────────────────┬───────────────────────────────┘
                             │
┌───────────────────────────▼───────────────────────────────┐
│  Backend API (FastAPI/Flask)  →  Cloud Run                │
│                                                             │
│  1. Retrieval: query → embed → vector search (Chroma or   │
│     Vertex AI Vector Search) → metadata filter by role    │
│  2. Agent (Gemini function-calling loop, or Vertex AI      │
│     Agent Builder / Antigravity):                          │
│       - search_docs tool                                   │
│       - conflict-detection reasoning step (compare         │
│         retrieved chunks by date/status/content)            │
│       - fallback-to-human logic (route to doc owner        │
│         metadata field when no confident answer, or when   │
│         the only match is stale/orphaned)                  │
│  3. Response: answer + citations + conflict flags +        │
│     staleness warnings                                     │
└─────────────────────────────────────────────────────────┘
```

### Ingestion pipeline
(Updated 2026-09-27 for the real AlgoWorks dataset; full contract in [CHUNK_SCHEMA.md](CHUNK_SCHEMA.md).)
1. Load `data/{policies,tickets,emails,slack,confluence}.json` (633 records across 5
   sources), plus `employees/teams/systems/projects/events` as lookup and graph tables.
2. Chunk: policies and Confluence pages by section heading; tickets, email threads and
   Slack conversations one chunk per record.
3. Embed chunks with `gemini-embedding-2` and store them with full metadata on every chunk
   (not just the parent record). Never use Chroma's default (non-Google) embedder.
4. Metadata drives: permission filtering (`department` + `sensitivity`), multi-hop expansion
   (`referenced_ids`), and staleness/conflict signals **inferred** from dates, inactive owners
   and newer records that contradict older ones. There is no `status: stale` field (all
   policies are `active`), and `is_stale_by_design` / `drift_note` / `demo_queries` are the
   answer key, so they must never be used at runtime.

### Agent behavior contract (what "good" looks like)
- If retrieved chunks disagree → **do not just answer with the most recent one
  silently**. Explicitly state both, their dates, and which is current per metadata.
- If the only relevant chunk has `status: stale` or an orphaned owner → warn the user
  explicitly before giving the (possibly outdated) steps, and do not suggest paging a
  person who no longer exists.
- If nothing relevant is retrieved with reasonable confidence → say so, and if
  possible, name the person from the closest-topic document's `author`/`owner`
  metadata as who to ask.
- If a role-restricted document is the only source → do not leak restricted content
  to a lower-privilege role; state that the answer requires elevated access, and name
  who to contact if appropriate.

---

## 7. Team Split (2 people)

- **Person A — Ingestion & Retrieval:** dataset parsing, chunking, embeddings, vector
  DB, metadata schema, permission filtering, retrieval ranking quality.
- **Person B — Agent & UI:** Gemini function-calling / agent platform integration,
  conflict-detection prompting, fallback-to-human logic, frontend (chat UI, citations,
  conflict callouts, role switcher), demo polish.

Work in parallel against a shared, agreed-upon JSON schema for "chunk with metadata"
so neither person blocks on the other for the first several days.

---

## 8. Day-by-Day Plan (22 days, Sep 26 → Oct 18)

**Days 1–2 (Sep 26–27): Scope lock + Google Cloud spike**
- Confirm dataset is sufficient (it is — see Section 5.1); do not spend time sourcing
  more data unless a specific gap is found.
- Stand up a minimal Gemini API "hello world" call (via AI Studio key) and a bare
  Cloud Run deploy of a trivial FastAPI app, end-to-end, before building real features.
  This retires the single biggest risk (deployment surprises) early.
- Decide: raw Gemini function-calling loop vs. Vertex AI Agent Builder/Antigravity.
  Time-box this decision to half a day of spiking, not longer.

**Days 3–7: Core pipeline (parallel)**
- A: ingestion → chunking → embeddings → vector DB with metadata attached.
- B: basic agent loop with a `search_docs` tool, plain Q&A working end-to-end
  (dumb but functional) on top of whatever Person A has ready.
- Checkpoint day 7: question in → answer with citation out, deployed to Cloud Run.

**Days 8–13: Differentiators**
- A: role-based permission filtering (3 roles proposed in CHUNK_SCHEMA.md §4); retrieval
  quality tuning.
- B: conflict-detection logic (compare retrieved chunks by date/status/content, per
  the behavior contract in Section 6); fallback-to-human routing using
  `author`/owner metadata; staleness warnings for `status: stale` docs.
- Checkpoint day 13: the 8 recommended demo queries (data_README.md) produce the intended
  behavior reliably, with the rest of the 27 in `data/demo_queries.json` as a regression set.

**Days 14–17: UI + integration + Google-native polish**
- Merge into one UI: chat box, citations with links, visible role switcher, conflict
  callouts styled distinctly, staleness badges.
- If time allows: swap in Vertex AI Vector Search / Firestore vector search, or
  Firebase Auth for the role switcher, for extra "native Google Cloud" credit.

**Days 18–19: Demo dataset rehearsal + proposal deck**
- Full run-through of all demo scenarios, timed.
- Draft the proposal deck (problem → approach → architecture → demo → impact).

**Day 20: Buffer / bug fixing** — no new features past this point.

**Day 21: Record the 3-minute demo video + finalize deck.**

**Day 22 (Oct 18): Submit** — prototype + deck + video.

---

## 9. Guardrails

- No new features after Day 17 (UI/integration). Anything else is a "future work"
  slide bullet, not code.
- Do not build real OAuth connectors to live Slack/Drive/Confluence — out of scope,
  the synthetic dataset is the intended input.
- Test the fallback-to-human path and conflict-detection path early and often — these
  are the actual differentiators being judged under "Innovation" and "Technical
  merit," not the basic RAG Q&A loop.
- Keep the model/deployment choices compliant with Section 4 at all times — verify
  before submission that no non-Google model calls remain in the shipped prototype path.
- Watch for hidden non-Google models: Chroma's default embedding function
  (`all-MiniLM-L6-v2`), sentence-transformers, or Hugging Face rerankers. Before submission,
  check that `requirements.txt` lists only Google SDKs plus the web/numeric libraries.
- Record the demo video against the deployed Cloud Run URL, not localhost.

---

## 10. Open Items / Decisions Needed From the User

- [ ] Confirm: raw Gemini function-calling loop vs. Vertex AI Agent Builder vs.
      Antigravity — pick after the Day 1–2 spike.
- [ ] Confirm: Chroma-in-container vs. Vertex AI Vector Search / Firestore vector
      search for the retrieval store.
- [ ] Confirm: single Cloud Run service (backend+frontend) vs. Cloud Run (backend) +
      Firebase Hosting (frontend) split.
- [x] ~~Locate `northwind_synthetic_kb.zip`~~: superseded by the AlgoWorks dataset in `data/`.
- [ ] Confirm: the 3 demo roles and access rule in CHUNK_SCHEMA.md §4.
- [ ] Decide: make the Cloud Run service public (judges need an unauthenticated URL).

---

## 11. Progress Log

**2026-09-27 (Day 2) — spike complete**
- GCP project `groovy-analyst-509819-d5`; enabled Cloud Run, Cloud Build, Artifact
  Registry, Vertex AI APIs.
- Gemini is called via **Vertex AI with ADC** (no API keys). Verified models: `gemini-3.8-flash`
  (agent), `gemini-3.5-flash-lite` (fast), `gemini-embedding-2` (3072-d). All configurable in
  [app/config.py](app/config.py).
- Service accounts: `kb-copilot-run` (runtime: `aiplatform.user`, `logging.logWriter`),
  `kb-copilot-build` (Cloud Build: `cloudbuild.builds.builder`). The default compute SA has no
  roles in this project, so these are required.
- Deployed `kb-copilot` to Cloud Run (us-central1):
  https://kb-copilot-304689352997.us-central1.run.app. Currently **private** (IAM-auth required).
  `/api/health` and `/api/ping-gemini` verified end to end.
- Deploy command:
  `gcloud run deploy kb-copilot --source . --region us-central1 --service-account kb-copilot-run@groovy-analyst-509819-d5.iam.gserviceaccount.com --build-service-account projects/groovy-analyst-509819-d5/serviceAccounts/kb-copilot-build@groovy-analyst-509819-d5.iam.gserviceaccount.com --set-env-vars GOOGLE_CLOUD_PROJECT=groovy-analyst-509819-d5,GOOGLE_CLOUD_LOCATION=global --memory 1Gi`
- Shared contract: [CHUNK_SCHEMA.md](CHUNK_SCHEMA.md) + [app/schema.py](app/schema.py).

**2026-09-27 (Day 2, cont.): ingestion + retrieval (Person A track, Days 3–7) working**
- `python -m app.ingest` → `index/`: 649 chunks from 633 records, embedded with `gemini-embedding-2`
  (768-d) in about 40 s. The index is committed and baked into the image; re-runs reuse unchanged embeddings.
- Staleness signals inferred without the answer key (CHUNK_SCHEMA.md §3), e.g. POL-18 is flagged
  because it names the departed DPO and has an open policy-update request.
- Hybrid retrieval (Gemini + BM25, RRF), role filter, reserved policy slots, link expansion,
  and withheld-record reporting. Deployed: `POST /api/search`.
- Eval (`python -m scripts.eval_retrieval`): governing policy in top 8 for 93% of the 27 demo
  queries; practice evidence in top 5 for 96%; evidence recall 0.60 (0.70 with expansion).
- Next: agent loop (Person B track) with `search_docs` + `get_related(record_id)` tools,
  returning `AgentResponse`.

**2026-09-27 (Day 2, cont.): agent loop live (M4 + M5, due 2 Oct)**
- M4 decision: own Gemini function-calling loop (not ADK). 5 research tools + `submit_answer`, role bound
  server-side, max 6 tool calls, `gemini-3.8-flash` with thinking LOW. Checks in code: citations only to
  retrieved records, signal-based staleness flags, active-only fallback contacts, access notes.
- `POST /api/chat` and `GET /api/personas` deployed (max 3 instances, 180 s timeout); interim tester page at `/`.
- Eval (`python -m scripts.eval_agent --all`, 28 questions): flags correct 24/28, policy cited 23/27, citation
  precision 0.78, judge 4.6/5, median 13.1 s. Role check: `hr` cites no restricted records.
- Next (Phase 3): code-level conflict detection for "same request, different outcome" (DQ-19/21), retrieval
  fix for DQ-01/22, latency outliers. Full detail: [docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md) §4.10–4.11.

**2026-10-06: sign-in and need-to-know access**
- Requirement: role-wise login; employees see knowledge within their scope only; confidential data not open to everyone.
- Demo sign-in (employee picker + shared demo password, signed session cookie); secrets in Secret Manager.
- Access per employee (no fixed roles): non-confidential = all signed-in employees; confidential = people involved
  + head of owning department + relevant team lead. Confidential includes records found by a Gemini
  personal-data check at ingest (14 extra records). Leave reasons hidden from non-HR colleagues.
- 37 access tests pass; deployed (revision kb-copilot-00005). Details: docs/BUILD_GUIDE.md §4.12, CHUNK_SCHEMA.md §4.

**2026-10-07: 1,000 employees + role-based access**
- Dataset expanded to 1,000 employees (9 departments, 63 teams, contractors/interns), 1,324 tickets, 291 Slack
  threads, 140 Confluence pages; new policy POL-36. All 80 scenarios intact; build + validator pass.
- 14 access roles (payroll, HR business partner, security admin, executive, compliance auditor, ...) by data
  category and domain; every confidential citation shows the rule that allowed it; audit log in Cloud Logging.
- 58 access checks + live role checks pass; quality holds (flags 8/8, judge 4.8/5). Deployed revision kb-copilot-00006.

**2026-10-07: final user interface (Phase 4)**
- New chat app and sign-in page on one design system: roles and scope in the sidebar, grouped sample questions,
  colour-coded callouts (conflict, out of date, withheld, contact), clickable citations, source viewer drawer,
  "How I found this" steps, follow-up questions, phone layout. Per-user rate limit (20 answers / 10 min).
- 60/60 access checks; deployed revision kb-copilot-00007. Remaining for M7: make the URL public (owner action).

**2026-10-08: feedback round (speed, short answers, history)**
- Latency cut from 100-180 s to a 21 s median (max 37 s): pre-retrieval, hedged calls to a fallback model
  (gemini-2.5-flash) when gemini-3.8-flash is slow, shorter answers, tighter budgets, Cloud Run CPU boost.
- Answers ≤ 90 words with contact and references at the end; name-only login; sample questions replaced by
  per-employee question history stored in Firestore. 60/60 access checks; deployed revision kb-copilot-00011.

**2026-10-10: chat-wise history + sidebar redesign**
- Feedback: "signed in as" and history looked alike; history sat below the chat on phones; New chat and Sign out
  side by side; history was per question and follow-ups opened new chats.
- Now: conversations stored in Firestore with their answers, re-shown only if the user may still see every record
  behind them; follow-ups stay in the same chat with server-side context. Sidebar: New chat, chats, account card
  with Sign out at the bottom; phones get a slide-in panel. All access + chat tests pass. Details: BUILD_GUIDE §4.16.

**2026-10-12: rename to AlgoWorks / TouchStone**
- Company Kestrel Technologies -> **AlgoWorks**; tool name -> **TouchStone**; product
  KestrelFleet -> AlgoWorks Fleet; emails @algoworks.io; repos algoworks-*; audit log name `touchstone-audit`.
- Applied to UI, agent prompt, data/, generator (so rebuilds keep it), scripts and docs; data validates; index rebuilt
  (181 chunks re-embedded, 160 records re-checked for personal data; 236 confidential, unchanged).
- Unchanged on purpose: Google Cloud names (`kb-copilot` service and URL, secrets) and the demo password value.
- Tests: all access checks pass; 8 demo questions flags 7/8, judge 4.4/5 (same as before; DQ-01 known gap).

**2026-10-12: production-style sign-in**
- Removed demo framing from sign-in (demo tag, employee count, persona list); public directory reduced to name, title,
  department. Password rotated (Secret Manager v2, v1 disabled). Access tests pass. Details: BUILD_GUIDE §4.17.

