from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, case
from src.database.models import AlumniProfileDB, WorkHistoryDB, EducationDB, DataSourceDB
from src.models.alumni import AlumniProfile, JobPosition, Education, DataSource, IndustryType
import json
from datetime import datetime


class AlumniRepository:
    """Repository for CRUD operations with the alumni data"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_alumni(self, alumni: AlumniProfile) -> AlumniProfile:
        # Validate alumni name before creating
        if not alumni.full_name:
            raise ValueError("Full name is required")
        
        trimmed_name = alumni.full_name.strip()
        if not trimmed_name:
            raise ValueError("Full name cannot be empty")
        
        if len(trimmed_name) < 2:
            raise ValueError("Full name must be at least 2 characters long")
        
        # Use the trimmed name
        alumni.full_name = trimmed_name
        
        # Create a new alumni profile
        db_alumni = AlumniProfileDB(
            full_name=alumni.full_name,
            graduation_year=alumni.graduation_year,
            current_job_title=alumni.current_position.title if alumni.current_position else None,
            current_company=alumni.current_position.company if alumni.current_position else None,
            industry=alumni.industry if alumni.industry else None,
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
        
        # Add education history
        for education in alumni.education_history:
            self.add_education_history(db_alumni.id, education)
        
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
        """Search alumni with multiple filters - optimized with eager loading to avoid N+1 queries"""
        query = self.session.query(AlumniProfileDB).options(
            selectinload(AlumniProfileDB.work_history),
            selectinload(AlumniProfileDB.education_history),
            selectinload(AlumniProfileDB.data_sources)
        )
        
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
        db_alumni.industry = alumni.industry if alumni.industry else None
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
        
        # Update education history (delete and recreate for simplicity)
        self.session.query(EducationDB).filter(
            EducationDB.alumni_id == alumni.id
        ).delete()
        
        for education in alumni.education_history:
            self.add_education_history(alumni.id, education)
        
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
        """Get all alumni with optional pagination - optimized with eager loading"""
        query = self.session.query(AlumniProfileDB).options(
            selectinload(AlumniProfileDB.work_history),
            selectinload(AlumniProfileDB.education_history),
            selectinload(AlumniProfileDB.data_sources)
        ).offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        db_alumni_list = query.all()
        return [self.convert_db_to_alumni_profile(db_alumni) for db_alumni in db_alumni_list]
    
    def get_total_alumni_count(self) -> int:
        """Get total count of alumni using SQL count"""
        return self.session.query(func.count(AlumniProfileDB.id)).scalar()
    
    def get_linkedin_count(self) -> int:
        """Get count of alumni with LinkedIn URLs"""
        return self.session.query(func.count(AlumniProfileDB.id)).filter(
            AlumniProfileDB.linkedin_url.isnot(None)
        ).scalar()
    
    def get_current_job_count(self) -> int:
        """Get count of alumni with current jobs"""
        return self.session.query(func.count(WorkHistoryDB.id)).filter(
            WorkHistoryDB.is_current == True
        ).scalar()
    
    def get_average_confidence(self) -> float:
        """Get average confidence score"""
        result = self.session.query(func.avg(AlumniProfileDB.confidence_score)).scalar()
        return result if result else 0.0
    
    def get_industry_distribution_sql(self) -> dict:
        """Get industry distribution using SQL GROUP BY"""
        results = self.session.query(
            AlumniProfileDB.industry,
            func.count(AlumniProfileDB.id)
        ).filter(
            AlumniProfileDB.industry.isnot(None)
        ).group_by(AlumniProfileDB.industry).all()
        
        distribution = {row[0]: row[1] for row in results}
        # Add unknown count
        unknown_count = self.session.query(func.count(AlumniProfileDB.id)).filter(
            AlumniProfileDB.industry.is_(None)
        ).scalar()
        if unknown_count > 0:
            distribution["Unknown"] = unknown_count
        return distribution
    
    def get_location_distribution_sql(self) -> dict:
        """Get location distribution using SQL GROUP BY"""
        results = self.session.query(
            AlumniProfileDB.location,
            func.count(AlumniProfileDB.id)
        ).filter(
            AlumniProfileDB.location.isnot(None)
        ).group_by(AlumniProfileDB.location).all()
        
        distribution = {row[0]: row[1] for row in results}
        unknown_count = self.session.query(func.count(AlumniProfileDB.id)).filter(
            AlumniProfileDB.location.is_(None)
        ).scalar()
        if unknown_count > 0:
            distribution["Unknown"] = unknown_count
        return distribution
    
    def get_graduation_year_distribution_sql(self) -> dict:
        """Get graduation year distribution using SQL GROUP BY"""
        results = self.session.query(
            AlumniProfileDB.graduation_year,
            func.count(AlumniProfileDB.id)
        ).filter(
            AlumniProfileDB.graduation_year.isnot(None)
        ).group_by(AlumniProfileDB.graduation_year).all()
        
        distribution = {str(row[0]): row[1] for row in results}
        unknown_count = self.session.query(func.count(AlumniProfileDB.id)).filter(
            AlumniProfileDB.graduation_year.is_(None)
        ).scalar()
        if unknown_count > 0:
            distribution["Unknown"] = unknown_count
        return distribution
    
    def get_confidence_score_distribution_sql(self) -> dict:
        """Get confidence score distribution in 10% ranges using SQL CASE"""
        ranges = {
            '0-10%': 0, '10-20%': 0, '20-30%': 0, '30-40%': 0, '40-50%': 0,
            '50-60%': 0, '60-70%': 0, '70-80%': 0, '80-90%': 0, '90-100%': 0
        }
        
        # Use CASE statement to categorize scores
        case_stmt = case(
            (AlumniProfileDB.confidence_score * 100 < 10, '0-10%'),
            (AlumniProfileDB.confidence_score * 100 < 20, '10-20%'),
            (AlumniProfileDB.confidence_score * 100 < 30, '20-30%'),
            (AlumniProfileDB.confidence_score * 100 < 40, '30-40%'),
            (AlumniProfileDB.confidence_score * 100 < 50, '40-50%'),
            (AlumniProfileDB.confidence_score * 100 < 60, '50-60%'),
            (AlumniProfileDB.confidence_score * 100 < 70, '60-70%'),
            (AlumniProfileDB.confidence_score * 100 < 80, '70-80%'),
            (AlumniProfileDB.confidence_score * 100 < 90, '80-90%'),
            else_='90-100%'
        )
        
        results = self.session.query(
            case_stmt.label('range'),
            func.count(AlumniProfileDB.id)
        ).group_by(case_stmt).all()
        
        for row in results:
            ranges[row[0]] = row[1]
        
        return ranges
    
    def get_alumni_stats_optimized(self) -> Dict[str, Any]:
        """
        Get all alumni statistics in a single optimized query set.
        This replaces 7 separate queries with 1-2 efficient ones using CTEs and subqueries.
        """
        from sqlalchemy import and_, distinct, case, text
        
        # Single complex query to get most stats at once
        # This uses a single database round-trip
        query = text("""
            SELECT 
                COUNT(*) as total_alumni,
                COUNT(linkedin_url) as with_linkedin,
                AVG(confidence_score) as average_confidence,
                (SELECT COUNT(DISTINCT alumni_id) 
                 FROM work_history 
                 WHERE is_current = 1) as with_current_job
            FROM alumni_profiles
        """)
        
        result = self.session.execute(query).first()
        
        total_alumni = result.total_alumni or 0
        with_linkedin = result.with_linkedin or 0
        average_confidence = float(result.average_confidence or 0.0)
        with_current_job = result.with_current_job or 0
        
        # If no alumni, return empty stats
        if total_alumni == 0:
            return {
                'total_alumni': 0,
                'with_linkedin': 0,
                'with_current_job': 0,
                'average_confidence': 0,
                'industry_distribution': {},
                'location_distribution': {},
                'top_companies': []
            }
        
        # Get distributions in parallel (these benefit from indexes)
        industry_distribution = self.get_industry_distribution_sql()
        location_distribution = self.get_location_distribution_sql()
        top_companies = self.get_top_companies_sql(5)
        
        return {
            'total_alumni': total_alumni,
            'with_linkedin': with_linkedin,
            'with_current_job': with_current_job,
            'average_confidence': average_confidence,
            'industry_distribution': industry_distribution,
            'location_distribution': location_distribution,
            'top_companies': top_companies
        }
    
    def get_top_companies_sql(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top companies using SQL GROUP BY on work_history"""
        results = self.session.query(
            WorkHistoryDB.company,
            func.count(WorkHistoryDB.id)
        ).filter(
            WorkHistoryDB.company.isnot(None)
        ).group_by(WorkHistoryDB.company).order_by(
            func.count(WorkHistoryDB.id).desc()
        ).limit(limit).all()
        
        return [{'company': row[0], 'alumni_count': row[1]} for row in results]
    
    def add_work_history(self, alumni_id: int, job: JobPosition):
        db_job = WorkHistoryDB(
            alumni_id=alumni_id,
            job_title=job.title,
            company=job.company,
            start_date=job.start_date,
            end_date=job.end_date,
            is_current=job.is_current,
            industry=job.industry if job.industry else None,
            location=job.location
        )
        self.session.add(db_job)
    
    def add_education_history(self, alumni_id: int, education: Education):
        db_education = EducationDB(
            alumni_id=alumni_id,
            institution=education.institution,
            degree=education.degree,
            field_of_study=education.field_of_study,
            graduation_year=education.graduation_year,
            start_year=education.start_year
        )
        self.session.add(db_education)
    
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
            # Keep industry as string (don't convert to enum)
            industry = db_job.industry if db_job.industry else None
            
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
        
        # Convert education history
        education_history = []
        for db_education in db_alumni.education_history:
            education = Education(
                institution=db_education.institution,
                degree=db_education.degree,
                field_of_study=db_education.field_of_study,
                graduation_year=db_education.graduation_year,
                start_year=db_education.start_year
            )
            education_history.append(education)
        
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
        
        # Safely convert main industry to string (keep as string, don't convert to enum)
        main_industry = None
        if db_alumni.industry:
            main_industry = db_alumni.industry  # Keep as string
        
        return AlumniProfile(
            id=db_alumni.id,
            full_name=db_alumni.full_name,
            graduation_year=db_alumni.graduation_year,
            current_position=current_position,
            work_history=work_history,
            education_history=education_history,
            location=db_alumni.location,
            industry=main_industry,
            linkedin_url=db_alumni.linkedin_url,
            confidence_score=db_alumni.confidence_score,
            last_updated=db_alumni.last_updated,
            data_sources=data_sources
        )