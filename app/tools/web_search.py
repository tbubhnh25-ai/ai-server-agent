from duckduckgo_search import DDGS


def web_search(query: str, max_results: int = 5) -> tuple[bool, str]:
    """חיפוש חינמי ללא מפתח API, דרך DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return True, "לא נמצאו תוצאות"
        lines = [f"- {r['title']}: {r['href']}\n  {r['body']}" for r in results]
        return True, "\n".join(lines)
    except Exception as exc:
        return False, str(exc)
