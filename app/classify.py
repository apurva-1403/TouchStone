"""Ingest-time personal-data check (FAST_MODEL, a second Gemini model).

The source `sensitivity` label misses records that are confidential because they contain personal data
(e.g. a named employee's bonus or the reason for their leave). Every non-policy record is checked once;
results are cached in index/personal_data.json by text hash, so re-ingesting only checks changed records.
"""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor

from google.genai import types

from app import config, llm

CLASSIFIER_VERSION = "1"
CACHE_FILE = "personal_data.json"

PROMPT = """You review internal company records before they go into a company-wide search tool.
Decide whether this record contains SENSITIVE PERSONAL DATA about an identifiable employee or person: \
information that person would not expect ordinary colleagues to read.

Counts as sensitive personal data:
- pay, salary, bonus, referral bonus, reimbursement owed to a named person, personal finances or bank details
- health, medical or sickness details; the reason for someone's leave (parental, medical, family, bereavement)
- performance reviews, ratings, improvement plans; disciplinary matters, complaints, investigations
- resignation, termination or exit details beyond the bare fact that someone left
- personal contact details (home address, personal phone or email), government ID numbers, background checks

Does NOT count: names, work email addresses, job titles, team membership, who approved what, ordinary work \
requests (access, laptops, VPN, software), business decisions, incidents, routine expense claims with no \
personal circumstances, the bare fact that someone joined or left.

Record:
---
{text}
---"""

SCHEMA = {
    "type": "object",
    "properties": {
        "personal_data": {"type": "boolean"},
        "category": {"type": "string", "enum": ["none", "pay", "health_or_leave_reason", "performance_or_disciplinary",
                                                 "exit_details", "personal_contact_or_ids", "other"]},
        "reason": {"type": "string", "description": "Under 15 words; do not repeat the personal details themselves."},
    },
    "required": ["personal_data", "category", "reason"],
}


def _key(text: str) -> str:
    return hashlib.sha1(f"{CLASSIFIER_VERSION}|{config.FAST_MODEL}|{text}".encode("utf-8")).hexdigest()


def _classify_one(text: str) -> dict:
    r = llm.client().models.generate_content(
        model=config.FAST_MODEL, contents=PROMPT.format(text=text[:8000]),
        config=types.GenerateContentConfig(response_mime_type="application/json", response_json_schema=SCHEMA,
                                           temperature=0.0))
    return json.loads(r.text)


def classify_records(texts: dict[str, str]) -> dict[str, dict]:
    """record_id -> {"personal_data", "category", "reason"}. Uses and updates the on-disk cache."""
    path = config.INDEX_DIR / CACHE_FILE
    try:
        cache = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        cache = {}
    keys = {rid: _key(t) for rid, t in texts.items()}
    todo = [rid for rid, k in keys.items() if k not in cache]
    print(f"personal-data check: {len(todo)} new records ({len(texts) - len(todo)} cached)")
    with ThreadPoolExecutor(max_workers=8) as pool:
        for rid, verdict in zip(todo, pool.map(lambda r: _classify_one(texts[r]), todo)):
            cache[keys[rid]] = verdict
    config.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    live = {k: cache[k] for k in keys.values()}  # drop entries for records that no longer exist
    path.write_text(json.dumps(live, indent=0, sort_keys=True), encoding="utf-8")
    return {rid: live[k] for rid, k in keys.items()}
