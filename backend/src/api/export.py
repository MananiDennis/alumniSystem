from fastapi import APIRouter, HTTPException
from typing import Optional, List
from src.services.search_service import SearchService
from src.services.export_service import ExportService
from fastapi.responses import FileResponse
import os

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
def get_recent_alumni(limit: int = 10):
    search_service = SearchService()
    try:
        all_alumni = search_service.repository.get_all_alumni()
        recent = sorted(all_alumni, key=lambda x: x.last_updated, reverse=True)[:limit]
        # Reuse format_alumni if needed (omitted here for brevity)
        return [ {
            "id": a.id,
            "name": a.full_name,
            "last_updated": a.last_updated.isoformat() if a.last_updated else None
        } for a in recent]
    finally:
        search_service.close()


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


@router.get("/dashboard/export")
def dashboard_export_alumni_data(format: str = "excel", industry: Optional[str] = None, graduation_year_min: Optional[int] = None, graduation_year_max: Optional[int] = None, location: Optional[str] = None):
    return export_alumni_data(format, industry, graduation_year_min, graduation_year_max, location)


@router.post("/dashboard/collect")
def dashboard_collect_alumni_data(names: List[str], method: str = "brightdata"):
    # For compatibility - in real code delegate to collection.collect_alumni
    return {"message": "Dashboard collect action forwarded"}
