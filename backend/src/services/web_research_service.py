import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class WebResearchService:
    """Simple web research service using common search tools"""
    
    def __init__(self):
        self.session = self._create_session_with_retry()
    
    def _create_session_with_retry(self):
        """Create a requests session with retry logic and proper headers"""
        session = requests.Session()
        
        # Configure retry strategy
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # Add browser-like headers to avoid blocking
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return session
    
    def search_person_web(self, name: str, additional_info: str = "") -> List[Dict[str, Any]]:
        """Search for person information on the web"""
        logger.info(f"Starting web research for: {name}")
        results = []
        
        # Search queries to try
        queries = [
            f'"{name}" ECU "Edith Cowan University"',
            f'"{name}" LinkedIn Australia',
            f'"{name}" {additional_info}' if additional_info else f'"{name}" professional'
        ]
        
        logger.info(f"Generated {len(queries)} search queries: {queries}")
        
        for query in queries:
            try:
                logger.debug(f"Executing search query: {query}")
                # Use DuckDuckGo for simple web search (no API key needed)
                search_results = self.duckduckgo_search(query)
                logger.info(f"Query '{query}' returned {len(search_results)} results")
                results.extend(search_results)
                time.sleep(2)  # Increased delay to be more respectful
            except Exception as e:
                logger.error(f"Search error for {query}: {e}")
                continue
                
        logger.info(f"Total results collected for {name}: {len(results)}")
        return results[:10]  # Return top 10 results
    
    def duckduckgo_search(self, query: str) -> List[Dict[str, Any]]:
        """Simple DuckDuckGo search using HTML scraping"""
        logger.debug(f"Starting DuckDuckGo search for query: {query}")
        try:
            # Use DuckDuckGo search URL
            url = "https://duckduckgo.com/html/"
            params = {"q": query}
            
            logger.debug(f"Making request to {url} with params {params}")
            response = self.session.get(url, params=params, timeout=15)  # Increased timeout
            logger.debug(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.warning(f"DuckDuckGo returned status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            
            # Find search results
            result_divs = soup.find_all('div', class_='result')
            logger.debug(f"Found {len(result_divs)} result divs")
            
            for i, div in enumerate(result_divs[:5]):  # Top 5 results
                title_elem = div.find('a', class_='result__a')
                snippet_elem = div.find('a', class_='result__snippet')
                
                if title_elem:
                    title = title_elem.get_text().strip()
                    url = title_elem.get('href', '')
                    
                    # Clean up URL (DuckDuckGo redirects)
                    if url.startswith('//duckduckgo.com/l/?uddg='):
                        url = url.split('uddg=')[1].split('&')[0]
                        url = requests.utils.unquote(url)
                    
                    snippet = ""
                    if snippet_elem:
                        snippet = snippet_elem.get_text().strip()
                    
                    result = {
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "source": "DuckDuckGo"
                    }
                    results.append(result)
                    logger.debug(f"Extracted result {i+1}: {title[:50]}...")
            
            logger.info(f"DuckDuckGo search completed, found {len(results)} results")
            return results
            
        except requests.exceptions.Timeout:
            logger.error(f"DuckDuckGo search timeout for query: {query}")
            return []
        except requests.exceptions.ConnectionError:
            logger.error(f"DuckDuckGo connection error for query: {query}")
            return []
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
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
        """Research multiple alumni at once"""
        logger.info(f"Starting batch research for {len(names)} alumni: {names}")
        results = {}
        
        for name in names:
            logger.info(f"Researching {name}...")
            results[name] = self.search_person_web(name)
            time.sleep(3)  # Increased delay between names to be more respectful
            
        logger.info(f"Batch research completed for {len(results)} alumni")
        return results