"""Access audit log (POL-36 §5): who asked what, which confidential records they were shown and under which rule.

Each entry is printed as one JSON line, which Cloud Run ships to Cloud Logging as a structured log
(query: jsonPayload.log="touchstone-audit"). The most recent entries are also kept in memory per instance for the
in-app view available to compliance auditors.
"""
import json
import threading
from collections import deque
from datetime import datetime, timezone

_recent: deque = deque(maxlen=500)
_lock = threading.Lock()


def record(entry: dict):
    entry = {"log": "touchstone-audit", "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), **entry}
    with _lock:
        _recent.appendleft(entry)
    print(json.dumps({"severity": "NOTICE" if entry.get("flagged") else "INFO", **entry}, ensure_ascii=False), flush=True)


def recent(limit: int = 200) -> list[dict]:
    with _lock:
        return list(_recent)[:limit]
