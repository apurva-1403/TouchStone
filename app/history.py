"""Per-employee chat history: conversations, not single questions.

Stored in Firestore at users/{employee_id}/chats/{chat_id}, so chats survive restarts and follow the employee across
devices and Cloud Run instances. Falls back to in-memory storage when Firestore isn't reachable (offline dev).

Each turn stores the question, the answer as it was returned, the IDs of every record the agent was shown while
answering, and a fingerprint of the user's access scope at the time. When a chat is reopened (`visible_turns`), an
answer is shown again only if the user still has the same scope and can still see every one of those records;
otherwise only the question is shown and the user is asked to re-ask it. So a later loss of access can't be bypassed
by reopening an old answer.
"""
import hashlib
import logging
import threading
import uuid
from collections import OrderedDict, defaultdict
from datetime import datetime, timezone

from app import config

MAX_CHATS = 50  # per employee, in listings
MAX_TURNS = 30  # per chat; older turns are dropped
TIMEOUT_S = 5  # history is a convenience: never let a slow Firestore stall an answer
SUMMARY_FIELDS = ["title", "created_at", "updated_at", "turn_count", "flags"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def scope_key(principal) -> str:
    """Fingerprint of everything that decides what this employee may see."""
    parts = [principal.department_id, principal.team_id, principal.employment_type, ",".join(sorted(principal.roles)),
             ",".join(sorted(principal.hrbp_department_ids)), ",".join(sorted(principal.reports))]
    return hashlib.sha1("|".join(parts).encode()).hexdigest()[:16]


class _Memory:
    def __init__(self):
        self._chats: dict[str, OrderedDict] = defaultdict(OrderedDict)
        self._lock = threading.Lock()

    def get(self, employee_id: str, chat_id: str) -> dict | None:
        with self._lock:
            c = self._chats[employee_id].get(chat_id)
            return dict(c) if c else None

    def put(self, employee_id: str, chat_id: str, chat: dict):
        with self._lock:
            self._chats[employee_id][chat_id] = chat
            self._chats[employee_id].move_to_end(chat_id, last=False)

    def list(self, employee_id: str, limit: int) -> list[dict]:
        with self._lock:
            chats = sorted(self._chats[employee_id].items(), key=lambda kv: kv[1]["updated_at"], reverse=True)
            return [{"chat_id": k, **{f: v.get(f) for f in SUMMARY_FIELDS}} for k, v in chats[:limit]]

    def delete(self, employee_id: str, chat_id: str):
        with self._lock:
            self._chats[employee_id].pop(chat_id, None)

    def clear(self, employee_id: str):
        with self._lock:
            self._chats.pop(employee_id, None)


class _Firestore:
    def __init__(self):
        from google.cloud import firestore
        self._db = firestore.Client(project=config.GCP_PROJECT)
        self._desc = firestore.Query.DESCENDING

    def _col(self, employee_id: str):
        return self._db.collection("users").document(employee_id).collection("chats")

    def get(self, employee_id: str, chat_id: str) -> dict | None:
        snap = self._col(employee_id).document(chat_id).get(timeout=TIMEOUT_S)
        return snap.to_dict() if snap.exists else None

    def put(self, employee_id: str, chat_id: str, chat: dict):
        self._col(employee_id).document(chat_id).set(chat, timeout=TIMEOUT_S)

    def list(self, employee_id: str, limit: int) -> list[dict]:
        q = self._col(employee_id).select(SUMMARY_FIELDS).order_by("updated_at", direction=self._desc).limit(limit)
        return [{"chat_id": d.id, **d.to_dict()} for d in q.stream(timeout=TIMEOUT_S)]

    def delete(self, employee_id: str, chat_id: str):
        self._col(employee_id).document(chat_id).delete(timeout=TIMEOUT_S)

    def clear(self, employee_id: str):
        for d in self._col(employee_id).select([]).limit(500).stream(timeout=TIMEOUT_S):
            d.reference.delete(timeout=TIMEOUT_S)


_store = None
_store_lock = threading.Lock()


def store():
    global _store
    if _store is None:
        with _store_lock:
            if _store is None:
                try:
                    _store = _Firestore()
                    _store.list("healthcheck", 1)
                except Exception as e:  # history is a convenience; never break answering because of it
                    logging.warning("Firestore unavailable, using in-memory history: %s", e)
                    _store = _Memory()
    return _store


def get_chat(employee_id: str, chat_id: str) -> dict | None:
    try:
        return store().get(employee_id, chat_id)
    except Exception as e:
        logging.warning("could not read chat: %s", e)
        return None


def save_turn(employee_id: str, chat_id: str | None, question: str, response: dict, flags: list[str],
              record_ids: list[str], scope: str) -> str:
    """Appends a turn to the chat (creating it if needed) and returns the chat_id. Never raises."""
    chat = get_chat(employee_id, chat_id) if chat_id else None
    if chat is None:
        chat_id = uuid.uuid4().hex[:16]
        chat = {"title": question[:120], "created_at": _now(), "turns": [], "flags": []}
    chat["turns"] = (chat.get("turns", []) + [{
        "question": question[:1000], "asked_at": _now(), "flags": flags,
        "response": response, "record_ids": record_ids, "scope": scope,
    }])[-MAX_TURNS:]
    chat["updated_at"] = _now()
    chat["turn_count"] = len(chat["turns"])
    chat["flags"] = sorted({f for t in chat["turns"] for f in t.get("flags", [])})
    try:
        store().put(employee_id, chat_id, chat)
    except Exception as e:
        logging.warning("could not save chat: %s", e)
    return chat_id


def visible_turns(chat: dict, scope: str, may_see) -> list[dict]:
    """The chat's turns for the current user: each with `response` only if it is still safe to show."""
    out = []
    for t in chat.get("turns", []):
        ok = t.get("scope") == scope and all(may_see(rid) for rid in t.get("record_ids", []))
        out.append({"question": t["question"], "asked_at": t["asked_at"], "flags": t.get("flags", []),
                    "response": t.get("response") if ok else None})
    return out


def list_chats(employee_id: str, limit: int = MAX_CHATS) -> list[dict]:
    try:
        return store().list(employee_id, limit)
    except Exception as e:
        logging.warning("could not list chats: %s", e)
        return []


def delete_chat(employee_id: str, chat_id: str):
    store().delete(employee_id, chat_id)


def clear(employee_id: str):
    store().clear(employee_id)
