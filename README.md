$readme = @'
# Butler

A fully-local, multi-agent AI assistant, built from scratch, that runs entirely on your own hardware and never sends your data anywhere.

Butler routes each request to a specialist worker (code execution, reasoning, or web search), runs untrusted code in a hardened Docker sandbox, remembers what you tell it to (with your approval), and delivers everything in a consistent persona - all powered by a local LLM via Ollama, with no cloud calls and no agent frameworks.

---

## Why I built it

I wanted an AI assistant that was genuinely *mine* - one where no prompt, file, or piece of personal context ever leaves my machine. Cloud assistants are powerful, but they are a black box you rent and feed your data to. Butler is the opposite: every component runs locally, the orchestration logic is hand-written (no LangChain, CrewAI, or similar), and I can see and control exactly what happens to every request.

It started as a learning project and became a real daily tool. Along the way it turned into an exercise in the things I care about: privacy-first design, security-conscious engineering, and understanding a system all the way down instead of gluing frameworks together.

---

## What it does

- **Browser chat UI** - a custom HTML/CSS/JS frontend served by a FastAPI backend, running locally at `127.0.0.1:8000`. Dark/teal console aesthetic, message bubbles, worker tags, live markdown rendering, and a slide-out memory drawer.
- **Multi-agent orchestration** - an orchestrator routes each message to the right specialist:
  - **Code worker** - writes and executes Python in a hardened Docker sandbox to compute exact results (hashes, math, data processing) instead of hallucinating them.
  - **Reasoning worker** - explanation and analysis, with hardened independent reasoning (see below).
  - **Web worker** - live internet search (DuckDuckGo), treating fetched content as untrusted data, not instructions.
- **Butler persona** - every worker answers in a consistent voice (dry, concise, English-only), with a strict faithfulness rule: computed values like hashes pass through exactly, never altered.
- **Review-gated memory** - Butler proposes durable personal facts worth remembering and asks for approval (Yes/No buttons). Nothing is stored without an explicit click. Memories are viewable and deletable in a UI drawer, stored in a local, human-readable JSON file, and recalled in full so the assistant reliably knows what you have told it.
- **Resource lifecycle control** - Butler runs on the same machine I game on, where GPU VRAM and RAM are finite. Two one-click desktop scripts control the whole stack: one brings it all up (Docker, Ollama, server, browser), and one tears it completely down - killing the server, unloading the model from VRAM, stopping Ollama, and shutting down Docker's WSL backend to reclaim its RAM. About 9GB of VRAM and several GB of RAM are freed the moment it is switched off, making a heavyweight local AI a deliberate, on-demand tool rather than a permanent resource drain.
- **Built for robustness** - per-call timeouts so a stalled model fails gracefully instead of freezing, a capped agent loop to prevent runaway iterations, and clean handling of model "thinking" output so only the final answer reaches the user.

---

## Architecture
               Browser (custom HTML/JS UI)
                          |
                  FastAPI server  (server.py)
                          |
               Orchestrator  (orchestrator.py)
               routes the request:
    +---------------------+---------------------+
    |                     |                     |
Code worker          Reasoning worker        Web worker
(agent loop)         (independent            (DuckDuckGo +
|                reasoning)              untrusted-content
Hardened Docker                                 handling)
sandbox
|
Local LLM via Ollama  (qwen3:14b)

**Routing** is a two-stage system: fast deterministic keyword/pattern rules handle common cases instantly (no model call), and only genuinely ambiguous requests fall back to a model-based router. This keeps latency low for most queries.

**The code worker** is an agent loop: it reasons, emits a `RUN_CODE` block, the orchestrator executes that code in the sandbox, feeds the real output back, and the agent continues until it has a grounded answer. This is what lets Butler give *correct* computed values - the sandbox catches the model's guesses and replaces them with reality. The persona is baked directly into this loop, so code results are delivered in voice in a single pass.

---

## Security & engineering decisions

This project is as much about *how* it is built as what it does.

**Hardened code sandbox.** All model-generated code runs in a locked-down, throwaway Docker container, never on the host. The full hardening set:
--rm                              container destroyed after each run
--network none                    no network access at all
--memory 256m                     capped RAM (cannot exhaust the host)
--cpus 1                          capped CPU
--pids-limit 64                   capped processes (fork-bomb protection)
--read-only                       read-only container filesystem
--cap-drop ALL                    all Linux capabilities dropped
--security-opt no-new-privileges  no privilege escalation
--user 65534:65534                runs as 'nobody', never root
code mounted read-only (:ro)      the script itself cannot be modified
30s execution timeout             runaway code is killed

