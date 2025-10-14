from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class IndustryType(Enum):

    TECHNOLOGY = "Technology"
    FINANCE = "Finance"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    CONSULTING = "Consulting"
    MINING = "Mining"
    GOVERNMENT = "Government"
    NON_PROFIT = "Non-Profit"
    RETAIL = "Retail"
    MANUFACTURING = "Manufacturing"
    OTHER = "Other"


@dataclass
class JobPosition:
    # the jobs of an alumni
    title: str
    company: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False
    industry: Optional[str] = None
    location: Optional[str] = None
    
    def __post_init__(self):
        
        if not self.title or not self.company:
            raise ValueError("Job title and company are required")
        
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("Start date cannot be after end date")
        
        if self.is_current and self.end_date:
            raise ValueError("Current job cannot have an end date")


@dataclass
class DataSource:
    # where we collected the data
    source_type: str  # 'linkedin', 'web', 'manual'
    source_url: Optional[str] = None
    collection_date: datetime = field(default_factory=datetime.now)
    confidence_score: float = 1.0
    
    def __post_init__(self):
        
        valid_types = ['linkedin', 'web', 'manual', 'brightdata', 'web-research']
        if self.source_type not in valid_types:
            raise ValueError(f"Source type must be one of: {valid_types}")
        
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")


@dataclass
class Education:
    """Education information for an alumni"""
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None
    start_year: Optional[int] = None
    
    def __post_init__(self):
        if not self.institution:
            raise ValueError("Institution is required")
        
        if self.graduation_year and self.start_year:
            if self.start_year > self.graduation_year:
                raise ValueError("Start year cannot be after graduation year")
        
        if self.graduation_year:
            current_year = datetime.now().year
            if not 1950 <= self.graduation_year <= current_year + 10:
                raise ValueError(f"Graduation year must be between 1950 and {current_year + 10}")


@dataclass
class AlumniProfile:

    full_name: str
    id: Optional[int] = None
    graduation_year: Optional[int] = None
    current_position: Optional[JobPosition] = None
    work_history: List[JobPosition] = field(default_factory=list)
    education_history: List[Education] = field(default_factory=list)
    location: Optional[str] = None
    industry: Optional[str] = None
    linkedin_url: Optional[str] = None
    confidence_score: float = 1.0
    last_updated: datetime = field(default_factory=datetime.now)
    data_sources: List[DataSource] = field(default_factory=list)
    
    def __post_init__(self):
        # validating the profile data
        if not self.full_name or len(self.full_name.strip()) < 2:
            raise ValueError("Full name is required and must be at least 2 characters")
        
        if self.graduation_year:
            current_year = datetime.now().year
            if not 1950 <= self.graduation_year <= current_year + 5:
                raise ValueError(f"Graduation year must be between 1950 and {current_year + 5}")
        
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")
    
    def add_job_position(self, position: JobPosition):
        if position.is_current:
            # Remove current flag from other positions
            for job in self.work_history:
                job.is_current = False
            self.current_position = position
        
        self.work_history.append(position)
        self.work_history.sort(key=lambda x: x.start_date or date.min, reverse=True)
    
    def add_education(self, education: Education):
        self.education_history.append(education)
        # Sort by graduation year (most recent first)
        self.education_history.sort(key=lambda x: x.graduation_year or 0, reverse=True)
    
    def get_current_job(self) -> Optional[JobPosition]:
        return self.current_position
    
    def get_industry_from_current_job(self) -> Optional[str]:
        # infer industry from current job if not set
        if self.industry:
            return self.industry
        
        if self.current_position and self.current_position.industry:
            return self.current_position.industry
        
        return None