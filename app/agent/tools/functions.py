from app.services.knowledge_base import search_api_doc


async def search_api(query: str) -> str:
    list_of_apis = await search_api_doc(query)
    if list_of_apis:
        first_match_api = list_of_apis[0]
        first_match_api.__delitem__("vector")
        return first_match_api
    return "No matching API found."
