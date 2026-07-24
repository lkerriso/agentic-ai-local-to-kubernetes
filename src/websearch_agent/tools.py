import ast
import math
import operator

from ddgs import DDGS

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
