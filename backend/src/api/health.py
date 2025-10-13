from fastapi import APIRouter
from src.services.search_service import SearchService

router = APIRouter(prefix="", tags=["health"])


@router.get("/health")
def health_check():
    try:
        search_service = SearchService()
        alumni_count = len(search_service.repository.get_all_alumni())
        search_service.close()
        return {"status": "healthy", "database": "connected", "alumni_count": alumni_count}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
