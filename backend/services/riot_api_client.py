"""
Riot API Client with rate limiting and error handling
"""

import os
import time
import logging
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
                    logger.warning(f"Resource not found (404): {url}")
                    return None
                elif response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 2))
                    logger.info(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                elif response.status_code == 403:
                    logger.error(f" Forbidden (403) - Access Denied")
                    logger.error(f"   URL: {url}")
                    logger.error(f"   API Key prefix: {self.api_key[:10]}...")
                    try:
                        error_body = response.json()
                        logger.error(f"   Response body: {error_body}")
                    except:
                        if response.text:
                            logger.error(f"   Response text: {response.text[:300]}")
                    logger.error(f"   Response headers: {dict(response.headers)}")
                    
                    # Check if this is a valid Riot ID format issue
                    if 'account/v1/accounts/by-riot-id' in url:
                        logger.error(f"     Possible issues:")
                        logger.error(f"      - Riot ID might not exist in this region")
                        logger.error(f"      - Name/tag might contain invalid characters")
                        logger.error(f"      - Regional routing might be incorrect")
                    return None
                else:
                    logger.error(f"Error {response.status_code}: {url}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    return None
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⏱  Timeout on attempt {attempt + 1}/{max_retries} - retrying...")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                logger.error(f" Request timed out after {max_retries} attempts")
                return None
            except requests.exceptions.SSLError as e:
                logger.warning(f" SSL Error on attempt {attempt + 1}/{max_retries} - connection issue")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                logger.error(f" SSL Error persists after {max_retries} attempts (skipping)")
                return None
            except requests.exceptions.ConnectionError as e:
                logger.warning(f" Connection Error on attempt {attempt + 1}/{max_retries} - network issue")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                logger.error(f" Connection failed after {max_retries} attempts (skipping)")
                return None
            except Exception as e:
                logger.error(f"  Unexpected error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return None
        
        return None
    
    # ==================== ACCOUNT-V1 API ====================
    
    def get_account_by_riot_id(self, game_name: str, tag_line: str, regional: str = "europe") -> Optional[Dict[str, Any]]:
        """
        Get account data by Riot ID using ACCOUNT-V1 (Regional routing).
        This is the modern recommended way to get player data.
        
        Args:
            game_name: The game name (e.g., "OSIRISX")
            tag_line: The tag line (e.g., "EUW")
            regional: Regional routing (americas, europe, asia, sea)
            
        Returns:
            Account data with puuid, gameName, tagLine
        """
        import urllib.parse
        
        # Strip whitespace and URL-encode game name and tag line to handle non-ASCII and special characters
        clean_game_name = game_name.strip()
        clean_tag_line = tag_line.strip()
        
        logger.info(f" Account Lookup Debug:")
        logger.info(f"   Original: '{game_name}' #{tag_line}")
        logger.info(f"   Cleaned: '{clean_game_name}' #{clean_tag_line}")
        logger.info(f"   Regional: {regional}")
        
        encoded_game_name = urllib.parse.quote(clean_game_name)
        encoded_tag_line = urllib.parse.quote(clean_tag_line)
        
        logger.info(f"   Encoded name: {encoded_game_name}")
        logger.info(f"   Encoded tag: {encoded_tag_line}")
        
        base_url = RIOT_API_REGIONAL_BASE.format(regional=regional)
        endpoint = RIOT_API_ENDPOINTS['account_by_riot_id'].format(
            gameName=encoded_game_name,
            tagLine=encoded_tag_line
        )
        url = base_url + endpoint
        
        logger.info(f"   Full URL: {url}")
        
        logger.info(f"Fetching account: {clean_game_name}#{clean_tag_line} on {regional}")
        logger.debug(f"Full URL: {url}")
        logger.debug(f"API Key (first 10 chars): {self.api_key[:10] if self.api_key else 'NOT SET'}...")
        
        return self._make_request(url)
    
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
        import urllib.parse
        base_url = RIOT_API_PLATFORM_BASE.format(platform=platform)
        # URL encode the summoner name to handle special characters
        encoded_name = urllib.parse.quote(summoner_name)
        endpoint = RIOT_API_ENDPOINTS['summoner_by_name'].format(summonerName=encoded_name)
        url = base_url + endpoint
        
        logger.info(f"Fetching summoner: {summoner_name} on {platform}")
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
        
        logger.info(f"Fetching ranked info for summoner: {summoner_id}")
        return self._make_request(url)
    
    def get_league_entries_by_puuid(self, puuid: str, platform: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get ranked league entries by PUUID using LEAGUE-V4 (Platform routing).
        This is the modern recommended way to get ranked info.
        
        Args:
            puuid: The player PUUID
            platform: Platform code
            
        Returns:
            List of league entries (Solo/Duo, Flex, etc.)
        """
        base_url = RIOT_API_PLATFORM_BASE.format(platform=platform)
        endpoint = RIOT_API_ENDPOINTS['league_by_puuid'].format(encryptedPUUID=puuid)
        url = base_url + endpoint
        
        logger.info(f"Fetching ranked info by PUUID: {puuid[:16]}...")
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
            logger.error(f"Unknown platform: {platform}")
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
        
        logger.info(f"Fetching {count} match IDs for PUUID: {puuid[:8]}...")
        logger.info(f" Match history URL: {url}")
        logger.info(f" Filters - Queue: {queue}, Start time: {start_time} ({datetime.fromtimestamp(start_time) if start_time else 'None'})")
        
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
            logger.error(f"Unknown platform: {platform}")
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
        batch_size: int = 10,
        parallel: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Fetch multiple match details with optional parallel processing.
        
        Args:
            match_ids: List of match IDs to fetch
            platform: Platform code
            batch_size: Number of concurrent requests (for rate limiting)
            parallel: Use parallel processing (recommended for 20+ matches)
            
        Returns:
            List of match details
        """
        total = len(match_ids)
        
        if parallel and total > 10:
            # Use parallel processing for better performance
            return self._get_matches_parallel(match_ids, platform, max_workers=batch_size)
        else:
            # Use sequential processing for small batches
            return self._get_matches_sequential(match_ids, platform, batch_size)
    
    def _get_matches_sequential(
        self,
        match_ids: List[str],
        platform: str,
        batch_size: int
    ) -> List[Dict[str, Any]]:
        """
        Sequential match fetching (original implementation).
        """
        matches = []
        total = len(match_ids)
        
        logger.info(f"Fetching {total} matches sequentially in batches of {batch_size}...")
        
        for i in range(0, total, batch_size):
            batch = match_ids[i:i + batch_size]
            
            for match_id in batch:
                match_data = self.get_match_details(match_id, platform)
                if match_data:
                    matches.append(match_data)
                else:
                    logger.warning(f"Failed to fetch match: {match_id}")
            
            if i + batch_size < total:
                time.sleep(0.5)
        
        logger.info(f"Successfully fetched {len(matches)}/{total} matches")
        
        if len(matches) < total:
            failed_count = total - len(matches)
            logger.warning(f"  {failed_count} matches failed to fetch (network/SSL errors - continuing anyway)")
        
        return matches
    
    def get_league_entries(
        self,
        summoner_id: str,
        platform: str
    ) -> List[Dict[str, Any]]:
        """
        Get league entries for a summoner (their rank positions).
        
        Args:
            summoner_id: Encrypted summoner ID
            platform: Platform code (e.g., 'na1', 'euw1')
            
        Returns:
            List of league entries (one per queue)
        """
        endpoint = f'/lol/league/v4/entries/by-summoner/{summoner_id}'
        url = f"{RIOT_API_PLATFORM_BASE[platform]}{endpoint}"
        
        try:
            response = self._make_request('GET', url)
            return response if response else []
        except Exception as e:
            logger.error(f"Failed to get league entries: {e}")
            return []
    
    def get_league_position_in_tier(
        self,
        queue: str,
        tier: str,
        division: str,
        lp: int,
        platform: str
    ) -> Optional[int]:
        """
        Estimate player's position within their tier/division.
        Fetches a page of entries to determine approximate position.
        
        Args:
            queue: Queue type (e.g., 'RANKED_SOLO_5x5')
            tier: Tier (e.g., 'GOLD', 'PLATINUM')
            division: Division (e.g., 'I', 'II', 'III', 'IV')
            lp: Player's league points
            platform: Platform code
            
        Returns:
            Approximate position/rank number
        """
        endpoint = f'/lol/league/v4/entries/{queue}/{tier}/{division}'
        url = f"{RIOT_API_PLATFORM_BASE[platform]}{endpoint}"
        
        try:
            # Fetch first page to see LP distribution
            params = {'page': 1}
            response = self._make_request('GET', url, params=params)
            
            if not response:
                return None
            
            # Count how many players have higher LP
            higher_lp_count = sum(1 for entry in response if entry.get('leaguePoints', 0) > lp)
            
            # Estimate: Assume ~200 players per page, add offset
            estimated_position = higher_lp_count + 1
            
            logger.info(f"Estimated position in {tier} {division}: {estimated_position}")
            return estimated_position
            
        except Exception as e:
            logger.error(f"Failed to get league position: {e}")
            return None
    
    def _get_matches_parallel(
        self,
        match_ids: List[str],
        platform: str,
        max_workers: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Parallel match fetching using ThreadPoolExecutor.
        Respects rate limits while maximizing throughput.
        
        Args:
            match_ids: List of match IDs to fetch
            platform: Platform code
            max_workers: Maximum concurrent threads (default 10 to respect 20 req/sec limit)
            
        Returns:
            List of match details
        """
        import concurrent.futures
        
        matches = []
        total = len(match_ids)
        completed = 0
        
        logger.info(f"Fetching {total} matches in parallel (max {max_workers} workers)...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_id = {
                executor.submit(self.get_match_details, match_id, platform): match_id
                for match_id in match_ids
            }
            
            for future in concurrent.futures.as_completed(future_to_id):
                match_id = future_to_id[future]
                completed += 1
                
                try:
                    match_data = future.result()
                    if match_data:
                        matches.append(match_data)
                    else:
                        logger.warning(f"Failed to fetch match: {match_id}")
                except Exception as e:
                    logger.error(f"Error fetching match {match_id}: {e}")
                
                if completed % 10 == 0 or completed == total:
                    logger.info(f"Progress: {completed}/{total} matches ({int(completed/total*100)}%)")
        
        logger.info(f"Successfully fetched {len(matches)}/{total} matches in parallel")
        return matches
    
    # ==================== DATA DRAGON HELPERS ====================
    
    _dd_version_cache = None
    _dd_version_timestamp = None
    
    @classmethod
    def get_data_dragon_version(cls) -> str:
        """
        Get the latest Data Dragon version. Cached for 1 hour.
        
        Returns:
            Version string (e.g., "14.23.1")
        """
        from .constants import DATA_DRAGON_VERSION_URL
        
        # Check cache (valid for 1 hour)
        if cls._dd_version_cache and cls._dd_version_timestamp:
            age = time.time() - cls._dd_version_timestamp
            if age < 3600:  # 1 hour
                return cls._dd_version_cache
        
        # Fetch latest version
        try:
            response = requests.get(DATA_DRAGON_VERSION_URL, timeout=10)
            response.raise_for_status()
            versions = response.json()
            latest_version = versions[0]
            
            cls._dd_version_cache = latest_version
            cls._dd_version_timestamp = time.time()
            
            logger.info(f"Data Dragon version: {latest_version}")
            return latest_version
        except Exception as e:
            logger.error(f"Failed to fetch Data Dragon version: {e}")
            # Fallback to a known recent version
            return "14.23.1"
    
    @classmethod
    def get_profile_icon_url(cls, profile_icon_id: int) -> str:
        """
        Build profile icon URL using Community Dragon CDN (more reliable than Data Dragon).
        
        Args:
            profile_icon_id: Profile icon ID from summoner data
            
        Returns:
            Full URL to profile icon JPG
        """
        # Use Community Dragon CDN - more reliable and doesn't require version
        # Falls back to latest version automatically, no 403 errors
        return f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{profile_icon_id}.jpg"

