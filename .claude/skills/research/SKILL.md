---
name: research
description: Evidence-first web research (Reddit, Hacker News, forums, arXiv, docs) that keeps raw pages on disk and out of context. Use whenever a task needs facts, opinions or numbers from the web.
---

# Research

carlie has had agents report Reddit threads they never fetched. Here, a claim exists only if a saved
response backs it. Research is also what fills context, so pages go to disk and you read matches.

## Before any research
1. Test each source you plan to use with one `fetch` and check `log`. Report plainly what works and
   what is blocked. Never fill a gap with search snippets, memory or guesses.
2. Reddit: `.json` endpoints are blocked (403). RSS works with `research.py`'s descriptive User-Agent
   (plain curl gets 403): `https://www.reddit.com/r/<sub>/search.rss?q=...&restrict_sr=1&sort=top&t=year`,
   comments at `<post link>.rss`. Reddit rate-limits hard, so the tool waits 10s between Reddit calls and
   retries a 429 once after 60s.

## Doing it
- `python .claude/skills/research/research.py fetch URL ...` saves every response (raw and text) and
  logs url, status, bytes, time. Non-200 or block pages are marked FAILED.
- Then `research.py grep "<pattern>" -C 1` and read only the matching lines. Open a whole page only when
  the matches show it is worth it, and then a section, not the page.
- Useful APIs: `hn.algolia.com/api/v1/search?query=...&tags=story`, `hn.algolia.com/api/v1/items/<id>`
  (comments), `export.arxiv.org/api/query?search_query=...` (wait 3s between calls),
  `code.claude.com/docs/llms.txt` and `platform.claude.com/llms.txt` (doc indexes, pages end in `.md`).
- Big passes go to a subagent or their own thread. It hands back a doc or file plus a short summary,
  not the pages. `/clear` between passes.

## Reporting
- Every quote, title and number is copied from a saved page and links to its URL.
- Keep your own inferences in a separate, labeled section. Label author-reported benchmarks as claims.
- Say what failed and what you didn't read (for example "abstracts only").
- The write-up is a document or file. The chat reply is a few lines plus its link.

## Rules
- Evidence stays out of git: it lives in `/mnt/project-files/research/` or `.research/` (gitignored).
- Never fetch with carlie's credentials or private data. In doppel, never search `data/` or `runs/`.
