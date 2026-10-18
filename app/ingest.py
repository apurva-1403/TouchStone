"""Ingestion: raw dataset -> chunks (CHUNK_SCHEMA.md) -> Gemini embeddings -> index/.

    python -m app.ingest              # chunk + embed (needs ADC)
    python -m app.ingest --no-embed   # chunk only; retrieval falls back to BM25

Embeddings from a previous build are reused for chunks whose text is unchanged.
"""
import argparse
import hashlib
import json
import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone

import numpy as np

from app import config
from app.classify import classify_records
from app.kb import ID_FIELD, Directory, directory, load_sources
from app.schema import SCHEMA_VERSION, Chunk, Signals

# Ticket category -> business domain (role grants are per domain); other records use their department.
CATEGORY_DOMAIN = {
    **dict.fromkeys(["access", "privileged-access", "security-incident", "secrets", "access-review", "contractor-access",
                     "mfa", "account", "vpn", "governance"], "security"),
    **dict.fromkeys(["finance-query", "expenses", "purchase-request"], "finance"),
    **dict.fromkeys(["hr-query", "onboarding", "offboarding", "hr-systems", "performance", "learning", "compensation",
                     "leave"], "hr"),
    "deal-desk": "commercial", "legal-review": "legal",
}
DEPARTMENT_DOMAIN = {"DEPT-02": "security", "DEPT-03": "commercial", "DEPT-04": "hr", "DEPT-05": "finance", "DEPT-08": "legal"}

MAX_CHARS = 1600  # target upper bound for a section-packed chunk
MIN_CHARS = 300  # sections smaller than this are merged with the next one
OPEN_STATUSES = {"open", "in_progress", "on_hold"}


# ---------------------------------------------------------------- text helpers

def _d(s: str | None) -> str | None:
    return s[:10] if s else None


def _days_since(iso: str) -> int:
    return (config.TODAY - date.fromisoformat(iso)).days


def split_sections(markdown: str) -> tuple[str, list[tuple[str, str]]]:
    """Splits markdown into (preamble, [(heading, body)]) on '## ' headings."""
    preamble, sections, heading, buf = [], [], None, []
    for line in markdown.splitlines():
        if line.startswith("## "):
            if heading is not None:
                sections.append((heading, "\n".join(buf).strip()))
            heading, buf = line[3:].strip(), []
        elif heading is None:
            if not line.startswith("# "):  # drop the H1 title; we prefix our own
                preamble.append(line)
        else:
            buf.append(line)
    if heading is not None:
        sections.append((heading, "\n".join(buf).strip()))
    return "\n".join(preamble).strip(), sections


def _split_long(heading: str, body: str) -> list[tuple[str, str]]:
    """Splits an oversized section on blank lines into roughly MAX_CHARS pieces."""
    if len(body) <= MAX_CHARS:
        return [(heading, body)]
    pieces, buf = [], ""
    for para in re.split(r"\n\s*\n", body):
        if buf and len(buf) + len(para) > MAX_CHARS:
            pieces.append(buf)
            buf = ""
        buf = f"{buf}\n\n{para}" if buf else para
    if buf:
        pieces.append(buf)
    return [(heading if i == 0 else f"{heading} (cont.)", p) for i, p in enumerate(pieces)]


def pack_sections(sections: list[tuple[str, str]]) -> list[tuple[list[str], str]]:
    """Greedily packs consecutive sections into chunks of about MAX_CHARS."""
    packs, heads, body = [], [], ""
    for h, b in (piece for sec in sections for piece in _split_long(*sec)):
        piece = f"## {h}\n{b}"
        if heads and len(body) >= MIN_CHARS and len(body) + len(piece) > MAX_CHARS:
            packs.append((heads, body))
            heads, body = [], ""
        heads.append(h)
        body = f"{body}\n\n{piece}" if body else piece
    if heads:
        packs.append((heads, body))
    return packs


# ---------------------------------------------------------------- mention detection

