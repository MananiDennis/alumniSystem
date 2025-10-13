from fastapi import APIRouter
from src.services.search_service import SearchService

router = APIRouter(prefix="", tags=["stats"])


@router.get("/stats")
def get_statistics():
    search = SearchService()
    try:
        return search.get_alumni_stats()
    finally:
        search.close()


@router.get("/industries")
def get_industries():
    search_service = SearchService()
    try:
        distribution = search_service.get_industry_distribution()
        return {"industries": distribution}
    finally:
        search_service.close()


@router.get("/companies")
def get_top_companies():
    search_service = SearchService()
    try:
        companies = search_service.get_top_companies()
        return {"companies": companies}
    finally:
        search_service.close()


@router.get("/locations")
def get_locations():
    search_service = SearchService()
    try:
        distribution = search_service.get_location_distribution()
        return {"locations": distribution}
    finally:
        search_service.close()
