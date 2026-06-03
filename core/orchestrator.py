from ollama_client import ask_ollama
from agent import run_agent

# ---- WORKERS ----
# A worker is just a function that takes a request and returns a result.

def code_worker(request):
    """Worker that can run code in the hardened sandbox (the agent loop)."""
    print("\n[Orchestrator] Routing to: CODE WORKER")
    return run_agent(request, model="qwen3:8b")

def reasoning_worker(request):
    """Worker for pure reasoning/explanation — no tools, just thinks."""
    print("\n[Orchestrator] Routing to: REASONING WORKER")
    system = "You are a clear, accurate reasoning assistant. Explain concisely and correctly."
    return ask_ollama(request, model="qwen3:14b", system=system)

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
    worker_name = rule_based_route(request)
    if worker_name is None:
        worker_name = model_based_route(request)
    worker = WORKERS[worker_name]
    return worker(request)


# Self-test: one clearly-code request, one clearly-reasoning request.
if __name__ == "__main__":
    print("\n########## TEST 1: a compute task ##########")
    r1 = orchestrate("What is the SHA-256 hash of 'butler test'?")
    print("\n>>> RESULT 1:\n", r1)

    print("\n\n########## TEST 2: a reasoning task ##########")
    r2 = orchestrate("Explain in two sentences why network segmentation improves security.")
    print("\n>>> RESULT 2:\n", r2)