class Mentions:
    """Finds policies, systems and people mentioned by name in free text."""

    def __init__(self, d: Directory, policies: list[dict]):
        self.policy_titles = {p["title"].lower(): p["policy_id"] for p in policies}
        self.systems = {s["name"].lower(): sid for sid, s in d.systems.items()}
        self.people = {e["name"].lower(): eid for eid, e in d.employees.items()}
        # A role title counts as a mention only when exactly one person holds it
        # (e.g. "Data Protection Officer"), so generic roles like "SRE" don't match.
        role_holders = defaultdict(list)
        for eid, e in d.employees.items():
            for part in re.split(r"\s*&\s*|\s*,\s*", e["role"]):
                if len(part.split()) >= 2:
                    role_holders[part.lower()].append(eid)
        self.roles = {r: ids[0] for r, ids in role_holders.items() if len(ids) == 1}

    @staticmethod
    def _find(text: str, table: dict[str, str]) -> list[str]:
        return sorted({v for k, v in table.items() if k in text})

    def policies(self, text: str) -> list[str]:
        return self._find(text.lower(), self.policy_titles)

    def systems_in(self, text: str) -> list[str]:
        return self._find(text.lower(), self.systems)

    def employees(self, text: str) -> list[str]:
        t = text.lower()
        return sorted(set(self._find(t, self.people)) | set(self._find(t, self.roles)))


# ---------------------------------------------------------------- per-source conversion

def _base(rec: dict, source_type: str) -> dict:
    m = rec["metadata"]
    return {
        "record_id": rec[ID_FIELD[source_type]],
        "source_type": source_type,
        "source_system": m["source_system"],
        "department_id": m["department"],
        "sensitivity": m["sensitivity"],
        "created_date": m["created_date"],
        "last_referenced_date": m.get("last_referenced_date"),
        "event_id": rec.get("event_id"),
        "referenced_ids": [i for i in rec.get("referenced_ids", []) if not i.startswith("EVT-")],
        "related_system_ids": list(rec.get("related_system_ids", [])),
        "related_policy_ids": list(rec.get("related_policy_ids", [])),
    }


def convert_policy(p: dict, d: Directory):
    base = _base(p, "policy")
    lead = d.team_lead(p["owner_team_id"])
    base.update(
        last_updated=p["last_updated"],
        owner_employee_ids=[lead] if lead else [],
        owner_team_id=p["owner_team_id"],
        status=p["status"],
        kind=p["version"],
        related_system_ids=p["related_system_ids"],
    )
    preamble, sections = split_sections(p["full_text"])
    head = f"{p['title']} ({p['version']}, last updated {p['last_updated']})\n{preamble}".strip()
    parts = [(f"{p['title']} — {' / '.join(h)}", f"{head}\n\n{body}") for h, body in pack_sections(sections)]
    return base, parts or [(p["title"], head)]


def convert_confluence(doc: dict, d: Directory):
    base = _base(doc, "confluence")
    base.update(
        last_updated=doc["last_updated"],
        owner_employee_ids=doc["author_employee_ids"],
        participant_employee_ids=list(doc["author_employee_ids"]),
        status="active",
        kind=doc["doc_type"],
    )
    authors = ", ".join(d.name(a) for a in doc["author_employee_ids"])
    preamble, sections = split_sections(doc["body"])
    head = (f"{doc['title']} (Confluence {doc['space']} · {doc['doc_type']} · by {authors} · "
            f"last updated {doc['last_updated']})\n{preamble}").strip()
    parts = [(f"{doc['title']} — {' / '.join(h)}", f"{head}\n\n{body}") for h, body in pack_sections(sections)]
    return base, parts or [(doc["title"], head)]


def _notes(work_notes) -> str:
    if not work_notes:
        return ""
    if isinstance(work_notes, str):
        return work_notes
    out = []
    for n in work_notes:
        if isinstance(n, dict):
            who = n.get("author_name") or n.get("author") or n.get("by") or ""
            when = n.get("date") or n.get("ts") or ""
            out.append(f"{when} {who}: {n.get('note') or n.get('text') or n.get('body') or ''}".strip())
        else:
            out.append(str(n))
    return "\n".join(out)


def convert_ticket(t: dict, d: Directory):
    base = _base(t, "ticket")
    owner = t.get("assigned_to_employee_id") or t.get("requester_employee_id")
    base.update(
        last_updated=_d(t.get("resolved_date")) or t["created_date"],
        owner_employee_ids=[owner] if owner else [],
        participant_employee_ids=list(dict.fromkeys(
            x for x in [t.get("requester_employee_id"), t.get("on_behalf_of_employee_id"),
                        t.get("assigned_to_employee_id"), *t.get("approver_employee_ids", [])] if x)),
        status=t["status"],
        kind=t["ticket_type"],
        category=t["category"],
    )
    lines = [
        f"ServiceNow {t['ticket_type']} {t['ticket_id']} · category {t['category']} · status {t['status']} · priority {t['priority']}",
        f"Subject: {t['subject']}",
        f"Requester: {t['requester_name']} ({t['department']}) · Assigned to: {t.get('assigned_to_name') or '-'} "
        f"({t.get('assignment_group') or '-'}) · Created {t['created_date']} · Resolved {t.get('resolved_date') or '-'}",
        f"Description: {t['description']}",
    ]
    if t.get("resolution"):
        lines.append(f"Resolution: {t['resolution']}")
    if notes := _notes(t.get("work_notes")):
        lines.append(f"Work notes:\n{notes}")
    return base, [(t["subject"], "\n".join(lines))]


