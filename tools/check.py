#!/usr/bin/env python3
"""One pass/fail check for Butler: python tools/check.py

Runs offline: no Ollama or web calls (the model client is stubbed so a stray call fails loudly).
1. Every tracked .py file compiles.
2. Routing rules, code extraction, think-tag cleanup, memory store and the "remember" shortcut.
3. The API answers / , /memories, /save_memory, /delete_memory and /chat (needs requirements.txt + httpx).
4. The Docker sandbox runs code with no network (needs Docker running).
A step whose tools are missing prints SKIP. Exit code 0 means nothing failed.
"""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True  # keep __pycache__ out of the tree
sys.path.insert(0, os.path.join(ROOT, "core"))
sys.path.insert(0, ROOT)
results = []


def step(name, fn):
    try:
        note = fn()
        results.append("SKIP" if note else "PASS")
        print(f"{results[-1]} {name}" + (f": {note}" if note else ""))
    except Exception as e:
        results.append("FAIL")
        print(f"FAIL {name}: {type(e).__name__}: {e}")


def no_model(*a, **k):
    raise AssertionError("unexpected Ollama call")


def load_core():
    import ollama_client
    ollama_client.ask_ollama = no_model
    import memory
    memory.MEMORY_FILE = os.path.join(tempfile.mkdtemp(), "memory.json")  # fresh per step; never the real one
    import agent
    import orchestrator
    orchestrator.ask_ollama = agent.ask_ollama = no_model
    return memory, agent, orchestrator


def compile_all():
    files = subprocess.run(["git", "ls-files", "*.py"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    for f in files:
        compile(open(os.path.join(ROOT, f), encoding="utf-8").read(), f, "exec")


def logic():
    try:
        memory, agent, orch = load_core()
    except ImportError as e:
        return f"{e.name} not installed (pip install -r requirements.txt)"
    for text, want in [("search the latest news on rust", "web"), ("what is the sha256 of 'butler'", "code"),
                       ("calculate 17 factorial", "code"), ("explain TCP handshakes", "reasoning"),
                       ("hello there", None)]:
        got = orch.rule_based_route(text)
        assert got == want, f"route({text!r}) = {got!r}, expected {want!r}"
    assert agent.extract_code("RUN_CODE:\n```python\nprint(1)\n```") == "print(1)"
    assert agent.extract_code("no code here") is None
    assert orch.clean_leak("<think>\nplan\n</think>\n Good evening, sir.") == "Good evening, sir."
    assert orch.looks_personal("I work as a network engineer") and not orch.looks_personal("explain TCP")
    memory.save_memory("fact one")
    memory.save_memory("fact one")
    assert memory.load_memories() == ["fact one"], "duplicate memory saved"
    assert memory.delete_memory(0)[0] == "fact one" and memory.load_memories() == []
    worker, reply, _ = orch.orchestrate("remember that the wifi password is on the fridge")
    assert worker == "memory" and memory.load_memories() == ["the wifi password is on the fridge"], memory.load_memories()
    memory.delete_memory(0)


def api():
    try:
        import httpx  # noqa: F401  (TestClient needs it)
        from fastapi.testclient import TestClient
        load_core()
        import server
    except ImportError as e:
        return f"{e.name} not installed (pip install -r requirements.txt httpx)"
    server.orchestrate = lambda msg, history=None: ("reasoning", f"echo: {msg}", None)
    c = TestClient(server.app)
    assert c.get("/").status_code == 200
    assert c.post("/save_memory", json={"fact": "api fact"}).json()["status"] == "saved"
    assert c.get("/memories").json()["memories"] == ["api fact"]
    assert c.post("/delete_memory", json={"index": 0}).json()["removed"] == "api fact"
    assert c.post("/chat", json={"message": "hi"}).json()["reply"] == "echo: hi"


def sandbox():
    if not shutil.which("docker") or subprocess.run(["docker", "info"], capture_output=True).returncode:
        return "Docker not running"
    from sandbox import run_code_sandboxed
    if subprocess.run(["docker", "image", "inspect", "python:3.12-slim"], capture_output=True).returncode:
        subprocess.run(["docker", "pull", "-q", "python:3.12-slim"], capture_output=True, check=True)
    out = run_code_sandboxed("print(6 * 7)", timeout=120)
    assert out == "42", out
    out = run_code_sandboxed("import socket\ntry:\n    socket.create_connection(('1.1.1.1', 53), 3); print('online')\nexcept OSError:\n    print('offline')", timeout=120)
    assert out == "offline", f"sandbox has network: {out}"


step("python files compile", compile_all)
step("routing, cleanup and memory logic", logic)
step("API endpoints", api)
step("Docker sandbox", sandbox)
print("RESULT:", "FAIL" if "FAIL" in results else "PASS")
sys.exit(1 if "FAIL" in results else 0)
