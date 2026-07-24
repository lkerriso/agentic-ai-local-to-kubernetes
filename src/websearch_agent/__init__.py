from llama_index.core.tools import FunctionTool

from .tools import web_search

TOOLS = [FunctionTool.from_defaults(web_search)]
