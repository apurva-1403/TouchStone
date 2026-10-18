# Build Guide: TouchStone

**Purpose:** a complete, tool-independent procedure for building this project by hand: what has
been done (with exact commands so you can reproduce it), what is planned, and when.
**Last updated:** 2026-10-10 (Day 15 of 23) · **Deadline:** 2026-10-18 · **Built by:** one developer · **Dataset:** 1,000 employees (the A/B split below describes work tracks, not people)

Companion docs: [PROJECT_HANDOVER.md](../PROJECT_HANDOVER.md) (the why and constraints),
[CHUNK_SCHEMA.md](../CHUNK_SCHEMA.md) (the data contract), [data_README.md](../data_README.md) (the dataset).

**Where we are (10 Oct, Day 15):** all build work is done: M0–M6 complete, M7's UI done; only making the
Cloud Run URL public remains for M7 (owner action, before the 12 Oct feature freeze). Live revision:
`kb-copilot-00011` (private). Next: rehearsal and deck (13–14 Oct), compliance check (15), video (16), submit (17).

| Done | When | Section |
|---|---|---|
| Cloud + Gemini spike, schema, ingestion, hybrid retrieval | 27 Sep | §4.1–4.9 |
| Agent loop + evaluation | 27 Sep | §4.10–4.11 |
| Similar-case conflict detection, latency fixes, answer cache (Phase 3) | 30 Sep | §4.11b |
| Employee sign-in + need-to-know access | 6 Oct | §4.12 |
| 1,000-employee dataset + 14 access roles + audit log | 7 Oct | §4.13 |
| Final UI (Phase 4) | 7 Oct | §4.14 |
| Speed (21 s median), short answers, Firestore question history | 8 Oct | §4.15 |
| Chat-wise history (access-safe), sidebar redesign, mobile slide-in panel | 10 Oct | §4.16 |

---

## Contents

