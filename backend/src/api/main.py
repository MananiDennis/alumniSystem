
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd, io
import jwt
import uuid
from datetime import datetime, timedelta
from threading import Lock

from src.services.search_service import SearchService
from src.services.alumni_collector import AlumniCollector
from src.services.update_service import UpdateService
from src.services.ai_query_service import AIQueryService
from src.services.web_research_service import WebResearchService
from src.models.alumni import AlumniProfile
from src.models.user import User
from src.database.connection import db_manager
from src.config.settings import settings

# Import modular routers
from src.api import auth as auth_router
from src.api import alumni as alumni_router
from src.api import collection as collection_router
from src.api import upload as upload_router
from src.api import query as query_router
from src.api import stats as stats_router
from src.api import export as export_router
from src.api import health as health_router


# Task management for background collection
task_store: Dict[str, Dict[str, Any]] = {}
task_lock = Lock()

app = FastAPI(title="Alumni Tracking API", version="1.0.0")
# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://alumni-system-nu.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication
security = HTTPBearer()

class LoginRequest(BaseModel):
    email: str
    password: str

class QueryRequest(BaseModel):
    query: str

def create_token(user_email: str) -> str:
    """Create JWT token"""
    payload = {
        "email": user_email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token and return user email"""
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=["HS256"])
        email = payload.get("email")
        
        # Verify user exists in database
        session = db_manager.get_session()
        user = session.query(User).filter(User.email == email).first()
        session.close()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# --- Basic Endpoints ---
@app.get("/")
def home():
    """API welcome message"""
    return {"message": "Alumni Tracking System API", "version": "1.0.0"}


# Include modular routers
app.include_router(auth_router.router)
app.include_router(alumni_router.router)
app.include_router(collection_router.router)
app.include_router(upload_router.router)
app.include_router(query_router.router)
app.include_router(stats_router.router)
app.include_router(export_router.router)
app.include_router(health_router.router)


@app.get("/health")
def health_check():
    """System health check"""
    try:
        count = len(SearchService().repository.get_all_alumni())
        return {"status": "healthy", "alumni_count": count}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# --- Alumni Endpoints ---
@app.get("/alumni")
def get_all_alumni():
    """List all alumni"""
    search = SearchService()
    try:
        alumni = search.search_alumni()
        return {"alumni": [format_alumni(a) for a in alumni]}
    finally:
        search.close()


@app.get("/alumni/{alumni_id}")
def get_alumni_by_id(alumni_id: int):
    """Get alumni by ID"""
    search = SearchService()
    try:
        alumni = search.repository.get_alumni_by_id(alumni_id)
        if not alumni:
            raise HTTPException(status_code=404, detail="Alumni not found")
        return format_alumni(alumni)
    finally:
        search.close()


# --- Delete Alumni Endpoint ---
@app.delete("/alumni/{alumni_id}")
def delete_alumni(alumni_id: int, user_email: str = Depends(verify_token)):
    """Delete an alumni profile and all related data"""
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


class ManualCollectRequest(BaseModel):
    full_name: str
    graduation_year: Optional[int] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    linkedin_url: Optional[str] = None
    current_job_title: Optional[str] = None
    current_job_company: Optional[str] = None
    current_job_start_date: Optional[str] = None
    current_job_industry: Optional[str] = None
    current_job_location: Optional[str] = None
    work_history: Optional[str] = None
    education: Optional[str] = None


@app.put("/alumni/{alumni_id}")
def update_alumni(alumni_id: int, request: ManualCollectRequest, user_email: str = Depends(verify_token)):
    """Update alumni profile"""
    try:
        from src.database.models import AlumniProfileDB, WorkHistoryDB, DataSourceDB
        from datetime import date
        
        session = db_manager.get_session()
        try:
            # Get existing alumni profile
            profile = session.query(AlumniProfileDB).filter(AlumniProfileDB.id == alumni_id).first()
            if not profile:
                raise HTTPException(status_code=404, detail="Alumni not found")
            
            # Update basic fields
            profile.full_name = request.full_name
            profile.graduation_year = request.graduation_year
            profile.location = request.location
            profile.industry = request.industry
            profile.linkedin_url = request.linkedin_url
            profile.current_job_title = request.current_job_title
            profile.current_company = request.current_job_company
            
            # Delete existing work history and recreate
            session.query(WorkHistoryDB).filter(WorkHistoryDB.alumni_id == alumni_id).delete()
            
            # Add current job to work history if provided
            if request.current_job_title and request.current_job_company:
                current_job = WorkHistoryDB(
                    alumni_id=profile.id,
                    job_title=request.current_job_title,
                    company=request.current_job_company,
                    start_date=date.fromisoformat(request.current_job_start_date) if request.current_job_start_date else None,
                    industry=request.current_job_industry,
                    location=request.current_job_location,
                    is_current=True
                )
                session.add(current_job)
            
            # Parse and add work history
            if request.work_history:
                for line in request.work_history.strip().split('\n'):
                    if line.strip():
                        # Simple parsing: Title - Company - Start - End - Industry - Location
                        parts = [p.strip() for p in line.split('-')]
                        if len(parts) >= 2:
                            title = parts[0]
                            company = parts[1]
                            start_date = None
                            end_date = None
                            industry = None
                            location = None
                            
                            if len(parts) >= 3 and parts[2]:
                                try:
                                    start_date = date.fromisoformat(parts[2])
                                except:
                                    pass
                            if len(parts) >= 4 and parts[3]:
                                try:
                                    end_date = date.fromisoformat(parts[3])
                                except:
                                    pass
                            if len(parts) >= 5 and parts[4]:
                                industry = parts[4]
                            if len(parts) >= 6 and parts[5]:
                                location = parts[5]
                            
                            work_entry = WorkHistoryDB(
                                alumni_id=profile.id,
                                job_title=title,
                                company=company,
                                start_date=start_date,
                                end_date=end_date,
                                industry=industry,
                                location=location,
                                is_current=False
                            )
                            session.add(work_entry)
            
            # Update data source
            data_source = session.query(DataSourceDB).filter(DataSourceDB.alumni_id == alumni_id).first()
            if data_source:
                data_source.source_url = request.linkedin_url
            else:
                # Create new data source if it doesn't exist
                data_source = DataSourceDB(
                    alumni_id=profile.id,
                    source_type="manual",
                    source_url=request.linkedin_url,
                    confidence_score=1.0
                )
                session.add(data_source)
            
            session.commit()
            session.refresh(profile)
            
            return {
                "message": "Alumni profile updated successfully",
                "profile": format_alumni(profile)
            }
        finally:
            session.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update alumni profile: {str(e)}")


@app.get("/search")
def search_alumni(name: str = None, industry: str = None, company: str = None, location: str = None):
    """Search alumni with filters"""
    search = SearchService()
    try:
        results = search.search_alumni(name=name, industry=industry, company=company, location=location)
        return {"results": [format_alumni(a) for a in results]}
    finally:
        search.close()


@app.get("/stats")
def get_statistics():
    """Get alumni statistics"""
    search = SearchService()
    try:
        return search.get_alumni_stats()
    finally:
        search.close()


# --- Collection Endpoints ---
class CollectRequest(BaseModel):
    names: List[str]
    use_web_research: bool = False

@app.post("/collect")
def collect_alumni(request: CollectRequest, background_tasks: BackgroundTasks, user_email: str = Depends(verify_token)):
    """Collect alumni using web research (default) or BrightData"""
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Initialize task
    with task_lock:
        task_store[task_id] = {
            "status": "running",
            "names": request.names,
            "method": "web-research" if request.use_web_research else "brightdata",
            "start_time": datetime.utcnow(),
            "results_count": 0,
            "results": [],
            "error": None
        }
    
    # Start background collection
    background_tasks.add_task(run_collection_task, task_id, request.names, request.use_web_research)
    
    return {
        "task_id": task_id,
        "message": "Collection started",
        "status": "running"
    }

def run_collection_task(task_id: str, names: List[str], use_web_research: bool):
    """Background task to run alumni collection"""
    collector = None
    try:
        collector = AlumniCollector()
        method = "web-research" if use_web_research else "brightdata"
        profiles = collector.collect_alumni(names, method=method)
        
        # Update task with results
        with task_lock:
            if len(profiles) == 0:
                task_store[task_id].update({
                    "status": "failed",
                    "error": "No alumni profiles were collected. This may be due to low confidence scores or no matching information found.",
                    "end_time": datetime.utcnow()
                })
            else:
                task_store[task_id].update({
                    "status": "completed",
                    "results_count": len(profiles),
                    "results": [format_alumni(p) for p in profiles],
                    "end_time": datetime.utcnow()
                })
            
    except Exception as e:
        # Update task with error
        with task_lock:
            task_store[task_id].update({
                "status": "failed",
                "error": str(e),
                "end_time": datetime.utcnow()
            })
    finally:
        if collector:
            collector.close()

@app.get("/collect/status/{task_id}")
def get_collect_status(task_id: str, user_email: str = Depends(verify_token)):
    """Get collection task status"""
    with task_lock:
        task = task_store.get(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task_id,
        "status": task["status"],
        "results_count": task.get("results_count", 0),
        "results": task.get("results", []),
        "error": task.get("error"),
        "start_time": task.get("start_time").isoformat() if task.get("start_time") else None,
        "end_time": task.get("end_time").isoformat() if task.get("end_time") else None
    }

@app.post("/manual-collect")
def manual_collect_alumni(request: ManualCollectRequest, user_email: str = Depends(verify_token)):
    """Manually add alumni data"""
    try:
        from src.database.models import AlumniProfileDB, WorkHistoryDB, DataSourceDB
        from datetime import date
        
        # Save to database using SQLAlchemy models
        session = db_manager.get_session()
        try:
            # Create alumni profile
            profile = AlumniProfileDB(
                full_name=request.full_name,
                graduation_year=request.graduation_year,
                location=request.location,
                industry=request.industry,
                linkedin_url=request.linkedin_url,
                current_job_title=request.current_job_title,
                current_company=request.current_job_company,
                confidence_score=1.0  # Manual entries have full confidence
            )
            session.add(profile)
            session.flush()  # Get the ID
            
            # Add current job to work history if provided
            if request.current_job_title and request.current_job_company:
                current_job = WorkHistoryDB(
                    alumni_id=profile.id,
                    job_title=request.current_job_title,
                    company=request.current_job_company,
                    start_date=date.fromisoformat(request.current_job_start_date) if request.current_job_start_date else None,
                    industry=request.current_job_industry,
                    location=request.current_job_location,
                    is_current=True
                )
                session.add(current_job)
            
            # Parse and add work history
            if request.work_history:
                for line in request.work_history.strip().split('\n'):
                    if line.strip():
                        # Simple parsing: Title - Company - Start - End - Industry - Location
                        parts = [p.strip() for p in line.split('-')]
                        if len(parts) >= 2:
                            title = parts[0]
                            company = parts[1]
                            start_date = None
                            end_date = None
                            industry = None
                            location = None
                            
                            if len(parts) >= 3 and parts[2]:
                                try:
                                    start_date = date.fromisoformat(parts[2])
                                except:
                                    pass
                            if len(parts) >= 4 and parts[3]:
                                try:
                                    end_date = date.fromisoformat(parts[3])
                                except:
                                    pass
                            if len(parts) >= 5 and parts[4]:
                                industry = parts[4]
                            if len(parts) >= 6 and parts[5]:
                                location = parts[5]
                            
                            work_entry = WorkHistoryDB(
                                alumni_id=profile.id,
                                job_title=title,
                                company=company,
                                start_date=start_date,
                                end_date=end_date,
                                industry=industry,
                                location=location,
                                is_current=False
                            )
                            session.add(work_entry)
            
            # Add data source
            data_source = DataSourceDB(
                alumni_id=profile.id,
                source_type="manual",
                source_url=request.linkedin_url,
                confidence_score=1.0
            )
            session.add(data_source)
            
            session.commit()
            session.refresh(profile)
            
            return {
                "message": "Alumni data saved successfully",
                "profile": {
                    "id": profile.id,
                    "name": profile.full_name,
                    "graduation_year": profile.graduation_year,
                    "location": profile.location,
                    "industry": profile.industry,
                    "linkedin_url": profile.linkedin_url,
                    "confidence_score": profile.confidence_score,
                    "current_job": {
                        "title": profile.current_job_title, 
                        "company": profile.current_company
                    } if profile.current_job_title else None,
                    "last_updated": profile.last_updated.isoformat() if profile.last_updated else None
                }
            }
        finally:
            session.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save manual data: {str(e)}")

@app.post("/query")
def ai_natural_language_query(request: QueryRequest, user_email: str = Depends(verify_token)):
    """Process natural language queries about alumni"""
    ai_service = AIQueryService()
    try:
        result = ai_service.process_natural_query(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/web-research")
def research_alumni_web(names: List[str]):
    """Research alumni using web search"""
    web_service = WebResearchService()
    try:
        results = web_service.research_alumni_batch(names)
        return {"research_results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/login")
def login(request: LoginRequest):
    """Authenticate user and return JWT token"""
    session = db_manager.get_session()
    try:
        user = session.query(User).filter(User.email == request.email).first()
        
        if not user or not user.check_password(request.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Update last login
        user.last_login = datetime.utcnow()
        session.commit()
        
        # Create token
        token = create_token(user.email)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user.to_dict()
        }
    finally:
        session.close()

@app.get("/auth/me")
def get_current_user(user_email: str = Depends(verify_token)):
    """Get current user info"""
    session = db_manager.get_session()
    try:
        user = session.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.to_dict()
    finally:
        session.close()


@app.post("/upload-names")
async def upload_names_file(file: UploadFile = File(...), auto_collect: bool = False, user_email: str = Depends(verify_token)):
    """Upload Excel file and optionally auto-collect alumni data"""
    try:
        if not file.filename.endswith((".xlsx", ".xls", ".csv")):
            raise HTTPException(status_code=400, detail="File must be an Excel file (.xlsx, .xls) or CSV file (.csv)")
        
        # Read file based on extension
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(await file.read()))
        else:
            df = pd.read_excel(io.BytesIO(await file.read()))
        for col in ['GIVEN NAME', 'FIRST NAME']:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Missing required column: {col}")
        names = [f"{row['GIVEN NAME']} {row['FIRST NAME']}".strip() for _, row in df.iterrows() if pd.notna(row['GIVEN NAME']) and pd.notna(row['FIRST NAME'])]
        profiles = []
        if auto_collect and names:
            try:
                collector = AlumniCollector()
                profiles = collector.collect_alumni(names)
                collector.close()
            except Exception as collect_error:
                # Log the error but don't fail the upload
                print(f"Auto-collection failed: {collect_error}")
                # Still return the names even if collection fails
        return {
            "success": True,
            "names": names,
            "count": len(names),
            "collected_profiles": [format_alumni(p) for p in profiles],
            "profiles_collected": len(profiles),
            "message": f"Loaded {len(names)} names from {file.filename}" + (f", collected {len(profiles)} profiles" if profiles else "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/update")
def update_profiles(profile_ids: Optional[List[int]] = None):
    """Update existing profiles"""
    update_service = UpdateService()
    try:
        if profile_ids:
            updated = update_service.update_profiles_by_ids(profile_ids)
        else:
            updated = update_service.update_all_profiles()
        
        return {
            "message": f"Updated {len(updated)} profiles",
            "profiles": [format_alumni(p) for p in updated]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        update_service.close()

@app.get("/industries")
def get_industries():
    """Get industry distribution"""
    search_service = SearchService()
    try:
        distribution = search_service.get_industry_distribution()
        return {"industries": distribution}
    finally:
        search_service.close()

@app.get("/companies")
def get_top_companies():
    """Get top companies"""
    search_service = SearchService()
    try:
        companies = search_service.get_top_companies()
        return {"companies": companies}
    finally:
        search_service.close()

@app.get("/locations")
def get_locations():
    """Get location distribution"""
    search_service = SearchService()
    try:
        distribution = search_service.get_location_distribution()
        return {"locations": distribution}
    finally:
        search_service.close()

# Dashboard endpoints (for frontend compatibility)
@app.get("/dashboard/stats")
def get_dashboard_stats(user_email: str = Depends(verify_token)):
    """Get dashboard statistics"""
    search_service = SearchService()
    try:
        stats = search_service.get_alumni_stats()
        # Add additional stats for frontend
        alumni = search_service.repository.get_all_alumni()
        stats.update({
            "with_linkedin": len([a for a in alumni if a.linkedin_url]),
            "with_current_job": len([a for a in alumni if a.get_current_job()]),
            "average_confidence": sum(a.confidence_score for a in alumni) / len(alumni) if alumni else 0
        })
        return stats
    finally:
        search_service.close()

@app.get("/dashboard/export")
def dashboard_export_alumni_data(
    format: str = "excel",
    industry: Optional[str] = None,
    graduation_year_min: Optional[int] = None,
    graduation_year_max: Optional[int] = None,
    location: Optional[str] = None
):
    """Dashboard export - same as main export"""
    return export_alumni_data(format, industry, graduation_year_min, graduation_year_max, location)

@app.get("/dashboard/recent")
def dashboard_get_recent_alumni(limit: int = 10):
    """Dashboard recent alumni - same as main recent"""
    return get_recent_alumni(limit)

@app.post("/dashboard/collect")
def dashboard_collect_alumni_data(names: List[str], method: str = "brightdata"):
    """Dashboard collect - same as main collect"""
    return collect_alumni(names, method)

@app.get("/export")
def export_alumni_data(
    format: str = "excel",
    industry: Optional[str] = None,
    graduation_year_min: Optional[int] = None,
    graduation_year_max: Optional[int] = None,
    location: Optional[str] = None
):
    """Export alumni data"""
    from src.services.export_service import ExportService
    from fastapi.responses import FileResponse
    import os
    
    search_service = SearchService()
    export_service = ExportService()
    
    try:
        # Get filtered alumni
        alumni = search_service.search_alumni(
            industry=industry,
            graduation_year_min=graduation_year_min,
            graduation_year_max=graduation_year_max,
            location=location
        )
        
        if not alumni:
            raise HTTPException(status_code=404, detail="No alumni found")
        
        # Export data
        if format.lower() == "csv":
            filename = export_service.export_to_csv(alumni)
        else:
            filename = export_service.export_to_excel(alumni)
        
        # Return file
        if os.path.exists(filename):
            return FileResponse(
                path=filename,
                filename=filename,
                media_type='application/octet-stream'
            )
        else:
            raise HTTPException(status_code=500, detail="Export file not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
    finally:
        search_service.close()

@app.get("/recent")
def get_recent_alumni(limit: int = 10):
    """Get recently added alumni"""
    search_service = SearchService()
    try:
        all_alumni = search_service.repository.get_all_alumni()
        recent = sorted(all_alumni, key=lambda x: x.last_updated, reverse=True)[:limit]
        return [format_alumni(alumni) for alumni in recent]
    finally:
        search_service.close()

@app.get("/health")
def health_check():
    """System health check"""
    try:
        search_service = SearchService()
        alumni_count = len(search_service.repository.get_all_alumni())
        search_service.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "alumni_count": alumni_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# --- Helper ---
def format_alumni(alumni) -> dict:
    """Format alumni profile for API response"""
    # Handle both SQLAlchemy models and dataclasses
    if hasattr(alumni, 'current_job_title'):  # SQLAlchemy model
        job = {
            "title": alumni.current_job_title,
            "company": alumni.current_company
        } if alumni.current_job_title else None
    else:  # Dataclass
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

    # NOTE: Application is launched via `backend/main.py`.
    # The previous `if __name__ == '__main__'` block was removed to avoid
    # accidentally starting the server when this module is imported.