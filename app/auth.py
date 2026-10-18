"""Demo sign-in: pick an employee + shared demo password -> signed, HttpOnly session cookie.

The session carries only the employee_id; scope is always recomputed server-side from the directory
(app/access.py), so the browser can't claim a role or widen its own access.

Secrets come from the environment (never the repo): DEMO_PASSWORD and SESSION_SECRET. Locally they live in
.env (gitignored); on Cloud Run they come from Secret Manager.
"""
import base64
import hashlib
import hmac
import json
import os
import secrets
import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, Response

from app.access import Principal, principal_for

COOKIE = "kc_session"
SESSION_TTL_S = 8 * 3600
MAX_FAILED_LOGINS = 10  # per client IP per window
FAILED_WINDOW_S = 600

_SECRET = (os.getenv("SESSION_SECRET") or "").encode()
if not _SECRET:  # dev fallback: sessions won't survive a restart or span instances
    _SECRET = secrets.token_bytes(32)
_failed: dict[str, deque] = defaultdict(deque)
_failed_lock = threading.Lock()


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _sign(payload: str) -> str:
    return _b64(hmac.new(_SECRET, payload.encode(), hashlib.sha256).digest())


def issue(employee_id: str) -> str:
    payload = _b64(json.dumps({"sub": employee_id, "exp": int(time.time()) + SESSION_TTL_S}).encode())
    return f"{payload}.{_sign(payload)}"


def verify(token: str | None) -> Principal | None:
    if not token or token.count(".") != 1:
        return None
    payload, sig = token.split(".")
    if not hmac.compare_digest(sig, _sign(payload)):
        return None
    try:
        data = json.loads(_unb64(payload))
    except ValueError:
        return None
    if data.get("exp", 0) < time.time():
        return None
    return principal_for(data.get("sub", ""))


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    return fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "?")


def _too_many_failures(ip: str) -> bool:
    now = time.time()
    with _failed_lock:
        q = _failed[ip]
        while q and q[0] < now - FAILED_WINDOW_S:
            q.popleft()
        return len(q) >= MAX_FAILED_LOGINS


def _record_failure(ip: str):
    with _failed_lock:
        _failed[ip].append(time.time())


def login(request: Request, response: Response, employee_id: str, password: str) -> Principal:
    ip = _client_ip(request)
    if _too_many_failures(ip):
        raise HTTPException(status_code=429, detail="Too many failed sign-in attempts. Try again in 10 minutes.")
    expected = os.getenv("DEMO_PASSWORD", "")
    if not expected:
        raise HTTPException(status_code=503, detail="Sign-in is not configured on this server (DEMO_PASSWORD).")
    p = principal_for(employee_id.strip().upper())
    if not p or not hmac.compare_digest(password.encode(), expected.encode()):
        _record_failure(ip)
        raise HTTPException(status_code=401, detail="Wrong employee or password, or this employee has left AlgoWorks.")
    secure = request.headers.get("x-forwarded-proto", request.url.scheme) == "https"
    response.set_cookie(COOKIE, issue(p.employee_id), max_age=SESSION_TTL_S, httponly=True, secure=secure,
                        samesite="lax", path="/")
    return p


def logout(response: Response):
    response.delete_cookie(COOKIE, path="/")


def current_user(request: Request) -> Principal:
    """FastAPI dependency: the signed-in employee, or 401."""
    p = verify(request.cookies.get(COOKIE))
    if not p:
        raise HTTPException(status_code=401, detail="Please sign in.")
    return p
