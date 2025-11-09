"""
Session Cache Manager
====================
Manages cached user sessions in S3 to avoid repeated API calls.

Key Features:
- Stores complete session data by username (gameName#tagLine-region)
- Checks for existing cached data before making new API calls
- Uploads session data in background while user views slides
- Includes all slide variables, image links, and humor
- Implements cache expiration (default: 7 days)
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from services.aws_clients import upload_to_s3, download_from_s3, check_s3_object_exists

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SessionCacheManager:
    """
    Manages session caching in S3 for faster repeated access.
    """
    
    def __init__(self, cache_expiry_days: int = 7):
        """
        Initialize cache manager.
        
        Args:
            cache_expiry_days: Number of days before cache expires (default: 7)
        """
        self.cache_expiry_days = cache_expiry_days
    
    def _get_cache_key(self, game_name: str, tag_line: str, region: str) -> str:
        """
        Generate cache key from player identity.
        
        Args:
            game_name: Riot ID game name
            tag_line: Riot ID tag line
            region: Platform region
        
        Returns:
            S3 cache key
        """
        # Normalize to lowercase and create safe filename
        safe_name = f"{game_name}#{tag_line}-{region}".lower().replace(" ", "_")
        return f"cache/users/{safe_name}/complete_session.json"
    
    def _get_metadata_key(self, game_name: str, tag_line: str, region: str) -> str:
        """
        Generate metadata key for cache entry.
        
        Args:
            game_name: Riot ID game name
            tag_line: Riot ID tag line
            region: Platform region
        
        Returns:
            S3 metadata key
        """
        safe_name = f"{game_name}#{tag_line}-{region}".lower().replace(" ", "_")
        return f"cache/users/{safe_name}/metadata.json"
    
    def check_cache_exists(self, game_name: str, tag_line: str, region: str) -> bool:
        """
        Check if cached session exists and is not expired.
        
        Args:
            game_name: Riot ID game name
            tag_line: Riot ID tag line
            region: Platform region
        
        Returns:
            True if valid cache exists, False otherwise
        """
        try:
            metadata_key = self._get_metadata_key(game_name, tag_line, region)
            
            # Check if metadata exists
            if not check_s3_object_exists(metadata_key):
                logger.info(f" No cache found for {game_name}#{tag_line}-{region}")
                return False
            
            # Download and check expiration
            metadata_str = download_from_s3(metadata_key)
            if not metadata_str:
                return False
            
            metadata = json.loads(metadata_str)
            cached_at = datetime.fromisoformat(metadata['cachedAt'])
            expires_at = cached_at + timedelta(days=self.cache_expiry_days)
            
            if datetime.now() > expires_at:
                logger.info(f"⏰ Cache expired for {game_name}#{tag_line}-{region}")
                return False
            
            logger.info(f" Valid cache found for {game_name}#{tag_line}-{region}")
            return True
        
        except Exception as e:
            logger.error(f"Error checking cache: {e}")
            return False
    
    def get_cached_session(self, game_name: str, tag_line: str, region: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached session data.
        
        Args:
            game_name: Riot ID game name
            tag_line: Riot ID tag line
            region: Platform region
        
        Returns:
            Complete session data or None if not found/expired
        """
        try:
            if not self.check_cache_exists(game_name, tag_line, region):
                return None
            
            cache_key = self._get_cache_key(game_name, tag_line, region)
            cache_str = download_from_s3(cache_key)
            
            if not cache_str:
                return None
            
            cached_data = json.loads(cache_str)
            logger.info(f" Retrieved cached session for {game_name}#{tag_line}-{region}")
            
            return cached_data
        
        except Exception as e:
            logger.error(f"Error retrieving cached session: {e}")
            return None
    
    def save_session_to_cache(
        self, 
        game_name: str, 
        tag_line: str, 
        region: str,
        session_id: str,
        analytics: Dict[str, Any],
        humor_data: Dict[str, str],
        player_info: Dict[str, Any],
        match_count: int,
        total_matches: int
    ) -> bool:
        """
        Save complete session to cache.
        
        Args:
            game_name: Riot ID game name
            tag_line: Riot ID tag line
            region: Platform region
            session_id: Original session ID
            analytics: Complete analytics data
            humor_data: All humor texts by slide
            player_info: Player information
            match_count: Number of matches analyzed
            total_matches: Total matches available
        
        Returns:
            True if successful, False otherwise
        """
        try:
            cache_key = self._get_cache_key(game_name, tag_line, region)
            metadata_key = self._get_metadata_key(game_name, tag_line, region)
            
            # Prepare complete session data
            complete_session = {
                'player': {
                    'gameName': game_name,
                    'tagLine': tag_line,
                    'region': region,
                    **player_info
                },
                'analytics': analytics,
                'humor': humor_data,
                'metadata': {
                    'sessionId': session_id,
                    'matchCount': match_count,
                    'totalMatches': total_matches,
                    'cachedAt': datetime.now().isoformat(),
                    'expiresAt': (datetime.now() + timedelta(days=self.cache_expiry_days)).isoformat()
                }
            }
            
            # Save complete session
            upload_to_s3(cache_key, complete_session)
            
            # Save metadata separately for quick expiration checks
            metadata = {
                'gameName': game_name,
                'tagLine': tag_line,
                'region': region,
                'cachedAt': datetime.now().isoformat(),
                'expiresAt': (datetime.now() + timedelta(days=self.cache_expiry_days)).isoformat(),
                'matchCount': match_count,
                'totalMatches': total_matches
            }
            upload_to_s3(metadata_key, metadata)
            
            logger.info(f" Cached session for {game_name}#{tag_line}-{region} (expires in {self.cache_expiry_days} days)")
            return True
        
        except Exception as e:
            logger.error(f"Error saving session to cache: {e}")
            return False
    
    def invalidate_cache(self, game_name: str, tag_line: str, region: str) -> bool:
        """
        Invalidate (delete) cached session for a user.
        Useful for forcing fresh data fetch.
        
        Args:
            game_name: Riot ID game name
            tag_line: Riot ID tag line
            region: Platform region
        
        Returns:
            True if successful, False otherwise
        """
        try:
            from services.aws_clients import get_s3_client
            from services.constants import S3_BUCKET_NAME
            
            s3_client = get_s3_client()
            safe_name = f"{game_name}#{tag_line}-{region}".lower().replace(" ", "_")
            
            # Delete both cache and metadata
            cache_key = f"cache/users/{safe_name}/complete_session.json"
            metadata_key = f"cache/users/{safe_name}/metadata.json"
            
            s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=cache_key)
            s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=metadata_key)
            
            logger.info(f" Invalidated cache for {game_name}#{tag_line}-{region}")
            return True
        
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return False
    
    def get_cache_stats(self, game_name: str, tag_line: str, region: str) -> Optional[Dict[str, Any]]:
        """
        Get cache statistics for a user.
        
        Args:
            game_name: Riot ID game name
            tag_line: Riot ID tag line
            region: Platform region
        
        Returns:
            Cache statistics or None
        """
        try:
            metadata_key = self._get_metadata_key(game_name, tag_line, region)
            metadata_str = download_from_s3(metadata_key)
            
            if not metadata_str:
                return None
            
            metadata = json.loads(metadata_str)
            cached_at = datetime.fromisoformat(metadata['cachedAt'])
            expires_at = datetime.fromisoformat(metadata['expiresAt'])
            now = datetime.now()
            
            return {
                'exists': True,
                'cachedAt': metadata['cachedAt'],
                'expiresAt': metadata['expiresAt'],
                'isExpired': now > expires_at,
                'daysUntilExpiry': (expires_at - now).days if now < expires_at else 0,
                'matchCount': metadata.get('matchCount', 0),
                'totalMatches': metadata.get('totalMatches', 0)
            }
        
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return None
    
    def find_session_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a cached session by its session ID.
        This searches through cache metadata to find a matching session.
        
        Args:
            session_id: Session ID to search for
        
        Returns:
            Complete session data or None if not found
        """
        try:
            from services.aws_clients import get_s3_client
            from services.constants import S3_BUCKET_NAME
            
            s3_client = get_s3_client()
            
            # List all cache metadata files
            response = s3_client.list_objects_v2(
                Bucket=S3_BUCKET_NAME,
                Prefix='cache/users/',
                Delimiter='/'
            )
            
            if 'CommonPrefixes' not in response:
                return None
            
            # Search through each user's cache
            for prefix in response['CommonPrefixes']:
                user_prefix = prefix['Prefix']
                metadata_key = f"{user_prefix}metadata.json"
                
                try:
                    metadata_str = download_from_s3(metadata_key)
                    if not metadata_str:
                        continue
                    
                    metadata = json.loads(metadata_str)
                    if metadata.get('sessionId') == session_id:
                        # Found it! Now get the complete session
                        cache_key = f"{user_prefix}complete_session.json"
                        cache_str = download_from_s3(cache_key)
                        if cache_str:
                            logger.info(f" Found session {session_id} in cache at {user_prefix}")
                            return json.loads(cache_str)
                except Exception as e:
                    # Skip this user if there's an error
                    logger.debug(f"Error checking cache at {user_prefix}: {e}")
                    continue
            
            logger.warning(f"Session {session_id} not found in any cache")
            return None
        
        except Exception as e:
            logger.error(f"Error searching for session by ID: {e}")
            return None
