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
from services.constants import REGIONS, VALID_PLATFORMS
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
            'body': json.dumps(body)
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
    
    def health_check(self) -> Dict[str, Any]:
        """
        GET /api/health
        Health check endpoint
        
        Returns:
            Health status and configuration info
        """
        try:
            return self.create_response(200, {
                'status': 'healthy',
                'testMode': self.test_mode,
                'maxMatches': self.max_matches_analyze,
                'cacheEnabled': True,
                'cacheExpiryDays': self.cache_manager.cache_expiry_days
            })
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return self.create_response(500, {'error': 'Health check failed'})
    
    def _update_session_status(self, session_id: str, status: str, message: str = '', player_info: dict = None, fetcher_data: dict = None):
        """Update session processing status in S3"""
        import datetime
        status_data = {
            'status': status,
            'message': message,
            'updatedAt': datetime.datetime.now().isoformat()
        }
        if player_info:
            status_data['player'] = player_info
        if fetcher_data:
            status_data['fetcherData'] = fetcher_data
        
        status_key = f"sessions/{session_id}/status.json"
        upload_to_s3(status_key, status_data)
        logger.info(f" Status updated: {status} - {message}")
    
    def _process_rewind_async(self, session_id: str, game_name: str, tag_line: str, region: str, fetcher_data: dict):
        """Background processing of rewind data"""
        try:
            # Update status: analyzing
            self._update_session_status(session_id, 'analyzing', 'Analyzing your match history...')
            
            # Re-create fetcher with cached data
            fetcher = LeagueDataFetcher()
            fetcher.data = fetcher_data
            puuid = fetcher_data['account']['puuid']
            
            # Fetch match history
            match_ids = fetcher.fetch_match_history(puuid, region)
            total_matches = len(match_ids)
            
            # Check if player has any matches
            if total_matches == 0:
                error_message = (
                    f"No ranked matches found for {game_name}#{tag_line} in 2025. "
                    "This account either hasn't played ranked games this year, or only plays other game modes (ARAM, normals, etc.). "
                    "Please try a different account that has played ranked matches in 2025."
                )
                logger.warning(f"  {error_message}")
                self._update_session_status(session_id, 'error', error_message)
                return
            
            # NO SAMPLING - Analyze ALL matches
            matches_to_fetch = match_ids
            fetcher.data['samplingMetadata'] = {
                'totalMatches': total_matches,
                'analyzedMatches': total_matches,
                'samplePercentage': 100.0,
                'strategy': 'full_analysis'
            }
            logger.info(f"Analyzing ALL {total_matches} ranked matches (no sampling)")
            
            matches = fetcher.fetch_match_details_batch(matches_to_fetch, region, use_sampling=False)
            
            # Calculate analytics
            logger.info(" Calculating analytics...")
            raw_data = {
                'account': fetcher.data.get('account', {}),
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
            logger.info(f" Analytics uploaded to S3")
            
            # Update status: generating humor
            self._update_session_status(session_id, 'generating', 'Generating personalized insights...')
            
            # Generate humor for ALL slides (2-15)
            logger.info(" Generating AI humor for all slides...")
            humor_generator = HumorGenerator()
            humor_slides = list(range(2, 16))
            
            import time
            for idx, slide_num in enumerate(humor_slides):
                try:
                    if idx > 0:
                        time.sleep(4)
                    
                    humor_generator.generate(session_id, slide_num)
                    logger.info(f"   Slide {slide_num} humor generated")
                except Exception as e:
                    logger.warning(f"    Slide {slide_num} humor failed: {e}")
            
            logger.info(" All humor generation complete!")
            
            # Generate insights
            logger.info(" Generating AI insights...")
            try:
                insights_generator = InsightsGenerator()
                insights_result = insights_generator.generate(session_id)
                insights = insights_result.get('insights', {})
                
                # Update analytics with insights
                if 'slide10_11_analysis' in analytics:
                    analytics['slide10_11_analysis'].update({
                        'strengths': insights.get('strengths', []),
                        'weaknesses': insights.get('weaknesses', []),
                        'coaching_tips': insights.get('coaching_tips', []),
                        'play_style': insights.get('play_style', ''),
                        'personality_title': insights.get('personality_title', 'The Rising Summoner')
                    })
                    
                    # Re-upload analytics with insights
                    upload_to_s3(analytics_key, analytics)
                    logger.info(" Insights integrated into analytics")
                    
            except Exception as e:
                logger.error(f" Insights generation failed: {e}")
            
            # Collect all humor for caching
            humor_data = {}
            for slide_num in range(2, 16):
                humor_str = download_from_s3(f"sessions/{session_id}/humor/slide_{slide_num}.json")
                if humor_str:
                    humor_json = json.loads(humor_str)
                    humor_text = humor_json.get('humorText', '')
                    
                    if slide_num == 15:
                        humor_data['slide15_farewell'] = humor_text
                    else:
                        humor_data[f"slide{slide_num}_humor"] = humor_text
            
            # Build updated player info
            from services.riot_api_client import RiotAPIClient
            profile_icon_id = fetcher.data['summoner']['profileIconId']
            profile_icon_url = RiotAPIClient.get_profile_icon_url(profile_icon_id)
            
            player_info = {
                'gameName': game_name,
                'tagLine': tag_line,
                'region': region,
                'summonerLevel': fetcher.data['summoner']['summonerLevel'],
                'profileIconId': profile_icon_id,
                'profileIconUrl': profile_icon_url,
                'rank': analytics.get('slide6_rankedJourney', {}).get('currentRank', 'UNRANKED')
            }
            
            # Save to cache
            self.cache_manager.save_session_to_cache(
                game_name, tag_line, region,
                session_id, analytics, humor_data, player_info,
                len(matches_to_fetch), total_matches
            )
            logger.info(" Session saved to cache")
            
            # Update status: complete
            self._update_session_status(session_id, 'complete', 'Your rewind is ready!', player_info)
            logger.info(f" Session {session_id} processing complete!")
            
        except Exception as e:
            logger.error(f" Background processing failed for session {session_id}: {e}")
            import traceback
            traceback.print_exc()
            self._update_session_status(session_id, 'error', str(e))
    
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

            # Defensive normalization of region values coming from varied clients
            # Accept common malformed values like 'TR.riotgamesapi', 'TR', or uppercased codes
            def _normalize_region(val: str) -> str:
                if not val:
                    return val
                v = val.strip()
                # Already a known platform
                if v in VALID_PLATFORMS:
                    return v
                low = v.lower()
                if low in VALID_PLATFORMS:
                    return low
                # If the value looks like 'tr.riotgamesapi' -> take first segment 'tr'
                if '.' in low:
                    first = low.split('.')[0]
                    if first in VALID_PLATFORMS:
                        return first
                    # handle short country codes like 'tr' -> 'tr1'
                    if len(first) <= 3 and (first + '1') in VALID_PLATFORMS:
                        return first + '1'
                # Try prefix/suffix matching against known platforms
                for p in VALID_PLATFORMS:
                    if low.startswith(p) or p.startswith(low):
                        return p
                # Fallback to original
                return v

            region = _normalize_region(region)
            
            # Check cache first (unless force refresh)
            if not force_refresh:
                cached_session = self.cache_manager.get_cached_session(game_name, tag_line, region)
                if cached_session:
                    logger.info(f" Returning cached session for {game_name}#{tag_line}-{region}")
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
                logger.info(f" No cache found, fetching fresh data for {game_name}#{tag_line}-{region}")
            
            # Generate session ID first
            import uuid
            session_id = str(uuid.uuid4())
            logger.info(f" Session ID: {session_id}")
            
            # Step 1: Quick account lookup to confirm player exists
            fetcher = LeagueDataFetcher()
            
            logger.info(f" Looking up account for {game_name}#{tag_line}-{region}")
            account_data = fetcher.fetch_account_data(game_name, tag_line, region)
            puuid = account_data['puuid']
            
            fetcher.fetch_summoner_data(puuid, region)
            fetcher.fetch_ranked_info(puuid, region)
            
            logger.info(f" Account found: {game_name}#{tag_line}")
            
            # Build player info from initial fetch
            from services.riot_api_client import RiotAPIClient
            profile_icon_id = fetcher.data['summoner']['profileIconId']
            profile_icon_url = RiotAPIClient.get_profile_icon_url(profile_icon_id)
            
            player_info = {
                'gameName': game_name,
                'tagLine': tag_line,
                'region': region,
                'summonerLevel': fetcher.data['summoner']['summonerLevel'],
                'profileIconId': profile_icon_id,
                'profileIconUrl': profile_icon_url,
                'rank': fetcher.data.get('ranked', {}).get('tier', 'UNRANKED')
            }
            
            # Save initial status with player info
            self._update_session_status(session_id, 'found', 'Haha, found you! Analyzing your match history...', player_info, fetcher.data)
            
            # Start background processing
            import threading
            # Instead of starting a local background thread (which won't run reliably on AWS Lambda),
            # upload the raw fetcher data to S3 and invoke a processor Lambda asynchronously.
            try:
                # Save raw data to S3 so the processor can pick it up (avoid large payloads in invoke)
                raw_key = f"sessions/{session_id}/raw_data.json"
                upload_to_s3(raw_key, fetcher.data)

                # Invoke processor Lambda asynchronously
                import boto3
                lambda_client = boto3.client('lambda')
                processor_name = os.getenv('PROCESSOR_LAMBDA_NAME', 'rift-rewind-processor')

                payload = {
                    'session_id': session_id,
                    'raw_data_s3_key': raw_key,
                    'game_name': game_name,
                    'tag_line': tag_line,
                    'region': region,
                }

                lambda_client.invoke(
                    FunctionName=processor_name,
                    InvocationType='Event',  # asynchronous
                    Payload=json.dumps(payload).encode('utf-8')
                )
                logger.info(f" Started async processor Lambda '{processor_name}' for session {session_id}")
            except Exception as e:
                logger.error(f"Failed to invoke processor Lambda: {e}")
                import traceback
                traceback.print_exc()
            logger.info(f" Started background processing for session {session_id}")
            
            # Return immediately with 'found' status
            return self.create_response(200, {
                'sessionId': session_id,
                'status': 'found',
                'fromCache': False,
                'testMode': self.test_mode,
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
            Session data or processing status
        """
        try:
            # Check processing status first
            status_str = download_from_s3(f"sessions/{session_id}/status.json")
            if status_str:
                status_data = json.loads(status_str)
                current_status = status_data.get('status', 'unknown')
                
                # If still processing, return status update
                if current_status in ['searching', 'found', 'analyzing', 'generating']:
                    return self.create_response(200, {
                        'sessionId': session_id,
                        'status': current_status,
                        'message': status_data.get('message', ''),
                        'player': status_data.get('player', {}),
                        'fromCache': False
                    })
                
                # If error, return error status
                if current_status == 'error':
                    return self.create_response(500, {
                        'sessionId': session_id,
                        'status': 'error',
                        'error': status_data.get('message', 'Processing failed')
                    })
            
            # Try cache first if user info provided
            if game_name and tag_line and region:
                cached_session = self.cache_manager.get_cached_session(game_name, tag_line, region)
                if cached_session:
                    logger.info(f" Returning cached session data")
                    return self.create_response(200, {
                        'sessionId': cached_session['metadata']['sessionId'],
                        'status': 'complete',
                        'fromCache': True,
                        'analytics': {**cached_session['analytics'], **cached_session['humor']},
                        'player': cached_session.get('player', {})
                    })
            
            # Try to download analytics from session storage
            analytics_str = download_from_s3(f"sessions/{session_id}/analytics.json")
            
            if not analytics_str:
                # Session files not found - this might be a cached session
                # Try to find it by searching for session ID in cache metadata
                logger.warning(f"Session {session_id} not found in sessions storage, checking cache...")
                cached_session = self.cache_manager.find_session_by_id(session_id)
                if cached_session:
                    logger.info(f" Found session in cache")
                    return self.create_response(200, {
                        'sessionId': cached_session['metadata']['sessionId'],
                        'status': 'complete',
                        'fromCache': True,
                        'analytics': {**cached_session['analytics'], **cached_session['humor']},
                        'player': cached_session.get('player', {})
                    })
                
                # Instead of returning 404 when analytics aren't uploaded yet (or
                # cache lookup fails due to S3 issues), return a processing
                # status so clients can continue polling. This avoids treating
                # "session not ready" as an account-not-found error on the
                # frontend.
                return self.create_response(200, {
                    'sessionId': session_id,
                    'status': 'searching',
                    'message': 'Session created and processing; analytics not available yet',
                    'fromCache': False
                })
            
            analytics = json.loads(analytics_str)
            
            # Download insights and merge into analytics
            insights_str = download_from_s3(f"sessions/{session_id}/insights.json")
            if insights_str:
                insights_data = json.loads(insights_str)
                insights = insights_data.get('insights', {})
                
                # Merge insights into slide10_11_analysis
                if 'slide10_11_analysis' in analytics:
                    analytics['slide10_11_analysis'].update({
                        'strengths': insights.get('strengths', []),
                        'weaknesses': insights.get('weaknesses', []),
                        'coaching_tips': insights.get('coaching_tips', []),
                        'play_style': insights.get('play_style', ''),
                        'personality_title': insights.get('personality_title', 'The Rising Summoner')
                    })
            
            # Download all humor data
            humor_data = {}
            for slide_num in range(2, 16):  # Slides 2-15 have humor
                humor_str = download_from_s3(f"sessions/{session_id}/humor/slide_{slide_num}.json")
                if humor_str:
                    humor_json = json.loads(humor_str)
                    humor_text = humor_json.get('humorText', '')
                    
                    # Slide 15 is the farewell message, store it differently
                    if slide_num == 15:
                        humor_data['slide15_farewell'] = humor_text
                    else:
                        humor_data[f"slide{slide_num}_humor"] = humor_text
            
            # Merge humor into analytics
            analytics.update(humor_data)
            
            # Download player info (created during session creation)
            player_info = {}
            raw_data_str = download_from_s3(f"sessions/{session_id}/raw_data.json")
            if raw_data_str:
                raw_data = json.loads(raw_data_str)
                summoner = raw_data.get('summoner', {})
                account = raw_data.get('account', {})
                player_info = {
                    'gameName': account.get('gameName', ''),
                    'tagLine': account.get('tagLine', ''),
                    'summonerLevel': summoner.get('summonerLevel', 0),
                    'profileIconId': summoner.get('profileIconId', 0)
                }
            
            return self.create_response(200, {
                'sessionId': session_id,
                'status': 'complete',
                'fromCache': False,
                'analytics': analytics,
                'player': player_info
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
        
        # Strip whitespace from inputs to prevent encoding issues
        game_name = body.get('gameName', '').strip()
        tag_line = body.get('tagLine', '').strip()
        region = body.get('region', '').strip()
        
        return api.start_rewind(game_name, tag_line, region)
    
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
