import requests

def ask_ollama(prompt, model="qwen3:8b", system=None, timeout=70):
    """Send a prompt to local Ollama and return the text response. No framework."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False
            },
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except requests.exceptions.Timeout:
        return "(Butler timed out on that one, sir — the request was too heavy. Try breaking it into smaller parts.)"
    except requests.exceptions.RequestException as e:
        return f"(Connection error reaching the model, sir: {e})"


# Quick test when run directly
if __name__ == "__main__":
    reply = ask_ollama("Say hello and introduce yourself in one sentence.")
    print("\n=== OLLAMA REPLY ===")
    print(reply)