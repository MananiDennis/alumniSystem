from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, Date, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    ADMIN = "admin"
    FACULTY = "faculty"
    STAFF = "staff"

class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STAFF)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class AlumniProfileDB(Base):
    
    __tablename__ = "alumni_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False, index=True)
    graduation_year = Column(Integer, nullable=True, index=True)
    current_job_title = Column(String(255), nullable=True)
    current_company = Column(String(255), nullable=True, index=True)
    industry = Column(String(100), nullable=True, index=True)
    location = Column(String(255), nullable=True, index=True)
    linkedin_url = Column(String(500), nullable=True)
    confidence_score = Column(Float, default=1.0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    work_history = relationship("WorkHistoryDB", back_populates="alumni", cascade="all, delete-orphan")
    education_history = relationship("EducationDB", back_populates="alumni", cascade="all, delete-orphan")
    data_sources = relationship("DataSourceDB", back_populates="alumni", cascade="all, delete-orphan")


class WorkHistoryDB(Base):
    
    __tablename__ = "work_history"
    
    id = Column(Integer, primary_key=True, index=True)
    alumni_id = Column(Integer, ForeignKey("alumni_profiles.id"), nullable=False)
    job_title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_current = Column(Boolean, default=False)
    industry = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    
    # Relationships
    alumni = relationship("AlumniProfileDB", back_populates="work_history")


class EducationDB(Base):
    
    __tablename__ = "education_history"
    
    id = Column(Integer, primary_key=True, index=True)
    alumni_id = Column(Integer, ForeignKey("alumni_profiles.id"), nullable=False)
    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=True)
    field_of_study = Column(String(255), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    start_year = Column(Integer, nullable=True)
    
    # Relationships
    alumni = relationship("AlumniProfileDB", back_populates="education_history")


class DataSourceDB(Base):
    """SQLAlchemy model for data sources"""
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    alumni_id = Column(Integer, ForeignKey("alumni_profiles.id"), nullable=False)
    source_type = Column(String(50), nullable=False)  # 'linkedin', 'web', 'manual'
    source_url = Column(String(500), nullable=True)
    data_collected = Column(Text, nullable=True)  # JSON string
    collection_date = Column(DateTime, default=datetime.utcnow)
    confidence_score = Column(Float, default=1.0)
    
    # Relationships
    alumni = relationship("AlumniProfileDB", back_populates="data_sources")


class TaskDB(Base):
    """SQLAlchemy model for background collection tasks"""
    __tablename__ = "collection_tasks"
    
    id = Column(String(36), primary_key=True, index=True)  # UUID as string
    status = Column(String(20), nullable=False, default="running")  # 'running', 'completed', 'failed'
    names = Column(Text, nullable=False)  # JSON array of names
    method = Column(String(20), nullable=False, default="web-research")
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    results_count = Column(Integer, default=0)
    results = Column(Text, nullable=True)  # JSON array of results
    failed_names = Column(Text, nullable=True)  # JSON array of failed names
    error = Column(Text, nullable=True)