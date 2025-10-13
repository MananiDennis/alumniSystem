"""
Database initialization script
Creates tables and adds initial user data
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base
from src.models.user import User, UserRole
from src.config.settings import settings, get_database_url
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with tables and initial data"""
    try:
        # Use the same database setup as the main application
        database_url = get_database_url()
        engine = create_engine(database_url, connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {})
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        # Check if users already exist
        existing_users = session.query(User).count()
        if existing_users > 0:
            logger.info(f"Database already has {existing_users} users")
            session.close()
            return
        
        # Create initial users
        admin_user = User(
            email="admin@ecu.edu.au",
            name="Administrator",
            role=UserRole.ADMIN
        )
        admin_user.set_password("admin123")
        
        faculty_user = User(
            email="flavio@ecu.edu.au", 
            name="Flavio",
            role=UserRole.FACULTY
        )
        faculty_user.set_password("flavio123")
        
        # Add users to session
        session.add(admin_user)
        session.add(faculty_user)
        session.commit()
        
        logger.info("Initial users created successfully:")
        logger.info("- admin@ecu.edu.au (admin)")
        logger.info("- flavio@ecu.edu.au (faculty)")
        
        session.close()
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    init_database()