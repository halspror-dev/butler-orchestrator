\# Butler Orchestrator



A fully local, self-owned multi-agent AI system. A hybrid orchestrator routes

requests to specialist workers — including a worker that runs code inside a

hardened, network-isolated Docker sandbox. No cloud, no telemetry, no API keys.

Everything runs on your own hardware.



\## What it does



\- \*\*Local LLM layer\*\* — talks directly to models served by Ollama on your GPU.

\- \*\*Hardened code sandbox\*\* — runs model-generated Python in a locked-down Docker

&#x20; container (no network, non-root, resource-capped, read-only, auto-removed).

\- \*\*Agent loop\*\* — a worker that thinks, runs code in the sandbox, observes the

&#x20; real result, and answers.

\- \*\*Hybrid orchestrator\*\* — routes requests by deterministic rules first, falling

&#x20; back to a coordinator model only for ambiguous cases.



\## Requirements



You need these installed before running anything:



1\. \*\*Python 3.12\*\* — https://www.python.org/downloads/ (check "Add to PATH" on install)

2\. \*\*Ollama\*\* — https://ollama.com (the local model server)

3\. \*\*Docker Desktop\*\* — https://www.docker.com/products/docker-desktop/ (for the code sandbox)



Then pull the models this project uses (run in a terminal):



&#x20;   ollama pull qwen3:8b

&#x20;   ollama pull qwen3:14b



(Each is several GB. The 8B is the code/worker model; the 14B is the coordinator/reasoning model.)



\## Setup



From the project folder:



&#x20;   # 1. Create and activate a virtual environment

&#x20;   py -3.12 -m venv venv

&#x20;   .\\venv\\Scripts\\Activate.ps1        # Windows PowerShell



&#x20;   # 2. Install the (minimal) dependencies

&#x20;   pip install -r requirements.txt



That's it — the core project only needs the `requests` library.



\## Running it



Make sure \*\*Ollama is running\*\* and \*\*Docker Desktop is running\*\*, then:



&#x20;   python core\\orchestrator.py



This runs the built-in self-test: one compute request (routed to the code worker,

executed in the sandbox) and one reasoning request (routed to the reasoning worker).



\## Configuration



\- \*\*Which models are used\*\* — set in `core/orchestrator.py` and `core/agent.py`

&#x20; (the `model=` arguments).

\- \*\*VRAM / model unload time\*\* — controlled by Ollama's `keep\_alive`. By default a

&#x20; model unloads from VRAM \~5 minutes after last use. To change globally, set the

&#x20; environment variable `OLLAMA\_KEEP\_ALIVE` (e.g. `30m` to keep loaded longer, `0`

&#x20; to unload immediately, `-1` to keep loaded indefinitely).

\- \*\*Sandbox hardening\*\* — security flags are set in `core/sandbox.py` (network

&#x20; disabled, memory/CPU/process caps, read-only filesystem, dropped capabilities,

&#x20; non-root user).



\## Project structure



&#x20;   core/                 The actual project (the owned, from-scratch build)

&#x20;     ollama\_client.py    Direct local LLM communication

&#x20;     sandbox.py          Hardened Docker code-execution sandbox

&#x20;     agent.py            The agent loop (think -> run code -> observe -> answer)

&#x20;     orchestrator.py     Hybrid rule + model routing to workers

&#x20;   experiments/          Earlier CrewAI-based experiments (kept for reference)

&#x20;   requirements.txt      Minimal dependencies for the core project



\## Notes



\- Fully local: no data leaves your machine. The code sandbox has no network access.

\- The `experiments/` folder contains earlier attempts using the CrewAI framework,

&#x20; kept to document the evaluation that led to the custom build. They require the

&#x20; full CrewAI dependency set, not installed by the minimal `requirements.txt`.