The threat model: the LLM is treated as an **untrusted code generator**. Even if it produces malicious or buggy code, the blast radius is a disposable, network-isolated, resource-capped, unprivileged container with no capabilities, no privilege escalation, and explicit fork-bomb and timeout protection.

**Untrusted web content.** The web worker treats search results as *data to answer a question*, not as instructions. Any instructions embedded in fetched pages (a prompt-injection vector) are explicitly ignored, and the web worker can only report text - it can never run code or touch the system.

**Independent reasoning.** The reasoning worker is prompted to prioritize correctness over agreeableness: it works out the right answer before committing, flags when none of the provided options is correct rather than forcing a pick, and holds its conclusion under pressure - it will disagree with the user, a test, or an answer key if its reasoning says they are wrong, and explain why, rather than inventing a justification for an answer it believes is incorrect.

**Privacy by design.** No request, file, or memory ever leaves the machine. The only optional outbound traffic is explicit web searches the user requests.

**Faithfulness.** When Butler delivers a computed value (a hash, a number), it reproduces it exactly. The persona adds personality to the framing only - the facts pass through unchanged.

---

## Stack

- **Language:** Python 3.12
- **Backend:** FastAPI + Uvicorn
- **LLM runtime:** Ollama (qwen3:14b)
- **Sandbox:** Docker (hardened, isolated)
- **Frontend:** custom HTML / CSS / JavaScript (no framework)
- **Search:** DuckDuckGo
- **Hardware:** runs on a single consumer GPU (AMD Radeon RX 9070 XT, 16GB VRAM)
- **Frameworks deliberately NOT used:** no LangChain, CrewAI, AutoGen, or similar - the orchestration, agent loop, routing, memory, and persona layers are all hand-written.

---

## On model selection

Butler runs on qwen3:14b. That choice was earned, not assumed: I tested several alternatives - larger models, uncensored/abliterated variants, and other families - against the things that actually matter here. The model has to reliably follow the custom code-execution protocol, fit in VRAM with enough headroom for context (a ~9GB footprint on a 16GB card), reason well, stay faithful with computed values, and respond in English without drift. qwen3:14b was the most consistent across all of those. The hunt itself was where I learned the most about VRAM headroom, quantization tradeoffs, and how differently models behave under the same prompts.

---

## Project structure
server.py              FastAPI backend + static serving + memory endpoints
static/
index.html           Custom chat UI (HTML/CSS/JS) with memory drawer
launch.bat             One-click launcher (Windows)
scripts/
Butler ON / OFF      Stack lifecycle toggles (paths are machine-specific)
core/
orchestrator.py      Routing, workers, persona, memory proposer
agent.py             Code-execution agent loop
sandbox.py           Hardened Docker sandbox
ollama_client.py     Direct Ollama API client (with timeout handling)
web.py               DuckDuckGo search
memory.py            Local JSON memory store (CRUD)
memory.json            Stored memories (local, gitignored)

---

## Running it

Requires: Python 3.12, Ollama (with a model pulled, e.g. `qwen3:14b`), and Docker.
1. Start Ollama and Docker
2. Launch Butler
launch.bat
3. Open http://127.0.0.1:8000

---

## What this project demonstrates

- **Full-stack systems thinking** - frontend, backend, an orchestration engine, sandboxing, and an LLM runtime, integrated into one working tool.
- **Security-conscious engineering** - defense-in-depth sandboxing, an explicit threat model for untrusted code and untrusted web content, and privacy-by-design.
- **AI orchestration from first principles** - multi-agent routing, an agent execution loop, and persona/memory layers built without leaning on agent frameworks.
- **Pragmatic optimization** - diagnosed and fixed real performance problems (model-loading, VRAM contention, redundant inference passes) to take typical responses from roughly 140s down to ~15-25s.

---

## Roadmap

- Token-by-token response streaming
- Secure LAN access from other devices on an always-on host (a goal better suited to dedicated hardware than a shared gaming machine)
- Deeper agent hierarchy for multi-step autonomous tasks

---

*Built and maintained by [halspror-dev](https://github.com/halspror-dev).*
'@
[System.IO.File]::WriteAllText("$PWD\README.md", $readme, (New-Object System.Text.UTF8Encoding $false))
Write-Host "README.md rewritten - encoding fixed, capabilities updated."