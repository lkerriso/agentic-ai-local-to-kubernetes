from llama_index.core.tools import FunctionTool

from .tools import calculator, web_search

TOOLS = [
    FunctionTool.from_defaults(web_search),
    FunctionTool.from_defaults(calculator),
]