1. [What we are building](#1-what-we-are-building)
2. [Architecture and tech stack](#2-architecture-and-tech-stack)
3. [Prerequisites (one-time machine setup)](#3-prerequisites-one-time-machine-setup)
4. [Completed work, step by step](#4-completed-work-step-by-step)
5. [Plan by phase (status as of 10 Oct)](#5-plan-by-phase-status-as-of-10-oct)
6. [Timeline and milestones](#6-timeline-and-milestones)
7. [Risks and mitigations](#7-risks-and-mitigations)
8. [Cost control](#8-cost-control)
9. [Submission checklist](#9-submission-checklist)
10. [Command cheat sheet](#10-command-cheat-sheet)
11. [Gotchas we already hit](#11-gotchas-we-already-hit)

---

## 1. What we are building

An enterprise knowledge assistant over a synthetic company (AlgoWorks) that answers employee
questions from policies, tickets, emails, Slack and Confluence, and differs from naive RAG in four ways:

| # | Behaviour | Example (demo query) |
|---|---|---|
| 1 | **Surfaces conflicts** instead of silently picking one source | "Has the VPN dropping every 30 min been solved?" gives two different fixes that were both tried |
| 2 | **Flags stale sources** (written policy vs actual practice) | "Do I need a CHG to deploy?" says the policy says yes, but since Dec 2025 a merged GitOps PR is the approval |
| 3 | **Falls back to a person** when unsure, and never to someone who left | "Who approves Snowflake PII now the DPO left?" warns that the DPO has exited and names who actually approves |
| 4 | **Role-scoped answers**: restricted content never reaches the wrong role | Same question as `hr` vs `exec` gives different evidence, plus "ask <department head> for access" |

Hard constraints (hackathon): model calls must be **Gemini/Gemma** (or a Google agent platform);
hosting must be **Cloud Run or Firebase**. Deliverables: deployed prototype, proposal deck, 3-min video.

---

## 2. Architecture and tech stack

```
Browser (static HTML/JS: chat, citations, conflict/staleness badges, role switcher)
   │  HTTPS
   ▼
Cloud Run service "kb-copilot"  (one container: FastAPI + static files)
   ├── /api/search   role-filtered hybrid retrieval            [done]
   ├── /api/chat     Gemini agent loop with tools             [planned]
   ├── index/        chunks.jsonl + embeddings.npy (baked into the image)
   └── data/         raw dataset (directory lookups: people, teams, systems)
   │  Vertex AI (service account auth, no API keys)
   ▼
Gemini on Vertex AI: gemini-3.8-flash (agent) · gemini-3.5-flash-lite (fast tasks) · gemini-embedding-2
```

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.11 | Team familiarity, best Gemini SDK support |
| Web framework | FastAPI + Uvicorn | Simple, typed (Pydantic), serves static files too |
| LLM SDK | `google-genai` with `vertexai=True` | Official SDK; Vertex uses IAM instead of API keys |
| Models | `gemini-3.8-flash`, `gemini-3.5-flash-lite`, `gemini-embedding-2` | Newest available in the project (verified by listing models, §4.2) |
| Vector search | NumPy matrix in memory (649 × 768) | Tiny dataset: exact cosine takes microseconds, no DB to operate |
| Keyword search | Own BM25 implementation (≈30 lines) | Catches exact terms (IDs, product names) that embeddings miss |
| Hosting | Cloud Run, single service | Meets the rule; scales to zero; one thing to deploy |
| Build | `gcloud run deploy --source` (Cloud Build + Dockerfile) | No local Docker needed |
| Frontend | Plain HTML/CSS/JS (upgrade to Vite+React only if needed) | Zero build step, served by FastAPI |

**Deliberately not used:** Chroma or other vector DBs (unnecessary at this size, and Chroma's *default*
embedder is a non-Google model, which is a compliance risk), LangChain (hides the agent loop we want to
control), real Slack/Drive connectors (out of scope; the dataset is synthetic by design).

### Repository layout

```
app/
  config.py        env-driven settings (project, models, paths, simulated today)
  llm.py           the one place a Gemini client is created
  kb.py            dataset loader + Directory (people/teams/systems, "who is active", routing)
  schema.py        Pydantic models: Chunk, Signals, AgentResponse, role access rule
  ingest.py        raw data → chunks → signals → embeddings → index/
  retrieval.py     BM25 + dense + RRF, role filter, expansion, withheld reporting
  main.py          FastAPI app: /api/health, /api/search, /api/ping-gemini, static /
  static/          frontend
data/              dataset (+ demo_queries.json = test answer key, never used at runtime)
generate/          dataset generator (stdlib only, deterministic)
index/             built retrieval index (committed; baked into the image)
scripts/           gemini_hello.py (smoke test), eval_retrieval.py (retrieval metrics)
docs/              this guide
Dockerfile · requirements.txt · .gcloudignore · .env.example · CHUNK_SCHEMA.md · PROJECT_HANDOVER.md
```

---

## 3. Prerequisites (one-time machine setup)

Both team members, Windows 10/11 (commands are for Git Bash unless marked PowerShell).

1. **Python 3.11**: https://www.python.org/downloads/ (tick "Add to PATH"). Check: `python --version`.
2. **Git**: https://git-scm.com/download/win. Set identity:
   `git config --global user.name "Your Name"` and `git config --global user.email "you@example.com"`.
3. **Google Cloud SDK (gcloud)**: https://cloud.google.com/sdk/docs/install. Default install path on
   this machine is `C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin`. If `gcloud` is "not
   recognized", add that folder to PATH (or restart the terminal after install).
4. **Log in twice** (they are different things):
   ```bash
   gcloud auth login                         # lets YOU run gcloud commands
   gcloud auth application-default login     # lets CODE on your laptop call Google APIs (ADC)
   gcloud config set project groovy-analyst-509819-d5
   ```
5. **Project access for the teammate:** the project owner adds them in Cloud Console → IAM → Grant
   access → their Google account → role *Editor* (simplest for a hackathon).
6. **Editor:** VS Code with the Python extension.

---

## 4. Completed work, step by step

Status on 2026-10-10 (Day 15): everything below is built and deployed; see the table at the top for dates.

### 4.0 Dataset (existed before the build started)

Synthetic, relationally consistent dataset: 633 searchable records (35 policies, 281 tickets, 106 email
threads, 141 Slack conversations, 70 Confluence pages) plus 100 employees, 18 teams, 30 systems,
24 projects, 80 events. Regenerate and validate (stdlib only, deterministic seed):

```bash
python generate/build.py
python generate/validate.py
```

**Critical rule:** these fields are the dataset's *answer key* and must never be read by the product:
`policies[].is_stale_by_design`, `events[].is_drift_scenario`, `events[].drift_note`, event `type`
labels, and all of `data/demo_queries.*`. The product must *infer* staleness and conflict.

### 4.1 Google Cloud project setup

1. Create a project in Cloud Console (ours: `groovy-analyst-509819-d5`) and link a billing account.
2. Enable the four APIs we need:
   ```bash
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
       artifactregistry.googleapis.com aiplatform.googleapis.com
   ```
   | API | Used for |
   |---|---|
   | Cloud Run | hosting the container |
   | Cloud Build | building the image from source on deploy |
   | Artifact Registry | storing the built images |
   | Vertex AI (aiplatform) | Gemini generation + embeddings |

### 4.2 Choose and verify models

We call Gemini through **Vertex AI** (not an AI Studio API key): auth is by Google identity (your ADC
locally, a service account on Cloud Run), so there is no key to leak, and it is still "Gemini" per the rules.

1. List the Google models available to the project (PowerShell):
   ```powershell
   $t = gcloud auth print-access-token
   $h = @{Authorization="Bearer $t"; "x-goog-user-project"="groovy-analyst-509819-d5"}
   (Invoke-RestMethod -Headers $h -Uri "https://aiplatform.googleapis.com/v1beta1/publishers/google/models?pageSize=300").publisherModels.name
   ```
2. Smoke-test candidates with a tiny script (generate "Reply with exactly: OK" and embed a sentence).
   Results on 2026-09-27: all of `gemini-3.8-flash`, `3.7-flash`, `3.5-flash`, `3.5-flash-lite`,
   `3.1-pro-preview`, `2.5-flash` and `gemini-embedding-2` worked via location `global`.
3. Chosen: `gemini-3.8-flash` (agent), `gemini-3.5-flash-lite` (cheap side tasks),
   `gemini-embedding-2` (embeddings, truncated to 768 dims). All overridable by env vars
   (`AGENT_MODEL`, `FAST_MODEL`, `EMBEDDING_MODEL`, `EMBEDDING_DIM`), see `app/config.py`.

### 4.3 Repository scaffold

```bash
git init -b main
python -m venv .venv
.venv/Scripts/python -m pip install --upgrade pip
.venv/Scripts/python -m pip install -r requirements.txt   # google-genai, fastapi, uvicorn, python-dotenv, numpy
cp .env.example .env                                       # optional: override settings locally
```

Key files and what they do:
- `.gitignore`: excludes `.venv/`, `.env`, `__pycache__/`.
- `.gcloudignore`: what is **not** uploaded to Cloud Build (venv, generator, scripts, docs; `data/*.md` kept).
- `app/llm.py`: `genai.Client(vertexai=True, project=..., location="global")`, cached. Nowhere else
  creates a client, so switching auth or region is a one-line change.

Run locally and check:
```bash
.venv/Scripts/python -m scripts.gemini_hello              # generation + embedding smoke test (needs ADC)
.venv/Scripts/python -m uvicorn app.main:app --reload --port 8000
# open http://localhost:8000  and  http://localhost:8000/api/health
```

### 4.4 Service accounts and IAM

On this project the default compute service account has **no roles** (newer projects no longer get the
broad automatic *Editor* grant). So Cloud Run's build and runtime both need explicitly permitted
accounts. We use two narrow ones (least privilege):

```bash
P=groovy-analyst-509819-d5

# Runtime identity of the Cloud Run service: may call Vertex AI and write logs, nothing else.
gcloud iam service-accounts create kb-copilot-run --display-name="TouchStone (Cloud Run runtime)"
gcloud projects add-iam-policy-binding $P --member="serviceAccount:kb-copilot-run@$P.iam.gserviceaccount.com" --role=roles/aiplatform.user --condition=None
gcloud projects add-iam-policy-binding $P --member="serviceAccount:kb-copilot-run@$P.iam.gserviceaccount.com" --role=roles/logging.logWriter --condition=None

# Identity Cloud Build uses when building our image.
gcloud iam service-accounts create kb-copilot-build --display-name="TouchStone (Cloud Build)"
gcloud projects add-iam-policy-binding $P --member="serviceAccount:kb-copilot-build@$P.iam.gserviceaccount.com" --role=roles/cloudbuild.builds.builder --condition=None
```

If a binding fails with "service account does not exist", wait 30–60 s (IAM propagation) and retry.

### 4.5 Containerise and deploy to Cloud Run

`Dockerfile`: `python:3.11-slim` → `pip install -r requirements.txt` → copy `app/`, `data/`, `index/`
→ `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

Deploy (from the repo root; about 3–5 minutes):
```bash
P=groovy-analyst-509819-d5
gcloud run deploy kb-copilot --source . --region us-central1 \
  --service-account kb-copilot-run@$P.iam.gserviceaccount.com \
  --build-service-account projects/$P/serviceAccounts/kb-copilot-build@$P.iam.gserviceaccount.com \
  --no-allow-unauthenticated --memory 1Gi --max-instances 3 --timeout 180 --cpu-boost \
  --update-secrets DEMO_PASSWORD=demo-password:latest,SESSION_SECRET=session-secret:latest \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$P,GOOGLE_CLOUD_LOCATION=global
```

| Flag | Meaning |
|---|---|
| `--source .` | upload the folder; Cloud Build builds it using the Dockerfile |
| `--service-account` | identity the running container uses to call Vertex AI |
| `--build-service-account` | identity Cloud Build uses (must be user-managed, not the legacy Cloud Build account) |
| `--no-allow-unauthenticated` | private: callers need IAM permission (switch to public before judging) |
| `--memory 1Gi` | headroom for the index + NumPy |
| `--max-instances 3` | cost guard: a traffic flood is throttled instead of scaled up |
| `--timeout 180` | an agent answer can take 10–40 s; fail cleanly after 3 min |

Service URL: `https://kb-copilot-304689352997.us-central1.run.app` (currently private). Test it:
```bash
T=$(gcloud auth print-identity-token)
curl -H "Authorization: Bearer $T" https://kb-copilot-304689352997.us-central1.run.app/api/health
# or open it in a browser through a local authenticated proxy:
gcloud run services proxy kb-copilot --region us-central1      # then http://localhost:8080
```
Make public (only when ready for judges):
```bash
gcloud run services add-iam-policy-binding kb-copilot --region us-central1 --member=allUsers --role=roles/run.invoker
```

### 4.6 The shared data contract (chunk schema)

Defined in `CHUNK_SCHEMA.md` and mirrored in `app/schema.py`. Every chunk carries its **own** full
metadata (not just a pointer to the parent): record ID, source type/system, department, sensitivity,
dates, owners, status, cross-references and derived `signals`. This lets retrieval filter and rank
without extra lookups, and lets the two team members work in parallel against a fixed shape.

Roles (proposal, not yet confirmed by the team):

| Role | Sees |
|---|---|
| `engineer` | all public/internal + restricted from Engineering (DEPT-01) and IT & Infra (DEPT-02) |
| `hr` | all public/internal + restricted from HR (DEPT-04) |
| `exec` | everything |

### 4.7 Ingestion pipeline (`python -m app.ingest`)

Input: the 5 source files. Output: `index/chunks.jsonl`, `index/embeddings.npy`, `index/manifest.json`.

1. **Convert each record to text with a header**, so every chunk makes sense on its own:
   - Ticket: type, ID, category, status, priority, subject, requester/assignee, dates, description,
     resolution, work notes → **1 chunk**.
   - Email thread: subject, then each message as "From X to Y on date: body" → **1 chunk**.
   - Slack: channel + date, then "[ts] Name: text" lines → **1 chunk**.
   - Policy / Confluence: split the markdown on `##` headings, then **pack** consecutive sections up
     to ≈1,600 characters (sections under 300 chars merge into the next; oversized sections split on
     blank lines). Each chunk repeats the header (title, version, last-updated date, owner/authors).
   - Result: **649 chunks from 633 records**.
2. **Resolve owners** (who to route questions to): policy → owning team's lead; Confluence → authors;
   ticket → assignee (else requester); email/Slack → participants.
3. **Detect mentions in text** (case-insensitive substring match against the directory):
   - policy titles → `related_policy_ids` (tickets and emails name policies by *title*, never by ID);
   - system names → `related_system_ids`;
   - people by full name, **and job titles held by exactly one person** (e.g. "Data Protection Officer")
     so a policy that names a role is linked to the person holding it.
4. **Build a reverse-link table** (who references whom) from `referenced_ids` + detected policy
   mentions. `EVT-*` IDs and `event_id` are **not** used for linking (they are a dataset construct
   that groups each scenario's evidence, which would inflate results).
5. **Compute staleness signals** per record (hints for the agent, not verdicts):
   | Signal | Rule |
   |---|---|
   | `days_since_update` | simulated today (2026-09-24) − `last_updated` |
   | `owners_inactive` | owners whose `employees.status` ≠ `active` |
   | `inactive_people_mentioned` | inactive people named in the text (by name or unique role title) |
   | `open_update_request_ids` | tickets with category `policy-update` and status open/in-progress/on-hold that name this record |
   | `later_mention_ids` | records referencing this one that are newer than its `last_updated` |
   Sanity check: signals flag 11 of the 13 stale-by-design policies with 1 false positive (POL-13).
   POL-18 is flagged via "Data Protection Officer" → EMP-021 (exited) plus an open update request.
6. **Embed** each chunk with `gemini-embedding-2`, task type `RETRIEVAL_DOCUMENT`,
   `output_dimensionality=768`, then L2-normalise. **One text per request** (8 in parallel, with
   exponential-backoff retries): this model merges a list input into a single vector.
   Takes about 40 s for 649 chunks. Re-runs reuse vectors for unchanged chunk text (hash cache).
7. `--no-embed` builds a BM25-only index (no Gemini needed): handy offline.

### 4.8 Retrieval (`app/retrieval.py`, `POST /api/search`)

For query *q* and role *r*:
1. **BM25** over title+text (k1 = 1.4, b = 0.75; tokens are lowercase alphanumerics keeping `-`/`.`
   inside IDs; small stop-word list).
2. **Dense**: embed *q* with task type `RETRIEVAL_QUERY`, cosine = dot product with the normalised matrix.
3. **Fuse** with Reciprocal Rank Fusion: `score = Σ 1 / (60 + rank)` over both rankings.
4. **Role filter**: drop chunks the role cannot see (before anything can reach an LLM).
5. **Best chunk per record**, top *k* = 8 records, with **2 slots reserved for policies** so the agent
   always has the written rule to compare against practice.
6. **Expansion** (`related`, up to 6): open `policy-update` requests against retrieved policies first,
   then other linked records by score.
7. **Withheld reporting**: restricted records that would have ranked for this query but the role
   can't see → only a count plus the owning department's head as the contact. No text or titles.

```bash
curl -X POST localhost:8000/api/search -H "Content-Type: application/json" \
     -d '{"query":"Who approves Snowflake PII access now that the DPO has left?","role":"hr","k":8}'
```

### 4.9 Retrieval evaluation (`python -m scripts.eval_retrieval [-v]`)

Uses `demo_queries.json` **only as a test answer key**. Metrics over 27 queries (role `exec`, k = 8):

| Metric | Meaning | BM25 only | Hybrid + policy slots |
|---|---|---|---|
| pol@k | governing policy in top 8 | 67% | **93%** |
| prac@5 | ≥1 practice record (ticket/email/Slack/doc) in top 5 | 93% | **96%** |
| rec@k | share of evidence records in top 8 | 0.54 | **0.60** |
| rec+x | same, including expansion | 0.63 | **0.70** |

Known gap: DQ-01/DQ-22 (Salesforce/HubSpot access). Many routine access tickets crowd out the drift
evidence, which needs a second hop (policy → update request → the tickets it cites). The agent's
`get_related` tool is designed for that.

### 4.10 Agent loop (`app/agent.py`, `app/tools.py`, `POST /api/chat`)

**Decision (M4):** our own Gemini function-calling loop via `google-genai`, not ADK. Conflict detection
and fallback are what gets judged, so we keep full control of the loop and its checks.

**Tools** (bound to the request's role server-side; the model cannot change the role):

| Tool | Returns |
|---|---|
| `search_docs(query)` | top records with staleness signals, linked records, restricted-withheld summary |
| `get_record(record_id)` | full text, owners, references ("not available to this role" if restricted) |
| `get_related(record_id)` | open update requests, records it references, records referencing it |
| `lookup_person(name_or_id)` | role, team, status, and who to route to if exited/on leave |
| `find_owner(system_or_policy)` | owning team, active contact, access process |
| `submit_answer(...)` | the final structured answer (its parameters are the answer schema) |

**Loop:**
1. System prompt = the behaviour contract (research steps + answer rules), with today's date and the
   role's persona (engineer: Harish Gowda, SRE · hr: Swati Kulkarni, HRBP · exec: Vivek Anand, CFO).
2. Call `gemini-3.8-flash` with tools, `thinking_level=LOW`, automatic function calling off.
3. Run every function call the model returns (it may return several in parallel), send results back.
4. Repeat until it calls `submit_answer`. After 6 research calls, force it
   (`FunctionCallingConfig(mode="ANY", allowed_function_names=["submit_answer"])`). Hard cap: 10 model calls.

Why `submit_answer` instead of JSON mode: with tools **and** a JSON response schema in the same call,
Gemini kept re-calling tools instead of answering. A final-answer tool gives structured output in the
same loop with no extra model call.

**Checks in code after the model answers** (the model is not trusted blindly):
- `[RECORD-ID]` markers become `[1][2]`; IDs never returned by a tool for this role are dropped.
- Cited policies/docs with signals (inactive people named, open update requests) always get a staleness flag.
- The fallback contact must be active; if not, it is re-routed up the manager chain.
- If restricted records were withheld, an access note names the top data owner to ask.

**Reliability:** one shared Gemini client created under a lock (the SDK closes its HTTP connection when a
client object is garbage-collected, which broke concurrent first calls), 90 s timeout, and automatic
retries with backoff on 429/5xx (`HttpRetryOptions(attempts=5)`).

**Latency tuning** (same question, 27 Sep): default thinking 38–71 s → `LOW` + "call independent tools
together" 15 s. `gemini-3.5-flash` was 5× slower than `gemini-3.8-flash`.

### 4.11 Agent evaluation (`python -m scripts.eval_agent [--all] [--as EMP-046] [-v]`)

Runs questions end-to-end and scores against `demo_queries.json` (test-only): drift flag
(`policy_vs_practice` conflict) and conflict flag (`conflicting_resolutions`/`source_vs_source`) vs
expected, governing policy cited, citation precision/recall vs evidence, and a 1–5 agreement score from
`gemini-3.5-flash-lite` acting as judge against the expected answer summary.

All 27 demo queries + the March outage question, role `exec`, 27 Sep:

| Metric | Result |
|---|---|
| Drift + conflict flags both correct | **24 / 28** |
| Governing policy cited | **23 / 27** |
| Citation precision (cited records that are expected evidence) | **0.78** |
| Evidence recall | 0.53 |
| Judge agreement with expected answer | **4.6 / 5** |
| Median latency | **13.1 s** |
| Citations to never-retrieved records | 0 (enforced in code) |

Misses to fix in Phase 3: DQ-19 and DQ-21 (conflicting resolutions not flagged), DQ-09 and DQ-23 (a conflict/drift
flagged where the key expects none), DQ-22 (HubSpot access: weak answer, 105 s with quota retries).
Role check: as `hr`, the DPO and Admin Console questions cite **no** restricted records and show an access note.

### 4.11b Similar-case conflict detection and reliability (Phase 3, 30 Sep)

- **Similar past cases** ([app/retrieval.py](../app/retrieval.py) `_case_groups`, [app/cases.py](../app/cases.py)):
  each retrieved ticket is grouped with past tickets of the same category whose embeddings are ≥ 0.88 similar and
  that are also among the 40 records most relevant to the question (known same-problem pairs scored 0.90–0.93; the
  relevance pool filters out near-duplicate template noise). `gemini-3.5-flash-lite` then judges whether each group
  is the same issue and was handled the same way (answer, fix, route, turnaround; differences the tickets themselves
  explain don't count). `search_docs` returns these as `similar_past_cases`, so "same question, different answer"
  no longer depends on the agent model noticing it. Fixed DQ-18, DQ-19, DQ-21.
- **Prompt rules:** every flagged conflict/stale source must also appear in the answer text; only report conflicts
  that change the answer to what was asked (fixed false flags on DQ-02, DQ-24).
- **Evaluation fixes:** policy-vs-policy (`source_vs_source`) counts as drift, as the dataset defines it; the judge
  uses the agent model and sees the callouts the user sees.
- **Latency:** removed an embedding retry loop that stacked with the SDK's retries (caused a 62 s stall), startup
  warm-up of the index and Gemini connection, per-call and per-tool timings in the response, in-memory answer cache.
- **Results:** 28 questions, one at a time: flags 25/28, judge 4.9/5, median 17.1 s. Reliability (8 demo
  questions × 3): 23/24 flag checks, judge 4.8/5, median 14.4 s; no restricted citations for other roles.

### 4.12 Sign-in and need-to-know access (6 Oct)

- **Sign-in** ([app/auth.py](../app/auth.py)): pick an employee + shared demo password → HMAC-signed, HttpOnly,
  SameSite=Lax session cookie (8 h) carrying only the `employee_id`. 10 failed attempts per IP per 10 minutes → 429.
  Employees who have left can't sign in. `DEMO_PASSWORD` and `SESSION_SECRET` live in `.env` locally (gitignored)
  and in **Secret Manager** on Cloud Run (`demo-password`, `session-secret`, readable only by `kb-copilot-run`).
- **Access rules** ([app/access.py](../app/access.py)): see CHUNK_SCHEMA.md §4. No fixed roles; scope comes from
  the employee's department, team, tier and involvement. Seniority grants nothing outside one's department.
- **Personal-data check** ([app/classify.py](../app/classify.py)): `gemini-3.5-flash-lite` reviews all 598
  non-policy records at ingest (cached by text hash); 14 records labelled only "internal" were found to hold
  personal data and became confidential.
- **UI**: `/login.html` (searchable employee picker + 6 suggested personas with different scopes); the chat
  page shows who you are and how many confidential records you can see, with a Sign out button.
- **Tests** (`python -m scripts.test_access --agent`): 37 checks, all passing: the rules, forged/edited
  sessions, login rate limit, leavers, search/links/similar cases for 6 employees, tool refusals, hidden
  leave details, and live agent answers citing nothing out of scope.

Deploy now adds: `--update-secrets DEMO_PASSWORD=demo-password:latest,SESSION_SECRET=session-secret:latest`.
Evaluation scripts default to an evaluation-only principal that sees everything (`--as EMP-046` to run as
an employee); it is never issued to a session.

### 4.13 1,000 employees and role-based access (7 Oct)

- **Dataset:** [generate/layer1b_workforce.py](../generate/layer1b_workforce.py) adds 900 generated people
  (EMP-101..1000), Product Management, Legal & Compliance and Executive Office departments, and 45 teams (63 total).
  The 100 roster people keep EMP-001..100; no generated person takes a title a scenario depends on (asserted).
  Routine volume scaled: 1,324 tickets, 291 Slack threads, 140 Confluence pages (department rosters + a page per team).
  New policy POL-36 documents the roles. Ticket/doc numbers are by date, so they changed; demo_queries regenerated.
- **Roles:** 14 access roles assigned by job/team (`access_roles` on each employee); rules in CHUNK_SCHEMA.md §4.
- **Audit:** every answer (including cached) and search is logged as a structured line in Cloud Logging
  (`jsonPayload.log="touchstone-audit"`); auditor-only access is flagged; `/api/audit` for compliance auditors.
- **Results (7 Oct):** 58/58 access checks + live agent role checks pass. Retrieval: policy in top 8 93% (unchanged),
  evidence recall with links 0.67 (was 0.70). Agent on the 8 demo questions: flags 8/8, judge 4.8/5, median 15.7 s.
- **Re-index time:** ~10 min (1,638 personal-data checks + 1,687 embeddings); later runs reuse both caches.

### 4.14 Final user interface (Phase 4, 7 Oct)

Files: [app/static/index.html](../app/static/index.html), [app.js](../app/static/app.js),
[app.css](../app/static/app.css) (shared design system), [ui.js](../app/static/ui.js) (icons, the animated assistant
character, theme switch), [login.html](../app/static/login.html). Plain HTML/CSS/JS, no build step; light and dark
themes (saved per browser, defaulting to the system setting); at phone width the sidebar becomes a slide-in panel.
The character wears sunglasses in light mode and holds a candle in dark mode; while an answer is being prepared it
"searches" (glasses up / candle sweeping, source cards flying in). All motion stops under `prefers-reduced-motion`.

- **Sidebar:** who you are, your access roles (with what each grants), how many of the confidential records you can
  see, HR-partner departments; sample questions grouped by what they demonstrate (policy vs practice,
  conflicting past answers, straight answers, access in action).
- **Answers:** status chips, then callouts: conflicts (red), possibly out of date (amber), confidential records
  withheld (violet), who to contact (teal); the answer with clickable citation numbers; source cards (system,
  record ID, date, confidential badge with the rule that allowed it); "How I found this" with the agent's steps
  and timings. Follow-up questions send the last 4 turns as context.
- **Source viewer:** a drawer showing the full record (`GET /api/records/{id}`): access-checked, confidential
  views audit-logged, and a record outside your scope returns the same 404 as a missing one.
- **Guards:** 20 fresh answers per user per 10 minutes (cached answers don't count), on top of
  `--max-instances 3` and the 6-tool-call cap.
- Tests: 60/60 access checks. Deployed as revision kb-copilot-00007.

### 4.15 Feedback round: speed, short answers, history (8 Oct)

**Latency.** Answers were taking 100-180 s. Measurement showed tools take ~2 s; the time was the agent model:
`gemini-3.8-flash` calls that only emit a tool call took 2-97 s (no 429s: queueing on the model side), while
`gemini-2.5-flash` stayed at ~1-12 s. Fixes, in order of effect:
1. **Pre-retrieval:** the first `search_docs` runs before the first model call and its results go into the prompt
   (saves the round trip that only decided to search). Research budget: 3 tool calls; usually none beyond the first.
2. **Hedged model calls** (`app/agent.py` `_hedged_call`): if `AGENT_MODEL` hasn't answered after `HEDGE_AFTER_S`
   (8 s) or errors, the same call also goes to `FALLBACK_MODEL` (`gemini-2.5-flash`) and the first answer wins; the
   rest of that question stays on the winner. `meta.model` records which model answered.
3. **Short answers** (≤ 90 words) make the final call faster; similar-case comparison budget 8 → 4 s; HTTP timeout
   45 s with 3 attempts; max 5 model calls; Cloud Run `--cpu-boost` for cold starts.

Result on the 8 demo questions (8 Oct): median 20.9 s (was 71-126 s that morning), max 37 s, judge 4.4/5, flags 7/8.
DQ-01 now gives a correct short how-to but omits the subtle practice drift.

**Answers** are at most 90 words: one plain sentence, up to 3 bullets; conflicts as one line; contact and references
shown at the end of the answer card. **Sidebar**: sample questions removed; "Your recent questions" from
[app/history.py](../app/history.py), stored in **Firestore** (`users/{employee_id}/history`, questions + time +
flags only, never answers; 5 s timeouts, in-memory fallback). `/api/health` reports `history_backend`.
**Login**: names only. Cloud setup added: Firestore API, `(default)` database in us-central1 (Native mode),
`roles/datastore.user` for `kb-copilot-run`. Deploy now also passes `--cpu-boost`.

### 4.16 Chat-wise history and sidebar redesign (10 Oct)

- **Conversations, not questions** ([app/history.py](../app/history.py)): Firestore `users/{employee_id}/chats/{chat_id}`
  (in-memory fallback offline). `POST /api/chat` takes `chat_id`; the first answer creates the chat and returns its
  `chat_id`, follow-ups append to it, and the follow-up context (last 4 turns) is loaded server-side from the stored
  chat. New endpoints: `GET /api/chats`, `GET /api/chats/{id}`, `DELETE /api/chats/{id}`, `DELETE /api/chats`
  (replace `/api/history`). Max 30 turns per chat, 50 chats listed.
- **Stored answers stay access-safe:** each turn keeps the answer, the IDs of every record the agent was shown
  (`meta.retrieved_record_ids`) and a fingerprint of the user's access scope (department, team, roles, HR-partner
  departments, reporting line). Reopening a chat re-shows an answer only if the scope is unchanged and every one of
  those records is still visible; otherwise the question is shown with "Ask again". Chats live under the user's own
  path: another employee gets 404 and can't list or delete them.
- **UI** ([index.html](../app/static/index.html), [app.js](../app/static/app.js), [app.css](../app/static/app.css)):
  sidebar = "+ New chat" on top, chats in the middle (active chat highlighted, question count, flag dots, delete),
  and a distinct "Signed in as" account card pinned at the bottom (avatar, title, collapsible access details,
  Sign out). On phones (≤ 900 px) the sidebar is a slide-in panel: ☰ opens it, tapping outside / Esc / choosing a
  chat closes it; a + button in the top bar starts a new chat.
- **Tests:** `scripts/test_access.py` adds 9 chat checks (same-chat follow-ups, chat-wise listing, hidden answers
  after an access change, context filtering, isolation between employees, delete) plus 2 live follow-up checks
  under `--agent`; all pass.

### 4.17 Production-style sign-in and new password (12 Oct)

- Sign-in page shows only Employee + Password: no "Demo environment" tag, no employee count, no suggested personas
  (`DEMO_PERSONAS` removed from [app/main.py](../app/main.py)); dead persona CSS removed.
- Public `GET /api/directory` (used by the sign-in search) now returns only `employee_id`, `name`, `title`,
  `department`; access roles and employment type are no longer exposed before sign-in.
- Password rotated: new value in `.env` (local) and Secret Manager `demo-password` version 2; version 1 disabled.
  Cloud Run reads `latest` when an instance starts, so the deploy switches the live site to the new password.

---

## 5. Plan by phase (status as of 10 Oct)

### Phase 2: Agent loop ✅ done 27 Sep (planned for 2 Oct)

Built as planned; details and results in §4.10–4.11. Carried into Phase 3: conversation history in the
UI (the API already accepts `history`), and answer-level caching for the demo questions.

### Phase 3: Differentiators ✅ done 30 Sep (planned for 8 Oct)

Conflict detection (policy vs practice and "same question, different answer"), staleness warnings, fallback to an
active owner, and access-scoped answers: built and tested in §4.11b; access control then grew into per-employee
need-to-know (§4.12) and 14 roles (§4.13). The second Gemini model is used for case comparison and the
personal-data check.

### Phase 4: UI + integration + polish: UI ✅ 7–8 Oct · public URL pending (target 12 Oct)

Done: sign-in page, chat app with sidebar (roles, scope, question history), colour-coded callouts, clickable
citations, source viewer, agent steps, follow-ups, phone layout, per-user rate limit (§4.14–4.15).
Remaining before the **12 Oct feature freeze**:
1. **Make the service public** (owner action):
   `gcloud run services add-iam-policy-binding kb-copilot --region us-central1 --member=allUsers --role=roles/run.invoker`
2. Test sign-in and the 8 demo questions from a phone and an incognito window.
3. For demo day: `--min-instances 1` (no cold start) and ask the demo questions once beforehand (answer cache).

### Phase 5: Rehearsal + deck (Tue 13 – Wed 14 Oct, Days 18–19) · both

- Timed run-through of the demo script (target: 8 queries in under 3 min, roughly 20 s each).
- Proposal deck: problem → why naive RAG fails → approach (signals, conflict, fallback, roles) →
  architecture → live demo screenshots → evaluation numbers → impact → future work.

### Phase 6: Buffer, video, submit (Thu 15 – Sun 18 Oct)

- Thu 15 (Day 20): bug fixing only; final compliance check (§9).
- Fri 16 (Day 21): record the 3-minute video **against the public Cloud Run URL**; finalise deck.
- Sat 17 (Day 22): **submit** (prototype URL + deck + video).
- Sun 18 (Day 23): official deadline, kept as a spare day. Do not plan work for it.

---

## 6. Timeline and milestones

| # | Milestone | Target date | Exit criteria | Status |
|---|---|---|---|---|
| M0 | Dataset ready | before 26 Sep | `validate.py` passes | ✅ done |
| M1 | Cloud + Gemini spike | Sun 27 Sep (Day 2) | Cloud Run service calls Gemini end-to-end | ✅ done 27 Sep |
| M2 | Chunk schema agreed | Sun 27 Sep | `CHUNK_SCHEMA.md` v0.2 + `app/schema.py` | ✅ 27 Sep (now v0.6, role-based access) |
| M3 | Ingestion + retrieval | Fri 2 Oct (Day 7) | index built; `/api/search` deployed; eval baseline | ✅ done early, 27 Sep |
| M4 | Orchestration decision | Mon 28 Sep | Own loop vs ADK chosen after ≤ half-day spike | ✅ own loop, 27 Sep |
| M5 | **Agent loop live** | **Fri 2 Oct (Day 7)** | `/api/chat` returns cited `AgentResponse` for 8 demo queries on Cloud Run | ✅ done early, 27 Sep |
| M6 | **Differentiators** | **Thu 8 Oct (Day 13)** | conflict, staleness, fallback, role scoping reliable on the 8 queries (3 runs each) | ✅ done 30 Sep (23/24 checks, judge 4.8/5) |
| M7 | **UI complete + public URL** | **Mon 12 Oct (Day 17)** | full demo flow works in browser from the public URL; feature freeze | ⏳ UI ✅ 7–8 Oct · **public URL pending (next)** |
| M8 | Rehearsal + deck draft | Wed 14 Oct (Day 19) | demo under 3 min; deck complete | ⏳ starts 13 Oct |
| M9 | Code freeze + compliance | Thu 15 Oct (Day 20) | §9 checklist all green | ⏳ |
| M10 | Video recorded | Fri 16 Oct (Day 21) | 3-min video from the live URL | ⏳ |
| M11 | **Submitted** | **Sat 17 Oct (Day 22)** | all three deliverables submitted | ⏳ |
| — | Official deadline | Sun 18 Oct | spare day | — |

Week-by-week view:

| Week | Dates | Focus |
|---|---|---|
| 1 | 26 Sep – 2 Oct | ✅ Foundation: cloud, data, retrieval, agent loop, and the differentiators (30 Sep) |
| 2 | 3 – 8 Oct | ✅ Sign-in, need-to-know + 14 roles, 1,000-employee dataset, final UI, speed and history |
| 3 | 9 – 12 Oct | ⏳ **now**: make the URL public, phone/incognito test, feature freeze 12 Oct (M7) |
| 3–4 | 13 – 18 Oct | Rehearse, deck, freeze, video, submit (M8–M11) |

---

## 7. Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Agent answers inconsistently between runs | Medium | Low temperature, JSON schema output, code-level post-validation, run each demo query 3× |
| Conflict detection misses or over-flags | Medium | Signals give deterministic hints; false-positive controls (the 10 "routine baseline" queries must come back clean) |
| Restricted content leaks | Low | Filtering happens in retrieval before the LLM; tools never let the model choose the role; test DQ-05/18 per role |
| Model name deprecated or unavailable | Low | All model IDs are env vars; re-run the model listing (§4.2) |
| Cloud Run deploy breaks near deadline | Low | Deploy daily; keep the last good revision (Cloud Run can roll traffic back to a previous revision in one click) |
| Scope creep | High | Freeze after Day 17; the "future work" slide absorbs ideas |
| Non-Google model sneaks in | Low | Compliance grep in §9 |

---

## 8. Cost control

- A **budget alert** (Billing → Budgets & alerts) only emails you; it does not stop spending.
- Real limits: Cloud Run `--max-instances 3`; agent max 6 tool calls per question; rate limit once
  public; keep the service private until Day 17.
- Main cost driver is Gemini tokens; Cloud Run scales to zero when idle.

---

## 9. Submission checklist

- [ ] No non-Google model in the runtime path:
      `requirements.txt` lists only `google-genai`, `google-cloud-firestore`, FastAPI, Uvicorn, python-dotenv and NumPy.
- [ ] Runtime never reads answer-key fields:
      `grep -rnE "is_stale_by_design|is_drift_scenario|drift_note|demo_queries" app` returns nothing.
- [ ] Service is public; tested in an incognito window and on a phone.
- [ ] `--max-instances` set; rate limiting on.
- [ ] Video recorded against the Cloud Run URL (visible in the address bar).
- [ ] Deck includes architecture, Google services used (Gemini, Vertex AI, Cloud Run), eval numbers.
- [ ] Repo tagged: `git tag submission && git push --tags`.

---

## 10. Command cheat sheet

```bash
# environment
.venv/Scripts/activate                                    # or prefix commands with .venv/Scripts/python
gcloud auth application-default login                     # once per machine

# data & index
python generate/build.py && python generate/validate.py  # regenerate dataset (rarely needed)
python -m app.ingest                                      # rebuild index (Gemini embeddings)
python -m app.ingest --no-embed                           # BM25-only index, offline
python -m scripts.eval_retrieval -v                       # retrieval metrics + top records per query
python -m scripts.eval_agent                              # agent on the 8 demo questions (add --all, --role hr, -v)

# run
python -m uvicorn app.main:app --reload --port 8000
python -m scripts.gemini_hello

# deploy (see §4.5 for the full command)
gcloud run deploy kb-copilot --source . --region us-central1 ...
gcloud run services logs read kb-copilot --region us-central1 --limit 50
gcloud run revisions list --service kb-copilot --region us-central1
```

---

## 11. Gotchas we already hit

| Symptom | Cause | Fix |
|---|---|---|
| `gcloud: command not found` in a terminal | SDK bin not on that shell's PATH | add `C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin` to PATH / restart terminal |
| Code can't authenticate locally | ADC not set (different from `gcloud auth login`) | `gcloud auth application-default login` |
| Deploy: `invalid value for build.service_account` | legacy Cloud Build SA isn't accepted | use a user-managed build SA (§4.4) |
| IAM binding: "service account does not exist" right after creating it | IAM propagation delay | wait 30–60 s, retry |
| Embeddings: 3 inputs → 1 vector | `gemini-embedding-2` merges list inputs | embed one text per request |
| Mojibake (`â€”`) in files edited from scripts on Windows | non-UTF-8 default encoding | always open files with `encoding="utf-8"`; set `PYTHONUTF8=1` |
| Chroma quietly uses `all-MiniLM-L6-v2` | its default embedding function | we don't use Chroma; if you ever do, always pass Gemini embeddings |
| Model keeps calling tools, never answers | tools + JSON response schema in one call | final answer as a `submit_answer` tool |
| `Cannot send a request, as the client has been closed` | concurrent first calls built extra clients that got garbage-collected | one client, created under a lock (`app/llm.py`) |
| `429 RESOURCE_EXHAUSTED` | Vertex quota under parallel load | SDK retries with backoff; eval runs 2 questions at a time |
