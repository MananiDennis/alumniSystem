from typing import List, Dict, Any, Optional
from src.models.alumni import AlumniProfile
from src.database.repository import AlumniRepository
from src.database.connection import db_manager


class SearchService:
    """Optimized search service for alumni data"""
    
    def __init__(self):
        self.session = db_manager.get_session()
        self.repository = AlumniRepository(self.session)
    
    def search_alumni(self, **filters) -> List[AlumniProfile]:
        # Search alumni with filters
        limit = filters.pop('limit', 50)
        results = self.repository.search_alumni(**filters)
        return results[:limit]
    
    def get_top_companies(self, limit: int = 10) -> List[Dict[str, Any]]:
        # Get top companies where alumni work
        all_alumni = self.repository.get_all_alumni()
        company_counts = {}
        
        for alumni in all_alumni:
            current_job = alumni.get_current_job()
            if current_job and current_job.company:
                company_counts[current_job.company] = company_counts.get(current_job.company, 0) + 1
        
        return [{'company': k, 'alumni_count': v} 
                for k, v in sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:limit]]
    
    def get_distribution(self, field: str) -> Dict[str, int]:
        # Get distribution by field (industry, location, graduation_year)
        all_alumni = self.repository.get_all_alumni()
        counts = {}
        
        for alumni in all_alumni:
            if field == 'industry':
                value = alumni.industry if alumni.industry else "Unknown"
            elif field == 'location':
                value = alumni.location or "Unknown"
            elif field == 'graduation_year':
                value = str(alumni.graduation_year) if alumni.graduation_year else "Unknown"
            else:
                continue
            
            counts[value] = counts.get(value, 0) + 1
        
        return counts
    
    def get_industry_distribution(self) -> Dict[str, int]:
        return self.get_distribution('industry')
    
    def get_location_distribution(self) -> Dict[str, int]:
        return self.get_distribution('location')
    
    def get_alumni_stats(self) -> Dict[str, Any]:
        # Get comprehensive alumni statistics
        all_alumni = self.repository.get_all_alumni()
        
        if not all_alumni:
            return {'total_alumni': 0, 'with_linkedin': 0, 'with_current_job': 0, 
                   'average_confidence': 0, 'industry_distribution': {}, 'top_companies': []}
        
        return {
            'total_alumni': len(all_alumni),
            'with_linkedin': len([a for a in all_alumni if a.linkedin_url]),
            'with_current_job': len([a for a in all_alumni if a.get_current_job()]),
            'average_confidence': sum(a.confidence_score for a in all_alumni) / len(all_alumni),
            'industry_distribution': self.get_industry_distribution(),
            'location_distribution': self.get_location_distribution(),
            'top_companies': self.get_top_companies(5)
        }
    
    def close(self):
        """Close database session"""
        self.session.close()