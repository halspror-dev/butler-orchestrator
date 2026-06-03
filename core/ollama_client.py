import requests

def ask_ollama(prompt, model="huihui_ai/qwen3-abliterated:14b", system=None):
    """Send a prompt to local Ollama and return the text response. No framework."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": model,
            "messages": messages,
            "stream": False
        }
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


# Quick test when run directly
if __name__ == "__main__":
    reply = ask_ollama("Say hello and introduce yourself in one sentence.")
    print("\n=== OLLAMA REPLY ===")
    print(reply)