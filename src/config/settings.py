import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Database settings
    database_url: str = "sqlite:///./alumni_tracking.db"
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "alumni_tracking"
    database_user: str = "postgres"
    database_password: str = ""
    
    # API Keys (you'll need to provide these)
    openai_api_key: Optional[str] = None
    
    # BrightData API settings
    brightdata_api_key: Optional[str] = None
    brightdata_dataset_id: Optional[str] = None
    
    # LinkedIn scraping settings (fallback)
    linkedin_rate_limit: int = 50  # profiles per hour
    linkedin_delay_min: int = 2    # minimum seconds between requests
    linkedin_delay_max: int = 5    # maximum seconds between requests

    # LinkedIn Official API settings
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None
    linkedin_access_token: Optional[str] = None
    
    # Redis settings for Celery
    redis_url: str = "redis://localhost:6379/0"
    
    # Application settings
    app_name: str = "Alumni Tracking System"
    debug: bool = False
    log_level: str = "INFO"
    
    # Security settings
    secret_key: str = "your-secret-key-change-this"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_database_url() -> str:
    """Get the complete database URL"""
    if settings.database_url != "postgresql://localhost:5432/alumni_tracking":
        return settings.database_url
    
    return (
        f"postgresql://{settings.database_user}:{settings.database_password}"
        f"@{settings.database_host}:{settings.database_port}/{settings.database_name}"
    )