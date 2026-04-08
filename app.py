"""
GWA Streamlit UI -- "Theater of Mind" for LLMs.

Requires Python >= 3.8 and Streamlit >= 1.35.

Layout:
  Sidebar  -- API configuration + hyperparameter controls
  Main     -- Chat history + cognitive process expander per turn
  Input    -- st.chat_input at the bottom
"""
from __future__ import annotations

from typing import List, Optional

import streamlit as st

from config import GWAConfig
from engine import CognitiveEngine, TickSnapshot
import os
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
# -- Page config ---------------------------------------------------------------
st.set_page_config(
    page_title="GWA -- Theater of Mind",
    page_icon="🧠",
    layout="wide",
)


# -- Helper: render cognitive process expander ---------------------------------
def render_cognitive_process(ticks: List[TickSnapshot]) -> None:
    """Render the per-tick cognitive trace inside a Streamlit expander."""
    with st.expander(f"🧠 Cognitive Process -- {len(ticks)} tick(s)", expanded=False):
        for snap in ticks:
            tag_emoji = "OK" if snap.transition_tag == "RESPONSE" else "..."
            header = (
                f"**Tick {snap.tick}** -- "
                f"H(W) = `{snap.entropy:.3f}` | "
                f"T_gen = `{snap.T_gen:.3f}` | "
                f"{tag_emoji} `{snap.transition_tag}`"
            )
            if snap.compressed:
                header += " | STM compressed"
            st.markdown(header)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**RAG Queries**")
                for q in snap.rag_queries:
                    st.markdown(f"- {q}")
                if snap.rag_context:
                    with st.expander("Retrieved context"):
                        preview = snap.rag_context[:800]
                        if len(snap.rag_context) > 800:
                            preview += "..."
                        st.text(preview)

            with col2:
                st.markdown("**Candidates & Scores**")
                for i, (cand, eval_pair) in enumerate(
                    zip(snap.candidates, snap.evaluations), 1
                ):
                    score, critique = eval_pair
                    if score > 0:
                        score_label = f"+{score}"
                        score_color = "green"
                    elif score < 0:
                        score_label = str(score)
                        score_color = "red"
                    else:
                        score_label = "0"
                        score_color = "gray"

                    cand_preview = cand[:120]
                    if len(cand) > 120:
                        cand_preview += "..."

                    st.markdown(
                        f"**{i}.** :{score_color}[Score {score_label}]  \n"
                        f"_{cand_preview}_  \n"
                        f"-> {critique}"
                    )

            st.markdown("**Winning Thought W_t**")
            st.info(snap.winning_thought)
            st.divider()


# -- Session state initialisation ----------------------------------------------
if "config" not in st.session_state:
    st.session_state.config = GWAConfig()

if "engine" not in st.session_state:
    st.session_state.engine = None  # created after config save

if "conversation" not in st.session_state:
    # Each entry: {"role": str, "content": str, "ticks": List[TickSnapshot]}
    st.session_state.conversation = []


# -- Sidebar -- Configuration --------------------------------------------------
with st.sidebar:
    st.title("Configuration")

    st.subheader("API Settings")
    api_base = st.text_input(
        "API Base URL",
        value=st.session_state.config.api_base_url,
        placeholder="https://api.openai.com/v1",
    )
    api_key = st.text_input(
        "API Key",
        value=st.session_state.config.api_key,
        type="password",
        placeholder="sk-...",
    )
    chat_model = st.text_input(
        "Chat Model",
        value=st.session_state.config.chat_model,
        placeholder="gpt-4o",
    )
    embedding_model = st.text_input(
        "Embedding Model",
        value=st.session_state.config.embedding_model,
        placeholder="text-embedding-3-small",
    )

    st.subheader("Hyperparameters")
    N = st.slider("N -- Candidates per tick", 1, 6, st.session_state.config.N)
    T_base = st.slider(
        "T_base -- Baseline temperature",
        0.1, 1.5, float(st.session_state.config.T_base), 0.05,
    )
    alpha = st.slider(
        "alpha -- Max temp boost",
        0.0, 2.0, float(st.session_state.config.alpha), 0.1,
    )
    beta = st.slider(
        "beta -- Entropy sensitivity",
        0.5, 5.0, float(st.session_state.config.beta), 0.1,
    )
    tau = st.slider(
        "tau -- Softmax scaling",
        0.1, 2.0, float(st.session_state.config.tau), 0.05,
    )
    theta = st.slider(
        "theta -- STM token threshold",
        500, 8000, st.session_state.config.theta, 100,
    )
    max_ticks = st.slider(
        "max_ticks -- Tick cap",
        1, 16, st.session_state.config.max_ticks,
    )

    if st.button("Save & Initialise", use_container_width=True):
        cfg = GWAConfig(
            api_base_url=api_base,
            api_key=api_key,
            chat_model=chat_model,
            embedding_model=embedding_model,
            N=N,
            T_base=T_base,
            alpha=alpha,
            beta=beta,
            tau=tau,
            theta=theta,
            max_ticks=max_ticks,
        )
        st.session_state.config = cfg
        st.session_state.engine = CognitiveEngine(cfg)
        st.session_state.conversation = []
        st.success("Engine initialised")

    st.divider()
    st.caption("Global Workspace Agents / NeurIPS 2026")

    if st.session_state.engine is not None:
        ws = st.session_state.engine.workspace
        st.metric("STM tokens", ws.stm.token_count())
        st.metric("LTM documents", ws.ltm.count())
        st.metric("Total cognitive ticks", ws.tick)
        st.metric("Last H(W)", f"{ws.entropy_drive.last_entropy:.3f}")
        st.metric("Last T_gen", f"{ws.entropy_drive.last_T_gen:.3f}")


# -- Main -- Header ------------------------------------------------------------
st.title("🧠 Theater of Mind")
st.caption(
    "A cognitive architecture based on Global Workspace Theory. "
    "Configure the API in the sidebar and start a conversation."
)

if st.session_state.engine is None:
    st.info("Enter your API settings and click **Save & Initialise** to begin.")
    st.stop()


# -- Main -- Conversation history ----------------------------------------------
for turn in st.session_state.conversation:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])
        if turn["role"] == "assistant" and turn.get("ticks"):
            render_cognitive_process(turn["ticks"])


# -- Main -- Chat input --------------------------------------------------------
user_input = st.chat_input("Send a message to GWA...")
if user_input:
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.conversation.append(
        {"role": "user", "content": user_input, "ticks": []}
    )

    # Run the cognitive engine
    engine: CognitiveEngine = st.session_state.engine
    collected_ticks: List[TickSnapshot] = []
    final_response: str = ""

    with st.chat_message("assistant"):
        status_placeholder = st.empty()

        for snap in engine.run(user_input):
            collected_ticks.append(snap)
            tag_label = "RESPONSE" if snap.transition_tag == "RESPONSE" else "THINK_MORE"
            status_placeholder.markdown(
                f"**Tick {snap.tick}** -- "
                f"H(W) = `{snap.entropy:.3f}` | "
                f"T_gen = `{snap.T_gen:.3f}` | "
                f"`{tag_label}`"
            )
            if snap.final_response:
                final_response = snap.final_response

        status_placeholder.empty()
        st.markdown(final_response)
        render_cognitive_process(collected_ticks)

    st.session_state.conversation.append(
        {
            "role": "assistant",
            "content": final_response,
            "ticks": collected_ticks,
        }
    )
    st.rerun()
