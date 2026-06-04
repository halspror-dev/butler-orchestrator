# Butler Orchestrator

A fully local, self-owned multi-agent AI system with a browser chat UI, persistent
memory, and a personality. You talk to "Butler" — a calm, dry-witted assistant who
routes your requests to a team of specialist workers behind the scenes: a code
worker (runs Python in a hardened, network-isolated Docker sandbox), a reasoning
worker (explanation/analysis, memory-aware), and a web worker (live internet
research). No cloud, no telemetry, no API keys. Everything runs on your own hardware.

## What it does

- **Browser chat UI** — custom HTML/CSS/JS frontend served by the FastAPI backend,
  fully local at http://127.0.0.1:8000.
- **Butler persona** — responses delivered in character by Butler, who presents
  the workers' results faithfully (facts/numbers/hashes preserved exactly), in
  English, cleaned of model artifacts.
- **Three specialist workers:**
  - **Code** — writes and runs Python in a hardened Docker sandbox (no network,
    non-root, resource-capped, read-only, auto-removed).
  - **Reasoning** — explanation and analysis from general knowledge, memory-aware.
  - **Web** — live internet search (DuckDuckGo); fetched content is treated as
    untrusted data, not instructions.
- **Persistent memory** — tell it "remember ..." and it stores facts locally
  (`memory.json`), recalling them across sessions.
- **Hybrid orchestrator** — routes by deterministic rules first, falling back to a
  coordinator model only for ambiguous cases. Identity questions answered directly
  by Butler.

## Requirements

1. **Python 3.12** — https://www.python.org/downloads/ (check "Add to PATH")
2. **Ollama** — https://ollama.com
3. **Docker Desktop** — https://www.docker.com/products/docker-desktop/

Then pull the models:

    ollama pull qwen3:8b
    ollama pull qwen3:14b

(8B = code/worker model; 14B = coordinator/reasoning/web/Butler voice model.)

## Setup

    py -3.12 -m venv venv
    .\venv\Scripts\Activate.ps1        # Windows PowerShell
    pip install -r requirements.txt

## Running it

Make sure **Ollama** and **Docker Desktop** are running, then double-click
`launch.bat` (or run `python server.py`). Open http://127.0.0.1:8000 and chat
with Butler.

Examples:
- "What is the SHA-256 hash of 'butler test'?" — code worker + sandbox
- "Explain why network segmentation improves security." — reasoning worker
- "What is the latest news about AMD GPUs?" — web worker (live search)
- "Who are you?" — Butler answers in character
- "Remember that my favorite language is Rust." / "What is my favorite language?" — memory

## Configuration

- **Models** — set in `core/orchestrator.py` and `core/agent.py` (`model=` args).
  Butler's voice model is `BUTLER_MODEL` in `core/orchestrator.py`.
- **VRAM / unload time** — Ollama's `keep_alive`. Default unload ~5 min after use.
  Set `OLLAMA_KEEP_ALIVE` env var (`30m`, `0` = immediate, `-1` = keep loaded).
- **Sandbox hardening** — security flags in `core/sandbox.py`.
- **Memory** — stored in `memory.json` (local, gitignored, human-readable).
- **Routing keywords** — code/web routing rules in `rule_based_route` (orchestrator).

## Project structure

    server.py             FastAPI backend + static file serving
    static/
      index.html          Custom dark/teal chat UI (HTML/CSS/JS)
    launch.bat            One-click launcher (Windows)
    core/
      ollama_client.py    Direct local LLM communication
      sandbox.py          Hardened Docker code-execution sandbox
      agent.py            The agent loop (think -> run code -> observe -> answer)
      web.py              Web search (DuckDuckGo, keyless)
      memory.py           Local persistent memory (JSON-backed)
      orchestrator.py     Hybrid routing + memory + web + Butler persona delivery
    deprecated/           Earlier CrewAI experiments (kept for reference)
    requirements.txt      Dependencies (requests, fastapi, uvicorn, ddgs)

## Security notes

- Fully local: no data leaves your machine except deliberate web searches.
- The code sandbox has no network access; web access is a separate, narrow channel.
- Web-fetched content is treated as untrusted data — the web worker is instructed to
  ignore any instructions embedded in results. Its blast radius is limited: it can
  only report text, never run code or touch the system.
- Butler preserves facts exactly and responds only in English.
- `memory.json` holds personal facts and is gitignored.

## Background

The `deprecated/` folder contains earlier experiments using the CrewAI framework,
kept to document the evaluation that led to this from-scratch build (the framework's
removed/cloud-only code execution and telemetry conflicted with the local-first,
self-owned goals).
