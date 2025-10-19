from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from src.services.search_service import SearchService
from src.database.connection import db_manager
from src.api.utils import format_alumni

router = APIRouter(prefix="/alumni", tags=["alumni"])


@router.get("")
def get_all_alumni():
    search = SearchService()
    try:
        alumni = search.search_alumni()
        return {"alumni": [format_alumni(a) for a in alumni]}
    finally:
        search.close()


@router.get("/{alumni_id}")
def get_alumni_by_id(alumni_id: int):
    search = SearchService()
    try:
        alumni = search.repository.get_alumni_by_id(alumni_id)
        if not alumni:
            raise HTTPException(status_code=404, detail="Alumni not found")
        return format_alumni(alumni)
    finally:
        search.close()


@router.put("/{alumni_id}")
def update_alumni(alumni_id: int, alumni_data: dict, user_email: str = Depends(lambda: "admin")):
    # Note: Replace the simple Depends with real auth verify_token where available
    try:
        from src.database.models import AlumniProfileDB
        from src.models.alumni import AlumniProfile, JobPosition, Education
        import json
        
        session = db_manager.get_session()
        try:
            profile = session.query(AlumniProfileDB).filter(AlumniProfileDB.id == alumni_id).first()
            if not profile:
                raise HTTPException(status_code=404, detail="Alumni not found")
            
            # Update basic fields
            if 'full_name' in alumni_data:
                profile.full_name = alumni_data['full_name']
            if 'graduation_year' in alumni_data:
                profile.graduation_year = alumni_data['graduation_year']
            if 'location' in alumni_data:
                profile.location = alumni_data['location']
            if 'industry' in alumni_data:
                profile.industry = alumni_data['industry']
            if 'linkedin_url' in alumni_data:
                profile.linkedin_url = alumni_data['linkedin_url']
            
            # Update work history
            if 'work_history' in alumni_data:
                # Clear existing work history
                profile.work_history = []
                for job_data in alumni_data['work_history']:
                    job = JobPosition(
                        title=job_data['title'],
                        company=job_data['company'],
                        start_date=job_data.get('start_date'),
                        end_date=job_data.get('end_date'),
                        is_current=job_data.get('is_current', False),
                        industry=job_data.get('industry'),
                        location=job_data.get('location')
                    )
                    profile.add_job_position(job)
            
            # Update education history
            if 'education_history' in alumni_data:
                # Clear existing education history
                profile.education_history = []
                for edu_data in alumni_data['education_history']:
                    education = Education(
                        institution=edu_data['institution'],
                        degree=edu_data.get('degree'),
                        field_of_study=edu_data.get('field_of_study'),
                        graduation_year=edu_data.get('graduation_year'),
                        start_year=edu_data.get('start_year')
                    )
                    profile.add_education(education)
            
            # Update confidence score if provided
            if 'confidence_score' in alumni_data:
                profile.confidence_score = alumni_data['confidence_score']
            
            session.commit()
            return {"message": "Alumni profile updated successfully", "id": alumni_id}
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update alumni profile: {str(e)}")


@router.delete("/{alumni_id}")
def delete_alumni(alumni_id: int, user_email: str = Depends(lambda: "admin")):
    # Note: Replace the simple Depends with real auth verify_token where available
    try:
        from src.database.models import AlumniProfileDB
        session = db_manager.get_session()
        try:
            profile = session.query(AlumniProfileDB).filter(AlumniProfileDB.id == alumni_id).first()
            if not profile:
                raise HTTPException(status_code=404, detail="Alumni not found")
            session.delete(profile)
            session.commit()
            return {"message": "Alumni profile deleted successfully", "id": alumni_id}
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete alumni profile: {str(e)}")
