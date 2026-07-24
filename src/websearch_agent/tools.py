from ddgs import DDGS


def web_search(query: str, max_results: int = 5) -> list[str]:
    """
    Search the web with DuckDuckGo and return the top results.

    Args:
        query: User query to search in web.
        max_results: Maximum number of results to return.

    Returns:
        List of results formatted as "title | url | snippet".
    """
    # LLMs sometimes emit numeric tool arguments as JSON strings
    max_results = int(max_results)
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=max_results)
    return [
        f"{r.get('title', '')} | {r.get('href', '')} | {r.get('body', '')}"
        for r in results
    ]
