import sys
import os
import gradio as gr

# Make the core/ folder importable.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "core"))

from orchestrator import orchestrate

def respond(message, history):
    # Route the message through the real orchestrator (code/reasoning workers + sandbox).
    try:
        return orchestrate(message)
    except Exception as e:
        return f"(Error: {e})"

demo = gr.ChatInterface(
    fn=respond,
    title="Butler",
    description="Local AI orchestrator — routes to code or reasoning workers."
)

if __name__ == "__main__":
    demo.launch()