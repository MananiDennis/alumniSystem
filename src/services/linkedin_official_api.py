"""
LinkedIn Official API Service
Uses LinkedIn's official Partner APIs for compliant data collection
"""

import requests
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os
from src.models.alumni import AlumniProfile, JobPosition, IndustryType


class LinkedInOfficialAPI:
    """Service for LinkedIn's official API integration"""
    
    def __init__(self):
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.base_url = "https://api.linkedin.com/v2"
        self.rate_limit = {
            'calls_per_hour': 100,  # Conservative rate limit
            'calls_made': 0,
            'reset_time': datetime.now() + timedelta(hours=1)
        }
        
    def is_rate_limited(self) -> bool:
        """Check if we've hit the rate limit"""
        if datetime.now() > self.rate_limit['reset_time']:
            # Reset the counter
            self.rate_limit['calls_made'] = 0
            self.rate_limit['reset_time'] = datetime.now() + timedelta(hours=1)
            
        return self.rate_limit['calls_made'] >= self.rate_limit['calls_per_hour']
    
    def increment_rate_limit(self):
        """Increment the API call counter"""
        self.rate_limit['calls_made'] += 1
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers for LinkedIn API requests"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
    
    def search_people(self, name: str, company_keywords: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for people using LinkedIn's official People Search API
        NOTE: This requires LinkedIn Partner Program access
        """
        if not self.access_token:
            raise ValueError("LinkedIn access token not provided. Please set LINKEDIN_ACCESS_TOKEN environment variable.")
        
        if self.is_rate_limited():
            raise Exception("Rate limit exceeded. Please wait before making more requests.")
        
        # Split name into first and last name
        name_parts = name.strip().split()
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        # Build search query
        params = {
            'q': 'people',
            'keywords': name,
        }
        
        if first_name:
            params['firstName'] = first_name
        if last_name:
            params['lastName'] = last_name
            
        if company_keywords:
            params['companyKeywords'] = ','.join(company_keywords)
        
        try:
            self.increment_rate_limit()
            response = requests.get(
                f"{self.base_url}/people-search",
                headers=self.get_headers(),
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('elements', [])
            elif response.status_code == 403:
                raise Exception("Access denied. LinkedIn Partner Program access required for People Search API.")
            elif response.status_code == 429:
                raise Exception("Rate limit exceeded by LinkedIn. Please wait before retrying.")
            else:
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"LinkedIn API request failed: {str(e)}")
    
    def get_profile_details(self, profile_id: str) -> Dict[str, Any]:
        """
        Get detailed profile information using LinkedIn's Profile API
        """
        if self.is_rate_limited():
            raise Exception("Rate limit exceeded. Please wait before making more requests.")
        
        # Fields to retrieve (based on LinkedIn's available fields)
        fields = [
            'id',
            'firstName',
            'lastName',
            'headline',
            'location',
            'industry',
            'positions',
            'educations',
            'publicProfileUrl'
        ]
        
        params = {
            'projection': f"({','.join(fields)})"
        }
        
        try:
            self.increment_rate_limit()
            response = requests.get(
                f"{self.base_url}/people/{profile_id}",
                headers=self.get_headers(),
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                raise Exception("Access denied. Insufficient permissions for profile access.")
            elif response.status_code == 429:
                raise Exception("Rate limit exceeded by LinkedIn. Please wait before retrying.")
            else:
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"LinkedIn API request failed: {str(e)}")
    
    def collect_alumni_official(self, names: List[str]) -> List[AlumniProfile]:
        """
        Collect alumni data using LinkedIn's official APIs
        """
        collected_profiles = []
        
        print(f"🔗 Using LinkedIn Official API for {len(names)} alumni...")
        print("⚖️  This method is compliant with LinkedIn's Terms of Service")
        
        for i, name in enumerate(names, 1):
            print(f"Searching for {name} ({i}/{len(names)})...")
            
            try:
                # Rate limiting with delays
                if i > 1:
                    time.sleep(2)  # 2 second delay between requests
                
                # Search for the person
                search_results = self.search_people(
                    name=name,
                    company_keywords=['university', 'college', 'education']  # ECU-related keywords
                )
                
                if not search_results:
                    print(f"❌ No results found for {name}")
                    continue
                
                # Process the best match
                best_match = search_results[0]  # Take the first result
                profile_data = self.parse_official_profile(best_match, name)
                
                if profile_data:
                    collected_profiles.append(profile_data)
                    print(f"✅ Successfully collected data for {name}")
                else:
                    print(f"❌ Could not parse profile data for {name}")
                    
            except Exception as e:
                print(f"❌ Error collecting data for {name}: {str(e)}")
                continue
        
        print(f"🎯 Official API collection complete: {len(collected_profiles)}/{len(names)} profiles collected")
        return collected_profiles
    
    def parse_official_profile(self, linkedin_data: Dict[str, Any], original_name: str) -> Optional[AlumniProfile]:
        """
        Parse LinkedIn official API response into AlumniProfile
        """
        try:
            # Extract basic information
            first_name = linkedin_data.get('firstName', {}).get('localized', {}).get('en_US', '')
            last_name = linkedin_data.get('lastName', {}).get('localized', {}).get('en_US', '')
            full_name = f"{first_name} {last_name}".strip() or original_name
            
            # Extract location
            location_data = linkedin_data.get('location', {})
            location = None
            if location_data:
                location = location_data.get('name', '')
            
            # Extract headline and industry
            headline = linkedin_data.get('headline', {}).get('localized', {}).get('en_US', '')
            industry_raw = linkedin_data.get('industry', '')
            industry = self.map_industry(industry_raw, headline)
            
            # Extract LinkedIn URL
            linkedin_url = linkedin_data.get('publicProfileUrl', '')
            
            # Parse current job from positions
            positions_data = linkedin_data.get('positions', {}).get('values', [])
            current_job = None
            work_history = []
            
            for position in positions_data:
                job = self.parse_position(position)
                if job:
                    work_history.append(job)
                    if job.is_current and not current_job:
                        current_job = job
            
            # Create AlumniProfile
            profile = AlumniProfile(
                full_name=full_name,
                linkedin_url=linkedin_url,
                location=location,
                industry=industry,
                confidence_score=0.85,  # High confidence for official API
                graduation_year=None,  # Would need additional API calls
                work_history=work_history
            )
            
            return profile
            
        except Exception as e:
            print(f"❌ Error parsing LinkedIn official data: {str(e)}")
            return None
    
    def parse_position(self, position_data: Dict[str, Any]) -> Optional[JobPosition]:
        """Parse a position from LinkedIn official API"""
        try:
            title = position_data.get('title', '')
            company_data = position_data.get('company', {})
            company = company_data.get('name', '') if company_data else ''
            
            # Check if current position
            start_date = position_data.get('startDate', {})
            end_date = position_data.get('endDate')
            is_current = end_date is None
            
            # Map industry from company or position
            industry_raw = company_data.get('industry', '') if company_data else ''
            industry = self.map_industry(industry_raw, title)
            
            if title and company:
                return JobPosition(
                    title=title,
                    company=company,
                    is_current=is_current,
                    industry=industry,
                    location=None  # Would need additional API calls
                )
            
        except Exception as e:
            print(f"❌ Error parsing position: {str(e)}")
        
        return None
    
    def map_industry(self, industry_raw: str, title_context: str = '') -> Optional[IndustryType]:
        """Map LinkedIn industry to our IndustryType enum"""
        industry_lower = (industry_raw + ' ' + title_context).lower()
        
        # Technology mapping
        if any(keyword in industry_lower for keyword in ['technology', 'software', 'tech', 'developer', 'engineer', 'programming']):
            return IndustryType.TECHNOLOGY
        
        # Finance mapping
        elif any(keyword in industry_lower for keyword in ['finance', 'banking', 'investment', 'financial']):
            return IndustryType.FINANCE
        
        # Healthcare mapping
        elif any(keyword in industry_lower for keyword in ['healthcare', 'medical', 'hospital', 'health']):
            return IndustryType.HEALTHCARE
        
        # Education mapping
        elif any(keyword in industry_lower for keyword in ['education', 'university', 'school', 'teacher', 'academic']):
            return IndustryType.EDUCATION
        
        # Manufacturing mapping
        elif any(keyword in industry_lower for keyword in ['manufacturing', 'production', 'factory', 'industrial']):
            return IndustryType.MANUFACTURING
        
        # Retail mapping
        elif any(keyword in industry_lower for keyword in ['retail', 'sales', 'commerce', 'store']):
            return IndustryType.RETAIL
        
        # Government mapping
        elif any(keyword in industry_lower for keyword in ['government', 'public sector', 'civil service']):
            return IndustryType.GOVERNMENT
        
        # Consulting mapping
        elif any(keyword in industry_lower for keyword in ['consulting', 'consultant', 'advisory']):
            return IndustryType.CONSULTING
        
        return None
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get current API status and rate limit information"""
        return {
            'service': 'LinkedIn Official API',
            'authenticated': bool(self.access_token),
            'rate_limit': {
                'calls_per_hour': self.rate_limit['calls_per_hour'],
                'calls_remaining': max(0, self.rate_limit['calls_per_hour'] - self.rate_limit['calls_made']),
                'reset_time': self.rate_limit['reset_time'].isoformat()
            },
            'compliant': True,
            'requires_partnership': True
        }
    
    def test_connection(self) -> bool:
        """Test LinkedIn API connection"""
        try:
            if not self.access_token:
                return False
            
            response = requests.get(
                f"{self.base_url}/me",
                headers=self.get_headers(),
                timeout=10
            )
            
            return response.status_code == 200
            
        except:
            return False