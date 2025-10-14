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
    
    def start_rewind(self, game_name: str, tag_line: str, region: str) -> Dict[str, Any]:
        """
        POST /api/rewind
        Start a new Rift Rewind session
        
        Args:
            game_name: Riot ID game name (e.g., "Hide on bush")
            tag_line: Riot ID tag line (e.g., "KR1")
            region: Platform region code (e.g., "kr")
        
        Returns:
            Session ID and status
        """
        try:
            # Validate inputs
            if not all([game_name, tag_line, region]):
                return self.create_response(400, {
                    'error': 'Missing required fields: gameName, tagLine, region'
                })
            
            # Step 1: Fetch player data
            fetcher = LeagueDataFetcher()
            
            # Fetch account and summoner info
            account_data = fetcher.fetch_account_data(game_name, tag_line, region)
            puuid = account_data['puuid']
            
            fetcher.fetch_summoner_data(puuid, region)
            fetcher.fetch_ranked_info(puuid, region)
            
            # Fetch matches
            from services.riot_api_client import RiotAPIClient
            from services.match_analyzer import IntelligentSampler
            
            riot = RiotAPIClient()
            match_ids = riot.get_match_ids(puuid, region, count=self.max_matches_fetch)
            fetcher.data['matchIds'] = match_ids
            
            # Apply intelligent sampling if > 300 matches
            total_matches = len(match_ids)
            if total_matches > self.max_matches_analyze:
                sampler = IntelligentSampler()
                sampling_result = sampler.sample_matches(match_ids)
                matches_to_fetch = sampling_result['sampled_match_ids'][:self.max_matches_analyze]
                fetcher.data['samplingMetadata'] = {
                    'totalMatches': total_matches,
                    'analyzedMatches': len(matches_to_fetch),
                    'samplePercentage': sampling_result['sample_percentage'],
                    'strategy': 'intelligent_monthly_sampling'
                }
            else:
                matches_to_fetch = match_ids
                fetcher.data['samplingMetadata'] = {
                    'totalMatches': total_matches,
                    'analyzedMatches': total_matches,
                    'samplePercentage': 1.0,
                    'strategy': 'full_analysis'
                }
            
            matches = fetcher.fetch_match_details_batch(matches_to_fetch, region)
            
            # Store to S3
            s3_key = fetcher.store_to_s3()
            session_id = fetcher.session_id
            
            # Step 2: Calculate analytics
            raw_data_str = download_from_s3(f"sessions/{session_id}/raw_data.json")
            raw_data = json.loads(raw_data_str) if raw_data_str else {}
            
            analytics_engine = RiftRewindAnalytics(raw_data)
            analytics = analytics_engine.calculate_all()
            
            analytics_key = f"sessions/{session_id}/analytics.json"
            upload_to_s3(analytics_key, analytics)
            
            # Step 3: Generate humor (async in production, sync in test mode)
            if self.test_mode:
                # Generate humor for sample slides immediately
                humor_generator = HumorGenerator()
                for slide_num in self.humor_slides:
                    humor_generator.generate(session_id, slide_num)
            
            return self.create_response(200, {
                'sessionId': session_id,
                'status': 'processing' if not self.test_mode else 'complete',
                'testMode': self.test_mode,
                'matchCount': len(matches),
                'player': {
                    'gameName': game_name,
                    'tagLine': tag_line,
                    'region': region,
                    'summonerLevel': fetcher.data['summoner']['summonerLevel'],
                    'rank': analytics.get('slide6_rankedJourney', {}).get('currentRank', 'UNRANKED')
                }
            })
        
        except ValueError as e:
            return self.create_response(400, {
                'error': str(e)
            })
        except Exception as e:
            return self.create_response(500, {
                'error': f'Internal server error: {str(e)}'
            })
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        GET /api/rewind/{sessionId}
        Get session status and basic info
        
        Args:
            session_id: Session ID
        
        Returns:
            Session data
        """
        try:
            # Download analytics
            analytics_str = download_from_s3(f"sessions/{session_id}/analytics.json")
            
            if not analytics_str:
                return self.create_response(404, {
                    'error': 'Session not found'
                })
            
            analytics = json.loads(analytics_str)
            
            return self.create_response(200, {
                'sessionId': session_id,
                'status': 'complete',
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
