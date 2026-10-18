"""FastAPI entrypoint. Serves the JSON API under /api and the static frontend at /.

Every data endpoint requires a signed-in employee (app/auth.py); what they can see is decided by
app/access.py from the directory, never by anything the browser sends.
"""
import logging
import threading
import time
from collections import OrderedDict, defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import audit, auth, config, history
from app.access import ROLE_CATALOG, Principal, access_basis, can_see
from app.agent import answer_question
from app.kb import directory
from app.retrieval import Hit, retriever
from app.schema import AgentResponse

def _warm_up():
    """Load the index and open the Gemini connection before the first question arrives.
    The first call on a fresh client measured ~10 s vs ~2 s after; this moves that cost off the user."""
    try:
        retriever()._embed_query("warm-up")
        directory()
    except Exception as e:  # warm-up is best effort; requests still work without it
        logging.warning("warm-up failed: %s", e)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    threading.Thread(target=_warm_up, daemon=True).start()
    yield


app = FastAPI(title="TouchStone", lifespan=lifespan)


@app.middleware("http")
async def no_stale_pages(request: Request, call_next):
    """Make browsers revalidate the page files (HTML/CSS/JS) on every load, so a new deploy shows up immediately
    instead of an old cached app.css/ui.js. Unchanged files still come back as a cheap 304 via ETag. API responses
    are never cached (they are per-user)."""
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/api/") else "no-cache"
    return response


@app.get("/api/health")
def health():
    r = retriever()
    return {
        "status": "ok",
        "agent_model": config.AGENT_MODEL,
        "index": {"chunks": len(r.chunks), "dense": r.dense},
        "history_backend": type(history.store()).__name__.strip("_").lower(),  # firestore | memory
    }


# ------------------------------------------------------------------ sign-in

def _employee_card(eid: str) -> dict:
    d = directory()
    e = d.employees[eid]
    return {"employee_id": eid, "name": e["name"], "title": e["role"],
            "department": d.departments[e["department_id"]]["name"], "team": d.teams[e["team_id"]]["name"],
            "employment_type": e.get("employment_type", "employee"), "roles": e.get("access_roles", ["employee"])}


@app.get("/api/directory")
def employee_directory():
    """Employees who can sign in, for the sign-in search. Public, so it carries only name, title and department:
    no access roles, employment type, status or HR details."""
    d = directory()
    people = [{"employee_id": eid, "name": e["name"], "title": e["role"],
               "department": d.departments[e["department_id"]]["name"]}
              for eid, e in d.employees.items() if e["status"] != "exited"]
    people.sort(key=lambda x: (x["department"], x["name"]))
    return {"employees": people}


def _scope(user: Principal | None) -> dict:
    """How many of the confidential records this person may see (shown on the login page and account card)."""
    confidential = {c.record_id: c for c in retriever().chunks if c.confidential}
    visible = sum(can_see(user, c) for c in confidential.values()) if user else 0
    return {"confidential_visible": visible, "confidential_total": len(confidential)}


class LoginRequest(BaseModel):
    employee_id: str
    password: str


@app.post("/api/login")
def login(req: LoginRequest, request: Request, response: Response):
    p = auth.login(request, response, req.employee_id, req.password)
    return _employee_card(p.employee_id)


@app.post("/api/logout")
def logout(response: Response):
    auth.logout(response)
    return {"ok": True}


@app.get("/api/me")
def me(user: Principal = Depends(auth.current_user)):
    d = directory()
    return {**_employee_card(user.employee_id), "tier": user.tier,
            "role_details": [{"role": x, "grants": ROLE_CATALOG.get(x, "")} for x in user.roles],
            "hrbp_departments": sorted(d.departments[x]["name"] for x in user.hrbp_department_ids),
            "reporting_line_size": len(user.reports),
            "scope": _scope(user)}


@app.get("/api/roles")
def roles():
    """The access roles and what each grants (POL-36)."""
    return [{"role": k, "grants": v} for k, v in ROLE_CATALOG.items()]


@app.get("/api/audit")
def audit_log(limit: int = 100, user: Principal = Depends(auth.current_user)):
    """Recent access-log entries on this instance. Compliance auditors only."""
    if not user.has("compliance_auditor"):
        raise HTTPException(status_code=403, detail="The audit log is available to compliance auditors only.")
    audit.record({"event": "audit_log_viewed", "user": user.employee_id, "user_name": user.name})
    return audit.recent(min(limit, 500))


