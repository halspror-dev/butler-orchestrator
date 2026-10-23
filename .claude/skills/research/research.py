"""Evidence-first web research: every fetch is saved and logged, and you read matches, not pages.

  python research.py fetch URL [URL ...]      save raw body + text, log url/status/bytes/time/result
  python research.py grep PATTERN [-C N]     matching lines (with source URL) from every OK page
  python research.py log                     one line per fetch, FAILED ones included

Evidence lives in $RESEARCH_DIR, else /mnt/project-files/research if it exists, else ./.research.
A non-200, a tiny body or a block page is logged FAILED and never searched. A 429 is retried once after 60s.
"""
import hashlib, html, json, os, re, sys, time, urllib.error, urllib.request
from pathlib import Path

_shared = Path("/mnt/project-files/research")
ROOT = Path(os.environ.get("RESEARCH_DIR") or (_shared if _shared.parent.is_dir() else ".research"))
LOG = ROOT / "log.jsonl"
UA = "claude-research/1.0 (by halspror-dev)"
BLOCKED = ("blocked by network security", "Just a moment...", "Access denied", "captcha")


def to_text(body):
    t = body.decode("utf-8", "replace")
    if "<html" in t[:3000].lower() or "<!doctype" in t[:200].lower():
        m = re.search(r"(?s)<article.*?</article>", t) or re.search(r"(?s)<main.*?</main>", t)
        t = m.group(0) if m else t
        t = re.sub(r"(?s)<(script|style|svg|nav|footer).*?</\1>", "", t)
        t = re.sub(r"</(p|h\d|li|pre|div|tr)>|<br\s*/?>", "\n", t)
        t = html.unescape(re.sub(r"<[^>]+>", "", t))
    return re.sub(r"\n\s*\n+", "\n\n", t)


def fetch(url, retry=True):
    rec = {"url": url, "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30) as r:
            body, rec["status"] = r.read(), r.status
    except urllib.error.HTTPError as e:
        body, rec["status"] = e.read(), e.code
    except Exception as e:
        body, rec["status"], rec["error"] = b"", None, repr(e)
    if rec["status"] == 429 and retry:
        print("429, retrying once in 60s", url)
        time.sleep(60)
        return fetch(url, retry=False)
    key = hashlib.sha1(url.encode()).hexdigest()
    rec["bytes"], rec["sha1"] = len(body), key
    (ROOT / "raw" / f"{key}.body").write_bytes(body)
    head = body[:4000].decode("utf-8", "replace").lower()
    marker = next((m for m in BLOCKED if m.lower() in head), None)
    rec["result"] = "OK" if rec["status"] == 200 and len(body) > 500 and not marker else "FAILED"
    if marker:
        rec["block_marker"] = marker
    if rec["result"] == "OK":
        (ROOT / "text" / f"{key}.txt").write_text(url + "\n\n" + to_text(body))
    with LOG.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    print(rec["result"], rec["status"], rec["bytes"], url)


def grep(pattern, context=0):
    rx = re.compile(pattern, re.I)
    for f in sorted((ROOT / "text").glob("*.txt")):
        lines = f.read_text().splitlines()
        hits = [i for i, l in enumerate(lines) if i > 1 and rx.search(l)]
        for i in hits:
            snippet = " ".join(l.strip() for l in lines[max(2, i - context): i + context + 1])
            print(f"{lines[0]} | {snippet[:600]}")


if __name__ == "__main__":
    for d in ("raw", "text"):
        (ROOT / d).mkdir(parents=True, exist_ok=True)
    cmd, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ("help", [])
    if cmd == "fetch":
        for u in args or [l.strip() for l in sys.stdin if l.strip()]:
            fetch(u)
            time.sleep(10 if "reddit.com" in u else 3)
    elif cmd == "grep" and args:
        grep(args[0], int(args[2]) if args[1:2] == ["-C"] else 0)
    elif cmd == "log" and LOG.exists():
        for l in LOG.open():
            r = json.loads(l)
            print(r["result"], r["status"], r["bytes"], r["time"], r["url"])
    else:
        print(__doc__)
