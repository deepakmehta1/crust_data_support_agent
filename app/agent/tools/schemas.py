search_api_schema = {
    "type": "function",
    "function": {
        "name": "search_api",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
}
