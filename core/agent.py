import re
from ollama_client import ask_ollama
from sandbox import run_code_sandboxed

# The system prompt teaches the model HOW to ask for code execution.
AGENT_SYSTEM = """You are Butler, a personal AI assistant - calm, dry-witted, concise, with a touch of class. You address the user as "sir." You respond in ENGLISH ONLY.

You can run Python code. When you need to compute, calculate, hash, or process anything precisely, do NOT guess. Instead, output a code block in EXACTLY this format:

RUN_CODE:
```python
your code here
print(the_result)
```

Your code runs in a sandbox with no internet. You MUST use print() to output every result - bare expressions (like `x, y` on a line) produce NO output in a script and will return nothing. If you want to see a value, wrap it in print(). Example: print(f"result: {value}").
After I run it, I'll give you the output. When you have the final answer, respond normally WITHOUT a RUN_CODE block, in your Butler persona.

CRITICAL: When presenting computed values (hashes, numbers, code output), reproduce them EXACTLY as the sandbox printed them - never alter, round, or paraphrase a computed value. Add personality to the framing only; the facts pass through unchanged."""

def extract_code(text):
    """Pull Python code out of a RUN_CODE block, if present."""
    if "RUN_CODE:" not in text:
        return None
    match = re.search(r"RUN_CODE:\s*```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else None

def run_agent(user_request, model="qwen3:14b", max_steps=4):
    """An agent that can think, run code in the sandbox, observe, and answer."""
    conversation = f"User request: {user_request}"

    for step in range(max_steps):
        print(f"\n--- Step {step + 1}: thinking ---")
        reply = ask_ollama(conversation, model=model, system=AGENT_SYSTEM)
        print(reply)

        code = extract_code(reply)

        if code is None:
            print("\n--- Agent finished (no more code) ---")
            return reply

        print(f"\n--- Step {step + 1}: running code in sandbox ---")
        result = run_code_sandboxed(code)
        print(f"Sandbox output: {result}")

        if not result or result.strip() in ("", "(no output)"):
            conversation += f"\n\nYou ran this code:\n{code}\n\nIt produced NO output - you forgot to print(). Re-run with print() around every value you need to see."
        else:
            conversation += f"\n\nYou ran this code:\n{code}\n\nThe output was:\n{result}\n\nNow continue. Give your final answer, or run more code if needed."

    return "(agent hit max steps without finishing)"

if __name__ == "__main__":
    answer = run_agent("What is the SHA-256 hash of the string 'butler test'? Compute it, don't guess.")
    print("\n\n=== FINAL ANSWER ===")
    print(answer)