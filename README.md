# Butler Orchestrator

A fully local, self-owned multi-agent AI system with a browser chat UI. A hybrid
orchestrator routes your messages to specialist workers — including a worker that
runs code inside a hardened, network-isolated Docker sandbox. No cloud, no
telemetry, no API keys. Everything runs on your own hardware.

## What it does

- **Browser chat UI** (Gradio) — talk to the system in your browser, fully local.
- **Local LLM layer** — talks directly to models served by Ollama on your GPU.
- **Hardened code sandbox** — runs model-generated Python in a locked-down Docker
  container (no network, non-root, resource-capped, read-only, auto-removed).
- **Agent loop** — a worker that thinks, runs code in the sandbox, observes the
  real result, and answers.
- **Hybrid orchestrator** — routes requests by deterministic rules first, falling
  back to a coordinator model only for ambiguous cases.

## Requirements

Install these before running anything:

1. **Python 3.12** — https://www.python.org/downloads/ (check "Add to PATH" on install)
2. **Ollama** — https://ollama.com (the local model server)
3. **Docker Desktop** — https://www.docker.com/products/docker-desktop/ (for the code sandbox)

Then pull the models this project uses:

    ollama pull qwen3:8b
    ollama pull qwen3:14b

(The 8B is the code/worker model; the 14B is the coordinator/reasoning model.)

## Setup

From the project folder:

    # 1. Create and activate a virtual environment
    py -3.12 -m venv venv
    .\venv\Scripts\Activate.ps1        # Windows PowerShell

    # 2. Install dependencies
    pip install -r requirements.txt

## Running it

Make sure **Ollama** and **Docker Desktop** are both running, then:

**Easiest — one click:** double-click `launch.bat`. It activates the environment,
starts the UI, and prints a local URL.

**Or manually:**

    python ui.py

Either way, open the printed URL (usually http://127.0.0.1:7860) in your browser
and start chatting. Try "What is the SHA-256 hash of 'butler test'?" (routes to the
code worker + sandbox) or "Explain why network segmentation improves security."
(routes to the reasoning worker).

## Configuration

- **Which models are used** — set in `core/orchestrator.py` and `core/agent.py`
  (the `model=` arguments).
- **VRAM / model unload time** — controlled by Ollama's `keep_alive`. A model
  unloads from VRAM ~5 minutes after last use by default. To change globally, set
  the environment variable `OLLAMA_KEEP_ALIVE` (e.g. `30m` to keep loaded longer,
  `0` to unload immediately, `-1` to keep loaded indefinitely).
- **Sandbox hardening** — security flags are set in `core/sandbox.py` (network
  disabled, memory/CPU/process caps, read-only filesystem, dropped capabilities,
  non-root user).

## Project structure

    ui.py                 Browser chat UI (Gradio), wired to the orchestrator
    launch.bat            One-click launcher (Windows)
    core/                 The orchestration system (owned, from-scratch build)
      ollama_client.py    Direct local LLM communication
      sandbox.py          Hardened Docker code-execution sandbox
      agent.py            The agent loop (think -> run code -> observe -> answer)
      orchestrator.py     Hybrid rule + model routing to workers
    deprecated/           Earlier CrewAI-based experiments (kept for reference)
    requirements.txt      Dependencies for the core project + UI

## Notes

- Fully local: no data leaves your machine. The code sandbox has no network access.
- The `deprecated/` folder contains earlier attempts using the CrewAI framework,
  kept to document the evaluation that led to this custom build. They require the
  full CrewAI dependency set (see `requirements-experiments.txt`), not the minimal
  `requirements.txt`.