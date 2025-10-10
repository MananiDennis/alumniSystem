from openai import OpenAI
from typing import Dict, Any, List
from src.config.settings import settings
from src.database.repository import AlumniRepository
from src.database.connection import db_manager

class AIQueryService:
    """AI-powered natural language query service"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        
    def process_natural_query(self, query: str) -> Dict[str, Any]:
        """Convert natural language to database query and execute"""
        if not self.client:
            return {"error": "AI service not available - OpenAI API key not configured"}
            
        try:
            # Convert natural language to structured query
            structured_query = self.convert_to_structured_query(query)
            print(f"Structured query: {structured_query}")  # Debug logging
            
            # Execute the query
            session = db_manager.get_session()
            repo = AlumniRepository(session)
            
            results = repo.search_alumni(**structured_query)
            session.close()
            
            return {
                "query": query,
                "structured_query": structured_query,
                "results": [self.format_alumni(a) for a in results],
                "count": len(results)
            }
            
        except Exception as e:
            print(f"AI query processing error: {e}")
            return {"error": f"Failed to process query: {str(e)}"}
    
    def convert_to_structured_query(self, query: str) -> Dict[str, Any]:
        """Use AI to convert natural language to structured query"""
        prompt = f"""
        Convert this natural language query about alumni into structured search parameters:
        Query: "{query}"
        
        Available parameters:
        - name: string (partial name match)
        - industry: string (Technology, Finance, Healthcare, Education, Consulting, Mining, Government, etc.)
        - company: string (partial company name match)
        - location: string (partial location match)
        - graduation_year_min: integer
        - graduation_year_max: integer
        
        Return only valid JSON with the parameters that match the query. If no specific criteria mentioned, return empty object.
        
        Examples:
        "mining sector graduates" -> {{"industry": "Mining"}}
        "people working at Microsoft" -> {{"company": "Microsoft"}}
        "graduates from 2018 to 2020" -> {{"graduation_year_min": 2018, "graduation_year_max": 2020}}
        "John Smith" -> {{"name": "John Smith"}}
        "Perth alumni in technology" -> {{"location": "Perth", "industry": "Technology"}}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            print(f"AI Response: {content}")  # Debug logging
            
            if not content:
                return {}
            
            # Remove markdown code block formatting if present
            if content.startswith('```json'):
                content = content[7:]  # Remove ```json
            if content.startswith('```'):
                content = content[3:]  # Remove ```
            if content.endswith('```'):
                content = content[:-3]  # Remove trailing ```
            
            content = content.strip()
            print(f"Cleaned content: {content}")  # Debug logging
                
            import json
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}, content: '{content}'")
            return {}
        except Exception as e:
            print(f"AI query conversion error: {e}")
            return {}
    
    def format_alumni(self, alumni) -> Dict[str, Any]:
        """Format alumni for response"""
        job = alumni.get_current_job()
        return {
            "id": alumni.id,
            "name": alumni.full_name,
            "industry": getattr(alumni.industry, 'value', None) if alumni.industry else None,
            "location": alumni.location,
            "current_job": {"title": job.title, "company": job.company} if job else None,
            "linkedin_url": alumni.linkedin_url,
            "confidence_score": alumni.confidence_score
        }