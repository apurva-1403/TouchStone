# Prototype benchmarks: how each number was measured

This file backs up the **Prototype Performance report / Benchmarking** slide. Every number comes from the project's
own test scripts, run against the real system (Gemini on Vertex AI, the full 1,897-record index). The raw outputs are
saved in [`docs/benchmarks/`](benchmarks/), so anyone can check the arithmetic.

| Slide number | What it means | Source run |
|---|---|---|
| **~17 s** typical answer | Median time to answer one question | 18 Oct 2026 |
| **3.9× faster** | Median before tuning ÷ median after tuning | 8 Oct vs 18 Oct |
| **93%** right policy found | Governing policy in the top 8 search results, 25 of 27 questions | 18 Oct 2026 |
| **6 / 8** flags correct | Demo questions where the drift and conflict flags were both right | 18 Oct 2026 |
| **70 / 70** access checks | Automated security and access tests that passed | 18 Oct 2026 |

---

## 1. Answer time (~17 s) and speed-up (3.9×)

**Script:** `python -m scripts.eval_agent --workers 1` asks the 8 demo questions one at a time and times each
complete answer: search, every Gemini call, tool calls and the checks in code.

### After tuning (18 Oct 2026), raw: [`benchmarks/agent_2026-10-18.json`](benchmarks/agent_2026-10-18.json)

| Question | Seconds |
|---|---:|
| DQ-25 Leave carry-forward | 4.2 |
| OUTAGE March API outage | 4.8 |
| DQ-18 Admin Console access | 11.8 |
| DQ-05 Snowflake PII approver | 16.6 |
| DQ-03 Change request to deploy | 18.1 |
| DQ-14 VPN 30-minute drops | 18.5 |
| DQ-07 Expense claim deadline | 19.4 |
| DQ-01 Salesforce access | 21.0 |

```
8 answers, sorted. The median is the average of the two middle values (4th and 5th):
median  = (16.6 + 18.1) / 2 = 17.35 s  →  "~17 s"
slowest = 21.0 s
```

### Before tuning (8 Oct 2026), same 8 questions on the same model (gemini-3.8-flash)

Raw: [`benchmarks/agent_2026-10-08_before.txt`](benchmarks/agent_2026-10-08_before.txt) (the `gemini-3.8-flash` block),
recorded before pre-retrieval and the backup model were added (see [`BUILD_GUIDE.md`](BUILD_GUIDE.md) §4.15):

```
sorted: 7.0, 40.1, 50.0, 63.4, 71.3, 78.6, 103.5, 125.9
median  = (63.4 + 71.3) / 2 = 67.35 s  →  "67 s"
slowest = 125.9 s
```

### Speed-up

```
typical answer: 67.35 / 17.35 = 3.88  →  "3.9× faster"
slowest answer: 125.9 / 21.0  = 6.0×
```

**What changed between the two runs:**
- **Pre-retrieval:** the first search runs before the model is called, saving a full model round trip.
- **Hedged calls:** if the main model hasn't replied within 8 s, the same call also goes to `gemini-2.5-flash`, and the
  first reply wins. In the 18 Oct run, 4 of 8 answers came from the backup model.
- **Shorter answers:** at most 90 words, so the final call is faster.

**Correction:** earlier versions of the deck and video said "71 s, 4.3× faster". The evaluation script prints
the *upper* middle value as its "median" (71.3 s for 8 answers). The true median is 67.35 s, so the correct
figures are **67 s and 3.9×**. The deck and the video now use these.

**Caveat:** times depend on Gemini's response time on the day, so they vary between runs.

---

## 2. Right policy found (93%)

**Script:** `python -m scripts.eval_retrieval --k 8`
Raw: [`benchmarks/retrieval_2026-10-18.txt`](benchmarks/retrieval_2026-10-18.txt)

For each of the 27 test questions in `data/demo_queries.json`, the test checks whether the *governing* policy (the
answer key names it) appears in the top 8 search results.

```
found for 25 of 27 questions
25 / 27 = 0.926  →  "93%"
missed: DQ-14 (VPN drops) and DQ-19 (Jira project)
```

Search here is the hybrid search the app uses: keyword (BM25) plus Gemini embeddings, combined by reciprocal rank
fusion. The answer key is used only by this test, never by the app.

---

## 3. Flags correct (6 / 8)

**Script:** the same `eval_agent` run as section 1. Raw: [`benchmarks/agent_2026-10-18.txt`](benchmarks/agent_2026-10-18.txt)

Each demo question has an expected answer for two flags: **policy differs from practice** (drift) and
**conflicting past answers**. A question counts as correct only if **both** flags match.

| Question | Drift flag | Conflict flag | Both right? |
|---|---|---|---|
| DQ-01 Salesforce access | missed | ok | ✗ |
| DQ-03 Change request | ok | ok | ✓ |
| DQ-05 Snowflake PII | ok | ok | ✓ |
| DQ-07 Expense deadline | ok | ok | ✓ |
| DQ-14 VPN drops | ok | ok | ✓ |
| DQ-18 Admin Console | ok | missed | ✗ |
| DQ-25 Leave carry-forward | ok | ok | ✓ |
| OUTAGE March outage | ok | ok | ✓ |

```
6 of 8 correct  →  "6 / 8"
```

Model answers vary from run to run. The same 8 questions scored **8 / 8** on 8 Oct before tuning
([`agent_2026-10-08_before.txt`](benchmarks/agent_2026-10-08_before.txt)) and **7 / 8** after it
([`BUILD_GUIDE.md`](BUILD_GUIDE.md) §4.15). The slide shows today's run and mentions the earlier
range.

---

## 4. Access checks (70 / 70)

**Script:** `python -m scripts.test_access`
Raw: [`benchmarks/access_2026-10-18.txt`](benchmarks/access_2026-10-18.txt)

70 automated checks, each printing `ok` or `FAIL`:

```
ok: 70   FAIL: 0   →  "70 / 70"
```

What they cover:
- **Role and need-to-know rules:** who may see pay, health, leave and security records.
- **Sessions:** forged or edited sessions, the sign-in rate limit, leavers who can't sign in.
- **Leak checks:** search results, linked records and similar cases never include a record outside the asker's scope.
- **Tool refusals:** the agent's tools refuse out-of-scope records.
- **Chats:** chat history stays private to each employee.

---

## How to reproduce

From the project folder, with the virtual environment active:

```
python -m scripts.eval_retrieval --k 8
python -m scripts.test_access
python -m scripts.eval_agent --workers 1 --out docs/benchmarks/agent_<date>.json
```

The cost figure (~₹1 per question) has its own workings in [`COST_PER_QUESTION.md`](COST_PER_QUESTION.md).
