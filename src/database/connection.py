from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from src.database.models import Base
from src.config.settings import settings
from src.models.user import User, UserRole
from datetime import datetime
import os


class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.setup_database()
    
    def setup_database(self):
        """Set up database engine and session factory"""
        # Use SQLite for development (easier setup)
        database_path = "alumni_tracking.db"
        database_url = f"sqlite:///{database_path}"
        
        # Create engine with connection pooling for SQLite
        self.engine = create_engine(
            database_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            echo=settings.debug  # Log SQL queries in debug mode
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Create tables
        self.create_tables()
        
        # Add default users if none exist
        self.add_default_users()
    
    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)
    
    def add_default_users(self):
        """Add default users if database is empty"""
        session = self.get_session()
        try:
            # Check if users already exist
            existing_users = session.query(User).count()
            if existing_users > 0:
                return
            
            # Create default admin user
            admin_user = User(
                id=1,
                email="admin@ecu.edu.au",
                password_hash="$2b$12$J1.nbM963qqDwsgsVgN3NOwqm23eZrG7KrLfbpaPkCGAHZaltDeaq",
                name="Administrator",
                role=UserRole.ADMIN,
                created_at=datetime.utcnow()
            )
            
            # Create default faculty user
            faculty_user = User(
                id=2,
                email="flavio@ecu.edu.au",
                password_hash="$2b$12$O7fHPv9WKAxRGlEloeO5Nuh1zBPMqiyvuo6ndjnL1324RNlyb23Li",
                name="Flavio",
                role=UserRole.FACULTY,
                created_at=datetime(2025, 9, 23, 21, 31, 46, 552285)
            )
            
            session.add(admin_user)
            session.add(faculty_user)
            session.commit()
            
            print("Default users created:")
            print("- admin@ecu.edu.au (Administrator)")
            print("- flavio@ecu.edu.au (Flavio)")
            
        except Exception as e:
            print(f"Error creating default users: {e}")
            session.rollback()
        finally:
            session.close()
    
    def get_session(self) -> Session:
        # gets the session of the database
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        # close a database session
        session.close()


# Global database manager instance
db_manager = DatabaseManager()


def get_db_session() -> Session:
    # gets the database session
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()