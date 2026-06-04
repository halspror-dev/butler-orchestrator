from ddgs import DDGS

def web_search(query, max_results=5):
    """Search the web (DuckDuckGo) and return top results as text. No API key."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        return f"(web search error: {e})"

    if not results:
        return "(no results found)"

    # Format results as plain text: title, snippet, source.
    lines = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "")
        body = r.get("body", "")
        href = r.get("href", "")
        lines.append(f"{i}. {title}\n   {body}\n   (source: {href})")
    return "\n\n".join(lines)


# Self-test
if __name__ == "__main__":
    print("=== WEB SEARCH TEST ===")
    print(web_search("what is the capital of Japan"))