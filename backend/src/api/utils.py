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

        # Format work history
        work_history = []
        for job_pos in getattr(alumni, 'work_history', []):
            work_history.append({
                "title": job_pos.title,
                "company": job_pos.company,
                "start_date": job_pos.start_date.isoformat() if job_pos.start_date else None,
                "end_date": job_pos.end_date.isoformat() if job_pos.end_date else None,
                "is_current": job_pos.is_current,
                "industry": job_pos.industry,
                "location": job_pos.location
            })

        # Format education history
        education_history = []
        for edu in getattr(alumni, 'education_history', []):
            education_history.append({
                "institution": edu.institution,
                "degree": edu.degree,
                "field_of_study": edu.field_of_study,
                "graduation_year": edu.graduation_year,
                "start_year": edu.start_year
            })

        return {
            "id": getattr(alumni, 'id', None),
            "name": getattr(alumni, 'full_name', 'Unknown'),
            "graduation_year": getattr(alumni, 'graduation_year', None),
            "location": getattr(alumni, 'location', None),
            "industry": industry,
            "linkedin_url": getattr(alumni, 'linkedin_url', None),
            "confidence_score": getattr(alumni, 'confidence_score', 0.0),
            "current_job": job,
            "work_history": work_history,
            "education_history": education_history,
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