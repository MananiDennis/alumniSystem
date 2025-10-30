from typing import List, Dict, Any, Optional
from src.models.alumni import AlumniProfile
from src.database.repository import AlumniRepository
from src.database.connection import db_manager
import logging


class SearchService:
    """Optimized search service for alumni data"""
    
    def __init__(self):
        self.session = db_manager.get_session()
        self.repository = AlumniRepository(self.session)
        self.logger = logging.getLogger(__name__)
    
    def search_alumni(self, **filters) -> List[AlumniProfile]:
        # Search alumni with filters
        limit = filters.pop('limit', 50)
        results = self.repository.search_alumni(**filters)
        return results[:limit]
    
    def get_top_companies(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.repository.get_top_companies_sql(limit)
    
    def get_industry_distribution(self) -> Dict[str, int]:
        return self.repository.get_industry_distribution_sql()
    
    def get_location_distribution(self) -> Dict[str, int]:
        return self.repository.get_location_distribution_sql()
    
    def get_graduation_year_distribution(self) -> Dict[str, int]:
        return self.repository.get_graduation_year_distribution_sql()
    
    def get_confidence_score_distribution(self) -> Dict[str, int]:
        return self.repository.get_confidence_score_distribution_sql()
    
    def get_confidence_score_distribution(self) -> Dict[str, int]:
        """Get distribution of confidence scores in 10% ranges (0-10%, 10-20%, etc.)"""
        return self.repository.get_confidence_score_distribution_sql()
    
    def get_alumni_stats(self) -> Dict[str, Any]:
        # Get comprehensive alumni statistics using optimized single query
        return self.repository.get_alumni_stats_optimized()
    
    def close(self):
        """Close database session"""
        self.session.close()