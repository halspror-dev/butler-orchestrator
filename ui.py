import sys
import os
import gradio as gr

# Make the core/ folder importable.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "core"))

from orchestrator import orchestrate, rule_based_route

def respond(message, history):
    # Show an immediate status so the UI never sits silent.
    # Peek at routing just to display the right "working" message.
    guess = rule_based_route(message)
    if guess == "code":
        yield "💻 Routing to the code worker — writing and running code in the sandbox..."
    else:
        yield "🤔 Working on it..."

    # Do the real work via the orchestrator (unchanged core).
    try:
        result = orchestrate(message)
    except Exception as e:
        yield f"(Error: {e})"
        return

    # Replace the status with the final answer.
    yield result

demo = gr.ChatInterface(
    fn=respond,
    title="Butler",
    description="Local AI orchestrator — routes to code or reasoning workers.",
)

if __name__ == "__main__":
    demo.launch()