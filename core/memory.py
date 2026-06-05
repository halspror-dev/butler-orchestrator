import json
import os

# Memory lives in a local file in the project root, next to core/.
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "memory.json")

def load_memories():
    """Load all stored memories. Returns a list of strings."""
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_memory(fact):
    """Add a new fact to memory. Returns the updated list."""
    memories = load_memories()
    fact = fact.strip()
    if fact and fact not in memories:   # avoid exact duplicates
        memories.append(fact)
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memories, f, indent=2)
    return memories

def delete_memory(index):
    """Delete a memory by its 0-based index. Returns (removed_fact, updated_list) or (None, list)."""
    memories = load_memories()
    if 0 <= index < len(memories):
        removed = memories.pop(index)
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memories, f, indent=2)
        return removed, memories
    return None, memories

def search_memories(query, limit=5):
    """Naive keyword search: return memories sharing words with the query."""
    memories = load_memories()
    if not memories:
        return []
    query_words = set(query.lower().split())
    scored = []
    for m in memories:
        overlap = len(query_words & set(m.lower().split()))
        if overlap > 0:
            scored.append((overlap, m))
    scored.sort(reverse=True)
    return [m for _, m in scored[:limit]]

def all_memories_text():
    """Return all memories as a simple bulleted string, for prompts."""
    memories = load_memories()
    if not memories:
        return "(no stored memories yet)"
    return "\n".join(f"- {m}" for m in memories)


# Self-test
if __name__ == "__main__":
    print("Saving a few test memories...")
    save_memory("Carlie's main GPU is an AMD RX 9070 XT with 16GB VRAM.")
    save_memory("Carlie is studying for the CompTIA Network+ exam.")
    save_memory("This project is a local multi-agent system called Butler.")

    print("\nAll memories:")
    print(all_memories_text())

    print("\nSearch for 'GPU VRAM':")
    for m in search_memories("GPU VRAM"):
        print(" -", m)