import os
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from dotenv import load_dotenv
load_dotenv()

import asyncio
import dataclasses
import json
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
import threading
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from config import GWAConfig
from engine import CognitiveEngine

app = FastAPI(title="GWA Cognitive Engine API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://giansha.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-Session-ID"],
)

SESSION_INACTIVITY_TIMEOUT: float = 10 * 60  # 10 minutes

# ── Per-session state ────────────────────────────────────────────────────────

class SessionState:
    def __init__(self):
        self.engine: Optional[CognitiveEngine] = None
        self.config: GWAConfig = GWAConfig()
        self.lock = threading.Lock()
        self.idle_enabled: bool = False
        self.idle_subscribers: list[asyncio.Queue] = []
        self.idle_subscribers_lock = threading.Lock()
        self.last_activity: float = time.time()
        self.event_loop: asyncio.AbstractEventLoop | None = None

    def touch(self):
        self.last_activity = time.time()

    def clear(self):
        """Destroy engine and wipe sensitive config fields."""
        self.idle_enabled = False
        self.engine = None
        self.config = GWAConfig(api_key="", api_base_url=self.config.api_base_url)
        log = logging.getLogger("gwa.session")
        log.info("Session cleared due to inactivity.")


_sessions: dict[str, SessionState] = {}
_sessions_lock = threading.Lock()

IDLE_PROMPT = "No one is speaking to me right now. I can continue thinking on my own, or reach out and say something to the user."


def _get_session(session_id: str) -> SessionState:
    with _sessions_lock:
        if session_id not in _sessions:
            _sessions[session_id] = SessionState()
        return _sessions[session_id]


# ── Pydantic models ──────────────────────────────────────────────────────────

class ConfigPayload(BaseModel):
    api_base_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    chat_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    N: int = 3
    K: int = 5
    T_base: float = 0.7
    alpha: float = 1.3
    beta: float = 2.0
    tau: float = 0.5
    theta: int = 3000
    entropy_window: int = 10
    max_ticks: int = 8
    critic_temperature: float = 0.1
    meta_temperature: float = 0.3
    top_k_rag: int = 3
    chroma_persist_dir: str = "./chroma_db"
    attention_max_tokens: int = 256
    generator_max_tokens: int = 1024
    critic_max_tokens: int = 1024
    meta_max_tokens: int = 1024
    response_max_tokens: int = 512
    idle_interval: float = 30.0
    idle_enabled: bool = False
    default_language: str = "English"


class ChatRequest(BaseModel):
    message: str
    debug: bool = False


# ── Idle broadcast helpers ───────────────────────────────────────────────────

def _idle_broadcast(sess: SessionState, event_type: str, data: dict | None):
    loop = sess.event_loop
    if loop is None:
        return
    with sess.idle_subscribers_lock:
        dead = []
        for q in sess.idle_subscribers:
            try:
                asyncio.run_coroutine_threadsafe(q.put((event_type, data)), loop)
            except Exception:
                dead.append(q)
        for q in dead:
            sess.idle_subscribers.remove(q)


def _idle_scheduler_loop():
    """Background daemon: fires idle ticks for each session."""
    while True:
        time.sleep(5)
        with _sessions_lock:
            sessions = list(_sessions.items())

        for sid, sess in sessions:
            if not sess.idle_enabled or sess.engine is None:
                continue
            if sess.event_loop is None:
                continue

            interval = sess.config.idle_interval if sess.config else 30.0
            if time.time() - sess.last_activity < interval:
                continue

            if not sess.lock.acquire(blocking=False):
                continue

            try:
                for snap in sess.engine.run(
                    IDLE_PROMPT,
                    is_idle=True,
                    debug_callback=lambda agent, tick, token: _idle_broadcast(
                        sess, "debug", {"agent": agent, "tick": tick, "token": token}
                    ),
                ):
                    snap_dict = dataclasses.asdict(snap)
                    if snap.transition_tag == "RESPONSE":
                        _idle_broadcast(sess, "tick", snap_dict)
                        _idle_broadcast(sess, "done", {"final_response": snap.final_response})
            except Exception as e:
                logging.getLogger("gwa.idle").exception("Idle tick error [%s]: %s", sid, e)
            finally:
                sess.lock.release()


def _inactivity_cleanup_loop():
    """Background daemon: clears sessions inactive for SESSION_INACTIVITY_TIMEOUT."""
    while True:
        time.sleep(60)
        now = time.time()
        with _sessions_lock:
            expired = [
                sid for sid, sess in _sessions.items()
                if sess.engine is not None and now - sess.last_activity > SESSION_INACTIVITY_TIMEOUT
            ]
        for sid in expired:
            sess = _sessions.get(sid)
            if sess:
                with sess.lock:
                    sess.clear()


threading.Thread(target=_idle_scheduler_loop, daemon=True, name="idle-scheduler").start()
threading.Thread(target=_inactivity_cleanup_loop, daemon=True, name="inactivity-cleanup").start()


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/config")
def set_config(payload: ConfigPayload, x_session_id: str = Header(...)):
    sess = _get_session(x_session_id)
    sess.touch()
    with sess.lock:
        sess.config = GWAConfig(**payload.model_dump())
        sess.engine = CognitiveEngine(sess.config)
        sess.idle_enabled = sess.config.idle_enabled
    return {"status": "initialized"}


