import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import time
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
import json
import re
from ddgs import DDGS

logger = logging.getLogger(__name__)


class WebResearchService:
    """Simple web research service using common search tools."""

    def __init__(self) -> None:
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
        """Search for person information on the web using DuckDuckGo only"""
        logger.info(f"Starting web research for: {name}")
        results = []
        
        # Generate multiple search queries with better targeting
        queries = self._generate_search_queries(name, additional_info)
        
        logger.info(f"Generated {len(queries)} search queries: {queries}")
        
        # Try each query with DuckDuckGo only
        for query in queries:
            try:
                logger.debug(f"Executing search query: {query}")
                
                # Only use DuckDuckGo - no fallbacks
                search_results = self.duckduckgo_search(query)
                if search_results:
                    logger.info(f"DuckDuckGo found {len(search_results)} results for '{query}'")
                    results.extend(search_results)
                    continue  # Move to next query if we got results
                else:
                    logger.debug(f"DuckDuckGo found no results for '{query}'")
                
                time.sleep(2)  # Respectful delay between queries
                
            except Exception as e:
                logger.error(f"Search error for {query}: {e}")
                # Continue to next query instead of failing completely
                continue
                
        logger.info(f"Total results collected for {name}: {len(results)}")
        return results[:10]  # Return top 10 results
    
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
                "has_professional_info": any(
                    word in text
                    for word in [
                        "engineer",
                        "manager",
                        "director",
                        "analyst",
                        "consultant",
                        "developer",
                        "specialist",
                        "coordinator",
                        "officer",
                    ]
                ),
                "mentions_ecu": any(
                    phrase in text
                    for phrase in ["edith cowan", "ecu", "edith cowan university"]
                ),
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

    def _truncate_text(self, text: str, max_chars: Optional[int]) -> str:
        if not max_chars or len(text) <= max_chars:
            return text
        return text[:max_chars]

    def get_page_text(self, url: str, max_chars: Optional[int] = 30000) -> str:
        """Fetch a page and return cleaned text content for AI processing.

        Returns an empty string on failure.
        """
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'html.parser')
            # Remove script and style tags for cleaner text
            for s in soup(['script', 'style', 'noscript']):
                s.decompose()
            text = soup.get_text(separator='\n')
            # Collapse multiple whitespace
            cleaned = '\n'.join([line.strip() for line in text.splitlines() if line.strip()])
            return self._truncate_text(cleaned, max_chars)
        except Exception as e:
            logger.warning(f"Failed to fetch page text from {url}: {e}")
            return ""
    
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