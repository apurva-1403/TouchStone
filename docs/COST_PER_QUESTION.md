# Cost per question: how "about ₹1" is calculated

**Result: about ₹1 per question** (₹1.04 average, ₹1.00 median, ₹0.73 to ₹1.51 across the six measured answers).
Worked out on 17 Oct 2026.

## 1. What a question costs

Answering one question uses one main paid item: **Gemini 3.8 Flash tokens**, which is the agent that reads the evidence and
writes the answer. Every answer records how many tokens it used (`meta.input_tokens` and `meta.output_tokens` in the
`/api/chat` response).

- **Input tokens:** the system prompt, the question, the search results and any records the agent opens. This is the
  bulk, roughly 8,000 to 19,000 per question.
- **Output tokens:** the agent's tool calls and the short answer, roughly 200 to 450 per question.

## 2. Prices used

Gemini 3.8 Flash list prices, as recorded for the submission deck (valid until 31 Dec 2026):

| | Price per 1 million tokens | Price per token |
|---|---|---|
| Input | $0.75 | $0.00000075 |
| Output | $3.75 | $0.00000375 |

**Exchange rate:** ₹95 per US dollar (mid-market, 17 Oct 2026; trackers showed ₹94.96 to ₹95.08).

## 3. The formula

```
cost in $ = input_tokens × 0.75 / 1,000,000  +  output_tokens × 3.75 / 1,000,000
cost in ₹ = cost in $ × 95
```

## 4. Measured answers (live run, 17 Oct 2026)

These are the six demo answers generated today on the real system, with the token counts the app recorded.

| # | Question (asked as) | Input tokens | Output tokens | Input cost | Output cost | Total $ | Total ₹ |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Do I need a change request to deploy? (engineer) | 11,680 | 450 | $0.00876 | $0.00169 | $0.01045 | ₹0.99 |
| 2 | And for infrastructure changes? (follow-up) | 11,606 | 262 | $0.00870 | $0.00098 | $0.00969 | ₹0.92 |
| 3 | Has the VPN 30-minute drop been solved? | 18,911 | 464 | $0.01418 | $0.00174 | $0.01592 | ₹1.51 |
| 4 | Who approves Snowflake PII access? | 12,008 | 406 | $0.00901 | $0.00152 | $0.01053 | ₹1.00 |
| 5 | Referral bonus problems? (engineer) | 14,666 | 202 | $0.01100 | $0.00076 | $0.01176 | ₹1.12 |
| 6 | Referral bonus problems? (HR partner) | 7,988 | 442 | $0.00599 | $0.00166 | $0.00765 | ₹0.73 |
| | **Average** | **12,810** | **371** | | | **$0.0110** | **₹1.04** |
| | **Median** | 11,844 | 424 | | | $0.0105 | ₹1.00 |

Worked example, question 1:

```
11,680 × 0.75 / 1,000,000 = $0.00876
   450 × 3.75 / 1,000,000 = $0.00169
                    total = $0.01045  ×  95  =  ₹0.99
```

The average ($0.0110) matches the $0.011 on the deck's cost slide, which came from the earlier evaluation runs (median
11.6k input and 0.4k output tokens). That's why the video says **about ₹1**, not "under ₹1": at today's rate the average
is just over ₹1.

## 5. What is not in this figure

- **Small extra Gemini calls**, not itemised here:
  - the question's embedding (a few dozen tokens);
  - `gemini-3.5-flash-lite` comparing similar past tickets;
  - the occasional backup call to `gemini-2.5-flash` when the main model is slow.

  These are much smaller than the agent's token use. They are why the per-question figure is best quoted as "about ₹1"
  rather than to the paisa.
- **Thinking tokens:** the agent runs with a low thinking setting. If any thinking tokens are billed but not included in
  `output_tokens`, the real cost is slightly higher.
- **Infrastructure:** Cloud Run, Firestore, Cloud Logging and Secret Manager fall within Google Cloud's free tiers at
  pilot scale, so they're excluded.
- **One-time indexing** of the 1,897 records (embeddings plus personal-data check): under $1 (about ₹95) in total, not per
  question.
- **Repeat questions** are served from the answer cache and cost nothing.

## 6. What it means at company scale

```
1,000 employees × 2 questions per working day × 22 working days = 44,000 questions a month
44,000 × $0.0110 × 95 ≈ ₹46,000 a month (about $484)
```

## 7. How sensitive the number is

| Change | Cost per question |
|---|---|
| ₹90 per $ | ₹0.99 |
| ₹95 per $ (used here) | ₹1.04 |
| ₹100 per $ | ₹1.10 |
| A longer question that opens more records (like #3) | about ₹1.5 |
| Gemini 3.8 Flash list price doubling (noted for 2027) | about ₹2.1 |

## 8. How to re-check it

1. Ask any question in the app and read `meta.input_tokens` and `meta.output_tokens` from the `/api/chat` response
   (browser dev tools → Network).
2. Put them into the formula in section 3 with the current list price and exchange rate.
3. Check the current prices on Google's Vertex AI pricing page before quoting externally.

**Sources for the exchange rate:** [Wise](https://wise.com/us/currency-converter/usd-to-inr-rate),
[XE](https://www.xe.com/en-us/currencyconverter/convert/?Amount=1&From=USD&To=INR),
[BookMyForex](https://www.bookmyforex.com/us-dollar/rates/).
