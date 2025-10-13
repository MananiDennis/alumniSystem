from typing import List

def format_alumni(alumni) -> dict:
    """Format alumni profile for API response.
    This mirrors the helper previously in the monolithic main.py.
    """
    if hasattr(alumni, 'current_job_title'):
        job = {
            "title": alumni.current_job_title,
            "company": alumni.current_company
        } if alumni.current_job_title else None
    else:
        job = alumni.get_current_job()
        job = {"title": job.title, "company": job.company} if job else None

    return {
        "id": alumni.id,
        "name": getattr(alumni, 'full_name', alumni.full_name),
        "graduation_year": getattr(alumni, 'graduation_year', alumni.graduation_year),
        "location": getattr(alumni, 'location', alumni.location),
        "industry": getattr(alumni, 'industry', alumni.industry),
        "linkedin_url": getattr(alumni, 'linkedin_url', alumni.linkedin_url),
        "confidence_score": getattr(alumni, 'confidence_score', alumni.confidence_score),
        "current_job": job,
        "work_history_count": len(getattr(alumni, 'work_history', alumni.work_history)),
        "last_updated": alumni.last_updated.isoformat() if hasattr(alumni, 'last_updated') and alumni.last_updated else getattr(alumni, 'last_updated', None)
    }
