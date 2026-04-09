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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
import threading
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from config import GWAConfig
from engine import CognitiveEngine

app = FastAPI(title="GWA Cognitive Engine API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Singleton state ──────────────────────────────────────────────────────────
_engine: Optional[CognitiveEngine] = None
_config: GWAConfig = GWAConfig()
_engine_lock = threading.Lock()

_idle_enabled: bool = False
_idle_subscribers: list[asyncio.Queue] = []
_idle_subscribers_lock = threading.Lock()
_event_loop: asyncio.AbstractEventLoop | None = None

IDLE_PROMPT = "No one is speaking to me right now. I can continue thinking on my own, or reach out and say something to the user."


# ── Pydantic models ──────────────────────────────────────────────────────────
class ConfigPayload(BaseModel):
    api_base_url: str = os.getenv("GWA_API_BASE_URL", "https://api.openai.com/v1")
    api_key: str = os.getenv("GWA_API_KEY", "")
    chat_model: str = os.getenv("GWA_CHAT_MODEL", "gpt-4o")
    embedding_model: str = os.getenv("GWA_EMBEDDING_MODEL", "text-embedding-3-small")
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


class ChatRequest(BaseModel):
    message: str
    debug: bool = False


def _get_or_set_event_loop() -> asyncio.AbstractEventLoop | None:
    """Capture the running uvicorn event loop from an async context, store it once."""
    global _event_loop
    if _event_loop is None:
        try:
            _event_loop = asyncio.get_running_loop()
        except RuntimeError:
            pass
    return _event_loop


def _idle_broadcast(event_type: str, data: dict | None, loop: asyncio.AbstractEventLoop):
    """Push an SSE event to all connected /api/idle-stream clients."""
    with _idle_subscribers_lock:
        dead = []
        for q in _idle_subscribers:
            try:
                asyncio.run_coroutine_threadsafe(q.put((event_type, data)), loop)
            except Exception:
                dead.append(q)
        for q in dead:
            _idle_subscribers.remove(q)


def _idle_scheduler_loop():
    """Background daemon: fires idle ticks on a timer."""
    import time
    while True:
        # Sleep first so initial startup doesn't immediately fire
        cfg_interval = _config.idle_interval if _config else 30.0
        time.sleep(cfg_interval)

        if not _idle_enabled or _engine is None:
            continue

        loop = _event_loop
        if loop is None:
            continue  # event loop not yet captured (no async request has arrived yet)

        if not _engine_lock.acquire(blocking=True, timeout=cfg_interval):
            continue  # engine still busy after one full interval, skip this cycle

        try:
            for snap in _engine.run(
                IDLE_PROMPT,
                debug_callback=lambda agent, tick, token: _idle_broadcast(
                    "debug", {"agent": agent, "tick": tick, "token": token}, loop
                ),
            ):
                snap_dict = dataclasses.asdict(snap)
                if snap.transition_tag == "RESPONSE":
                    _idle_broadcast("tick", snap_dict, loop)
                    _idle_broadcast("done", {"final_response": snap.final_response}, loop)
                # THINK_MORE: winning_thought already in STM via engine; no broadcast
        except Exception as e:
            logging.getLogger("gwa.idle").exception("Idle tick error: %s", e)
        finally:
            _engine_lock.release()


_idle_thread = threading.Thread(target=_idle_scheduler_loop, daemon=True, name="idle-scheduler")
_idle_thread.start()


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "engine_ready": _engine is not None}


@app.post("/api/config")
def set_config(payload: ConfigPayload):
    global _engine, _config
    _config = GWAConfig(**payload.model_dump())
    _engine = CognitiveEngine(_config)
    global _idle_enabled
    _idle_enabled = _config.idle_enabled
    return {"status": "initialized"}


@app.get("/api/config")
def get_config():
    return dataclasses.asdict(_config)


@app.get("/api/stats")
def get_stats():
    if _engine is None:
        return {"initialized": False}
    ws = _engine.workspace
    return {
        "initialized": True,
        "stm_tokens": ws.stm.token_count(),
        "ltm_documents": ws.ltm.count(),
        "total_ticks": ws.tick,
        "last_entropy": ws.entropy_drive.last_entropy,
        "last_T_gen": ws.entropy_drive.last_T_gen,
    }


@app.get("/api/idle-stream")
async def idle_stream():
    """Persistent SSE stream for idle tick events."""
    q: asyncio.Queue = asyncio.Queue()
    with _idle_subscribers_lock:
        _idle_subscribers.append(q)

    async def generator():
        _get_or_set_event_loop()
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
            with _idle_subscribers_lock:
                if q in _idle_subscribers:
                    _idle_subscribers.remove(q)

    return EventSourceResponse(generator())


@app.post("/api/idle/enable")
def idle_enable():
    global _idle_enabled
    _idle_enabled = True
    return {"status": "idle_enabled"}


@app.post("/api/idle/disable")
def idle_disable():
    global _idle_enabled
    _idle_enabled = False
    return {"status": "idle_disabled"}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    if _engine is None:
        raise HTTPException(
            status_code=400,
            detail="Engine not initialized. POST /api/config first.",
        )

    if not _engine_lock.acquire(blocking=False):
        async def busy_gen():
            yield {
                "event": "error",
                "data": json.dumps(
                    {"message": "Engine is busy processing another request.", "code": "ENGINE_BUSY"}
                ),
            }
        return EventSourceResponse(busy_gen())

    async def event_generator():
        _get_or_set_event_loop()
        q: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def debug_cb(agent: str, tick: int, token: str):
            asyncio.run_coroutine_threadsafe(
                q.put(("debug", {"agent": agent, "tick": tick, "token": token})), loop
            )

        def producer():
            try:
                for snap in _engine.run(
                    req.message,
                    debug_callback=debug_cb if req.debug else None,
                ):
                    asyncio.run_coroutine_threadsafe(
                        q.put(("tick", dataclasses.asdict(snap))), loop
                    )
                asyncio.run_coroutine_threadsafe(q.put(("done", None)), loop)
            except Exception as e:
                asyncio.run_coroutine_threadsafe(
                    q.put(("error", str(e))), loop
                )
            finally:
                _engine_lock.release()

        threading.Thread(target=producer, daemon=True).start()

        final_response = ""
        while True:
            event_type, data = await q.get()
            if event_type == "debug":
                yield {
                    "event": "debug",
                    "data": json.dumps(data),
                }
            elif event_type == "tick":
                if data.get("final_response"):
                    final_response = data["final_response"]
                yield {
                    "event": "tick",
                    "data": json.dumps(data),
                }
            elif event_type == "done":
                yield {
                    "event": "done",
                    "data": json.dumps({"final_response": final_response}),
                }
                break
            elif event_type == "error":
                yield {
                    "event": "error",
                    "data": json.dumps({"message": data, "code": "ENGINE_ERROR"}),
                }
                break

    return EventSourceResponse(event_generator())


@app.delete("/api/session")
def reset_session():
    global _engine
    if _engine_lock.locked():
        raise HTTPException(status_code=409, detail="Engine is busy.")
    _engine = None
    return {"status": "reset"}
