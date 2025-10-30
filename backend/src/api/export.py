from fastapi import APIRouter, HTTPException
from typing import Optional, List
from src.services.search_service import SearchService
from src.services.export_service import ExportService
from src.api.cache import cached
from src.api.executor import get_executor
from fastapi.responses import FileResponse
import os
import asyncio

router = APIRouter(prefix="", tags=["export"])


@router.get("/export")
def export_alumni_data(
    format: str = "excel",
    industry: Optional[str] = None,
    graduation_year_min: Optional[int] = None,
    graduation_year_max: Optional[int] = None,
    location: Optional[str] = None
):
    search_service = SearchService()
    export_service = ExportService()
    try:
        alumni = search_service.search_alumni(
            industry=industry,
            graduation_year_min=graduation_year_min,
            graduation_year_max=graduation_year_max,
            location=location
        )

        if not alumni:
            raise HTTPException(status_code=404, detail="No alumni found")

        if format.lower() == "csv":
            filename = export_service.export_to_csv(alumni)
        else:
            filename = export_service.export_to_excel(alumni)

        if os.path.exists(filename):
            return FileResponse(path=filename, filename=filename, media_type='application/octet-stream')
        else:
            raise HTTPException(status_code=500, detail="Export file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
    finally:
        search_service.close()


@router.get("/recent")
@cached(ttl=60)
async def get_recent_alumni(limit: int = 10):
    """
    Get the most recently updated alumni profiles.
    Short cache time (1 minute) since this updates frequently.
    """
    loop = asyncio.get_event_loop()
    executor = get_executor()
    
    def fetch_recent_alumni():
        search_service = SearchService()
        try:
            # Fetch more than we need to account for sorting
            all_profiles = search_service.repository.get_all_alumni(
                limit=limit * 2, 
                offset=0
            )
            
            # Sort by last updated date and take the most recent
            sorted_profiles = sorted(
                all_profiles, 
                key=lambda profile: profile.last_updated, 
                reverse=True
            )
            recent_profiles = sorted_profiles[:limit]
            
            # Format the response
            results = []
            for profile in recent_profiles:
                alumni_data = {
                    "id": profile.id,
                    "name": profile.full_name,
                    "graduation_year": profile.graduation_year,
                    "location": profile.location,
                    "industry": profile.industry,
                    "current_job": None,
                    "last_updated": profile.last_updated.isoformat() if profile.last_updated else None
                }
                
                if profile.current_position:
                    alumni_data["current_job"] = {
                        "title": profile.current_position.title,
                        "company": profile.current_position.company
                    }
                
                results.append(alumni_data)
            
            return results
        finally:
            search_service.close()
    
    return await loop.run_in_executor(executor, fetch_recent_alumni)


@router.get("/dashboard/stats")
def get_dashboard_stats():
    search_service = SearchService()
    try:
        stats = search_service.get_alumni_stats()
        alumni = search_service.repository.get_all_alumni()
        stats.update({
            "with_linkedin": len([a for a in alumni if a.linkedin_url]),
            "with_current_job": len([a for a in alumni if a.get_current_job()]),
            "average_confidence": sum(a.confidence_score for a in alumni) / len(alumni) if alumni else 0
        })
        return stats
    finally:
        search_service.close()


@router.get("/dashboard/graduation-years")
@cached(ttl=300)
async def get_graduation_year_distribution():
    """
    Get distribution of alumni grouped by graduation year.
    Useful for understanding cohort sizes over time.
    """
    loop = asyncio.get_event_loop()
    executor = get_executor()
    
    def fetch_year_distribution():
        search_service = SearchService()
        try:
            distribution = search_service.get_graduation_year_distribution()
            return distribution
        finally:
            search_service.close()
    
    return await loop.run_in_executor(executor, fetch_year_distribution)


@router.get("/dashboard/confidence-scores")
@cached(ttl=300)
async def get_confidence_score_distribution():
    """
    Get distribution of data confidence scores in ranges.
    Helps assess overall data quality for alumni profiles.
    """
    loop = asyncio.get_event_loop()
    executor = get_executor()
    
    def fetch_confidence_distribution():
        search_service = SearchService()
        try:
            scores = search_service.get_confidence_score_distribution()
            return scores
        finally:
            search_service.close()
    
    return await loop.run_in_executor(executor, fetch_confidence_distribution)


@router.get("/dashboard/export")
def dashboard_export_alumni_data(format: str = "excel", industry: Optional[str] = None, graduation_year_min: Optional[int] = None, graduation_year_max: Optional[int] = None, location: Optional[str] = None):
    return export_alumni_data(format, industry, graduation_year_min, graduation_year_max, location)


@router.post("/dashboard/collect")
def dashboard_collect_alumni_data(names: List[str], method: str = "brightdata"):
    # For compatibility - in real code delegate to collection.collect_alumni
    return {"message": "Dashboard collect action forwarded"}
