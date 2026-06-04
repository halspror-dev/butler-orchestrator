import sys
import os
import gradio as gr

# Make the core/ folder importable.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "core"))

from orchestrator import orchestrate, rule_based_route

# ---- Custom CSS: dark/teal "premium console" ----
CSS = """
.gradio-container {
    background: #0d1117 !important;
    font-family: 'Segoe UI', 'Inter', system-ui, sans-serif !important;
}
.gradio-container > .main, .contain {
    max-width: 820px !important;
    margin: 0 auto !important;
}#butler-header {
    text-align: center;
    padding: 10px 0 2px 0;
}
#butler-header h1 {
    color: #2dd4bf;
    font-size: 1.5rem;
    letter-spacing: 4px;
    margin: 0;
    font-weight: 600;
    font-family: 'Consolas', 'SF Mono', monospace;
}
#butler-header p {
    color: #6e7681;
    font-size: 0.8rem;
    margin: 2px 0 0 0;
    letter-spacing: 0.5px;
}
footer { display: none !important; }

/* Butler (assistant) messages: subtle teal left edge */
.message.bot, .bot-row .message, [data-testid="bot"] {
    border-left: 2px solid #2dd4bf !important;
    background: #161b22 !important;
}
/* User messages: distinct darker teal-tinted */
.message.user, .user-row .message, [data-testid="user"] {
    background: #1c2733 !important;
}
/* Monospace for code/preformatted text (hashes, code blocks) */
.message code, .message pre, .prose code, .prose pre {
    font-family: 'Consolas', 'SF Mono', monospace !important;
    color: #2dd4bf !important;
    background: #0d1117 !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
}
"""

THEME = gr.themes.Base(
    primary_hue=gr.themes.colors.teal,
    neutral_hue=gr.themes.colors.slate,
).set(
    body_background_fill="#0d1117",
    block_background_fill="#161b22",
    border_color_primary="#30363d",
)

def format_history(history):
    """Turn Gradio's history into a simple text transcript."""
    if not history:
        return ""
    lines = []
    for turn in history:
        # Gradio 6 uses dicts with 'role' and 'content'.
        if isinstance(turn, dict):
            role = turn.get("role", "")
            content = turn.get("content", "")
            who = "User" if role == "user" else "Butler"
            lines.append(f"{who}: {content}")
    return "\n".join(lines)

def respond(message, history):
    if not message.strip():
        yield "..."
        return
    guess = rule_based_route(message)
    if guess == "code":
        yield "⚙  Routing to the code worker — running in the sandbox…"
    elif guess == "web":
        yield "🌐  Searching the web…"
    else:
        yield "…  Working on it…"
    try:
        transcript = format_history(history)
        result = orchestrate(message, history=transcript)
    except Exception as e:
        yield f"(Error: {e})"
        return
    yield result

with gr.Blocks(title="Butler") as demo:
    gr.HTML(
        """
        <div id="butler-header">
            <h1>BUTLER</h1>
            <p>local · private · at your service, sir</p>
        </div>
        """
    )
    gr.ChatInterface(
        fn=respond,
        chatbot=gr.Chatbot(
            height=560,
            show_label=False,
        ),
        textbox=gr.Textbox(
            placeholder="Speak to Butler…",
            show_label=False,
            container=False,
        ),
    )

if __name__ == "__main__":
    demo.launch(theme=THEME, css=CSS)