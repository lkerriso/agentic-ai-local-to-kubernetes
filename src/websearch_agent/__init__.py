from llama_index.core.tools import FunctionTool

from .tools import calculator, fetch_url, search_documents, web_search

TOOLS = [
    FunctionTool.from_defaults(web_search),
    FunctionTool.from_defaults(calculator),
    FunctionTool.from_defaults(fetch_url),
    FunctionTool.from_defaults(search_documents),
]
