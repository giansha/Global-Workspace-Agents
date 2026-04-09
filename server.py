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


class ChatRequest(BaseModel):
    message: str
    debug: bool = False


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "engine_ready": _engine is not None}


@app.post("/api/config")
def set_config(payload: ConfigPayload):
    global _engine, _config
    _config = GWAConfig(**payload.model_dump())
    _engine = CognitiveEngine(_config)
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
        q: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_event_loop()

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
