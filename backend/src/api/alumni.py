from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from src.services.search_service import SearchService
from src.database.connection import db_manager
from src.api.utils import format_alumni
from src.api.cache import cached, cache
from src.api.executor import get_executor
import asyncio
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/alumni", tags=["alumni"])


@router.get("")
@cached(ttl=120)
async def get_all_alumni():
    """
    Retrieve all alumni profiles from the database.
    Results are cached for 2 minutes to improve performance.
    """
    start_time = time.time()
    logger.info(f"[ALUMNI] Starting get_all_alumni request")
    
    loop = asyncio.get_event_loop()
    executor = get_executor()
    
    def fetch_alumni():
        fetch_start = time.time()
        logger.info(f"[ALUMNI] Inside fetch_alumni function - elapsed: {time.time() - start_time:.3f}s")
        
        # Create search service
        service_start = time.time()
        search_service = SearchService()
        logger.info(f"[ALUMNI] SearchService created - elapsed: {time.time() - service_start:.3f}s, total: {time.time() - start_time:.3f}s")
        
        try:
            # Search for alumni
            search_start = time.time()
            logger.info(f"[ALUMNI] Calling search_alumni() - total elapsed: {time.time() - start_time:.3f}s")
            all_alumni = search_service.search_alumni()
            logger.info(f"[ALUMNI] search_alumni() completed - found {len(all_alumni)} alumni - took: {time.time() - search_start:.3f}s, total: {time.time() - start_time:.3f}s")
            
            # Format results
            format_start = time.time()
            logger.info(f"[ALUMNI] Starting to format {len(all_alumni)} alumni profiles")
            formatted_results = [format_alumni(profile) for profile in all_alumni]
            logger.info(f"[ALUMNI] Formatting completed - took: {time.time() - format_start:.3f}s, total: {time.time() - start_time:.3f}s")
            
            # Create response
            response_start = time.time()
            result = {"alumni": formatted_results}
            logger.info(f"[ALUMNI] Response created - took: {time.time() - response_start:.3f}s, total: {time.time() - start_time:.3f}s")
            
            return result
        finally:
            close_start = time.time()
            search_service.close()
            logger.info(f"[ALUMNI] Service closed - took: {time.time() - close_start:.3f}s, total: {time.time() - start_time:.3f}s")
    
    logger.info(f"[ALUMNI] Submitting to executor - elapsed: {time.time() - start_time:.3f}s")
    result = await loop.run_in_executor(executor, fetch_alumni)
    logger.info(f"[ALUMNI] Request completed - TOTAL TIME: {time.time() - start_time:.3f}s")
    
    return result


@router.get("/{alumni_id}")
@cached(ttl=180)
async def get_alumni_by_id(alumni_id: int):
    """
    Get a specific alumni profile by ID.
    Returns 404 if the profile doesn't exist.
    Results are cached for 3 minutes.
    """
    loop = asyncio.get_event_loop()
    executor = get_executor()
    
    def fetch_single_alumni():
        search_service = SearchService()
        try:
            profile = search_service.repository.get_alumni_by_id(alumni_id)
            if not profile:
                raise HTTPException(status_code=404, detail="Alumni not found")
            
            return format_alumni(profile)
        finally:
            search_service.close()
    
    return await loop.run_in_executor(executor, fetch_single_alumni)


@router.put("/{alumni_id}")
def update_alumni(alumni_id: int, alumni_data: dict, user_email: str = Depends(lambda: "admin")):
    """
    Update an existing alumni profile with new information.
    Clears the cache to ensure fresh data is served after update.
    """
    from src.database.models import AlumniProfileDB
    from src.models.alumni import JobPosition, Education
    
    session = db_manager.get_session()
    
    try:
        # Find the alumni profile
        profile = session.query(AlumniProfileDB).filter(
            AlumniProfileDB.id == alumni_id
        ).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Alumni not found")
        
        # Update basic profile information
        basic_fields = ['full_name', 'graduation_year', 'location', 'industry', 'linkedin_url']
        for field in basic_fields:
            if field in alumni_data:
                setattr(profile, field, alumni_data[field])
        
        # Handle work history updates
        if 'work_history' in alumni_data:
            profile.work_history = []
            for job_info in alumni_data['work_history']:
                new_job = JobPosition(
                    title=job_info['title'],
                    company=job_info['company'],
                    start_date=job_info.get('start_date'),
                    end_date=job_info.get('end_date'),
                    is_current=job_info.get('is_current', False),
                    industry=job_info.get('industry'),
                    location=job_info.get('location')
                )
                profile.add_job_position(new_job)
        
        # Handle education history updates
        if 'education_history' in alumni_data:
            profile.education_history = []
            for edu_info in alumni_data['education_history']:
                new_education = Education(
                    institution=edu_info['institution'],
                    degree=edu_info.get('degree'),
                    field_of_study=edu_info.get('field_of_study'),
                    graduation_year=edu_info.get('graduation_year'),
                    start_year=edu_info.get('start_year')
                )
                profile.add_education(new_education)
        
        # Update confidence score if provided
        if 'confidence_score' in alumni_data:
            profile.confidence_score = alumni_data['confidence_score']
        
        session.commit()
        cache.clear()  # Invalidate cache since data changed
        
        return {
            "message": "Alumni profile updated successfully",
            "id": alumni_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update alumni profile: {str(e)}"
        )
    finally:
        session.close()


@router.delete("/{alumni_id}")
def delete_alumni(alumni_id: int, user_email: str = Depends(lambda: "admin")):
    """
    Delete an alumni profile permanently from the database.
    This also removes all associated work history and education records.
    """
    from src.database.models import AlumniProfileDB
    
    session = db_manager.get_session()
    
    try:
        profile = session.query(AlumniProfileDB).filter(
            AlumniProfileDB.id == alumni_id
        ).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Alumni not found")
        
        session.delete(profile)
        session.commit()
        cache.clear()  # Refresh cache after deletion
        
        return {
            "message": "Alumni profile deleted successfully",
            "id": alumni_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete alumni profile: {str(e)}"
        )
    finally:
        session.close()
