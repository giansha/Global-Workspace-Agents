<div align="center">

# 🧠 Global Workspace Agents (GWA)

### *"Theater of Mind" for LLMs: A Cognitive Architecture Based on Global Workspace Theory*

[![Paper](https://img.shields.io/badge/Paper-XXX%202026-blue?style=flat-square&logo=arxiv)](https://arxiv.org/abs/PLACEHOLDER)
[![Demo](https://img.shields.io/badge/Demo-Live%20Website-green?style=flat-square&logo=vercel)](https://PLACEHOLDER.example.com)
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
C:/ProgramData/anaconda3/envs/agent/python.exe -m pip install -r requirements_server.txt
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
C:/ProgramData/anaconda3/envs/agent/python.exe -m uvicorn server:app --reload --port 8000
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

## Configuration

All hyperparameters live in `config.py` as the `GWAConfig` dataclass:

| Parameter | Description |
|---|---|
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
C:/ProgramData/anaconda3/envs/agent/python.exe -m pytest tests/
```

---

## Citation

If you find this work useful, please cite:

```bibtex
@inproceedings{gwa2026,
  title     = {"Theater of Mind" for LLMs: A Cognitive Architecture Based on Global Workspace Theory},
  author    = {PLACEHOLDER},
  booktitle = {XXX},
  year      = {2026},
  url       = {https://arxiv.org/abs/PLACEHOLDER}
}
```
