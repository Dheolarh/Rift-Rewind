"""
API Wrapper for Frontend Integration
=====================================
Provides simple HTTP-like interface for React/TypeScript frontend
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables
load_dotenv()

# Import backend services
from lambdas.league_data import LeagueDataFetcher
from lambdas.humor_context import HumorGenerator
from lambdas.insights import InsightsGenerator
from services.analytics import RiftRewindAnalytics
from services.aws_clients import upload_to_s3, download_from_s3
from services.constants import REGIONS
from services.session_cache import SessionCacheManager


class RiftRewindAPI:
    """
    API wrapper for frontend integration.
    Mimics Lambda + API Gateway behavior for local development.
    """
    
    def __init__(self):
        """Initialize API with test mode configuration"""
        self.test_mode = os.getenv('TEST_MODE', 'false').lower() == 'true'
        # Fetch all matches, but cap analysis at 300
        self.max_matches_fetch = int(os.getenv('MAX_MATCHES_TO_FETCH', '1000'))
        self.max_matches_analyze = 300  # Always analyze max 300 matches
        self.humor_slides = [2, 3, 6] if self.test_mode else list(range(2, 16))  # Slides 2-15
        self.cache_manager = SessionCacheManager(cache_expiry_days=7)  # 7 day cache
    
    def create_response(self, status_code: int, body: Any, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create API Gateway-style response.
        
        Args:
            status_code: HTTP status code
            body: Response body (will be JSON serialized)
            headers: Optional response headers
        
        Returns:
            API Gateway response format
        """
        default_headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        }
        
        if headers:
            default_headers.update(headers)
     
        return {
            'statusCode': status_code,
            'headers': default_headers,
            'body': body
        }
    
    def get_regions(self) -> Dict[str, Any]:
        """
        GET /api/regions
        Get available regions for player lookup
        
        Returns:
            List of available regions
        """
        try:
            return self.create_response(200, {
                'regions': REGIONS
            })
        except Exception as e:
            return self.create_response(500, {
                'error': f'Failed to fetch regions: {str(e)}'
            })
    
    def start_rewind(self, game_name: str, tag_line: str, region: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        POST /api/rewind
        Start a new Rift Rewind session
        
        Args:
            game_name: Riot ID game name (e.g., "Hide on bush")
            tag_line: Riot ID tag line (e.g., "KR1")
            region: Platform region code (e.g., "kr")
            force_refresh: Force new data fetch even if cache exists
        
        Returns:
            Session ID and status
        """
        try:
            # Validate inputs
            if not all([game_name, tag_line, region]):
                return self.create_response(400, {
                    'error': 'Missing required fields: gameName, tagLine, region'
                })
            
            # Check cache first (unless force refresh)
            if not force_refresh:
                cached_session = self.cache_manager.get_cached_session(game_name, tag_line, region)
                if cached_session:
                    logger.info(f"🎯 Returning cached session for {game_name}#{tag_line}-{region}")
                    return self.create_response(200, {
                        'sessionId': cached_session['metadata']['sessionId'],
                        'status': 'complete',
                        'fromCache': True,
                        'testMode': self.test_mode,
                        'matchCount': cached_session['metadata']['matchCount'],
                        'totalMatches': cached_session['metadata']['totalMatches'],
                        'player': cached_session['player'],
                        'cachedAt': cached_session['metadata']['cachedAt']
                    })
                logger.info(f"📡 No cache found, fetching fresh data for {game_name}#{tag_line}-{region}")
            
            # Step 1: Fetch player data
            fetcher = LeagueDataFetcher()
            
            # Fetch account and summoner info
            account_data = fetcher.fetch_account_data(game_name, tag_line, region)
            puuid = account_data['puuid']
            
            fetcher.fetch_summoner_data(puuid, region)
            fetcher.fetch_ranked_info(puuid, region)
            
            # Fetch ALL match IDs from the past year
            match_ids = fetcher.fetch_match_history(puuid, region)
            total_matches = len(match_ids)
            
            # Apply intelligent sampling ONLY if > 300 matches
            if total_matches > 300:
                from services.match_analyzer import IntelligentSampler
                sampler = IntelligentSampler()
                sampling_result = sampler.sample_matches(match_ids)
                matches_to_fetch = sampling_result['sampled_match_ids'][:300]  # Cap at 300
                fetcher.data['samplingMetadata'] = {
                    'totalMatches': total_matches,
                    'analyzedMatches': len(matches_to_fetch),
                    'samplePercentage': (len(matches_to_fetch) / total_matches) * 100,
                    'strategy': 'intelligent_monthly_sampling'
                }
                logger.info(f"🎯 Sampling {len(matches_to_fetch)} matches out of {total_matches} total")
            else:
                # Fetch ALL matches if <= 300
                matches_to_fetch = match_ids
                fetcher.data['samplingMetadata'] = {
                    'totalMatches': total_matches,
                    'analyzedMatches': total_matches,
                    'samplePercentage': 100.0,
                    'strategy': 'full_analysis'
                }
                logger.info(f"✓ Analyzing all {total_matches} matches (no sampling needed)")
            
            matches = fetcher.fetch_match_details_batch(matches_to_fetch, region, use_sampling=False)
            
            # Generate session ID
            import uuid
            session_id = str(uuid.uuid4())
            logger.info(f"📝 Session ID: {session_id}")
            
            # Step 2: Calculate analytics directly (no S3 upload/download of raw data)
            logger.info("📊 Calculating analytics...")
            raw_data = {
                'account': account_data,
                'summoner': fetcher.data.get('summoner', {}),
                'ranked': fetcher.data.get('ranked', {}),
                'matches': matches,
                'puuid': puuid
            }
            
            analytics_engine = RiftRewindAnalytics(raw_data)
            analytics = analytics_engine.calculate_all()
            
            # Upload analytics to S3
            analytics_key = f"sessions/{session_id}/analytics.json"
            upload_to_s3(analytics_key, analytics)
            logger.info(f"✓ Analytics uploaded to S3")
            
            # Step 3: Generate humor for ALL slides (2-15) before completing
            logger.info("🎭 Generating AI humor for all slides...")
            humor_generator = HumorGenerator()
            humor_slides = list(range(2, 16))  # Slides 2-15 need humor
            
            import time
            for idx, slide_num in enumerate(humor_slides):
                try:
                    # Add delay between requests to avoid throttling (except first request)
                    if idx > 0:
                        time.sleep(4)  # 4 second delay between requests to avoid throttling
                    
                    humor_generator.generate(session_id, slide_num)
                    logger.info(f"  ✓ Slide {slide_num} humor generated")
                except Exception as e:
                    logger.warning(f"  ⚠️  Slide {slide_num} humor failed: {e}")
                    # Continue with other slides even if one fails
            
            logger.info("✅ All humor generation complete!")
            
            # Collect all humor for caching
            humor_data = {}
            for slide_num in range(2, 16):
                humor_str = download_from_s3(f"sessions/{session_id}/humor/slide_{slide_num}.json")
                if humor_str:
                    humor_json = json.loads(humor_str)
                    humor_data[f"slide{slide_num}_humor"] = humor_json.get('humorText', '')
            
            player_info = {
                'gameName': game_name,
                'tagLine': tag_line,
                'region': region,
                'summonerLevel': fetcher.data['summoner']['summonerLevel'],
                'rank': analytics.get('slide6_rankedJourney', {}).get('currentRank', 'UNRANKED')
            }
            
            # Save to cache in background (don't wait for it)
            import threading
            def save_cache_async():
                self.cache_manager.save_session_to_cache(
                    game_name, tag_line, region,
                    session_id, analytics, humor_data, player_info,
                    len(matches_to_fetch), total_matches
                )
            
            cache_thread = threading.Thread(target=save_cache_async, daemon=True)
            cache_thread.start()
            logger.info("💾 Started background cache save")
            
            return self.create_response(200, {
                'sessionId': session_id,
                'status': 'complete',  # Always return complete after all processing
                'fromCache': False,
                'testMode': self.test_mode,
                'matchCount': len(matches_to_fetch),
                'totalMatches': total_matches,
                'player': player_info
            })
        
        except ValueError as e:
            return self.create_response(400, {
                'error': str(e)
            })
        except Exception as e:
            return self.create_response(500, {
                'error': f'Internal server error: {str(e)}'
            })
    
    def get_session(self, session_id: str, game_name: str = None, tag_line: str = None, region: str = None) -> Dict[str, Any]:
        """
        GET /api/rewind/{sessionId}
        Get session status and basic info
        
        Args:
            session_id: Session ID
            game_name: Optional - for cache lookup
            tag_line: Optional - for cache lookup
            region: Optional - for cache lookup
        
        Returns:
            Session data
        """
        try:
            # Try cache first if user info provided
            if game_name and tag_line and region:
                cached_session = self.cache_manager.get_cached_session(game_name, tag_line, region)
                if cached_session:
                    logger.info(f"📦 Returning cached session data")
                    return self.create_response(200, {
                        'sessionId': cached_session['metadata']['sessionId'],
                        'status': 'complete',
                        'fromCache': True,
                        'analytics': {**cached_session['analytics'], **cached_session['humor']}
                    })
            
            # Download analytics from session storage
            analytics_str = download_from_s3(f"sessions/{session_id}/analytics.json")
            
            if not analytics_str:
                return self.create_response(404, {
                    'error': 'Session not found'
                })
            
            analytics = json.loads(analytics_str)
            
            # Download all humor data
            humor_data = {}
            for slide_num in range(2, 16):  # Slides 2-15 have humor
                humor_str = download_from_s3(f"sessions/{session_id}/humor/slide_{slide_num}.json")
                if humor_str:
                    humor_json = json.loads(humor_str)
                    humor_data[f"slide{slide_num}_humor"] = humor_json.get('humorText', '')
            
            # Merge humor into analytics
            analytics.update(humor_data)
            
            return self.create_response(200, {
                'sessionId': session_id,
                'status': 'complete',
                'fromCache': False,
                'analytics': analytics
            })
        
        except Exception as e:
            return self.create_response(500, {
                'error': f'Failed to fetch session: {str(e)}'
            })
    
    def get_slide(self, session_id: str, slide_number: int) -> Dict[str, Any]:
        """
        GET /api/rewind/{sessionId}/slide/{slideNumber}
        Get specific slide data including analytics and humor
        
        Args:
            session_id: Session ID
            slide_number: Slide number (1-15)
        
        Returns:
            Slide data with analytics and humor
        """
        try:
            if not (1 <= slide_number <= 15):
                return self.create_response(400, {
                    'error': 'Slide number must be between 1 and 15'
                })
            
            # Download analytics
            analytics_str = download_from_s3(f"sessions/{session_id}/analytics.json")
            if not analytics_str:
                return self.create_response(404, {
                    'error': 'Session not found'
                })
            
            analytics = json.loads(analytics_str)
            
            # Map slide number to analytics key
            slide_keys = {
                1: None,  # Player details - no analytics
                2: 'slide2_timeSpent',
                3: 'slide3_favoriteChampions',
                4: 'slide4_bestMatch',
                5: 'slide5_kda',
                6: 'slide6_rankedJourney',
                7: 'slide7_visionScore',
                8: 'slide8_championPool',
                9: 'slide9_duoPartner',
                10: 'slide10_11_analysis',
                11: 'slide10_11_analysis',
                12: 'slide12_progress',
                13: 'slide13_achievements',
                14: 'slide14_percentile',
                15: None  # Final recap - uses multiple analytics
            }
            
            slide_data = {}
            
            if slide_number == 1:
                # Player details from raw data
                raw_data_str = download_from_s3(f"sessions/{session_id}/raw_data.json")
                raw_data = json.loads(raw_data_str) if raw_data_str else {}
                slide_data = {
                    'account': raw_data.get('account', {}),
                    'summoner': raw_data.get('summoner', {}),
                    'ranked': raw_data.get('ranked', {})
                }
            elif slide_number == 15:
                # Final recap uses multiple analytics
                slide_data = {
                    'timeSpent': analytics.get('slide2_timeSpent', {}),
                    'rankedJourney': analytics.get('slide6_rankedJourney', {}),
                    'favoriteChampions': analytics.get('slide3_favoriteChampions', [])
                }
            else:
                # Regular slide
                slide_key = slide_keys.get(slide_number)
                slide_data = analytics.get(slide_key, {})
            
            # Try to get humor (may not exist for all slides yet)
            humor_text = None
            if slide_number > 1:  # Slides 2-15 have humor
                humor_str = download_from_s3(f"sessions/{session_id}/humor/slide_{slide_number}.json")
                if humor_str:
                    humor_data = json.loads(humor_str)
                    humor_text = humor_data.get('humorText')
            
            return self.create_response(200, {
                'sessionId': session_id,
                'slideNumber': slide_number,
                'data': slide_data,
                'humor': humor_text
            })
        
        except Exception as e:
            return self.create_response(500, {
                'error': f'Failed to fetch slide: {str(e)}'
            })
    
    def check_cache(self, game_name: str, tag_line: str, region: str) -> Dict[str, Any]:
        """
        GET /api/cache/check
        Check if cached session exists for a user
        
        Args:
            game_name: Riot ID game name
            tag_line: Riot ID tag line
            region: Platform region
        
        Returns:
            Cache status information
        """
        try:
            cache_stats = self.cache_manager.get_cache_stats(game_name, tag_line, region)
            
            if not cache_stats:
                return self.create_response(200, {
                    'exists': False,
                    'message': f'No cached data for {game_name}#{tag_line}-{region}'
                })
            
            return self.create_response(200, cache_stats)
        
        except Exception as e:
            return self.create_response(500, {
                'error': f'Failed to check cache: {str(e)}'
            })
    
    def invalidate_cache(self, game_name: str, tag_line: str, region: str) -> Dict[str, Any]:
        """
        DELETE /api/cache/invalidate
        Invalidate cached session for a user (force fresh data next time)
        
        Args:
            game_name: Riot ID game name
            tag_line: Riot ID tag line
            region: Platform region
        
        Returns:
            Success/failure status
        """
        try:
            success = self.cache_manager.invalidate_cache(game_name, tag_line, region)
            
            if success:
                return self.create_response(200, {
                    'message': f'Cache invalidated for {game_name}#{tag_line}-{region}',
                    'success': True
                })
            else:
                return self.create_response(500, {
                    'error': 'Failed to invalidate cache',
                    'success': False
                })
        
        except Exception as e:
            return self.create_response(500, {
                'error': f'Failed to invalidate cache: {str(e)}',
                'success': False
            })


# Convenience functions for direct use
def handle_request(method: str, path: str, body: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Handle API request (mimics API Gateway)
    
    Args:
        method: HTTP method (GET, POST)
        path: Request path
        body: Request body for POST
    
    Returns:
        API response
    """
    api = RiftRewindAPI()
    
    # Route the request
    if method == 'GET' and path == '/api/regions':
        return api.get_regions()
    
    elif method == 'POST' and path == '/api/rewind':
        if not body:
            return api.create_response(400, {'error': 'Request body required'})
        return api.start_rewind(
            body.get('gameName', ''),
            body.get('tagLine', ''),
            body.get('region', '')
        )
    
    elif method == 'GET' and path.startswith('/api/rewind/'):
        parts = path.split('/')
        if len(parts) == 4:  # /api/rewind/{sessionId}
            return api.get_session(parts[3])
        elif len(parts) == 6 and parts[4] == 'slide':  # /api/rewind/{sessionId}/slide/{slideNumber}
            try:
                slide_number = int(parts[5])
                return api.get_session(parts[3], slide_number)
            except ValueError:
                return api.create_response(400, {'error': 'Invalid slide number'})
    
    return api.create_response(404, {'error': 'Not found'})


if __name__ == "__main__":
    # Example usage
    api = RiftRewindAPI()
    
    print("Test Mode:", api.test_mode)
    print("Max Matches:", api.max_matches)
    print("Humor Slides:", api.humor_slides)
