from typing import List


def format_alumni(alumni) -> dict:
    """Format alumni profile for API response.

    This mirrors the helper previously in the monolithic main.py.
    """
    try:
        # Handle job information - check for different attribute patterns
        if hasattr(alumni, 'current_job_title'):
            job = {
                "title": alumni.current_job_title,
                "company": alumni.current_job_company
            } if alumni.current_job_title else None
        else:
            current_job = getattr(alumni, 'get_current_job', lambda: None)()
            job = {"title": current_job.title, "company": current_job.company} if current_job else None

        # Industry is already a string, no conversion needed
        industry = getattr(alumni, 'industry', None)

        # Handle datetime serialization
        last_updated = getattr(alumni, 'last_updated', None)
        if last_updated and hasattr(last_updated, 'isoformat'):
            last_updated = last_updated.isoformat()

        return {
            "id": getattr(alumni, 'id', None),
            "name": getattr(alumni, 'full_name', 'Unknown'),
            "graduation_year": getattr(alumni, 'graduation_year', None),
            "location": getattr(alumni, 'location', None),
            "industry": industry,
            "linkedin_url": getattr(alumni, 'linkedin_url', None),
            "confidence_score": getattr(alumni, 'confidence_score', 0.0),
            "current_job": job,
            "work_history_count": len(getattr(alumni, 'work_history', [])),
            "last_updated": last_updated
        }
    except Exception as e:
        print(f"ERROR in format_alumni for alumni {getattr(alumni, 'id', 'unknown')}: {e}")
        import traceback
        traceback.print_exc()
        # Fallback
        return {
            "id": getattr(alumni, 'id', None),
            "name": getattr(alumni, 'full_name', 'Unknown'),
            "last_updated": getattr(alumni, 'last_updated', None)
        }