@app.get("/api/config")
def get_config(x_session_id: str = Header(...)):
    sess = _get_session(x_session_id)
    return dataclasses.asdict(sess.config)


@app.get("/api/stats")
def get_stats(x_session_id: str = Header(...)):
    sess = _get_session(x_session_id)
    if sess.engine is None:
        return {"initialized": False}
    ws = sess.engine.workspace
    return {
        "initialized": True,
        "stm_tokens": ws.stm.token_count(),
        "ltm_documents": ws.ltm.count(),
        "total_ticks": ws.tick,
        "last_entropy": ws.entropy_drive.last_entropy,
        "last_T_gen": ws.entropy_drive.last_T_gen,
    }


@app.get("/api/workspace")
def get_workspace(x_session_id: str = Header(...)):
    sess = _get_session(x_session_id)
    if sess.engine is None:
        return {
            "stm_entries": [],
            "ltm_count": 0,
            "ltm_last_knowledge": "",
            "rag_context": "",
            "rag_queries": [],
        }
    ws = sess.engine.workspace
    return {
        "stm_entries": ws.stm.get_all_entries(),
        "ltm_count": ws.ltm.count(),
        "ltm_last_knowledge": ws.last_knowledge,
        "rag_context": ws.rag_context,
        "rag_queries": ws.last_rag_queries,
    }


@app.get("/api/idle-stream")
async def idle_stream(x_session_id: str = Header(...)):
    sess = _get_session(x_session_id)
    q: asyncio.Queue = asyncio.Queue()

    if sess.event_loop is None:
        sess.event_loop = asyncio.get_running_loop()

    with sess.idle_subscribers_lock:
        sess.idle_subscribers.append(q)

    async def generator():
        try:
            while True:
                event_type, data = await q.get()
                yield {
                    "event": event_type,
                    "data": json.dumps(data) if data is not None else "{}",
                }
        except asyncio.CancelledError:
            pass
        finally:
            with sess.idle_subscribers_lock:
                if q in sess.idle_subscribers:
                    sess.idle_subscribers.remove(q)

    return EventSourceResponse(generator())


@app.post("/api/idle/enable")
def idle_enable(x_session_id: str = Header(...)):
    sess = _get_session(x_session_id)
    sess.idle_enabled = True
    return {"status": "idle_enabled"}


@app.post("/api/idle/disable")
def idle_disable(x_session_id: str = Header(...)):
    sess = _get_session(x_session_id)
    sess.idle_enabled = False
    return {"status": "idle_disabled"}


@app.post("/api/chat")
async def chat(req: ChatRequest, x_session_id: str = Header(...)):
    sess = _get_session(x_session_id)
    sess.touch()

    if sess.engine is None:
        raise HTTPException(
            status_code=400,
            detail="Engine not initialized. POST /api/config first.",
        )

    if sess.event_loop is None:
        sess.event_loop = asyncio.get_running_loop()

    async def event_generator():
        q: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def debug_cb(agent: str, tick: int, token: str):
            asyncio.run_coroutine_threadsafe(
                q.put(("debug", {"agent": agent, "tick": tick, "token": token})), loop
            )

        def producer():
            sess.lock.acquire()
            try:
                for snap in sess.engine.run(
                    req.message,
                    debug_callback=debug_cb if req.debug else None,
                ):
                    asyncio.run_coroutine_threadsafe(
                        q.put(("tick", dataclasses.asdict(snap))), loop
                    )
                asyncio.run_coroutine_threadsafe(q.put(("done", None)), loop)
            except Exception as e:
                asyncio.run_coroutine_threadsafe(q.put(("error", str(e))), loop)
            finally:
                sess.lock.release()

        threading.Thread(target=producer, daemon=True).start()

        final_response = ""
        while True:
            event_type, data = await q.get()
            if event_type == "debug":
                yield {"event": "debug", "data": json.dumps(data)}
            elif event_type == "tick":
                if data.get("final_response"):
                    final_response = data["final_response"]
                yield {"event": "tick", "data": json.dumps(data)}
            elif event_type == "done":
                yield {"event": "done", "data": json.dumps({"final_response": final_response})}
                break
            elif event_type == "error":
                yield {"event": "error", "data": json.dumps({"message": data, "code": "ENGINE_ERROR"})}
                break

    return EventSourceResponse(event_generator())


@app.api_route("/api/session", methods=["DELETE", "POST"])
def reset_session(x_session_id: Optional[str] = Header(None), session_id: Optional[str] = None):
    sid = x_session_id or session_id
    if not sid:
        raise HTTPException(status_code=422, detail="Session ID required.")
    sess = _get_session(sid)
    if sess.lock.locked():
        raise HTTPException(status_code=409, detail="Engine is busy.")
    with sess.lock:
        sess.clear()
    return {"status": "reset"}
