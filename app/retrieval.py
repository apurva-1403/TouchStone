"""Hybrid retrieval over index/: Gemini embeddings + BM25, fused with reciprocal rank fusion.

Access filtering (app/access.py) happens here, before anything reaches the LLM. Withheld (confidential)
records are reported only as a count plus a contact, never with their text or title.
"""
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np

from app import config
from app.access import Principal, access_contact, can_see
from app.schema import Chunk

RRF_K = 60
# Similar past cases: same ticket category, embedding cosine at or above CASE_SIM, and both among the
# CASE_POOL records most relevant to the query. Measured 27 Sep: known same-problem pairs score 0.90-0.93,
# the median same-category pair 0.85; the query-relevance pool filters out near-duplicate template noise.
CASE_SIM = 0.88
CASE_POOL = 40
MAX_CASE_GROUPS = 2
MAX_CASES_PER_GROUP = 4
_TOKEN = re.compile(r"[a-z0-9]+(?:[-.][a-z0-9]+)*")
_STOP = set("""a an and are as at be but by can do does for from has have how i if in is it its me my of on or
our so that the their them there these this to was we what when where which who why will with you your""".split())


def tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOP]


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.4, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tf = [Counter(d) for d in docs]
        self.len = np.array([len(d) for d in docs], dtype=np.float32)
        self.avg = float(self.len.mean())
        df = Counter(t for d in docs for t in set(d))
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, query: list[str]) -> np.ndarray:
        out = np.zeros(len(self.tf), dtype=np.float32)
        norm = self.k1 * (1 - self.b + self.b * self.len / self.avg)
        for t in set(query):
            idf = self.idf.get(t)
            if idf is None:
                continue
            tf = np.array([d.get(t, 0) for d in self.tf], dtype=np.float32)
            out += idf * tf * (self.k1 + 1) / (tf + norm)
        return out


@dataclass
class Hit:
    chunk: Chunk
    score: float
    via: str = "search"  # "search" or "link:<record_id>"


@dataclass
class SearchResult:
    hits: list[Hit]  # best chunk per record, ranked
    related: list[Hit] = field(default_factory=list)  # linked records pulled in by expansion
    withheld_count: int = 0  # confidential records that would have ranked but this user can't see
    withheld_contacts: list[str] = field(default_factory=list)  # employee_ids to ask for access
    case_groups: list[list[Chunk]] = field(default_factory=list)  # similar past tickets, oldest first


