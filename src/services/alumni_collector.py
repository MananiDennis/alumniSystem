"""
Unified Alumni Collector - Consolidates all collection methods
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from src.models.alumni import AlumniProfile, JobPosition, DataSource
from src.database.connection import db_manager
from src.database.repository import AlumniRepository
from src.services.brightdata_service import BrightDataService
from src.services.brightdata_parser import BrightDataParser
from src.services.ai_verification import AIVerificationService
from src.config.settings import settings


class AlumniCollector:
    """Alumni collector supporting all collection methods"""
    
    def __init__(self):
        self.session = db_manager.get_session()
        self.repository = AlumniRepository(self.session)
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize BrightData service with error handling
        try:
            self.brightdata = BrightDataService()
            self.parser = BrightDataParser()
        except Exception as e:
            self.logger.warning(f"BrightData service initialization failed: {e}")
            self.brightdata = None
            self.parser = None
            
        self.ai_service = AIVerificationService() if settings.openai_api_key else None
        
        logging.basicConfig(
            level=getattr(logging, settings.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def collect_alumni(self, names: List[str], method: str = "web-research") -> List[AlumniProfile]:
        """Main collection method - uses web research by default"""
        if method == "manual":
            return self.collect_data_manually(names)
        elif method == "brightdata":
            return self.collect_automated(names)
        elif method == "web-research":
            return self.collect_web_research(names)
        else:
            return self.collect_linkedin_official(names)

    def collect_linkedin_official(self, names: List[str]) -> List[AlumniProfile]:
        """Collect alumni using LinkedIn official API (simple wrapper)"""
        from src.services.linkedin_official_api import LinkedInOfficialAPI
        linkedin_api = LinkedInOfficialAPI()
        return linkedin_api.collect_alumni_official(names)
    
    def collect_automated(self, names: List[str]) -> List[AlumniProfile]:
        """Automated collection using BrightData + AI verification"""
        self.logger.info(f"Starting automated collection for {len(names)} alumni")
        
        if not self.brightdata:
            self.logger.warning("BrightData service not available, creating placeholder profiles")
            return self.create_placeholder_profiles(names)
        
        try:
            linkedin_profiles = self.brightdata.get_alumni_profiles(names, ecu_filter=True)
        except Exception as e:
            self.logger.error(f"BrightData collection failed: {e}")
            return self.create_placeholder_profiles(names)
        collected_profiles = []
        
        for profile_data in linkedin_profiles:
            try:
                alumni_profile = self.parser.parse_profile(profile_data)
                if not alumni_profile:
                    continue
                
                # AI verification if available
                if self.ai_service:
                    verification = self.ai_service.verify_profile_match(
                        target_name=alumni_profile.full_name,
                        scraped_data=profile_data
                    )
                    
                    if verification.is_match:
                        alumni_profile.confidence_score *= verification.confidence_score
                    else:
                        self.logger.warning(f"AI verification failed for {alumni_profile.full_name}")
                        continue
                
                saved_profile = self.repository.create_alumni(alumni_profile)
                collected_profiles.append(saved_profile)
                
                self.logger.info(f"✓ Saved {alumni_profile.full_name}")
                
            except Exception as e:
                self.logger.error(f"Error processing profile: {e}")
                continue
        
        return collected_profiles
    
    def collect_web_research(self, names: List[str]) -> List[AlumniProfile]:
        """Collect alumni data using web research + AI structuring"""
        self.logger.info(f"Starting web research collection for {len(names)} alumni")
        
        from src.services.web_research_service import WebResearchService
        
        web_service = WebResearchService()
        collected_profiles = []
        
        for name in names:
            try:
                self.logger.info(f"Researching {name}...")
                
                # Get web research results
                web_results = web_service.search_person_web(name, "ECU Edith Cowan University Australia")
                
                if not web_results:
                    self.logger.warning(f"No web results found for {name}")
                    continue
                
                # Use AI to convert unstructured data to structured profile
                if self.ai_service:
                    structured_profile = self.ai_service.convert_web_data_to_profile(
                        target_name=name,
                        web_results=web_results
                    )
                    
                    if structured_profile:
                        # Save to database
                        saved_profile = self.repository.create_alumni(structured_profile)
                        collected_profiles.append(saved_profile)
                        self.logger.info(f"✓ Saved web research profile for {name}")
                    else:
                        self.logger.warning(f"AI conversion failed for {name}")
                else:
                    self.logger.warning("AI service not available for web data conversion")
                    
            except Exception as e:
                self.logger.error(f"Error in web research for {name}: {e}")
                continue
        
        return collected_profiles
    
    def collect_data_manually(self, names: List[str]) -> List[AlumniProfile]:
        """Manual collection through user input"""
        collected_profiles = []
        
        for name in names:
            print(f"\n--- Collecting data for: {name} ---")
            profile = self.collect_single_manual(name)
            if profile:
                saved_profile = self.repository.create_alumni(profile)
                collected_profiles.append(saved_profile)
                print(f"✓ Saved profile for {name}")
        
        return collected_profiles
    
    def collect_single_manual(self, name: str) -> Optional[AlumniProfile]:
        """Collect data for single alumni manually"""
        try:
            print(f"Enter information for {name}:")
            
            graduation_year = self.get_graduation_year()
            location = input("Location: ").strip() or None
            linkedin_url = input("LinkedIn URL (optional): ").strip() or None
            
            # Current job
            print("\nCurrent Job Information:")
            current_job = self.get_job_input(True)
            
            # Work history
            work_history = [current_job] if current_job else []
            
            while input("\nAdd previous job? (y/n): ").strip().lower() == 'y':
                prev_job = self.get_job_input(False)
                if prev_job:
                    work_history.append(prev_job)
            
            # Create profile
            profile = AlumniProfile(
                full_name=name,
                graduation_year=graduation_year if graduation_year > 0 else None,
                location=location,
                industry=current_job.industry if current_job else None,
                linkedin_url=linkedin_url,
                confidence_score=1.0
            )
            
            for job in work_history:
                profile.add_job_position(job)
            
            profile.data_sources.append(DataSource(source_type="manual", confidence_score=1.0))
            
            return profile
            
        except KeyboardInterrupt:
            print(f"\nSkipping {name}")
            return None
        except Exception as e:
            print(f"Error collecting data for {name}: {e}")
            return None
    
    def get_graduation_year(self) -> int:
        """Get graduation year with validation"""
        while True:
            try:
                year_input = input("Graduation year (or Enter to skip): ").strip()
                if not year_input:
                    return 0
                
                year = int(year_input)
                current_year = datetime.now().year
                
                if 1950 <= year <= current_year + 5:
                    return year
                else:
                    print(f"Please enter a year between 1950 and {current_year + 5}")
            except ValueError:
                print("Please enter a valid year")
    
    def get_job_input(self, is_current: bool = False) -> Optional[JobPosition]:
        """Get job position information"""
        job_type = "current" if is_current else "previous"
        
        title = input(f"Job title ({job_type}): ").strip()
        if not title:
            return None
        
        company = input(f"Company ({job_type}): ").strip()
        if not company:
            return None
        
        industry = self.get_industry_input()
        start_date = self.get_date_input(f"Start date ({job_type})", True)
        end_date = None if is_current else self.get_date_input(f"End date ({job_type})", True)
        job_location = input(f"Job location ({job_type}, optional): ").strip() or None
        
        return JobPosition(
            title=title,
            company=company,
            start_date=start_date,
            end_date=end_date,
            is_current=is_current,
            industry=industry,
            location=job_location
        )
    
    def get_industry_input(self) -> Optional[str]:
        """Get industry selection"""
        print("\nSelect industry:")
        industries = ["Technology", "Finance", "Healthcare", "Education", "Consulting", "Mining", "Government", "Non-Profit", "Retail", "Manufacturing", "Other"]
        for i, industry in enumerate(industries, 1):
            print(f"{i}. {industry}")
        
        while True:
            try:
                choice = input("Enter industry number (or Enter to skip): ").strip()
                if not choice:
                    return None
                
                index = int(choice) - 1
                if 0 <= index < len(industries):
                    return industries[index]
                else:
                    print(f"Please enter a number between 1 and {len(industries)}")
            except ValueError:
                print("Please enter a valid number")
    
    def get_date_input(self, prompt: str, optional: bool = True) -> Optional[date]:
        """Get date input"""
        while True:
            try:
                date_input = input(f"{prompt} (YYYY-MM-DD or Enter to skip): ").strip()
                if not date_input:
                    return None
                
                year, month, day = map(int, date_input.split('-'))
                return date(year, month, day)
                
            except ValueError:
                if optional:
                    print("Invalid format. Use YYYY-MM-DD or press Enter to skip")
                else:
                    print("Invalid format. Please use YYYY-MM-DD")
    
    def search_alumni(self, **filters) -> List[AlumniProfile]:
        """Search alumni with filters"""
        return self.repository.search_alumni(**filters)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        all_alumni = self.repository.get_all_alumni()
        
        if not all_alumni:
            return {"total_alumni": 0, "with_linkedin": 0, "with_current_job": 0, 
                   "average_confidence": 0, "by_industry": {}, "by_graduation_year": {}}
        
        stats = {
            "total_alumni": len(all_alumni),
            "with_linkedin": len([a for a in all_alumni if a.linkedin_url]),
            "with_current_job": len([a for a in all_alumni if a.get_current_job()]),
            "average_confidence": sum(a.confidence_score for a in all_alumni) / len(all_alumni),
            "by_industry": {},
            "by_graduation_year": {}
        }
        
        # Group by industry and graduation year
        for alumni in all_alumni:
            industry = alumni.industry if alumni.industry else "Unknown"
            year = str(alumni.graduation_year) if alumni.graduation_year else "Unknown"
            
            stats["by_industry"][industry] = stats["by_industry"].get(industry, 0) + 1
            stats["by_graduation_year"][year] = stats["by_graduation_year"].get(year, 0) + 1
        
        return stats
    
    def create_placeholder_profiles(self, names: List[str]) -> List[AlumniProfile]:
        """Create placeholder profiles when data collection fails"""
        profiles = []
        for name in names:
            try:
                # Create a basic profile with just the name
                profile = AlumniProfile(
                    full_name=name.strip(),
                    confidence_score=0.5,  # Low confidence since it's just a placeholder
                    data_sources=[DataSource(
                        source_type="manual",
                        source_url=None,
                        data_collected=f"Placeholder profile for {name}",
                        confidence_score=0.5
                    )]
                )
                
                # Save to database
                saved_profile = self.repository.save_alumni_profile(profile)
                profiles.append(saved_profile)
                self.logger.info(f"Created placeholder profile for {name}")
                
            except Exception as e:
                self.logger.error(f"Failed to create placeholder for {name}: {e}")
                continue
                
        return profiles
    
    def close(self):
        """Close database session"""
        self.session.close()