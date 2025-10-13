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