# ------------------------------------------------------------------ search (inspection)

class SearchRequest(BaseModel):
    query: str
    k: int = 8


def _hit_json(h: Hit) -> dict:
    c = h.chunk
    return {
        "chunk_id": c.chunk_id,
        "record_id": c.record_id,
        "title": c.title,
        "source_type": c.source_type,
        "source_system": c.source_system,
        "confidential": c.confidential,
        "last_updated": c.last_updated,
        "score": round(h.score, 4),
        "via": h.via,
        "signals": c.signals.model_dump(),
        "text": c.text,
    }


@app.post("/api/search")
def search(req: SearchRequest, user: Principal = Depends(auth.current_user)):
    """Access-filtered hybrid retrieval for the signed-in user (inspection; the agent calls the retriever directly)."""
    res = retriever().search(req.query, user, k=min(req.k, 20))
    d = directory()
    audit.record({"event": "search", "user": user.employee_id, "query": req.query[:300],
                  "confidential_shown": [h.chunk.record_id for h in res.hits + res.related if h.chunk.confidential]})
    return {
        "hits": [_hit_json(h) for h in res.hits],
        "related": [_hit_json(h) for h in res.related],
        "withheld": {
            "count": res.withheld_count,
            "contacts": [{"employee_id": e, "name": d.name(e)} for e in res.withheld_contacts],
        },
    }


# ------------------------------------------------------------------ record viewer

@app.get("/api/records/{record_id}")
def record(record_id: str, user: Principal = Depends(auth.current_user)):
    """Full text of one record for the source viewer, if this user may see it (access-checked and audited)."""
    r = retriever()
    c = r.record(record_id.strip().upper())
    if not c or not can_see(user, c):
        # Same answer whether it doesn't exist or isn't visible: don't confirm existence of confidential records.
        raise HTTPException(status_code=404, detail="This record doesn't exist or isn't available to you.")
    d = directory()
    basis = access_basis(user, c)
    if c.confidential:
        audit.record({"event": "record_viewed", "user": user.employee_id, "user_name": user.name,
                      "record": c.record_id, "basis": basis, "flagged": basis == "compliance_auditor role"})
    return {
        "record_id": c.record_id,
        "title": c.title.split(" — ")[0],
        "source_type": c.source_type,
        "source_system": c.source_system,
        "status": c.status,
        "created_date": c.created_date,
        "last_updated": c.last_updated,
        "owners": [{"employee_id": o, "name": d.name(o), "active": d.is_active(o)} for o in c.owner_employee_ids],
        "confidential": c.confidential,
        "confidential_reason": c.confidential_reason if c.confidential else None,
        "access_basis": basis if c.confidential else None,
        "signals": c.signals.model_dump(),
        # People named in the record who have left or are away, so the viewer can warn by name.
        "inactive_people": [{"name": d.name(p), "status": d.employees[p]["status"].replace("_", " ")}
                            for p in c.signals.inactive_people_mentioned if p in d.employees],
        "text": r.record_text(c.record_id),
    }


# ------------------------------------------------------------------ chat

class ChatTurn(BaseModel):
    question: str
    answer: str


class ChatRequest(BaseModel):
    question: str
    chat_id: str | None = None  # continue this conversation (context is loaded server-side); None = new chat
    history: list[ChatTurn] = []  # legacy: only used when no chat_id is given


# Answer cache for single-turn questions: same question + same user returns the stored answer (marked cached).
# Keyed per employee because answers depend on what that employee may see. In-memory per instance.
_CACHE: OrderedDict[tuple[str, str], AgentResponse] = OrderedDict()
_CACHE_SIZE = 200
_cache_lock = threading.Lock()


# Per-user rate limit on fresh (uncached) answers: each one costs several Gemini calls.
RATE_LIMIT, RATE_WINDOW_S = 20, 600
_asked: dict[str, deque] = defaultdict(deque)


def _check_rate(user: Principal):
    now = time.time()
    with _cache_lock:
        q = _asked[user.employee_id]
        while q and q[0] < now - RATE_WINDOW_S:
            q.popleft()
        if len(q) >= RATE_LIMIT:
            raise HTTPException(status_code=429, detail=f"You've asked {RATE_LIMIT} questions in 10 minutes. "
                                                        "Please wait a few minutes before asking another.")
        q.append(now)


def _cache_key(employee_id: str, question: str) -> tuple[str, str]:
    return employee_id, " ".join(question.lower().split()).rstrip("?.! ")


