from .schemas import search_api_schema
from .functions import search_api

# Tools dictionary mapping function names to actual functions
TOOLS = {"search_api": search_api}

# List of tool schemas
TOOL_SCHEMAS = [search_api_schema]


# Functions to access tools and schemas
def get_tool_schemas():
    return TOOL_SCHEMAS


def get_tools():
    return TOOLS
