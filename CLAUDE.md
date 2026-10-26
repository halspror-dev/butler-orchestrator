# butler-orchestrator

- Cross-project notes: `.claude/skills/project-notes`. Read your inbox in `halspror-dev/project-notes` when a thread starts and update your status file before it ends.
- Web research: `.claude/skills/research`. Fetch with its tool, read grep matches not whole pages, and only report what a saved page shows.
- Checking a change: run `python tools/check.py` before pushing and paste its PASS/FAIL/SKIP lines in your reply.
  It needs `pip install -r requirements.txt httpx`; the sandbox step needs Docker running. It never calls Ollama or the web.
