# Butler Orchestrator

A fully local, self-owned multi-agent AI system with a browser chat UI, persistent
memory, and a personality. You talk to "Butler" — a calm, dry-witted assistant who
routes your requests to a team of specialist workers behind the scenes, including
one that runs code in a hardened, network-isolated Docker sandbox. No cloud, no
telemetry, no API keys. Everything runs on your own hardware.

## What it does

- **Browser chat UI** (Gradio) with live status updates — fully local.
- **Butler persona** — responses are delivered in character by BigButler, who
  faithfully presents the workers' results (facts and computed values preserved
  exactly) with personality.
- **Persistent memory** — tell it "remember ..." and it stores facts locally
  (in `memory.json`), recalling them in future sessions.
- **Local LLM layer** — talks directly to models served by Ollama on your GPU.
- **Hardened code sandbox** — runs model-generated Python in a locked-down Docker
  container (no network, non-root, resource-capped, read-only, auto-removed).
- **Agent loop** — a worker that thinks, runs code, observes the real result, answers.
- **Hybrid orchestrator** — routes by deterministic rules first, falling back to a
  coordinator model only for ambiguous cases.

## Requirements

1. **Python 3.12** — https://www.python.org/downloads/ (check "Add to PATH")
2. **Ollama** — https://ollama.com
3. **Docker Desktop** — https://www.docker.com/products/docker-desktop/

Then pull the models:

    ollama pull qwen3:8b
    ollama pull qwen3:14b
    ollama pull huihui_ai/qwen3-abliterated:14b

(8B = code/worker model; 14B = coordinator/reasoning model; abliterated 14B = Butler's voice.)

## Setup

    py -3.12 -m venv venv
    .\venv\Scripts\Activate.ps1        # Windows PowerShell
    pip install -r requirements.txt

## Running it

Make sure **Ollama** and **Docker Desktop** are running, then double-click
`launch.bat` (or run `python ui.py`). Open the printed URL (usually
http://127.0.0.1:7860) and chat with Butler.

Examples:
- "What is the SHA-256 hash of 'butler test'?" — code worker + sandbox, delivered by Butler
- "Explain why network segmentation improves security." — reasoning worker
- "Remember that my favorite language is Rust." — stores a memory
- "What is my favorite language?" — recalls it (persists across restarts)

## Configuration

- **Models** — set in `core/orchestrator.py` and `core/agent.py` (`model=` args).
  Butler's voice model is `BUTLER_MODEL` in `core/orchestrator.py`.
- **VRAM / unload time** — Ollama's `keep_alive`. Default unload ~5 min after use.
  Set `OLLAMA_KEEP_ALIVE` env var (`30m`, `0` = immediate, `-1` = keep loaded).
- **Sandbox hardening** — security flags in `core/sandbox.py`.
- **Memory** — stored in `memory.json` (local, gitignored, human-readable).

## Project structure

    ui.py                 Browser chat UI (Gradio) with live status
    launch.bat            One-click launcher (Windows)
    core/
      ollama_client.py    Direct local LLM communication
      sandbox.py          Hardened Docker code-execution sandbox
      agent.py            The agent loop (think -> run code -> observe -> answer)
      orchestrator.py     Hybrid routing + memory + Butler persona delivery
      memory.py           Local persistent memory (JSON-backed)
    deprecated/           Earlier CrewAI experiments (kept for reference)
    requirements.txt      Dependencies (requests, gradio)

## Notes

- Fully local: no data leaves your machine. The code sandbox has no network access.
- Butler is instructed to preserve all facts/numbers/hashes from workers exactly,
  adding personality only to the framing — accuracy first, charm second.
- `memory.json` holds personal facts and is gitignored.
- The `deprecated/` folder documents the earlier CrewAI evaluation.