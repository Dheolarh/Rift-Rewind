"""
Riot API Client with rate limiting and error handling
"""

import os
import time
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from .constants import (
    RIOT_API_PLATFORM_BASE,
    RIOT_API_REGIONAL_BASE,
    RIOT_API_ENDPOINTS,
    PLATFORM_TO_REGIONAL,
    RIOT_API_RATE_LIMIT_PER_SECOND,
)


class RiotAPIClient:
    """
    Client for interacting with Riot Games API with rate limiting and retry logic.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Riot API client.
        
        Args:
            api_key: Riot API key (defaults to RIOT_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get('RIOT_API_KEY')
        if not self.api_key:
            raise ValueError("RIOT_API_KEY is required")
        
        self.headers = {
            'X-Riot-Token': self.api_key,
            'Accept': 'application/json'
        }
        
        # Simple rate limiting tracking
        self.request_times = []
        self.max_requests_per_second = RIOT_API_RATE_LIMIT_PER_SECOND
    
    def _wait_for_rate_limit(self):
        """
        Simple rate limiting: ensure we don't exceed max requests per second.
        """
        now = time.time()
        
        # Remove timestamps older than 1 second
        self.request_times = [t for t in self.request_times if now - t < 1.0]
        
        # If we've hit the limit, wait
        if len(self.request_times) >= self.max_requests_per_second:
            sleep_time = 1.0 - (now - self.request_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
            self.request_times = []
        
        self.request_times.append(time.time())
    
    def _make_request(self, url: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request with retry logic.
        
        Args:
            url: The full URL to request
            max_retries: Maximum number of retries
            
        Returns:
            JSON response or None if failed
        """
        self._wait_for_rate_limit()
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    print(f"Resource not found (404): {url}")
                    return None
                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    retry_after = int(response.headers.get('Retry-After', 2))
                    print(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                elif response.status_code == 403:
                    print(f"Forbidden (403) - check API key: {url}")
                    return None
                else:
                    print(f"Error {response.status_code}: {url}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    return None
                    
            except requests.exceptions.Timeout:
                print(f"Timeout on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return None
            except Exception as e:
                print(f"Request error: {e}")
                return None
        
        return None
    
    # ==================== SUMMONER-V4 API ====================
    
    def get_summoner_by_name(self, summoner_name: str, platform: str) -> Optional[Dict[str, Any]]:
        """
        Get summoner data by name using SUMMONER-V4 (Platform routing).
        
        Args:
            summoner_name: The summoner name
            platform: Platform code (e.g., 'na1', 'euw1')
            
        Returns:
            Summoner data with puuid, summonerId, accountId, etc.
        """
        base_url = RIOT_API_PLATFORM_BASE.format(platform=platform)
        endpoint = RIOT_API_ENDPOINTS['summoner_by_name'].format(summonerName=summoner_name)
        url = base_url + endpoint
        
        print(f"Fetching summoner: {summoner_name} on {platform}")
        return self._make_request(url)
    
    def get_summoner_by_puuid(self, puuid: str, platform: str) -> Optional[Dict[str, Any]]:
        """
        Get summoner data by PUUID using SUMMONER-V4 (Platform routing).
        
        Args:
            puuid: The player PUUID
            platform: Platform code
            
        Returns:
            Summoner data
        """
        base_url = RIOT_API_PLATFORM_BASE.format(platform=platform)
        endpoint = RIOT_API_ENDPOINTS['summoner_by_puuid'].format(encryptedPUUID=puuid)
        url = base_url + endpoint
        
        return self._make_request(url)
    
    # ==================== LEAGUE-V4 API ====================
    
    def get_league_entries(self, summoner_id: str, platform: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get ranked league entries for a summoner using LEAGUE-V4 (Platform routing).
        
        Args:
            summoner_id: The encrypted summoner ID
            platform: Platform code
            
        Returns:
            List of league entries (Solo/Duo, Flex, etc.)
        """
        base_url = RIOT_API_PLATFORM_BASE.format(platform=platform)
        endpoint = RIOT_API_ENDPOINTS['league_by_summoner'].format(encryptedSummonerId=summoner_id)
        url = base_url + endpoint
        
        print(f"Fetching ranked info for summoner: {summoner_id}")
        return self._make_request(url)
    
    # ==================== MATCH-V5 API ====================
    
    def get_match_ids(
        self,
        puuid: str,
        platform: str,
        count: int = 100,
        start: int = 0,
        queue: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> Optional[List[str]]:
        """
        Get match IDs for a player using MATCH-V5 (Regional routing).
        
        Args:
            puuid: Player PUUID
            platform: Platform code (will be converted to regional)
            count: Number of matches to return (max 100)
            start: Start index
            queue: Queue ID filter (optional)
            start_time: Unix timestamp filter (optional)
            end_time: Unix timestamp filter (optional)
            
        Returns:
            List of match IDs
        """
        regional = PLATFORM_TO_REGIONAL.get(platform)
        if not regional:
            print(f"Unknown platform: {platform}")
            return None
        
        base_url = RIOT_API_REGIONAL_BASE.format(regional=regional)
        endpoint = RIOT_API_ENDPOINTS['match_ids_by_puuid'].format(puuid=puuid)
        
        # Build query parameters
        params = [f"count={count}", f"start={start}"]
        if queue:
            params.append(f"queue={queue}")
        if start_time:
            params.append(f"startTime={start_time}")
        if end_time:
            params.append(f"endTime={end_time}")
        
        url = base_url + endpoint + "?" + "&".join(params)
        
        print(f"Fetching {count} match IDs for PUUID: {puuid[:8]}...")
        return self._make_request(url)
    
    def get_match_details(self, match_id: str, platform: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed match data using MATCH-V5 (Regional routing).
        
        Args:
            match_id: The match ID
            platform: Platform code (will be converted to regional)
            
        Returns:
            Match details including all participants, timeline, etc.
        """
        regional = PLATFORM_TO_REGIONAL.get(platform)
        if not regional:
            print(f"Unknown platform: {platform}")
            return None
        
        base_url = RIOT_API_REGIONAL_BASE.format(regional=regional)
        endpoint = RIOT_API_ENDPOINTS['match_by_id'].format(matchId=match_id)
        url = base_url + endpoint
        
        return self._make_request(url)
    
    # ==================== BATCH OPERATIONS ====================
    
    def get_matches_batch(
        self,
        match_ids: List[str],
        platform: str,
        batch_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch multiple match details with batching.
        
        Args:
            match_ids: List of match IDs to fetch
            platform: Platform code
            batch_size: Number of concurrent requests (for rate limiting)
            
        Returns:
            List of match details
        """
        matches = []
        total = len(match_ids)
        
        print(f"Fetching {total} matches in batches of {batch_size}...")
        
        for i in range(0, total, batch_size):
            batch = match_ids[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size}")
            
            for match_id in batch:
                match_data = self.get_match_details(match_id, platform)
                if match_data:
                    matches.append(match_data)
                else:
                    print(f"Failed to fetch match: {match_id}")
            
            # Small delay between batches
            if i + batch_size < total:
                time.sleep(0.5)
        
        print(f"Successfully fetched {len(matches)}/{total} matches")
        return matches
