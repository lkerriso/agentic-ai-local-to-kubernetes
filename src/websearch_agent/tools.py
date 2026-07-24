import ast
import math
import operator
from os import getenv

import httpx
from bs4 import BeautifulSoup
from ddgs import DDGS

VECTOR_STORE_NAME = "knowledge_base"

_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_ALLOWED_NAMES = {
    "pi": math.pi,
    "e": math.e,
    "sqrt": math.sqrt,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "abs": abs,
    "round": round,
}


def fetch_url(url: str, max_chars: int = 4000) -> str:
    """
    Fetch a web page and return its readable text content.

    Useful after web_search to read the full content of a result.

    Args:
        url: The http(s) URL to fetch.
        max_chars: Maximum number of characters to return.

    Returns:
        The page's text content (HTML stripped), or an error message.
    """
    max_chars = int(max_chars)
    if not url.startswith(("http://", "https://")):
        return "Error: only http(s) URLs are supported"
    try:
        resp = httpx.get(
            url,
            follow_redirects=True,
            timeout=15,
            headers={"User-Agent": "websearch-agent/0.1"},
        )
        resp.raise_for_status()
    except Exception as e:
        return f"Error fetching URL: {e}"

    if "html" in resp.headers.get("content-type", ""):
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = " ".join(soup.get_text(" ").split())
    else:
        text = resp.text
    return text[:max_chars] if text else "No text content found"


def search_documents(query: str, max_results: int = 3) -> list[str]:
    """
    Search the local knowledge base for relevant document passages.

    The knowledge base is a vector store served by the OGX server and
    contains this project's documentation. Use it for questions about
    this repository, its architecture, or its deployment process.

    Args:
        query: Natural-language query to search for.
        max_results: Maximum number of passages to return.

    Returns:
        List of matching passages formatted as "source: passage".
    """
    max_results = int(max_results)
    base_url = getenv("OGX_BASE_URL", "http://localhost:8321")
    try:
        stores = httpx.get(f"{base_url}/v1/vector_stores", timeout=15).json()
        store_id = next(
            (
                s["id"]
                for s in stores.get("data", [])
                if s.get("name") == VECTOR_STORE_NAME
            ),
            None,
        )
        if not store_id:
            return [
                "No knowledge base found. Ingest documents first: "
                "uv run python examples/ingest_docs.py"
            ]
        resp = httpx.post(
            f"{base_url}/v1/vector-io/query",
            json={
                "vector_store_id": store_id,
                "query": query,
                "params": {"max_chunks": max_results},
            },
            timeout=60,
        )
        resp.raise_for_status()
        chunks = resp.json().get("chunks", [])[:max_results]
    except Exception as e:
        return [f"Error querying knowledge base: {e}"]

    if not chunks:
        return ["No matching documents found."]
    return [
        f"{c.get('metadata', {}).get('document_id', 'unknown')}: {c.get('content', '')}"
        for c in chunks
    ]


def _eval_node(node: ast.expr) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise ValueError("Exponent too large")
        return _BINARY_OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval_node(node.operand))
    if isinstance(node, ast.Name) and node.id in _ALLOWED_NAMES:
        return _ALLOWED_NAMES[node.id]
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in _ALLOWED_NAMES
        and callable(_ALLOWED_NAMES[node.func.id])
        and not node.keywords
    ):
        return _ALLOWED_NAMES[node.func.id](*[_eval_node(arg) for arg in node.args])
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression and return the result.

    Supports +, -, *, /, //, %, ** (power), parentheses, the constants
    pi and e, and the functions sqrt, log, log10, exp, sin, cos, tan,
    abs, and round.

    Args:
        expression: Mathematical expression to evaluate, e.g. "(2 + 3) * sqrt(16)".

    Returns:
        The numeric result as a string, or an error message.
    """
    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval_node(tree.body)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"


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
