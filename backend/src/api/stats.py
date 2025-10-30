from fastapi import APIRouter
from src.services.search_service import SearchService
from src.api.cache import cached
from src.api.executor import get_executor
import asyncio

router = APIRouter(prefix="", tags=["stats"])


@router.get("/stats")
@cached(ttl=300)
async def get_statistics():
    """
    Get overall alumni statistics including total count,
    LinkedIn profiles, current employment, etc.
    Cached for 5 minutes since this data doesn't change frequently.
    """
    loop = asyncio.get_event_loop()
    executor = get_executor()
    
    def fetch_stats():
        search_service = SearchService()
        try:
            stats = search_service.get_alumni_stats()
            return stats
        finally:
            search_service.close()
    
    return await loop.run_in_executor(executor, fetch_stats)


@router.get("/industries")
@cached(ttl=300)
async def get_industries():
    """
    Get the distribution of alumni across different industries.
    Returns a dictionary with industry names and counts.
    """
    loop = asyncio.get_event_loop()
    executor = get_executor()
    
    def fetch_industry_data():
        search_service = SearchService()
        try:
            industry_distribution = search_service.get_industry_distribution()
            return {"industries": industry_distribution}
        finally:
            search_service.close()
    
    return await loop.run_in_executor(executor, fetch_industry_data)


@router.get("/companies")
@cached(ttl=300)
async def get_top_companies():
    """
    Get the top companies where alumni are currently employed.
    Useful for understanding career outcomes and networking opportunities.
    """
    loop = asyncio.get_event_loop()
    executor = get_executor()
    
    def fetch_company_data():
        search_service = SearchService()
        try:
            top_companies = search_service.get_top_companies()
            return {"companies": top_companies}
        finally:
            search_service.close()
    
    return await loop.run_in_executor(executor, fetch_company_data)


@router.get("/locations")
@cached(ttl=300)
async def get_locations():
    """
    Get geographical distribution of alumni locations.
    Helps understand where graduates end up working.
    """
    loop = asyncio.get_event_loop()
    executor = get_executor()
    
    def fetch_location_data():
        search_service = SearchService()
        try:
            location_distribution = search_service.get_location_distribution()
            return {"locations": location_distribution}
        finally:
            search_service.close()
    
    return await loop.run_in_executor(executor, fetch_location_data)
