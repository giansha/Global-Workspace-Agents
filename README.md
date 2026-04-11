<div align="center">

# 🧠 Global Workspace Agents (GWA)

### Enabling LLMs to Think Proactively and Initiate Dialogue with Consciousness

### *"Theater of Mind" for LLMs: A Cognitive Architecture Based on Global Workspace Theory*

[![Paper](https://img.shields.io/badge/Paper-Arxiv%202026-blue?style=flat-square&logo=arxiv)](https://arxiv.org/abs/2604.08206)
[![Demo](https://img.shields.io/badge/Demo-GWA%20Website-green?style=flat-square&logo=vercel)](https://giansha.github.io/Global-Workspace-Agents/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square&logo=next.js)](https://nextjs.org/)

</div>

---

> **GWA** transitions multi-agent LLM coordination from passive shared memory to an **active, event-driven discrete dynamical system** — inspired by Global Workspace Theory from cognitive science. The system maintains continuous self-directed reasoning through a heterogeneous agent swarm, entropy-based intrinsic drive, and dual-layer memory bifurcation.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Running the System](#running-the-system)
- [UI Overview](#ui-overview)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Citation](#citation)

---

## Overview

Modern LLMs are BIBO (Bounded-Input Bounded-Output) systems — reactive, stateless, unable to sustain autonomous deliberation. Existing multi-agent frameworks rely on static memory pools and passive message passing, which leads to **sycophancy, echo chambers, and cognitive stagnation**.

GWA addresses this by implementing:

- **The Cognitive Tick** — a 4-phase discrete loop: *Perceive → Think → Arbitrate → Update*
- **Entropy-Based Intrinsic Drive** — Shannon entropy over semantic clusters dynamically regulates generator temperature to break reasoning deadlocks
- **Core Self & Genesis State** — invariant identity injection each tick prevents semantic drift
- **Dual-Layer Memory** — STM (active cache) + LTM (vector DB via RAG) with automatic bifurcation at token threshold θ

---

## Architecture

```
                          ┌─────────────────────────────────────┐
                          │         Global Workspace (STM)      │
                          │  S_t = STM ∪ INPUT ∪ RAG ∪ P_Self│
                          └────────────────┬────────────────────┘
                                           ⬆ broadcast/update
               ┌───────────────────────────┼───────────────────────────┐
               ▼                           ▼                           ▼
    ┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
    │  Attention Node  │       │  Generator Node  │       │   Critic Node    │
    │  (The Spotlight) │       │ (Divergent, T↑)  │       │ (Convergent, T→0)│
    └────────┬─────────┘       └────────┬─────────┘       └────────┬─────────┘
             │ RAG queries              │ N candidates             │ scores + critique
             ▼                          └──────────┬───────────────┘
        LTM (ChromaDB)                             ▼
                                       ┌──────────────────┐
                                       │    Meta Node     │
                                       │  (Arbitrator)    │
                                       │  → W_t + tag     │
                                       └────────┬─────────┘
                                [THINK_MORE] ◄──┴──► [RESPONSE]
                                                            │
                                               ┌────────────▼─────────┐
                                               │   Response Node      │
                                               │ (Linguistic Output)  │
                                               └──────────────────────┘
```

The **Entropy Drive** monitors semantic cluster distribution of recent winning thoughts. When H(W) → 0 (stagnation), generator temperature rises automatically:

```
T_gen = T_base + α · exp(−β · H(W))
```

---

## Quick Start

### Prerequisites

- [Anaconda](https://www.anaconda.com/) with a conda env named `agent`
- [Node.js](https://nodejs.org/) 18+
- An OpenAI-compatible API key

### 1. Clone the repository

```bash
git clone https://github.com/PLACEHOLDER/gwt_consciousness_system.git
cd gwt_consciousness_system
```

### 2. Install Python dependencies

```bash
python -m pip install -r requirements_server.txt
```

### 3. Install frontend dependencies

```bash
cd frontend && npm install && cd ..
```

### 4. Configure environment

```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
```

---

## Running the System

Open **two terminals** from the project root:

**Terminal 1 — FastAPI backend (port 8000)**

```bash
python -m uvicorn server:app --reload --port 8000
```

**Terminal 2 — Next.js frontend (port 3000)**

```bash
cd frontend
node node_modules/next/dist/bin/next dev
```

Then open [http://localhost:3000](http://localhost:3000), configure your API key and model in the sidebar, and click **Save & Initialize**.

> **Alternative (legacy Streamlit UI)**
> ```bash
> C:/ProgramData/anaconda3/envs/agent/Scripts/streamlit.exe run app.py
> ```

---

## UI Overview

The Next.js frontend is organized into four areas. Here is a quick map followed by details on each control.

```
┌─────────────────┬──────────────────────────────────────┬──────────────────┐
│   Left Sidebar  │           Main Panel                 │  Debug Sidebar   │
│  (Config/Stats) │  [MEMORY] [IDLE] [DEBUG]  toggle bar │  (when DEBUG on) │
│                 ├──────────────────────────────────────┤                  │
│  • API settings │  Memory Inspector (when MEMORY on)   │  • Live State    │
│  • Hyperparams  ├──────────────────────────────────────┤  • Agent Streams │
│  • Save & Init  │  Conversation + Cognitive Trace      │    per tick      │
│  • Reset        ├──────────────────────────────────────┤                  │
│  • Workspace    │  Chat Input                          │                  │
│    Stats        │                                      │                  │
└─────────────────┴──────────────────────────────────────┴──────────────────┘
```

### Left Sidebar — Engine Configuration

Fill in these fields in sidebar before starting.

#### API section

| Field | Description |
| --- | --- |
| Base URL | Root URL of an OpenAI-compatible API (e.g. `https://api.openai.com/v1`) |
| API Key | Your secret key (`sk-…`). Stored only in the browser session. |
| Chat Model | Model used by all five agent nodes (e.g. `gpt-4o`, `claude-opus-4-5`) |
| Embedding Model | Model used for LTM / RAG embeddings (e.g. `text-embedding-3-small`) |

#### Hyperparameters section

Sliders let you tune the cognitive engine live:

| Slider | Range | Effect |
| --- | --- | --- |
| N (candidates) | 1 – 6 | Number of candidate thoughts the Generator produces per tick |
| T_base | 0.1 – 1.5 | Baseline sampling temperature for the Generator |
| α (alpha) | 0 – 2.0 | Maximum extra temperature added when entropy is low (stagnation) |
| β (beta) | 0.5 – 5.0 | Sensitivity of temperature boost to entropy drop |
| τ (tau) | 0.1 – 2.0 | Softmax temperature for semantic cluster distance scaling |
| θ (STM tokens) | 500 – 8000 | Token capacity of Short-Term Memory before bifurcation to LTM |
| max\_ticks | 1 – 16 | Maximum cognitive ticks per user turn before a forced response |
| Idle interval (s) | 5 – 300 | Seconds of inactivity before the engine thinks autonomously |
| Idle response language | selector | Language the system uses for unsolicited idle messages |

#### Max Tokens per Agent

Fine-grained token budgets for each node: Attention, Generator, Critic, Meta, and Response.

#### Buttons

| Button | Action |
| --- | --- |
| Save & Initialize | Pushes the current config to the backend and starts the engine. Must be clicked before chatting. |
| Reset Session | Clears the current session and conversation history on both frontend and backend. |

#### Workspace Stats

Updates automatically at the bottom of the sidebar.

| Metric | Meaning |
| --- | --- |
| STM | Tokens currently held in Short-Term Memory |
| LTM | Number of documents persisted to Long-Term Memory (ChromaDB) |
| Ticks | Total cognitive ticks since session start |
| H(W) bar | Current Shannon entropy over recent winning thoughts; low = stagnation risk |
| T_gen bar | Current generator temperature after entropy-based adjustment |

---

### Top Toggle Bar

Three toggles appear in the thin bar above the conversation. They are disabled until the engine is initialized.

| Toggle | Color when active | What it does |
| --- | --- | --- |
| MEMORY | Purple | Opens the Memory Inspector panel above the conversation |
| **IDLE** | Green | **Allows the engine to think and message you unprompted during inactivity** |
| DEBUG | Red | Opens the Debug Sidebar on the right |

---

### Memory Inspector (MEMORY toggle)

A three-column panel that polls the backend every second and shows the live state of both memory layers and the RAG pipeline.

| Column | Content |
| --- | --- |
| STM | Every entry in Short-Term Memory with its role tag (`USER`, `ASSISTANT`, `SYSTEM`, `MEMORY`) |
| LTM | Document count and the most recently consolidated knowledge chunk |
| RAG | The retrieval queries formulated by the Attention Node and the context passages retrieved |

---

### Conversation Panel

The main chat area. Key behaviors:

- **Live tick preview** — while the engine is streaming, a "Thinking… (N ticks)" card appears in real time showing each TickCard as it completes.
- **Cognitive Trace** — every assistant message has a collapsible `▶ cognitive trace (N ticks)` link beneath it. Click to expand all the TickCards for that response.
- **TickCard** — shows one cognitive tick: the winning thought chosen by the Meta Node, its decision tag (`[THINK_MORE]` / `[RESPONSE]`), entropy H(W), temperature T_gen, and the scored candidate list with Critic feedback.
- **Error banner** — any backend error appears as a dismissible red strip above the input.
- **Chat Input** — type a message and press Enter (or click Send). Disabled while the engine is streaming.

---

### Debug Sidebar (DEBUG toggle)

Opens on the right side of the screen. Contains two sub-panels:

**Live State** — real-time readout of the current tick number, entropy H(W), temperature T_gen, and streaming status.

**Agent Streams** — grouped by tick, one expandable stream per agent node (Attention → Generator → Critic → Meta). Each stream shows the raw token-level output as it arrives. The current streaming tick is highlighted in the accent color; a pulsing red dot in the header indicates active streaming.

---

## Configuration

All hyperparameters live in `config.py` as the `GWAConfig` dataclass:

| Parameter | Description |
| --- | --- |
| `N` | Number of candidate thoughts generated per tick |
| `K` | Number of semantic clusters for entropy computation |
| `T_base` | Baseline generator temperature |
| `α` (alpha) | Maximum exploratory temperature variance |
| `β` (beta) | Entropy sensitivity for temperature regulation |
| `τ` (tau) | Softmax temperature for cluster distance scaling |
| `θ` (theta) | STM token capacity threshold triggering memory bifurcation |

---

## Project Structure

```
gwt_consciousness_system/
├── engine.py            # CognitiveEngine — orchestrates the tick loop
├── config.py            # GWAConfig dataclass — all hyperparameters
├── workspace.py         # Global Workspace state — STM, LTM, RAG
├── entropy_drive.py     # Computes H(W), returns dynamic T_gen
├── server.py            # FastAPI bridge — singleton engine, SSE streaming
├── app.py               # Legacy Streamlit UI
├── agents/
│   ├── attention.py     # Attention Node (RAG query formulation)
│   ├── generator.py     # Generator Node (divergent candidate thoughts)
│   ├── critic.py        # Critic Node (convergent scoring)
│   ├── meta.py          # Meta Node (metacognitive arbitration)
│   ├── response.py      # Response Node (linguistic articulation)
│   └── base.py          # BaseAgent with retry/backoff
├── memory/
│   ├── stm.py           # Short-Term Memory (token-counted active cache)
│   └── ltm.py           # Long-Term Memory (ChromaDB persistence)
├── frontend/            # Next.js 14 App Router UI (TypeScript, Tailwind, Zustand)
└── tests/               # Pytest test suite
```

---

## Running Tests

```bash
python -m pytest tests/
```

---

## Citation

If you find this work useful, please cite:

```bibtex
@misc{shang2026theatermindllmscognitive,
      title={"Theater of Mind" for LLMs: A Cognitive Architecture Based on Global Workspace Theory}, 
      author={Wenlong Shang},
      year={2026},
      eprint={2604.08206},
      archivePrefix={arXiv},
      primaryClass={cs.MA},
      url={https://arxiv.org/abs/2604.08206}, 
}
```
