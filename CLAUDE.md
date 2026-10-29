# butler-orchestrator

- Cross-project notes: `.claude/skills/project-notes`. Read your inbox in `halspror-dev/project-notes` when a thread starts and update your status file before it ends.
- Web research: `.claude/skills/research`. Fetch with its tool, read grep matches not whole pages, and only report what a saved page shows.
- Checking a change: run `python tools/check.py` before pushing and paste its PASS/FAIL/SKIP lines in your reply.
  It needs `pip install -r requirements.txt httpx`; the sandbox step needs Docker running. It never calls Ollama or the web.
- Before opening a PR: run the `code-review` skill on the branch and fix what it finds. A bug fix comes with a test that fails without the fix and passes with it.
- Long work keeps `state/<task>.md` (goal, done, next, what failed) and commits it as it goes. Long work and big prompts: one phase per thread (catch-up/research/design, then act, then report), each starting from the committed state file. Past ~100k context, update the state file and continue in a fresh thread. Don't keep a thread awake to watch a long run: have the run write a short summary file and check it with a few spaced `send_later` checks, each in a fresh thread that reads only the state file and the summaries. Start deep dives right after the weekly usage reset (Sat 5 AM), after checking weekly %.
