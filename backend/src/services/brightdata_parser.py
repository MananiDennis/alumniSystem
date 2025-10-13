from typing import Dict, Any, Optional, List
from datetime import datetime
from src.models.alumni import AlumniProfile, JobPosition, DataSource, IndustryType


class BrightDataParser:
    """Parse BrightData LinkedIn profiles into AlumniProfile objects"""
    
    def __init__(self):
        self.industry_mapping = {
            'software': IndustryType.TECHNOLOGY,
            'engineer': IndustryType.TECHNOLOGY,
            'developer': IndustryType.TECHNOLOGY,
            'tech': IndustryType.TECHNOLOGY,
            'data': IndustryType.TECHNOLOGY,
            'finance': IndustryType.FINANCE,
            'bank': IndustryType.FINANCE,
            'investment': IndustryType.FINANCE,
            'analyst': IndustryType.FINANCE,
            'health': IndustryType.HEALTHCARE,
            'medical': IndustryType.HEALTHCARE,
            'nurse': IndustryType.HEALTHCARE,
            'doctor': IndustryType.HEALTHCARE,
            'education': IndustryType.EDUCATION,
            'teacher': IndustryType.EDUCATION,
            'university': IndustryType.EDUCATION,
            'consulting': IndustryType.CONSULTING,
            'consultant': IndustryType.CONSULTING,
            'mining': IndustryType.MINING,
            'resources': IndustryType.MINING,
            'government': IndustryType.GOVERNMENT,
            'public': IndustryType.GOVERNMENT,
            'retail': IndustryType.RETAIL,
            'sales': IndustryType.RETAIL,
        }
    
    def parse_profile(self, brightdata_profile: Dict[str, Any]) -> Optional[AlumniProfile]:
        """Convert BrightData profile to AlumniProfile"""
        try:
            # Extract basic info
            name = brightdata_profile.get('name', '').strip()
            if not name:
                return None
            
            # Location (city + country)
            location = self.parse_location(brightdata_profile)
            
            # Current job
            current_job = self.parse_current_job(brightdata_profile)
            
            # Work history
            work_history = self.parse_work_history(brightdata_profile)
            
            # Industry
            industry = self.determine_industry(current_job, work_history, brightdata_profile)
            
            # Create profile
            profile = AlumniProfile(
                full_name=name,
                location=location,
                industry=industry,
                linkedin_url=brightdata_profile.get('url', ''),
                confidence_score=0.9,  # High confidence for BrightData
                last_updated=datetime.now()
            )
            
            # Add work history
            if current_job:
                profile.add_job_position(current_job)
            
            for job in work_history:
                if job != current_job:  # Avoid duplicates
                    profile.add_job_position(job)
            
            # Add data source
            source = DataSource(
                source_type="brightdata",
                source_url=brightdata_profile.get('url', ''),
                confidence_score=0.9
            )
            profile.data_sources.append(source)
            
            return profile
            
        except Exception as e:
            print(f"Error parsing BrightData profile: {e}")
            return None
    
    def parse_location(self, profile: Dict[str, Any]) -> Optional[str]:
        """Parse location from BrightData profile"""
        city = profile.get('city', '')
        country_code = profile.get('country_code', '')
        
        if city and country_code == 'AU':
            return city
        elif city:
            return city
        
        return None
    
    def parse_current_job(self, profile: Dict[str, Any]) -> Optional[JobPosition]:
        """Parse current job from BrightData profile"""
        current_company = profile.get('current_company', {})
        
        if not current_company:
            # Try position field
            position = profile.get('position', '')
            if position and ' at ' in position:
                parts = position.split(' at ', 1)
                title = parts[0].strip()
                company = parts[1].strip()
                
                return JobPosition(
                    title=title,
                    company=company,
                    is_current=True,
                    industry=self.map_to_industry(title, company)
                )
            return None
        
        title = current_company.get('title', '').replace(f" at {current_company.get('name', '')}", '')
        company = current_company.get('name', '')
        
        if title and company:
            return JobPosition(
                title=title,
                company=company,
                is_current=True,
                industry=self.map_to_industry(title, company)
            )
        
        return None
    
    def parse_work_history(self, profile: Dict[str, Any]) -> List[JobPosition]:
        """Parse work history from BrightData profile"""
        experience = profile.get('experience', [])
        if not isinstance(experience, list):
            return []
        
        jobs = []
        for exp in experience:
            if not isinstance(exp, dict):
                continue
            
            title = exp.get('title', '').strip()
            company = exp.get('company', '').strip()
            
            if title and company:
                job = JobPosition(
                    title=title,
                    company=company,
                    is_current=False,  # Will be updated if it's the current job
                    industry=self.map_to_industry(title, company)
                )
                jobs.append(job)
        
        return jobs
    
    def determine_industry(self, current_job: Optional[JobPosition], 
                          work_history: List[JobPosition], 
                          profile: Dict[str, Any]) -> Optional[IndustryType]:
        """Determine primary industry"""
        # Try current job first
        if current_job and current_job.industry:
            return current_job.industry
        
        # Try recent work history
        for job in work_history[:3]:
            if job.industry:
                return job.industry
        
        # Try from about section
        about = profile.get('about', '')
        if about:
            industry = self.map_to_industry(about, '')
            if industry:
                return industry
        
        return None
    
    def map_to_industry(self, title: str, company: str) -> Optional[IndustryType]:
        """Map job title/company to industry"""
        text = f"{title} {company}".lower()
        
        for keyword, industry in self.industry_mapping.items():
            if keyword in text:
                return industry
        
        return None