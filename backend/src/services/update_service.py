from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from src.models.alumni import AlumniProfile
from src.database.repository import AlumniRepository
from src.database.connection import db_manager
from src.services.web_research_service import WebResearchService
from src.services.ai_verification import AIVerificationService


class UpdateService:
    """Service for updating existing alumni profiles"""
    
    def __init__(self):
        self.session = db_manager.get_session()
        self.repository = AlumniRepository(self.session)
        self.web_research = WebResearchService()
        self.ai_verification = AIVerificationService()
    
    def update_all_profiles(self, max_age_days: int = 30) -> List[AlumniProfile]:
        """Update all profiles older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        all_alumni = self.repository.get_all_alumni()
        outdated_profiles = [
            alumni for alumni in all_alumni 
            if alumni.last_updated < cutoff_date
        ]
        
        print(f"Found {len(outdated_profiles)} profiles to update")
        return self.update_profiles(outdated_profiles)
    
    def update_profiles(self, profiles: List[AlumniProfile]) -> List[AlumniProfile]:
        """Update specific alumni profiles"""
        updated_profiles = []
        
        for profile in profiles:
            try:
                print(f"🔄 Updating {profile.full_name}...")
                updated_profile = self.update_single_profile(profile)
                
                if updated_profile:
                    updated_profiles.append(updated_profile)
                    print(f"✅ Updated {profile.full_name}")
                else:
                    print(f"⚠️ No updates for {profile.full_name}")
                
            except Exception as e:
                print(f"Error updating {profile.full_name}: {e}")
                continue
        
        return updated_profiles
    
    def update_single_profile(self, profile: AlumniProfile) -> Optional[AlumniProfile]:
        """Update a single alumni profile"""
        try:
            # Get fresh data from web research
            web_results = self.web_research.search_person_web(profile.full_name)
            
            if not web_results:
                return None
            
            # Convert web data to structured profile using AI
            fresh_profile = self.ai_verification.convert_web_data_to_profile(profile.full_name, web_results)
            
            if not fresh_profile:
                return None
            
            # Update existing profile with fresh data
            profile.location = fresh_profile.location or profile.location
            profile.industry = fresh_profile.industry or profile.industry
            profile.linkedin_url = fresh_profile.linkedin_url or profile.linkedin_url
            profile.last_updated = datetime.now()
            
            # Update work history if we have new data
            if fresh_profile.work_history:
                profile.work_history = fresh_profile.work_history
                if fresh_profile.current_position:
                    profile.current_position = fresh_profile.current_position
            
            # Update confidence score (take the higher one)
            profile.confidence_score = max(profile.confidence_score, fresh_profile.confidence_score)
            
            # Save to database
            return self.repository.update_alumni(profile)
            
        except Exception as e:
            print(f"Error updating profile: {e}")
            return None
    
    def update_profiles_by_ids(self, profile_ids: List[int]) -> List[AlumniProfile]:
        """Update profiles by their IDs"""
        profiles = []
        
        for profile_id in profile_ids:
            profile = self.repository.get_alumni_by_id(profile_id)
            if profile:
                profiles.append(profile)
        
        return self.update_profiles(profiles)
    
    def update_profiles_without_linkedin(self) -> List[AlumniProfile]:
        """Update profiles that don't have LinkedIn URLs"""
        all_alumni = self.repository.get_all_alumni()
        profiles_without_linkedin = [
            alumni for alumni in all_alumni 
            if not alumni.linkedin_url
        ]
        
        print(f"Found {len(profiles_without_linkedin)} profiles without LinkedIn URLs")
        return self.update_profiles(profiles_without_linkedin)
    
    def update_low_confidence_profiles(self, min_confidence: float = 0.5) -> List[AlumniProfile]:
        """Update profiles with low confidence scores"""
        all_alumni = self.repository.get_all_alumni()
        low_confidence_profiles = [
            alumni for alumni in all_alumni 
            if alumni.confidence_score < min_confidence
        ]
        
        print(f"Found {len(low_confidence_profiles)} low confidence profiles")
        return self.update_profiles(low_confidence_profiles)
    
    def batch_update_by_names(self, names: List[str]) -> List[AlumniProfile]:
        """Update profiles by searching for names"""
        updated_profiles = []
        
        for name in names:
            existing_profiles = self.repository.get_alumni_by_name(name)
            
            if existing_profiles:
                # Update existing profiles
                for profile in existing_profiles:
                    updated = self.update_single_profile(profile)
                    if updated:
                        updated_profiles.append(updated)
            else:
                # Create new profile if not exists
                print(f"Profile for {name} not found, would need to create new one")
        
        return updated_profiles
    
    def get_update_statistics(self) -> Dict[str, Any]:
        """Get statistics about profile freshness"""
        all_alumni = self.repository.get_all_alumni()
        now = datetime.now()
        
        # Categorize by age
        fresh = []  # < 7 days
        recent = []  # 7-30 days
        old = []  # 30-90 days
        very_old = []  # > 90 days
        
        for alumni in all_alumni:
            days_old = (now - alumni.last_updated).days
            
            if days_old < 7:
                fresh.append(alumni)
            elif days_old < 30:
                recent.append(alumni)
            elif days_old < 90:
                old.append(alumni)
            else:
                very_old.append(alumni)
        
        return {
            'total_profiles': len(all_alumni),
            'fresh_profiles': len(fresh),  # < 7 days
            'recent_profiles': len(recent),  # 7-30 days
            'old_profiles': len(old),  # 30-90 days
            'very_old_profiles': len(very_old),  # > 90 days
            'profiles_without_linkedin': len([a for a in all_alumni if not a.linkedin_url]),
            'low_confidence_profiles': len([a for a in all_alumni if a.confidence_score < 0.5]),
            'average_age_days': sum((now - a.last_updated).days for a in all_alumni) / len(all_alumni) if all_alumni else 0
        }
    
    def schedule_updates(self) -> Dict[str, Any]:
        """Suggest which profiles should be updated"""
        stats = self.get_update_statistics()
        suggestions = {
            'immediate_update': [],
            'should_update': [],
            'can_update': [],
            'summary': {}
        }
        
        all_alumni = self.repository.get_all_alumni()
        now = datetime.now()
        
        for alumni in all_alumni:
            days_old = (now - alumni.last_updated).days
            
            if days_old > 90 or alumni.confidence_score < 0.3:
                suggestions['immediate_update'].append({
                    'id': alumni.id,
                    'name': alumni.full_name,
                    'days_old': days_old,
                    'confidence': alumni.confidence_score
                })
            elif days_old > 30 or alumni.confidence_score < 0.6:
                suggestions['should_update'].append({
                    'id': alumni.id,
                    'name': alumni.full_name,
                    'days_old': days_old,
                    'confidence': alumni.confidence_score
                })
            elif days_old > 7:
                suggestions['can_update'].append({
                    'id': alumni.id,
                    'name': alumni.full_name,
                    'days_old': days_old,
                    'confidence': alumni.confidence_score
                })
        
        suggestions['summary'] = {
            'immediate': len(suggestions['immediate_update']),
            'should': len(suggestions['should_update']),
            'can': len(suggestions['can_update'])
        }
        
        return suggestions
    
    def close(self):
        """Close database session"""
        self.session.close()