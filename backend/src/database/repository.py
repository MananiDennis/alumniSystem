from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from src.database.models import AlumniProfileDB, WorkHistoryDB, DataSourceDB
from src.models.alumni import AlumniProfile, JobPosition, DataSource, IndustryType
import json
from datetime import datetime


class AlumniRepository:
    """Repository for CRUD operations with the alumni data"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_alumni(self, alumni: AlumniProfile) -> AlumniProfile:
        # Create a new alumni profile
        db_alumni = AlumniProfileDB(
            full_name=alumni.full_name,
            graduation_year=alumni.graduation_year,
            current_job_title=alumni.current_position.title if alumni.current_position else None,
            current_company=alumni.current_position.company if alumni.current_position else None,
            industry=alumni.industry.value if alumni.industry else None,
            location=alumni.location,
            linkedin_url=alumni.linkedin_url,
            confidence_score=alumni.confidence_score,
            last_updated=alumni.last_updated
        )
        
        self.session.add(db_alumni)
        self.session.flush()  # Get the ID
        
        # Add work history
        for job in alumni.work_history:
            self.add_work_history(db_alumni.id, job)
        
        # Add data sources
        for source in alumni.data_sources:
            self.add_data_source(db_alumni.id, source)
        
        self.session.commit()
        
        # Return updated alumni with ID
        alumni.id = db_alumni.id
        return alumni
    
    def get_alumni_by_id(self, alumni_id: int) -> Optional[AlumniProfile]:
        """Get alumni by ID"""
        db_alumni = self.session.query(AlumniProfileDB).filter(
            AlumniProfileDB.id == alumni_id
        ).first()
        
        if not db_alumni:
            return None
        
        return self.convert_db_to_alumni_profile(db_alumni)
    
    def get_alumni_by_name(self, name: str) -> List[AlumniProfile]:
        """Get alumni by name (partial match)"""
        db_alumni_list = self.session.query(AlumniProfileDB).filter(
            AlumniProfileDB.full_name.ilike(f"%{name}%")
        ).all()
        
        return [self.convert_db_to_alumni_profile(db_alumni) for db_alumni in db_alumni_list]
    
    def search_alumni(self, 
                     name: Optional[str] = None,
                     industry: Optional[str] = None,
                     company: Optional[str] = None,
                     location: Optional[str] = None,
                     graduation_year_min: Optional[int] = None,
                     graduation_year_max: Optional[int] = None) -> List[AlumniProfile]:
        """Search alumni with multiple filters"""
        query = self.session.query(AlumniProfileDB)
        
        if name:
            query = query.filter(AlumniProfileDB.full_name.ilike(f"%{name}%"))
        
        if industry:
            query = query.filter(AlumniProfileDB.industry == industry)
        
        if company:
            query = query.filter(AlumniProfileDB.current_company.ilike(f"%{company}%"))
        
        if location:
            query = query.filter(AlumniProfileDB.location.ilike(f"%{location}%"))
        
        if graduation_year_min:
            query = query.filter(AlumniProfileDB.graduation_year >= graduation_year_min)
        
        if graduation_year_max:
            query = query.filter(AlumniProfileDB.graduation_year <= graduation_year_max)
        
        db_alumni_list = query.all()
        return [self.convert_db_to_alumni_profile(db_alumni) for db_alumni in db_alumni_list]
    
    def update_alumni(self, alumni: AlumniProfile) -> AlumniProfile:
        """Update an existing alumni profile"""
        if not alumni.id:
            raise ValueError("Alumni ID is required for update")
        
        db_alumni = self.session.query(AlumniProfileDB).filter(
            AlumniProfileDB.id == alumni.id
        ).first()
        
        if not db_alumni:
            raise ValueError(f"Alumni with ID {alumni.id} not found")
        
        # Update basic fields
        db_alumni.full_name = alumni.full_name
        db_alumni.graduation_year = alumni.graduation_year
        db_alumni.current_job_title = alumni.current_position.title if alumni.current_position else None
        db_alumni.current_company = alumni.current_position.company if alumni.current_position else None
        db_alumni.industry = alumni.industry.value if alumni.industry else None
        db_alumni.location = alumni.location
        db_alumni.linkedin_url = alumni.linkedin_url
        db_alumni.confidence_score = alumni.confidence_score
        db_alumni.last_updated = datetime.utcnow()
        
        # Update work history (delete and recreate for simplicity)
        self.session.query(WorkHistoryDB).filter(
            WorkHistoryDB.alumni_id == alumni.id
        ).delete()
        
        for job in alumni.work_history:
            self.add_work_history(alumni.id, job)
        
        self.session.commit()
        return alumni
    
    def delete_alumni(self, alumni_id: int) -> bool:
        """Delete an alumni profile"""
        db_alumni = self.session.query(AlumniProfileDB).filter(
            AlumniProfileDB.id == alumni_id
        ).first()
        
        if not db_alumni:
            return False
        
        self.session.delete(db_alumni)
        self.session.commit()
        return True
    
    def get_all_alumni(self, limit: Optional[int] = None, offset: int = 0) -> List[AlumniProfile]:
        """Get all alumni with optional pagination"""
        query = self.session.query(AlumniProfileDB).offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        db_alumni_list = query.all()
        return [self.convert_db_to_alumni_profile(db_alumni) for db_alumni in db_alumni_list]
    
    def add_work_history(self, alumni_id: int, job: JobPosition):
        db_job = WorkHistoryDB(
            alumni_id=alumni_id,
            job_title=job.title,
            company=job.company,
            start_date=job.start_date,
            end_date=job.end_date,
            is_current=job.is_current,
            industry=job.industry.value if job.industry else None,
            location=job.location
        )
        self.session.add(db_job)
    
    def add_data_source(self, alumni_id: int, source: DataSource):
        """Add data source entry"""
        db_source = DataSourceDB(
            alumni_id=alumni_id,
            source_type=source.source_type,
            source_url=source.source_url,
            collection_date=source.collection_date,
            confidence_score=source.confidence_score
        )
        self.session.add(db_source)
    
    def convert_db_to_alumni_profile(self, db_alumni: AlumniProfileDB) -> AlumniProfile:
        
        # Convert work history
        work_history = []
        for db_job in db_alumni.work_history:
            # Safely convert industry to enum, use None if invalid
            industry = None
            if db_job.industry:
                try:
                    industry = IndustryType(db_job.industry)
                except ValueError:
                    industry = None  # Invalid enum value, use None
            
            job = JobPosition(
                title=db_job.job_title,
                company=db_job.company,
                start_date=db_job.start_date,
                end_date=db_job.end_date,
                is_current=db_job.is_current,
                industry=industry,
                location=db_job.location
            )
            work_history.append(job)
        
        # Convert data sources
        data_sources = []
        for db_source in db_alumni.data_sources:
            source = DataSource(
                source_type=db_source.source_type,
                source_url=db_source.source_url,
                collection_date=db_source.collection_date,
                confidence_score=db_source.confidence_score
            )
            data_sources.append(source)
        
        # Find current position
        current_position = None
        for job in work_history:
            if job.is_current:
                current_position = job
                break
        
        # Safely convert main industry to enum, use None if invalid
        main_industry = None
        if db_alumni.industry:
            try:
                main_industry = IndustryType(db_alumni.industry)
            except ValueError:
                main_industry = None  # Invalid enum value, use None
        
        return AlumniProfile(
            id=db_alumni.id,
            full_name=db_alumni.full_name,
            graduation_year=db_alumni.graduation_year,
            current_position=current_position,
            work_history=work_history,
            location=db_alumni.location,
            industry=main_industry,
            linkedin_url=db_alumni.linkedin_url,
            confidence_score=db_alumni.confidence_score,
            last_updated=db_alumni.last_updated,
            data_sources=data_sources
        )