def _recipient(r: str, d: Directory) -> str:
    return d.name(r) if r in d.employees else r


def convert_email(e: dict, d: Directory):
    base = _base(e, "email")
    msgs = e["messages"]
    senders = list(dict.fromkeys(m["from_employee_id"] for m in msgs))
    base.update(
        created_date=_d(msgs[0]["date"]),
        last_updated=_d(msgs[-1]["date"]),
        owner_employee_ids=senders,
        participant_employee_ids=list(e["participant_employee_ids"]),
        status=None,
        kind="email",
    )
    body = [f"Email thread: {e['subject']}"]
    for m in msgs:
        to = ", ".join(_recipient(r, d) for r in m["to"])
        body.append(f"--- From {m['from_name']} to {to} on {m['date']}:\n{m['body']}")
    return base, [(e["subject"], "\n".join(body))]


def convert_slack(s: dict, d: Directory):
    base = _base(s, "slack")
    msgs = s["messages"]
    base.update(
        created_date=_d(msgs[0]["ts"]),
        last_updated=_d(msgs[-1]["ts"]),
        owner_employee_ids=list(dict.fromkeys(m["employee_id"] for m in msgs)),
        participant_employee_ids=list(s["participant_employee_ids"]),
        status=None,
        kind=s["channel"],
    )
    body = [f"Slack conversation in {s['channel']} ({msgs[0]['ts'][:10]})"]
    body += [f"[{m['ts']}] {m['name']}: {m['text']}" for m in msgs]
    return base, [(f"{s['channel']} · {msgs[0]['ts'][:10]}", "\n".join(body))]


CONVERTERS = {
    "policy": convert_policy,
    "confluence": convert_confluence,
    "ticket": convert_ticket,
    "email": convert_email,
    "slack": convert_slack,
}


# ---------------------------------------------------------------- build

def build_chunks(classify: bool = True) -> list[Chunk]:
    d = directory()
    sources = load_sources()
    mentions = Mentions(d, sources["policy"])
    categories = {t["ticket_id"]: t["category"] for t in sources["ticket"]}

    # Pass 1: convert records and detect mentions over the whole record text.
    records = []  # (base, parts, mentioned_employee_ids)
    for st, recs in sources.items():
        for rec in recs:
            base, parts = CONVERTERS[st](rec, d)
            full = "\n".join(text for _, text in parts)
            own_id = base["record_id"]
            base["related_policy_ids"] = sorted(
                (set(base["related_policy_ids"]) | set(mentions.policies(full))) - {own_id})
            base["related_system_ids"] = sorted(set(base["related_system_ids"]) | set(mentions.systems_in(full)))
            records.append((base, parts, mentions.employees(full)))

    # Reverse links: who mentions/references each record, and open update requests against it.
    by_id = {b["record_id"]: b for b, _, _ in records}
    inbound = defaultdict(set)
    open_requests = defaultdict(set)
    for b, _, _ in records:
        for target in set(b["referenced_ids"]) | set(b["related_policy_ids"]):
            if target in by_id and target != b["record_id"]:
                inbound[target].add(b["record_id"])
        is_update_request = (b["source_type"] == "ticket" and b["status"] in OPEN_STATUSES
                             and categories[b["record_id"]] == "policy-update")
        if is_update_request:
            for target in set(b["referenced_ids"]) | set(b["related_policy_ids"]):
                if target.startswith(("POL-", "DOC-")):
                    open_requests[target].add(b["record_id"])

    # Personal-data check (policies are generic documents and are skipped).
    texts = {b["record_id"]: "\n".join(t for _, t in parts) for b, parts, _ in records if b["source_type"] != "policy"}
    verdicts = classify_records(texts) if classify else {}

    # Pass 2: signals + chunk objects.
    chunks = []
    for base, parts, mentioned in records:
        rid = base["record_id"]
        v = verdicts.get(rid, {})
        base["personal_data"] = bool(v.get("personal_data"))
        base["personal_data_category"] = v.get("category") if base["personal_data"] else None
        base["data_domain"] = (CATEGORY_DOMAIN.get(base.get("category") or "")
                               or DEPARTMENT_DOMAIN.get(base["department_id"], "general"))
        base["confidential"] = base["sensitivity"] == "restricted" or base["personal_data"]
        reasons = (["labelled restricted at source"] if base["sensitivity"] == "restricted" else [])
        if base["personal_data"]:
            reasons.append(f"personal data ({v['category']}): {v['reason']}")
        base["confidential_reason"] = "; ".join(reasons) or None
        later = sorted(r for r in inbound[rid] if by_id[r]["last_updated"] > base["last_updated"])
        signals = Signals(
            days_since_update=_days_since(base["last_updated"]),
            owners_inactive=[o for o in base["owner_employee_ids"] if not d.is_active(o)],
            inactive_people_mentioned=[p for p in mentioned if not d.is_active(p)],
            open_update_request_ids=sorted(open_requests[rid]),
            later_mention_ids=later,
        )
        for i, (title, text) in enumerate(parts):
            chunks.append(Chunk(chunk_id=f"{rid}#{i}", chunk_index=i, title=title, text=text,
                                signals=signals, **base))
    return chunks


