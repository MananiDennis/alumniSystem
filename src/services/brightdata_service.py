import requests
import json
import time
from typing import List, Dict, Any, Optional
from src.config.settings import settings
import logging


class BrightDataService:
    """Streamlined BrightData LinkedIn scraping service"""
    
    def __init__(self):
        self.api_key = settings.brightdata_api_key
        self.dataset_id = settings.brightdata_dataset_id
        self.base_url = "https://api.brightdata.com/datasets/v3"
        self.logger = logging.getLogger(__name__)
        
        if not self.api_key or not self.dataset_id:
            raise ValueError("BrightData API key and Dataset ID must be set in .env file")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_alumni_profiles(self, names: List[str], ecu_filter: bool = True) -> List[Dict[str, Any]]:
        """Get LinkedIn profiles for multiple alumni names"""
        all_profiles = []
        
        for name in names:
            try:
                self.logger.info(f"Fetching LinkedIn data for: {name}")
                profiles = self.get_single_profile(name)
                
                if ecu_filter:
                    profiles = self.filter_ecu_graduates(profiles)
                
                all_profiles.extend(profiles)
                self.logger.info(f"Found {len(profiles)} ECU profiles for {name}")
                
            except Exception as e:
                self.logger.error(f"Error fetching data for {name}: {e}")
                continue
        
        return all_profiles
    
    def get_single_profile(self, full_name: str) -> List[Dict[str, Any]]:
        """Get LinkedIn profile for a single person"""
        # Parse name
        name_parts = full_name.strip().split()
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        # Trigger discovery
        records = [{"first_name": first_name, "last_name": last_name}]
        snapshot_id = self.trigger_discovery(records)
        
        # Wait for completion
        self.wait_for_completion(snapshot_id)
        
        # Get results
        raw_data = self.get_snapshot(snapshot_id)
        return self.normalize_data(raw_data)
    
    def trigger_discovery(self, records: List[Dict[str, Any]]) -> str:
        """Trigger BrightData discovery"""
        url = f"{self.base_url}/trigger"
        params = {
            "dataset_id": self.dataset_id,
            "include_errors": "true",
            "type": "discover_new",
            "discover_by": "name"
        }
        
        response = requests.post(url, headers=self.headers, json=records, params=params)
        response.raise_for_status()
        
        result = response.json()
        return result.get("snapshot_id")
    
    def wait_for_completion(self, snapshot_id: str, max_wait: int = 300) -> None:
        """Wait for snapshot to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            progress = self.check_progress(snapshot_id)
            status = progress.get("status")
            
            if status == "ready":
                return
            elif status == "failed":
                raise Exception(f"BrightData snapshot failed: {progress}")
            
            time.sleep(5)
        
        raise TimeoutError(f"Snapshot {snapshot_id} did not complete within {max_wait} seconds")
    
    def check_progress(self, snapshot_id: str) -> Dict[str, Any]:
        """Check snapshot progress"""
        url = f"{self.base_url}/progress/{snapshot_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_snapshot(self, snapshot_id: str) -> List[Dict[str, Any]]:
        """Get snapshot data"""
        url = f"{self.base_url}/snapshot/{snapshot_id}"
        params = {"format": "json"}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def normalize_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Normalize BrightData response to list of dicts"""
        normalized = []
        
        if isinstance(raw_data, list):
            for item in raw_data:
                if isinstance(item, str):
                    try:
                        normalized.append(json.loads(item))
                    except json.JSONDecodeError:
                        continue
                elif isinstance(item, dict):
                    normalized.append(item)
        elif isinstance(raw_data, dict):
            if "data" in raw_data and isinstance(raw_data["data"], list):
                return self.normalize_data(raw_data["data"])
            else:
                normalized.append(raw_data)
        
        return normalized
    
    def filter_ecu_graduates(self, profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter profiles to only include ECU graduates"""
        ecu_graduates = []
        
        for profile in profiles:
            if self.is_ecu_graduate(profile):
                ecu_graduates.append(profile)
        
        return ecu_graduates
    
    def is_ecu_graduate(self, profile: Dict[str, Any]) -> bool:
        """Check if profile indicates ECU graduation"""
        # Check education list
        education = profile.get('education', [])
        if isinstance(education, list):
            for edu in education:
                if not edu or not edu.get('title'):
                    continue
                title = edu['title'].lower()
                if any(term in title for term in ["edith cowan", "ecu"]):
                    return True
        
        # Check education details string
        edu_details = profile.get("educations_details", "")
        if edu_details:
            details = edu_details.lower()
            if any(term in details for term in ["edith cowan", "ecu"]):
                return True
        
        return False