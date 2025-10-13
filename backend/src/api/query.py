from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from src.services.ai_query_service import AIQueryService
from src.services.web_research_service import WebResearchService

router = APIRouter(prefix="", tags=["query"])


class QueryRequest(BaseModel):
    query: str


@router.post("/query")
def ai_natural_language_query(request: QueryRequest, user_email: str = Depends(lambda: "admin")):
    ai_service = AIQueryService()
    try:
        result = ai_service.process_natural_query(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/web-research")
def research_alumni_web(names: List[str]):
    web_service = WebResearchService()
    try:
        results = web_service.research_alumni_batch(names)
        return {"research_results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
