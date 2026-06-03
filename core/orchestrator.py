from ollama_client import ask_ollama
from agent import run_agent
from memory import save_memory, search_memories
# BigButler's persona — the charming face over the crew.
BUTLER_MODEL = "huihui_ai/qwen3-abliterated:14b"
BUTLER_SYSTEM = """You are Butler, Carlie's personal AI assistant. You are calm, dry-witted, and concise, with subtle humor and a touch of class. You address him as "sir."

CRITICAL RULE: You are the voice that delivers results produced by your team of workers. When given a result, you present it FAITHFULLY — never alter facts, numbers, hashes, code output, or technical details. If given a hash or computed value, repeat it EXACTLY. You may add brief personality to the framing, but the factual content must pass through unchanged. Accuracy first, charm second."""

def clean_leak(text):
    """Strip stray leaked tokens (abliteration artifacts) from model output."""
    import re
    text = text.strip()
    # Remove any leaked reasoning tags anywhere in the text.
    text = re.sub(r'</?think>', '', text)
    # Drop leading non-ASCII run (CJK leaks) and following punctuation/space.
    text = re.sub(r'^[^\x00-\x7F]+[\s,.:;！。、]*', '', text)
    return text.strip()

def butler_voice(user_request, raw_result):
    """Re-deliver a worker's result in Butler's persona, without altering facts."""
    prompt = (
        f"The user asked: {user_request}\n\n"
        f"Your team produced this result:\n{raw_result}\n\n"
        f"Deliver this result to the user in your voice. Keep all facts, numbers, "
        f"and technical details EXACTLY as given. Be concise and in character."
    )
    reply = ask_ollama(prompt, model=BUTLER_MODEL, system=BUTLER_SYSTEM)
    return clean_leak(reply)
# ---- WORKERS ----
# A worker is just a function that takes a request and returns a result.

def code_worker(request):
    """Worker that can run code in the hardened sandbox (the agent loop)."""
    print("\n[Orchestrator] Routing to: CODE WORKER")
    return run_agent(request, model="qwen3:8b")

def reasoning_worker(request):
    """Worker for pure reasoning/explanation — no tools, just thinks. Memory-aware."""
    print("\n[Orchestrator] Routing to: REASONING WORKER")
    system = "You are a clear, accurate reasoning assistant. Explain concisely and correctly."
    relevant = search_memories(request)
    if relevant:
        memory_note = "Relevant things you remember about the user:\n" + "\n".join(f"- {m}" for m in relevant)
        full_prompt = f"{memory_note}\n\nUser: {request}"
        print(f"[Orchestrator] Recalled {len(relevant)} memory item(s).")
    else:
        full_prompt = request
    return ask_ollama(full_prompt, model="qwen3:14b", system=system)

WORKERS = {
    "code": code_worker,
    "reasoning": reasoning_worker,
}

# ---- ROUTING ----

def rule_based_route(request):
    """Fast deterministic routing for obvious cases. Returns a worker name or None."""
    r = request.lower()
    code_keywords = ["calculate", "compute", "hash", "count", "convert",
                     "how many", "factorial", "prime", "sum of", "average",
                     "run code", "python", "encode", "decode"]
    if any(kw in r for kw in code_keywords):
        return "code"
    return None  # no clear rule -> fall back to the model

def model_based_route(request):
    """Ask a coordinator model to pick a worker, only when rules don't decide."""
    print("\n[Orchestrator] No rule matched — asking coordinator model to route...")
    system = (
        "You are a router. Given a user request, reply with EXACTLY ONE word: "
        "'code' if it needs calculation or running code, or 'reasoning' if it just "
        "needs explanation or analysis. Reply with only that one word, nothing else."
    )
    choice = ask_ollama(request, model="qwen3:14b", system=system).strip().lower()
    # Be defensive: pull a valid worker name out of whatever it said.
    if "code" in choice:
        return "code"
    return "reasoning"

def orchestrate(request):
    """The CO: route the request to the right worker (rules first, model fallback)."""
    print(f"\n=== ORCHESTRATOR received: {request} ===")

    # Memory command: "remember ..." stores a fact instead of routing.
    stripped = request.strip()
    if stripped.lower().startswith("remember"):
        fact = stripped[len("remember"):].lstrip(" :,that").strip()
        if fact:
            save_memory(fact)
            print("[Orchestrator] Saved to memory.")
            return f"Noted. I'll remember that: {fact}"
        return "There was nothing specific to remember."
# Identity questions: Butler answers directly, in character.
    r_lower = stripped.lower()
    identity_triggers = ["who are you", "who am i speaking", "what are you",
                         "your name", "introduce yourself", "who is this"]
    if any(t in r_lower for t in identity_triggers):
        print("[Orchestrator] Identity question — Butler answers directly.")
        reply = ask_ollama(stripped, model=BUTLER_MODEL, system=BUTLER_SYSTEM)
        return clean_leak(reply)

    worker_name = rule_based_route(request)
    if worker_name is None:
        worker_name = model_based_route(request)
    worker = WORKERS[worker_name]
    raw_result = worker(request)

    # Butler delivers the result in his voice (facts preserved exactly).
    print("\n[Orchestrator] Butler is delivering the result...")
    return butler_voice(request, raw_result)

# Self-test: one clearly-code request, one clearly-reasoning request.
if __name__ == "__main__":
    print("\n########## TEST 1: a compute task ##########")
    r1 = orchestrate("What is the SHA-256 hash of 'butler test'?")
    print("\n>>> RESULT 1:\n", r1)

    print("\n\n########## TEST 2: a reasoning task ##########")
    r2 = orchestrate("Explain in two sentences why network segmentation improves security.")
    print("\n>>> RESULT 2:\n", r2)