class Retriever:
    def __init__(self):
        with open(config.INDEX_DIR / "chunks.jsonl", encoding="utf-8") as f:
            self.chunks = [Chunk.model_validate_json(line) for line in f]
        self.bm25 = BM25([tokenize(f"{c.title}\n{c.text}") for c in self.chunks])
        emb_path = config.INDEX_DIR / "embeddings.npy"
        self.emb = np.load(emb_path) if emb_path.exists() else None
        self.by_record = defaultdict(list)
        for i, c in enumerate(self.chunks):
            self.by_record[c.record_id].append(i)
        # Link graph from text-derived references only (no event_id: that is a dataset construct).
        self.out_links = defaultdict(set)  # record -> records it references / names
        self.in_links = defaultdict(set)  # record -> records that reference / name it
        for c in self.chunks:
            for t in set(c.referenced_ids) | set(c.related_policy_ids):
                if t in self.by_record and t != c.record_id:
                    self.out_links[c.record_id].add(t)
                    self.in_links[t].add(c.record_id)
        self.links = {r: self.out_links[r] | self.in_links[r] for r in self.by_record}

    def record(self, record_id: str) -> Chunk | None:
        """First chunk of a record: carries the record-level metadata and signals."""
        idx = self.by_record.get(record_id)
        return self.chunks[idx[0]] if idx else None

    def record_text(self, record_id: str) -> str:
        """Full text of a record. Later chunks drop the header they share with the first one."""
        texts = [self.chunks[i].text for i in self.by_record.get(record_id, [])]
        if len(texts) <= 1:
            return texts[0] if texts else ""
        head = texts[0].split("\n\n## ", 1)[0]
        return texts[0] + "".join(t[len(head):] if t.startswith(head) else "\n\n" + t for t in texts[1:])

    @property
    def dense(self) -> bool:
        return self.emb is not None

    def _embed_query(self, query: str) -> np.ndarray:
        from app.ingest import embed_texts
        return embed_texts([query], "RETRIEVAL_QUERY")[0]

    def _fused(self, query: str) -> np.ndarray:
        """RRF score per chunk over all chunks (access filtering is applied afterwards)."""
        rankings = [self.bm25.scores(tokenize(query))]
        if self.dense:
            rankings.append(self.emb @ self._embed_query(query))
        fused = np.zeros(len(self.chunks), dtype=np.float32)
        for s in rankings:
            ranks = np.empty(len(s), dtype=np.int64)
            ranks[np.argsort(-s)] = np.arange(len(s))
            fused += 1.0 / (RRF_K + ranks + 1)
        return fused

    def _best_per_record(self, fused: np.ndarray, idx) -> list[Hit]:
        best: dict[str, Hit] = {}
        for i in idx:
            c = self.chunks[i]
            if c.record_id not in best or fused[i] > best[c.record_id].score:
                best[c.record_id] = Hit(c, float(fused[i]))
        return sorted(best.values(), key=lambda h: -h.score)

    def search(self, query: str, principal: Principal, k: int = 8, expand: int = 6,
               policy_slots: int = 2) -> SearchResult:
        """Top-k records, with `policy_slots` of them reserved for the best-matching policies so the
        agent always has the written rule to compare practice against."""
        fused = self._fused(query)
        visible = [i for i, c in enumerate(self.chunks) if can_see(principal, c)]
        hidden = [i for i, c in enumerate(self.chunks) if not can_see(principal, c)]
        ranked = self._best_per_record(fused, visible)
        policies = [h for h in ranked if h.chunk.source_type == "policy"][:policy_slots]
        others = [h for h in ranked if h not in policies][:k - len(policies)]
        hits = sorted(policies + others, key=lambda h: -h.score)

        # Confidential records that would have made the cut: report count + who to ask, nothing else.
        # Access is granted by the owning department's head (the data owner), not the record's authors.
        cutoff = others[-1].score if others else 0.0
        hidden_hits = [h for h in self._best_per_record(fused, hidden) if h.score >= cutoff]
        contacts = []
        for h in hidden_hits:
            c = access_contact(h.chunk)
            if c and c not in contacts:
                contacts.append(c)

        related = self._expand(hits, fused, principal, expand) if expand else []
        groups = self._case_groups(hits + related, ranked) if self.dense else []
        return SearchResult(hits, related, len(hidden_hits), contacts, groups)

    def _case_groups(self, seeds: list[Hit], ranked: list[Hit]) -> list[list[Chunk]]:
        """Groups each retrieved ticket with similar past tickets (see CASE_SIM). Deterministic: the
        agent gets same-problem cases side by side instead of having to notice them itself."""
        pool = [h.chunk for h in ranked[:CASE_POOL] if h.chunk.source_type == "ticket"]
        vec = lambda c: self.emb[self.by_record[c.record_id][0]]
        groups, used = [], set()
        for seed in (h.chunk for h in seeds if h.chunk.source_type == "ticket"):
            if seed.record_id in used:
                continue
            sims = [(float(vec(seed) @ vec(c)), c) for c in pool
                    if c.record_id != seed.record_id and c.record_id not in used and c.category == seed.category]
            members = [c for sim, c in sorted(sims, key=lambda x: -x[0]) if sim >= CASE_SIM][:MAX_CASES_PER_GROUP - 1]
            if members:
                group = sorted([seed] + members, key=lambda c: c.created_date)
                used.update(c.record_id for c in group)
                groups.append(group)
            if len(groups) == MAX_CASE_GROUPS:
                break
        return groups

    def _expand(self, hits: list[Hit], fused: np.ndarray, principal: Principal, n: int) -> list[Hit]:
        """Linked records of the hits. Open update requests against a retrieved policy/doc come first
        (they are the strongest evidence that practice has moved on), then other links by score."""
        seen = {h.chunk.record_id for h in hits}
        priority, cand = [], {}

        def best_visible(rid: str) -> int | None:
            idx = [i for i in self.by_record.get(rid, []) if can_see(principal, self.chunks[i])]
            return max(idx, key=lambda j: fused[j]) if idx else None

        for h in hits:
            for rid in h.chunk.signals.open_update_request_ids:
                i = best_visible(rid)
                if rid not in seen and i is not None:
                    seen.add(rid)
                    priority.append(Hit(self.chunks[i], float(fused[i]), via=f"update-request:{h.chunk.record_id}"))
        for h in hits:
            for rid in self.links[h.chunk.record_id] - seen:
                i = best_visible(rid)
                if i is not None and (rid not in cand or fused[i] > cand[rid].score):
                    cand[rid] = Hit(self.chunks[i], float(fused[i]), via=f"link:{h.chunk.record_id}")
        return (priority + sorted(cand.values(), key=lambda h: -h.score))[:max(n, len(priority))]


@lru_cache(maxsize=1)
def retriever() -> Retriever:
    return Retriever()