# ---------------------------------------------------------------- embeddings

def _text_hash(text: str) -> str:
    key = f"{config.EMBEDDING_MODEL}|{config.EMBEDDING_DIM}|{text}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()


def normalise(m: np.ndarray) -> np.ndarray:
    return m / np.clip(np.linalg.norm(m, axis=1, keepdims=True), 1e-12, None)


def embed_texts(texts: list[str], task_type: str) -> np.ndarray:
    from google.genai import types

    from app import llm

    cfg = types.EmbedContentConfig(task_type=task_type, output_dimensionality=config.EMBEDDING_DIM)

    # One text per request: gemini-embedding-2 merges a list of contents into a single
    # embedding rather than returning one per item, so batching silently gives wrong results.
    # Retries/backoff come from the shared client (app/llm.py); a second retry loop here would stack with it.
    def one(t: str) -> list[float]:
        r = llm.client().models.embed_content(model=config.EMBEDDING_MODEL, contents=t, config=cfg)
        return r.embeddings[0].values

    if len(texts) == 1:  # query path: skip the thread pool
        return normalise(np.asarray([one(texts[0])], dtype=np.float32))
    with ThreadPoolExecutor(max_workers=8) as pool:
        vecs = list(pool.map(one, texts))
    return normalise(np.asarray(vecs, dtype=np.float32))


def _load_previous() -> dict[str, np.ndarray]:
    try:
        manifest = json.loads((config.INDEX_DIR / "manifest.json").read_text(encoding="utf-8"))
        emb = np.load(config.INDEX_DIR / "embeddings.npy")
    except (FileNotFoundError, ValueError):
        return {}
    return {h: emb[i] for i, h in enumerate(manifest.get("text_hashes", []))}


def write_index(chunks: list[Chunk], embed: bool):
    config.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    hashes = [_text_hash(c.text) for c in chunks]
    emb = None
    if embed:
        previous = _load_previous()
        todo = [i for i, h in enumerate(hashes) if h not in previous]
        print(f"embedding {len(todo)} new chunks ({len(chunks) - len(todo)} reused)")
        fresh = embed_texts([chunks[i].text for i in todo], "RETRIEVAL_DOCUMENT") if todo else None
        emb = np.zeros((len(chunks), config.EMBEDDING_DIM), dtype=np.float32)
        fresh_i = {i: k for k, i in enumerate(todo)}
        for i, h in enumerate(hashes):
            emb[i] = fresh[fresh_i[i]] if i in fresh_i else previous[h]
        np.save(config.INDEX_DIR / "embeddings.npy", emb)

    with open(config.INDEX_DIR / "chunks.jsonl", "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(c.model_dump_json() + "\n")
    counts = defaultdict(int)
    for c in chunks:
        counts[c.source_type] += 1
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "embedding_model": config.EMBEDDING_MODEL if embed else None,
        "embedding_dim": config.EMBEDDING_DIM if embed else None,
        "n_chunks": len(chunks),
        "n_records": len({c.record_id for c in chunks}),
        "chunks_by_source": dict(counts),
        "text_hashes": hashes if embed else [],
    }
    (config.INDEX_DIR / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    if not embed:
        (config.INDEX_DIR / "embeddings.npy").unlink(missing_ok=True)
    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-embed", action="store_true", help="skip Gemini embeddings (BM25-only index)")
    ap.add_argument("--no-classify", action="store_true",
                    help="skip the personal-data check (only labelled-restricted records are confidential)")
    args = ap.parse_args()
    chunks = build_chunks(classify=not args.no_classify)
    m = write_index(chunks, embed=not args.no_embed)
    print({k: v for k, v in m.items() if k != "text_hashes"})


if __name__ == "__main__":
    main()
