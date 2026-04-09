from dataclasses import dataclass, field
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class GWAConfig:
    # ── API ──────────────────────────────────────────────────────────────────
    api_base_url: str = field(
        default_factory=lambda: os.getenv("GWA_API_BASE_URL", "https://api.openai.com/v1")
    )
    api_key: str = field(
        default_factory=lambda: os.getenv("GWA_API_KEY", "")
    )
    chat_model: str = field(
        default_factory=lambda: os.getenv("GWA_CHAT_MODEL", "gpt-4o")
    )
    embedding_model: str = field(
        default_factory=lambda: os.getenv("GWA_EMBEDDING_MODEL", "text-embedding-3-small")
    )

    # ── Hyperparameters (§3.3–3.5) ───────────────────────────────────────────
    N: int = 3                  # number of Generator candidate thoughts
    K: int = 5                  # semantic clusters for Shannon entropy
    T_base: float = 0.7        # baseline generator temperature
    alpha: float = 1.3         # max temperature boost α
    beta: float = 2.0          # entropy sensitivity β
    tau: float = 0.5           # softmax distance scaling τ
    theta: int = 3000          # STM token capacity threshold θ
    entropy_window: int = 10   # recent W_t window for H(W)
    max_ticks: int = 8         # safety cap on cognitive ticks per user turn
    critic_temperature: float = 0.1   # T→0 for deterministic Critic
    meta_temperature: float = 0.3    # Meta arbitration temperature
    top_k_rag: int = 3         # LTM retrieval top-k
    chroma_persist_dir: str = "./chroma_db"

    # ── Per-agent max_tokens ─────────────────────────────────────────────────
    attention_max_tokens: int = 256
    generator_max_tokens: int = 1024
    critic_max_tokens: int = 1024
    meta_max_tokens: int = 1024
    response_max_tokens: int = 512      # ResponseNode: conversational replies are short

    # ── Idle autonomous ticking ──────────────────────────────────────────────
    idle_interval: float = 30.0   # seconds between idle tick cycles
    idle_enabled: bool = False    # whether idle mode starts active on init
    default_language: str = "English"  # language for idle-initiated responses
