from typing import List
from fastapi import APIRouter, HTTPException, Depends
from app.models import ApiDoc, ApiDocInResponse, SuccessResponse
from app.dependencies import get_insert_api_doc, get_search_api_doc

router = APIRouter()


@router.post("/insert", response_model=SuccessResponse)
async def insert_api_doc_route(
    api_doc: ApiDoc, insert_api_doc=Depends(get_insert_api_doc)
):
    result = await insert_api_doc(api_doc)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return SuccessResponse(status=True, message=result["message"])


@router.post("/search", response_model=List[ApiDocInResponse])
async def search_api_doc_route(
    description_query: str, search_api_doc=Depends(get_search_api_doc)
):
    result = await search_api_doc(description_query)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
