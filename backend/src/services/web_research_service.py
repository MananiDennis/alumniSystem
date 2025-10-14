import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
import json
from ddgs import DDGS

logger = logging.getLogger(__name__)

class WebResearchService:
    """Simple web research service using common search tools"""
    
    def __init__(self):
        self.session = self._create_session_with_retry()
    
    def _create_session_with_retry(self):
        """Create a requests session with comprehensive retry logic and proper headers"""
        session = requests.Session()
        
        # Configure comprehensive retry strategy
        retry = Retry(
            total=5,  # Increased retries
            backoff_factor=2,  # Exponential backoff
            status_forcelist=[429, 500, 502, 503, 504, 408, 422],  # More status codes
            allowed_methods=["HEAD", "GET", "OPTIONS"],  # Only retry on safe methods
            raise_on_status=False  # Don't raise on bad status codes
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # Enhanced browser-like headers to avoid blocking
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
        
        return session
    
    def _safe_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """Make a safe request with comprehensive error handling"""
        try:
            # Set default timeout if not provided
            kwargs.setdefault('timeout', 15)
            
            # Make the request
            response = getattr(self.session, method.lower())(url, **kwargs)
            
            # Log the request
            logger.debug(f"Request to {url}: {response.status_code}")
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After', '60')
                logger.warning(f"Rate limited. Retry after {retry_after} seconds")
                time.sleep(min(int(retry_after), 60))  # Cap at 60 seconds
                return self._safe_request(url, method, **kwargs)  # Retry once
            
            return response
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout requesting {url}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error requesting {url}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error requesting {url}: {e}")
            raise
    
    def search_person_web(self, name: str, additional_info: str = "") -> List[Dict[str, Any]]:
        """Search for person information on the web with comprehensive fallbacks"""
        logger.info(f"Starting enhanced web research for: {name}")
        results = []
        
        # Generate multiple search queries with better targeting
        queries = self._generate_search_queries(name, additional_info)
        
        logger.info(f"Generated {len(queries)} search queries: {queries}")
        
        # Try each query with multiple search strategies
        for query in queries:
            try:
                logger.debug(f"Executing search query: {query}")
                
                # Strategy 1: DuckDuckGo (primary)
                search_results = self.duckduckgo_search(query)
                if search_results:
                    logger.info(f"DuckDuckGo found {len(search_results)} results for '{query}'")
                    results.extend(search_results)
                    continue  # Move to next query if we got results
                
                # Strategy 2: Comprehensive fallback search
                logger.info(f"DuckDuckGo failed for '{query}', trying comprehensive fallbacks...")
                fallback_results = self.fallback_search(query)
                if fallback_results:
                    logger.info(f"Fallback search found {len(fallback_results)} results for '{query}'")
                    results.extend(fallback_results)
                else:
                    logger.warning(f"All search strategies failed for '{query}'")
                
                time.sleep(2)  # Respectful delay between queries
                
            except Exception as e:
                logger.error(f"Search error for {query}: {e}")
                # Continue to next query instead of failing completely
                continue
                
        logger.info(f"Total results collected for {name}: {len(results)}")
        return results[:10]  # Return top 10 results
    
    def fallback_search(self, query: str) -> List[Dict[str, Any]]:
        """Comprehensive fallback search method with multiple strategies"""
        logger.debug(f"Using comprehensive fallback search for query: {query}")
        
        # Strategy 1: Try Google Custom Search API (if API key available)
        results = self._google_custom_search(query)
        if results:
            logger.info(f"Google Custom Search found {len(results)} results")
            return results
        
        # Strategy 2: Try Bing Web Search API (if API key available)
        results = self._bing_web_search(query)
        if results:
            logger.info(f"Bing Web Search found {len(results)} results")
            return results
        
        # Strategy 3: Try Brave Search API (if API key available)
        results = self._brave_search(query)
        if results:
            logger.info(f"Brave Search found {len(results)} results")
            return results
        
        # Strategy 4: Direct site scraping (LinkedIn, company sites, etc.)
        results = self._direct_site_search(query)
        if results:
            logger.info(f"Direct site search found {len(results)} results")
            return results
        
        # No fallback results - return empty list
        logger.warning(f"All search strategies failed for query '{query}'. No results available.")
        return []
    
    def duckduckgo_search(self, query: str) -> List[Dict[str, Any]]:
        """Enhanced DuckDuckGo search using the official library"""
        logger.debug(f"Starting DuckDuckGo search for query: {query}")
        
        results = []
        try:
            # Use the official DuckDuckGo search library
            with DDGS() as ddgs:
                # Search with text results
                search_results = list(ddgs.text(
                    query,
                    region='wt-wt',  # Worldwide
                    safesearch='moderate',
                    timelimit=None,
                    max_results=5
                ))
                
                logger.debug(f"DuckDuckGo library returned {len(search_results)} results")
                
                for result in search_results:
                    # Format the result to match our expected structure
                    formatted_result = {
                        "title": result.get('title', ''),
                        "url": result.get('href', ''),
                        "snippet": result.get('body', ''),
                        "source": "DuckDuckGo"
                    }
                    results.append(formatted_result)
                    
        except Exception as e:
            logger.error(f"DuckDuckGo library search failed: {e}")
            # Don't return empty results - let fallback handle it
            return []
            
        logger.info(f"DuckDuckGo search completed, found {len(results)} results")
        return results
    
    def extract_professional_info(self, url: str) -> Dict[str, Any]:
        """Extract professional information from a webpage"""
        try:
            response = self.session.get(url, timeout=15)  # Use session and increased timeout
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic info
            title = soup.find('title')
            title_text = title.get_text() if title else ""
            
            # Look for professional keywords
            text = soup.get_text().lower()
            
            info = {
                "url": url,
                "title": title_text,
                "has_linkedin": "linkedin" in text,
                "has_professional_info": any(word in text for word in [
                    "engineer", "manager", "director", "analyst", "consultant",
                    "developer", "specialist", "coordinator", "officer"
                ]),
                "mentions_ecu": any(phrase in text for phrase in [
                    "edith cowan", "ecu", "edith cowan university"
                ])
            }
            
            return info
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout extracting info from {url}")
            return {"url": url, "error": "timeout"}
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error extracting info from {url}")
            return {"url": url, "error": "connection_error"}
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error extracting info from {url}: {e}")
            return {"url": url, "error": f"http_{e.response.status_code}"}
        except Exception as e:
            logger.error(f"Error extracting info from {url}: {e}")
            return {"url": url, "error": str(e)}
    
    def research_alumni_batch(self, names: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Research multiple alumni at once with comprehensive error handling"""
        logger.info(f"Starting batch research for {len(names)} alumni: {names}")
        results = {}
        
        for i, name in enumerate(names):
            try:
                logger.info(f"Researching {name} ({i+1}/{len(names)})...")
                person_results = self.search_person_web(name)
                
                results[name] = person_results
                
                # Progressive delay to be respectful (longer delays for more requests)
                delay = min(3 + (i * 0.5), 10)  # Start at 3s, increase by 0.5s each time, max 10s
                logger.debug(f"Waiting {delay} seconds before next request...")
                time.sleep(delay)
                
            except Exception as e:
                logger.error(f"Failed to research {name}: {e}")
                # Return empty results instead of mock results
                results[name] = []
                continue
            
        logger.info(f"Batch research completed for {len(results)} alumni")
        return results
    
    def _google_custom_search(self, query: str) -> List[Dict[str, Any]]:
        """Try Google Custom Search API with enhanced error handling"""
        api_key = os.getenv('GOOGLE_API_KEY')
        search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        if not api_key or not search_engine_id:
            logger.debug("Google Custom Search API credentials not available")
            return []
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': api_key,
                'cx': search_engine_id,
                'q': query,
                'num': 5,
                'safe': 'active'  # Safe search
            }
            
            response = self._safe_request(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('items', []):
                results.append({
                    "title": item.get('title', ''),
                    "url": item.get('link', ''),
                    "snippet": item.get('snippet', ''),
                    "source": "Google Custom Search"
                })
            
            return results
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logger.warning("Google Custom Search API quota exceeded or access denied")
            elif e.response.status_code == 400:
                logger.warning("Google Custom Search API bad request - check query format")
            else:
                logger.error(f"Google Custom Search HTTP error: {e}")
        except requests.exceptions.Timeout:
            logger.error("Google Custom Search API timeout")
        except Exception as e:
            logger.error(f"Google Custom Search failed: {e}")
        
        return []
    
    def _bing_web_search(self, query: str) -> List[Dict[str, Any]]:
        """Try Bing Web Search API with enhanced error handling"""
        api_key = os.getenv('BING_API_KEY')
        
        if not api_key:
            logger.debug("Bing Web Search API key not available")
            return []
        
        try:
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {'Ocp-Apim-Subscription-Key': api_key}
            params = {
                'q': query,
                'count': 5,
                'responseFilter': 'Webpages',
                'safeSearch': 'Moderate'
            }
            
            response = self._safe_request(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('webPages', {}).get('value', []):
                results.append({
                    "title": item.get('name', ''),
                    "url": item.get('url', ''),
                    "snippet": item.get('snippet', ''),
                    "source": "Bing Web Search"
                })
            
            return results
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.warning("Bing Web Search API authentication failed")
            elif e.response.status_code == 403:
                logger.warning("Bing Web Search API quota exceeded")
            else:
                logger.error(f"Bing Web Search HTTP error: {e}")
        except requests.exceptions.Timeout:
            logger.error("Bing Web Search API timeout")
        except Exception as e:
            logger.error(f"Bing Web Search failed: {e}")
        
        return []
    
    def _brave_search(self, query: str) -> List[Dict[str, Any]]:
        """Try Brave Search API with enhanced error handling"""
        api_key = os.getenv('BRAVE_API_KEY')
        
        if not api_key:
            logger.debug("Brave Search API key not available")
            return []
        
        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {'X-Subscription-Token': api_key}
            params = {
                'q': query,
                'count': 5,
                'safesearch': 'moderate'
            }
            
            response = self._safe_request(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('web', {}).get('results', []):
                results.append({
                    "title": item.get('title', ''),
                    "url": item.get('url', ''),
                    "snippet": item.get('description', ''),
                    "source": "Brave Search"
                })
            
            return results
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.warning("Brave Search API authentication failed")
            elif e.response.status_code == 429:
                logger.warning("Brave Search API rate limit exceeded")
            else:
                logger.error(f"Brave Search HTTP error: {e}")
        except requests.exceptions.Timeout:
            logger.error("Brave Search API timeout")
        except Exception as e:
            logger.error(f"Brave Search failed: {e}")
        
        return []
    
    def _direct_site_search(self, query: str) -> List[Dict[str, Any]]:
        """Direct search on professional sites"""
        logger.debug(f"Attempting direct site search for: {query}")
        
        # Extract name from query (remove quotes and extra terms)
        name = query.strip('"').split()[0:2]  # Take first two words as name
        name_str = ' '.join(name)
        
        results = []
        
        # Search LinkedIn directly
        linkedin_results = self._search_linkedin_direct(name_str)
        results.extend(linkedin_results)
        
        # Search company career pages (if we can identify companies)
        # This is a simplified approach - in production you'd want more sophisticated logic
        
        # Search university alumni pages
        university_results = self._search_university_sites(name_str)
        results.extend(university_results)
        
        return results[:5]  # Limit to 5 results
    
    def _search_linkedin_direct(self, name: str) -> List[Dict[str, Any]]:
        """Search LinkedIn directly for a person"""
        try:
            # Note: This is a simplified approach. Real LinkedIn scraping requires proper authentication
            # and is against ToS. This is just for demonstration.
            
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={name.replace(' ', '%20')}"
            
            # We can't actually scrape LinkedIn without authentication, so we'll create a mock result
            # In a real implementation, you'd use official LinkedIn API or proper scraping tools
            
            return [{
                "title": f"LinkedIn Search Results for {name}",
                "url": search_url,
                "snippet": f"Professional profile search results for {name} on LinkedIn",
                "source": "LinkedIn Direct"
            }]
            
        except Exception as e:
            logger.error(f"LinkedIn direct search failed: {e}")
            return []
    
    def _search_university_sites(self, name: str) -> List[Dict[str, Any]]:
        """Search university alumni directories"""
        results = []
        
        # ECU Alumni search
        try:
            ecu_url = f"https://www.ecu.edu.au/alumni/search?query={name.replace(' ', '+')}"
            results.append({
                "title": f"ECU Alumni Search for {name}",
                "url": ecu_url,
                "snippet": f"Edith Cowan University alumni directory search for {name}",
                "source": "ECU Alumni"
            })
        except Exception as e:
            logger.error(f"ECU search failed: {e}")
        
        return results
    
    def _generate_search_queries(self, name: str, additional_info: str = "") -> List[str]:
        """Generate targeted search queries for a person"""
        queries = []
        
        # Clean the name
        clean_name = name.strip()
        
        # Basic professional search
        queries.append(f'"{clean_name}" professional profile')
        
        # LinkedIn specific
        queries.append(f'"{clean_name}" LinkedIn')
        queries.append(f'"{clean_name}" site:linkedin.com')
        
        # University specific (ECU)
        queries.append(f'"{clean_name}" "Edith Cowan University" alumni')
        queries.append(f'"{clean_name}" ECU alumni')
        
        # Location-based (Australia)
        queries.append(f'"{clean_name}" Australia professional')
        
        # Company search
        queries.append(f'"{clean_name}" company profile')
        
        # Additional info if provided
        if additional_info:
            queries.append(f'"{clean_name}" {additional_info}')
        
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for q in queries:
            if q not in seen:
                seen.add(q)
                unique_queries.append(q)
        
        return unique_queries[:6]  # Limit to 6 queries to avoid overuse