def _may_see(user: Principal):
    def check(record_id: str) -> bool:
        c = retriever().record(record_id)
        return c is None or can_see(user, c)  # a record that no longer exists reveals nothing
    return check


def _context(user: Principal, req: ChatRequest) -> list[dict]:
    """Earlier turns of this conversation as model context: from the stored chat (only answers the user may still
    see), or, for old clients without a chat_id, from the request."""
    if req.chat_id:
        chat = history.get_chat(user.employee_id, req.chat_id)
        if chat:
            turns = history.visible_turns(chat, history.scope_key(user), _may_see(user))
            return [{"question": t["question"], "answer": t["response"]["answer"]}
                    for t in turns if t["response"]][-4:]
        return []
    return [t.model_dump() for t in req.history[-4:]]


@app.post("/api/chat", response_model=AgentResponse)
def chat(req: ChatRequest, user: Principal = Depends(auth.current_user)):
    """The assistant: agent loop with tools scoped to the signed-in user, returning a validated, cited answer.
    Each answer is saved to a conversation (`chat_id` in the response); pass it back to ask a follow-up."""
    question = req.question.strip()[:1000]
    if not question:
        raise HTTPException(status_code=400, detail="Ask a question first.")
    context = _context(user, req)
    key = _cache_key(user.employee_id, question)
    resp = None
    if not context:  # only standalone questions are cached; follow-ups depend on the conversation
        with _cache_lock:
            hit = _CACHE.get(key)
            if hit:
                _CACHE.move_to_end(key)
                resp = hit.model_copy(update={"meta": hit.meta.model_copy(update={"cached": True})})
    if resp is None:
        _check_rate(user)
        try:
            resp = answer_question(question, user, history=context)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"TouchStone couldn't answer: {e}")
        if not context:
            with _cache_lock:
                _CACHE[key] = resp
                while len(_CACHE) > _CACHE_SIZE:
                    _CACHE.popitem(last=False)
    _audit_answer(user, question, resp)  # a cached answer is still an access: logged like a fresh one
    chat_id = history.save_turn(user.employee_id, req.chat_id, question, resp.model_dump(mode="json"), _flags(resp),
                                resp.meta.retrieved_record_ids if resp.meta else [], history.scope_key(user))
    return resp.model_copy(update={"chat_id": chat_id})


def _flags(resp: AgentResponse) -> list[str]:
    kinds = {c.kind for c in resp.conflicts}
    flags = []
    if kinds & {"policy_vs_practice", "source_vs_source"} or resp.staleness:
        flags.append("out_of_date")
    if "conflicting_resolutions" in kinds:
        flags.append("conflict")
    if resp.access_note:
        flags.append("withheld")
    return flags


@app.get("/api/chats")
def list_chats(user: Principal = Depends(auth.current_user)):
    """The signed-in employee's conversations, most recently active first (titles and flags only)."""
    return history.list_chats(user.employee_id)


@app.get("/api/chats/{chat_id}")
def get_chat(chat_id: str, user: Principal = Depends(auth.current_user)):
    """One conversation. Stored answers are included only if the user may still see everything behind them."""
    chat = history.get_chat(user.employee_id, chat_id)  # chats live under the user's own path
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found.")
    turns = history.visible_turns(chat, history.scope_key(user), _may_see(user))
    return {"chat_id": chat_id, "title": chat.get("title", ""), "updated_at": chat.get("updated_at"), "turns": turns}


@app.delete("/api/chats/{chat_id}")
def delete_chat(chat_id: str, user: Principal = Depends(auth.current_user)):
    history.delete_chat(user.employee_id, chat_id)
    return {"ok": True}


@app.delete("/api/chats")
def clear_chats(user: Principal = Depends(auth.current_user)):
    history.clear(user.employee_id)
    return {"ok": True}


def _audit_answer(user: Principal, question: str, resp: AgentResponse):
    confidential = [{"record_id": c.record_id, "basis": c.access_basis} for c in resp.citations if c.confidential]
    audit.record({
        "event": "answer",
        "user": user.employee_id,
        "user_name": user.name,
        "roles": list(user.roles),
        "question": question[:300],
        "cited": [c.record_id for c in resp.citations],
        "confidential_cited": confidential,
        "withheld": int(resp.access_note is not None),
        # POL-36 5.2: access granted only through the auditor role is flagged for review.
        "flagged": any(c["basis"] == "compliance_auditor role" for c in confidential),
    })


# Mounted last so /api routes take precedence.
app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
