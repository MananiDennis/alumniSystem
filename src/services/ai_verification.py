import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from openai import OpenAI
from src.config.settings import settings
import logging
from src.models.alumni import IndustryType


@dataclass
class VerificationResult:
    """Result of AI profile verification"""
    is_match: bool
    confidence_score: float
    reason: str
    extracted_info: Optional[Dict[str, Any]] = None


class AIVerificationService:
    """AI-powered profile verification using OpenAI"""
    
    def __init__(self):
        if settings.openai_api_key:
            self.client = OpenAI(api_key=settings.openai_api_key)
        else:
            self.client = None
        self.logger = logging.getLogger(__name__)
    
    def normalize_industry(self, industry_str: Optional[str]) -> Optional[IndustryType]:
        """Normalize industry string to IndustryType enum"""
        if not industry_str:
            return None
        
        # Clean and normalize the industry string
        normalized = industry_str.strip().lower()
        
        # Map common industry names to IndustryType enum
        industry_mapping = {
            # Technology
            'technology': IndustryType.TECHNOLOGY,
            'information technology': IndustryType.TECHNOLOGY,
            'software': IndustryType.TECHNOLOGY,
            'it': IndustryType.TECHNOLOGY,
            'computer': IndustryType.TECHNOLOGY,
            'tech': IndustryType.TECHNOLOGY,
            'engineering': IndustryType.TECHNOLOGY,
            'data': IndustryType.TECHNOLOGY,
            'ai': IndustryType.TECHNOLOGY,
            'artificial intelligence': IndustryType.TECHNOLOGY,
            
            # Finance
            'finance': IndustryType.FINANCE,
            'financial': IndustryType.FINANCE,
            'banking': IndustryType.FINANCE,
            'investment': IndustryType.FINANCE,
            'accounting': IndustryType.FINANCE,
            
            # Healthcare
            'healthcare': IndustryType.HEALTHCARE,
            'health': IndustryType.HEALTHCARE,
            'medical': IndustryType.HEALTHCARE,
            'pharmaceutical': IndustryType.HEALTHCARE,
            'biotech': IndustryType.HEALTHCARE,
            
            # Education
            'education': IndustryType.EDUCATION,
            'academic': IndustryType.EDUCATION,
            'teaching': IndustryType.EDUCATION,
            'university': IndustryType.EDUCATION,
            'school': IndustryType.EDUCATION,
            
            # Consulting
            'consulting': IndustryType.CONSULTING,
            'consultant': IndustryType.CONSULTING,
            'advisory': IndustryType.CONSULTING,
            
            # Mining
            'mining': IndustryType.MINING,
            'resources': IndustryType.MINING,
            'energy': IndustryType.MINING,
            
            # Government
            'government': IndustryType.GOVERNMENT,
            'public sector': IndustryType.GOVERNMENT,
            'military': IndustryType.GOVERNMENT,
            
            # Non-Profit
            'non-profit': IndustryType.NON_PROFIT,
            'nonprofit': IndustryType.NON_PROFIT,
            'charity': IndustryType.NON_PROFIT,
            'ngo': IndustryType.NON_PROFIT,
            
            # Retail
            'retail': IndustryType.RETAIL,
            'sales': IndustryType.RETAIL,
            'marketing': IndustryType.RETAIL,
            
            # Manufacturing
            'manufacturing': IndustryType.MANUFACTURING,
            'production': IndustryType.MANUFACTURING,
            'industrial': IndustryType.MANUFACTURING,
        }
        
        # Try exact match first
        if normalized in industry_mapping:
            return industry_mapping[normalized]
        
        # Try partial matches
        for key, value in industry_mapping.items():
            if key in normalized or normalized in key:
                return value
        
        # Default to OTHER for unknown industries
        return IndustryType.OTHER
    
    def verify_profile_match(self, 
                           target_name: str,
                           scraped_data: Dict[str, Any],
                           graduation_year: Optional[int] = None,
                           location_hint: Optional[str] = None) -> VerificationResult:
        """Check if LinkedIn profile matches the target person"""
        
        if not self.client:
            return self.basic_verification(target_name, scraped_data, graduation_year, location_hint)
        
        try:
            # Prepare data for AI
            context = self.prepare_context(target_name, scraped_data, graduation_year, location_hint)
            prompt = self.create_prompt(context)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using the more cost-effective model
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at verifying if LinkedIn profiles match target individuals. "
                                 "You analyze names, locations, education timing, and career progression to determine matches. "
                                 "Always respond with valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=500
            )
            
            # Parse response
            result_text = response.choices[0].message.content.strip()
            result_data = json.loads(result_text)
            
            return VerificationResult(
                is_match=result_data.get("is_match", False),
                confidence_score=result_data.get("confidence_score", 0.0),
                reason=result_data.get("reason", "AI verification completed"),
                extracted_info=result_data.get("extracted_info")
            )
            
        except json.JSONDecodeError as e:
            print(f"AI response parsing failed: {e}")
            return self.basic_verification(target_name, scraped_data, graduation_year, location_hint)
        
        except Exception as e:
            print(f"AI verification failed: {e}")
            return self.basic_verification(target_name, scraped_data, graduation_year, location_hint)
    
    def prepare_context(self, 
                      target_name: str,
                      scraped_data: Dict[str, Any],
                      graduation_year: Optional[int],
                      location_hint: Optional[str]) -> Dict[str, Any]:
        """Prepare context data for AI verification"""
        return {
            "target_name": target_name,
            "graduation_year": graduation_year,
            "location_hint": location_hint,
            "scraped_profile": {
                "name": scraped_data.get("name", ""),
                "headline": scraped_data.get("headline", ""),
                "location": scraped_data.get("location", ""),
                "current_position": scraped_data.get("current_position", {}),
                "experience": scraped_data.get("experience", [])[:3],  # Limit to recent experience
                "education": scraped_data.get("education", [])[:2]     # Limit to recent education
            }
        }
    
    def create_prompt(self, context: Dict[str, Any]) -> str:
        """Create AI prompt for profile verification"""
        return f"""
Please verify if this LinkedIn profile matches the target person:

TARGET PERSON:
- Name: {context['target_name']}
- Expected Graduation Year: {context['graduation_year'] or 'Unknown'}
- Expected Location: {context['location_hint'] or 'Unknown'}

LINKEDIN PROFILE:
- Name: {context['scraped_profile']['name']}
- Headline: {context['scraped_profile']['headline']}
- Location: {context['scraped_profile']['location']}
- Current Position: {context['scraped_profile']['current_position']}
- Recent Experience: {context['scraped_profile']['experience']}
- Education: {context['scraped_profile']['education']}

ANALYSIS CRITERIA:
1. Name similarity (exact match, nicknames, maiden names)
2. Location consistency (Australian locations preferred)
3. Education timing (graduation year alignment)
4. Career progression plausibility
5. Overall profile coherence

Please respond with ONLY valid JSON in this format:
{{
    "is_match": true/false,
    "confidence_score": 0.0-1.0,
    "reason": "Brief explanation of the decision",
    "extracted_info": {{
        "likely_graduation_year": year_or_null,
        "career_level": "entry/mid/senior",
        "industry_focus": "primary_industry"
    }}
}}

Focus on Australian alumni and be conservative with matches to avoid false positives.
"""
    
    def basic_verification(self, 
                         target_name: str,
                         scraped_data: Dict[str, Any],
                         graduation_year: Optional[int],
                         location_hint: Optional[str]) -> VerificationResult:
        """Basic verification without AI (fallback)"""
        
        scraped_name = scraped_data.get("name", "")
        scraped_location = scraped_data.get("location", "")
        
        # Basic name matching
        name_similarity = self.calculate_name_similarity(target_name, scraped_name)
        
        # Location check
        location_match = False
        if location_hint and scraped_location:
            location_match = location_hint.lower() in scraped_location.lower()
        elif scraped_location:
            # Check if it's an Australian location
            australian_indicators = ['australia', 'perth', 'sydney', 'melbourne', 'brisbane']
            location_match = any(indicator in scraped_location.lower() for indicator in australian_indicators)
        
        # Calculate basic confidence
        confidence = name_similarity * 0.7
        if location_match:
            confidence += 0.3
        
        # Determine if it's a match
        is_match = confidence > 0.6 and name_similarity > 0.5
        
        reason = f"Basic verification: name similarity {name_similarity:.2f}, location match: {location_match}"
        
        return VerificationResult(
            is_match=is_match,
            confidence_score=confidence,
            reason=reason
        )
    
    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names"""
        if not name1 or not name2:
            return 0.0
        
        name1_parts = set(name1.lower().split())
        name2_parts = set(name2.lower().split())
        
        if not name1_parts or not name2_parts:
            return 0.0
        
        intersection = name1_parts.intersection(name2_parts)
        union = name1_parts.union(name2_parts)
        
        return len(intersection) / len(union) if union else 0.0
    
    def enhance_profile_data(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to enhance and clean scraped profile data"""
        
        if not settings.openai_api_key:
            return scraped_data
        
        try:
            prompt = f"""
Please analyze and enhance this LinkedIn profile data:

{json.dumps(scraped_data, indent=2)}

Tasks:
1. Clean and standardize job titles
2. Identify the primary industry
3. Extract key skills and expertise areas
4. Estimate career progression level
5. Identify any missing or inconsistent information

Respond with enhanced data in JSON format:
{{
    "cleaned_name": "standardized name",
    "primary_industry": "main industry",
    "career_level": "entry/mid/senior/executive",
    "key_skills": ["skill1", "skill2"],
    "career_progression": "brief assessment",
    "data_quality_score": 0.0-1.0,
    "recommendations": ["improvement suggestions"]
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing professional profiles and career data. "
                                 "Provide structured, accurate analysis in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            enhancement_data = json.loads(response.choices[0].message.content.strip())
            
            # Merge enhancement data with original
            enhanced_data = scraped_data.copy()
            enhanced_data["ai_enhancement"] = enhancement_data
            
            return enhanced_data
            
        except Exception as e:
            self.logger.error(f"Profile enhancement failed: {e}")
            return scraped_data
    
    def convert_web_data_to_profile(self, target_name: str, web_results: List[Dict[str, Any]]) -> Optional[Any]:
        """Convert unstructured web research data into structured AlumniProfile"""
        self.logger.info(f"Starting AI conversion for {target_name} with {len(web_results)} web results")
        
        if not self.client:
            self.logger.warning("OpenAI client not available, skipping AI conversion")
            return None
            
        try:
            # Prepare web data for AI processing
            web_content = "\n\n".join([
                f"Title: {result.get('title', '')}\n"
                f"URL: {result.get('url', '')}\n"
                f"Snippet: {result.get('snippet', '')}"
                for result in web_results[:10]  # Limit to top 10 results
            ])
            
            self.logger.debug(f"Prepared web content for AI: {len(web_content)} characters")
            
            prompt = f"""
            Analyze the following web search results for "{target_name}" and extract structured alumni information.
            
            Web Search Results:
            {web_content}
            
            Based on this web data, create a structured alumni profile. Focus on:
            1. Professional information (current job, company, industry)
            2. Education information (university, graduation year if mentioned)
            3. Location information
            4. LinkedIn or professional profiles
            5. Career progression
            
            IMPORTANT: Respond with ONLY a valid JSON object. Do not include any explanatory text.
            
            JSON Format (copy this exact structure):
            {{
                "full_name": "extracted full name or null",
                "graduation_year": graduation_year_as_integer_or_null,
                "location": "location string or null",
                "industry": "industry name or null",
                "linkedin_url": "linkedin URL or null",
                "confidence_score": confidence_score_between_0_and_1,
                "current_job_title": "job title or null",
                "current_company": "company name or null",
                "current_job_industry": "industry name or null",
                "university": "university name or null",
                "degree": "degree type or null",
                "data_source_url": "best source URL or null"
            }}
            
            Rules:
            - If no relevant information found, return null
            - Be conservative with confidence scores (0.8+ only for clear matches)
            - graduation_year must be an integer or null
            - confidence_score must be between 0.0 and 1.0
            - Use null for missing information
            """
            
            self.logger.debug("Calling OpenAI API for web data conversion")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert at extracting structured professional information from web search results. "
                                 "You create accurate alumni profiles from unstructured web data. "
                                 "Always respond with valid JSON or null."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent structured output
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content.strip()
            self.logger.debug(f"AI response received: {len(result_text)} characters")
            self.logger.info(f"Raw AI response: '{result_text}'")
            
            # Handle null response
            if result_text.lower() == "null":
                self.logger.info(f"AI returned null for {target_name} - no relevant information found")
                return None
                
            # Parse JSON response
            self.logger.debug("Parsing AI response as JSON")
            try:
                profile_data = json.loads(result_text)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse AI response as JSON: {e}")
                self.logger.error(f"Raw response was: '{result_text}'")
                return None
            
            # Validate that we got a dictionary
            if not isinstance(profile_data, dict):
                self.logger.error(f"AI response is not a JSON object: {type(profile_data)}")
                return None
            
            self.logger.info(f"Successfully parsed profile data for {target_name}: {profile_data.get('full_name', 'Unknown')}")
            
            # Check confidence threshold
            confidence = profile_data.get("confidence_score", 0)
            if not isinstance(confidence, (int, float)) or confidence < 0.5:
                self.logger.info(f"Confidence score {confidence} below threshold 0.5 or invalid, skipping profile for {target_name}")
                return None
            
            # Validate required fields
            if not profile_data.get("full_name"):
                self.logger.warning(f"No full_name found in AI response for {target_name}")
                return None
            
            # Convert to AlumniProfile object
            from src.models.alumni import AlumniProfile, JobPosition, DataSource
            
            # Create current job if available
            work_history = []
            current_job = None
            if profile_data.get("current_job_title") and profile_data.get("current_company"):
                current_job = JobPosition(
                    title=profile_data.get("current_job_title", ""),
                    company=profile_data.get("current_company", ""),
                    start_date=None,
                    end_date=None,
                    is_current=True,
                    industry=self.normalize_industry(profile_data.get("current_job_industry")),
                    location=profile_data.get("location")
                )
                work_history.append(current_job)
                self.logger.debug(f"Created current job: {current_job.title} at {current_job.company}")
            
            # Create data sources
            data_sources = []
            if profile_data.get("data_source_url"):
                source = DataSource(
                    source_type="web-research",
                    source_url=profile_data.get("data_source_url"),
                    confidence_score=confidence
                )
                data_sources.append(source)
            
            self.logger.debug(f"Created {len(data_sources)} data sources")
            
            # Determine industry (use current job industry or general industry)
            industry = self.normalize_industry(profile_data.get("current_job_industry") or profile_data.get("industry"))
            self.logger.debug(f"Industry set to: {industry}")
            
            # Create the profile
            profile = AlumniProfile(
                full_name=profile_data.get("full_name", target_name),
                graduation_year=profile_data.get("graduation_year"),
                location=profile_data.get("location"),
                industry=industry,
                linkedin_url=profile_data.get("linkedin_url"),
                confidence_score=confidence,
                data_sources=data_sources
            )
            
            # Add work history
            for job in work_history:
                profile.add_job_position(job)
            
            self.logger.info(f"Successfully created AlumniProfile for {target_name} with confidence {profile.confidence_score}")
            return profile
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse AI response as JSON: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Web data conversion failed: {e}")
            return None