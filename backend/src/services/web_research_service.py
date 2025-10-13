import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
import logging

logger = logging.getLogger(__name__)

class WebResearchService:
    """Simple web research service using common search tools"""
    
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
                time.sleep(1)  # Be respectful
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
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            logger.debug(f"Making request to {url} with params {params}")
            response = requests.get(url, params=params, headers=headers, timeout=10)
            logger.debug(f"Response status: {response.status_code}")
            
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
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    def extract_professional_info(self, url: str) -> Dict[str, Any]:
        """Extract professional information from a webpage"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
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
            
        except Exception as e:
            return {"url": url, "error": str(e)}
    
    def research_alumni_batch(self, names: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Research multiple alumni at once"""
        logger.info(f"Starting batch research for {len(names)} alumni: {names}")
        results = {}
        
        for name in names:
            logger.info(f"Researching {name}...")
            results[name] = self.search_person_web(name)
            time.sleep(2)  # Be respectful to search engines
            
        logger.info(f"Batch research completed for {len(results)} alumni")
        return results