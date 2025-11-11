"""Progressive Orchestrator for Rift Rewind"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from services.session_manager import SessionManager
from services.analytics import RiftRewindAnalytics


# Import API wrapper for handler functions
from api import RiftRewindAPI

# Initialize API instance
api = RiftRewindAPI()


def handle_get_regions() -> Dict[str, Any]:
    """Handle GET /api/regions"""
    return api.get_regions()


def handle_health_check() -> Dict[str, Any]:
    """Handle GET /api/health"""
    return api.health_check()


def handle_start_rewind(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle POST /api/rewind"""
    game_name = request_data.get('gameName', '')
    tag_line = request_data.get('tagLine', '')
    region = request_data.get('region', '')
    force_refresh = request_data.get('forceRefresh', False)

    return api.start_rewind(game_name, tag_line, region, force_refresh)


def handle_get_session(session_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle GET /api/rewind/{sessionId}"""
    game_name = request_data.get('gameName')
    tag_line = request_data.get('tagLine')
    region = request_data.get('region')

    return api.get_session(session_id, game_name, tag_line, region)


def handle_get_slide(session_id: str, slide_number: int) -> Dict[str, Any]:
    """Handle GET /api/rewind/{sessionId}/slide/{slideNumber}"""
    return api.get_slide(session_id, slide_number)


def handle_check_cache(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle POST /api/cache/check"""
    game_name = request_data.get('gameName', '')
    tag_line = request_data.get('tagLine', '')
    region = request_data.get('region', '')

    return api.check_cache(game_name, tag_line, region)


def handle_invalidate_cache(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle POST /api/cache/invalidate"""
    game_name = request_data.get('gameName', '')
    tag_line = request_data.get('tagLine', '')
    region = request_data.get('region', '')

    return api.invalidate_cache(game_name, tag_line, region)


class ProgressiveOrchestrator:
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.loading_screen_max_seconds = 240
        self.priority_humor_trigger = 210
        self.start_time = None
    
    def orchestrate(self, game_name: str, tag_line: str, region: str) -> Dict[str, Any]:
        
        self.start_time = time.time()
        
        existing_session = self.session_manager.load_checkpoint(game_name, tag_line, region)
        
        if existing_session and existing_session['status'] == 'partial':
            return self._resume_session(existing_session, region)
        elif existing_session and existing_session['status'] == 'complete':
            return {
                'sessionId': existing_session['sessionId'],
                'status': 'complete',
                'cached': True,
                'message': 'Welcome back! Your Rewind is ready.'
            }
        else:
            return self._new_session(game_name, tag_line, region)
    
    def _new_session(self, game_name: str, tag_line: str, region: str) -> Dict[str, Any]:
        from league_data import LeagueDataFetcher
        from humor_context import HumorGenerator
        from insights import InsightsGenerator
        
        fetcher = LeagueDataFetcher()
        checkpoint_callback = self._create_checkpoint_callback()
        
        fetch_result = fetcher.fetch_progressive(
            game_name=game_name,
            tag_line=tag_line,
            region=region,
            checkpoint_callback=checkpoint_callback
        )
        
        session_id = fetch_result['sessionId']
        elapsed = time.time() - self.start_time
        
        # Generate AI insights for strengths/weaknesses (BEFORE humor)
        logger.info(f"Generating AI insights for session: {session_id}")
        insights_generator = InsightsGenerator()
        try:
            insights_result = insights_generator.generate(session_id)
            insights_data = insights_result.get('insights', {})
            
            # ALWAYS update analytics with insights (even if AI failed, fallback validation will run)
            self._update_analytics_with_insights(session_id, insights_data)
            
            if insights_result.get('status') == 'success' and insights_data:
                logger.info(f" AI insights generated successfully")
            else:
                logger.warning(f" AI insights incomplete, fallback validation applied")
        except Exception as e:
            logger.error(f" Failed to generate AI insights: {e}")
            # Force fallback update with empty dict - validation logic will provide defaults
            try:
                self._update_analytics_with_insights(session_id, {})
                logger.info(" Fallback insights applied via validation")
            except Exception as update_error:
                logger.error(f" Failed to apply fallback insights: {update_error}")

        
        # Generate ALL humor before marking complete (slides 2-12, 14 - skip 13 achievements)
        logger.info(f"Generating humor for all slides (2-12, 14)")
        humor_generator = HumorGenerator()
        
        # Generate slides 2-12, then 14 (skip 13 - achievements removed)
        all_slide_numbers = list(range(2, 13)) + [14]  # Slides 2-12, 14 have humor
        for slide_num in all_slide_numbers:
            try:
                logger.info(f"Generating humor for slide {slide_num}")
                result = humor_generator.generate(session_id, slide_num)
                if result.get('humor'):
                    logger.info(f" Slide {slide_num} humor generated")
                else:
                    logger.warning(f" Slide {slide_num} returned no humor")
            except Exception as e:
                logger.error(f" Failed to generate humor for slide {slide_num}: {e}")
                # Continue to next slide even if one fails
        
        # NOW mark complete - all processing done
        logger.info(f"All humor generation complete. Marking session as complete.")
        self.session_manager.mark_complete(session_id)
        
        total_time = time.time() - self.start_time
        
        return {
            'sessionId': session_id,
            'status': 'complete',
            'cached': False,
            'totalMatches': fetch_result.get('totalMatches'),
            'checkpoints': fetch_result.get('checkpoints'),
            'processingTime': round(total_time, 1),
            'message': 'Your Rewind is ready!'
        }
    
    def _resume_session(self, existing_session: Dict[str, Any], region: str) -> Dict[str, Any]:
        from league_data import LeagueDataFetcher
        from humor_context import HumorGenerator
        from insights import InsightsGenerator
        
        session_id = existing_session['sessionId']
        
        fetcher = LeagueDataFetcher()
        checkpoint_callback = self._create_checkpoint_callback()
        
        resume_result = fetcher._resume_from_checkpoint(
            existing_session=existing_session,
            region=region,
            checkpoint_callback=checkpoint_callback
        )
        
        # Check if AI insights need to be generated
        analytics = existing_session.get('analytics', {})
        slide_data = analytics.get('slide10_11_analysis', {})
        needs_ai = slide_data.get('needsAIProcessing', True)
        
        if needs_ai:
            logger.info(f"Generating missing AI insights for resumed session: {session_id}")
            insights_generator = InsightsGenerator()
            try:
                insights_result = insights_generator.generate(session_id)
                self._update_analytics_with_insights(session_id, insights_result.get('insights', {}))
            except Exception as e:
                logger.error(f"Failed to generate AI insights on resume: {e}")
        
        # Generate humor for any missing slides (2-12, 14 - skip 13 achievements)
        logger.info(f"Checking for missing humor in resumed session")
        humor_generator = HumorGenerator()
        existing_humor = existing_session.get('aiHumor', {})
        # Check slides 2-12 and 14 (skip 13 - achievements removed)
        missing_slides = [i for i in list(range(2, 13)) + [14] if not existing_humor.get(f"slide{i}")]
        
        if missing_slides:
            logger.info(f"Generating humor for {len(missing_slides)} missing slides: {missing_slides}")
            for slide_num in missing_slides:
                try:
                    logger.info(f"Generating humor for slide {slide_num}")
                    result = humor_generator.generate(session_id, slide_num)
                    if result.get('humor'):
                        self.session_manager.update_humor(session_id, slide_num, result['humor'])
                        logger.info(f" Slide {slide_num} humor generated")
                    else:
                        logger.warning(f" Slide {slide_num} returned no humor")
                except Exception as e:
                    logger.error(f" Failed to generate humor for slide {slide_num}: {e}")
                    # Continue to next slide
        else:
            logger.info("All humor already generated for this session")
        
        # NOW mark complete - all processing done
        logger.info(f"Resume complete. Marking session as complete.")
        self.session_manager.mark_complete(session_id)
        total_time = time.time() - self.start_time
        
        return {
            'sessionId': session_id,
            'status': 'complete',
            'resumed': True,
            'totalMatches': resume_result.get('totalMatches'),
            'processingTime': round(total_time, 1),
            'message': 'Welcome back! Your Rewind is ready!'
        }
    
    def _create_checkpoint_callback(self):
        def checkpoint_callback(checkpoint_num: int, analytics: Optional[Dict[str, Any]]):
            elapsed = time.time() - self.start_time
            if elapsed >= self.priority_humor_trigger and not hasattr(self, '_priority_humor_triggered'):
                self._priority_humor_triggered = True
        return checkpoint_callback
    
    def _update_analytics_with_insights(self, session_id: str, insights: Dict[str, Any]):
        """
        Update analytics with AI-generated insights.
        GUARANTEED to always provide valid insights - never leaves empty arrays.
        
        Args:
            session_id: Session ID
            insights: AI-generated insights dict with strengths, weaknesses, etc.
        """
        from services.aws_clients import download_from_s3, upload_to_s3
        
        try:
            # Download current analytics
            s3_key = f"sessions/{session_id}/analytics.json"
            analytics_str = download_from_s3(s3_key)
            
            if not analytics_str:
                logger.error(f"Analytics not found for session: {session_id}")
                return
            
            analytics = json.loads(analytics_str)
            
            # Validate insights have content (never allow empty arrays)
            strengths = insights.get('strengths', [])
            weaknesses = insights.get('weaknesses', [])
            
            if not strengths:
                strengths = ["Consistent ranked participation", "Dedication to improvement"]
                logger.warning("  No strengths in insights, using fallback")
            
            if not weaknesses:
                weaknesses = ["Focus on consistency for higher ranks", "Small improvements in positioning"]
                logger.warning("  No weaknesses in insights, using fallback")
            
            # Update slide10_11_analysis with AI-generated strengths/weaknesses
            if 'slide10_11_analysis' in analytics:
                analytics['slide10_11_analysis']['strengths'] = strengths
                analytics['slide10_11_analysis']['weaknesses'] = weaknesses
                analytics['slide10_11_analysis']['needsAIProcessing'] = False
                
                # Store additional insights for potential future use
                analytics['slide10_11_analysis']['coaching_tips'] = insights.get('coaching_tips', 
                    ["Review deaths after each game", "Master 3-5 champions", "Focus on objectives"])
                analytics['slide10_11_analysis']['play_style'] = insights.get('play_style', 
                    'Developing competitive player')
                analytics['slide10_11_analysis']['personality_title'] = insights.get('personality_title', 
                    'The Determined Competitor')
            
            # Upload updated analytics
            upload_to_s3(s3_key, analytics)
            logger.info(f" Analytics updated with AI insights for session: {session_id}")
            
        except Exception as e:
            logger.error(f" Error updating analytics with insights: {e}")
            raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for API Gateway events.
    Routes requests based on HTTP method and path.
    """
    try:
        # Extract API Gateway event details
        http_method = event.get('httpMethod', '')
        path = event.get('path', '').rstrip('/') 
        path_parameters = event.get('pathParameters', {}) or {}
        query_parameters = event.get('queryStringParameters', {}) or {}

        # Parse request body for POST requests
        body = event.get('body', '{}')
        if body:
            try:
                request_data = json.loads(body)
            except json.JSONDecodeError:
                request_data = {}
        else:
            request_data = {}

        logger.info(f"Request: {http_method} {path}")

        # --- CORRECTED ROUTING ---

        if path.endswith('/api/regions') and http_method == 'GET':
            return handle_get_regions()

        elif path.endswith('/api/health') and http_method == 'GET':
            return handle_health_check()

        elif path.endswith('/api/rewind') and http_method == 'POST':
            return handle_start_rewind(request_data)

        elif path.endswith('/api/cache/check') and http_method == 'POST':
            return handle_check_cache(request_data)

        elif path.endswith('/api/cache/invalidate') and http_method == 'POST':
            return handle_invalidate_cache(request_data)

        # Handle routes with path parameters
        elif '/api/rewind/' in path and http_method == 'GET':
            path_parts = path.split('/')
            
            # Find 'rewind' and expect sessionID after it
            try:
                rewind_index = path_parts.index('rewind')
                
                # Check for /api/rewind/{sessionId}/slide/{slideNumber}
                if len(path_parts) > rewind_index + 3 and path_parts[rewind_index + 2] == 'slide':
                    session_id = path_parts[rewind_index + 1]
                    slide_number = path_parts[rewind_index + 3]
                    return handle_get_slide(session_id, int(slide_number))
                
                # Check for /api/rewind/{sessionId}
                elif len(path_parts) > rewind_index + 1:
                    session_id = path_parts[rewind_index + 1]
                    # Pass query parameters (which are in request_data for some reason in your original handler)
                    return handle_get_session(session_id, query_parameters)
            
            except (ValueError, IndexError):
                 pass # Fall through to 404


        elif http_method == 'OPTIONS':
            return {
                'statusCode': 204,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                },
                'body': ''
            }

        # Unknown endpoint
        logger.warning(f"Endpoint not found: {http_method} {path}")
        return {
            'statusCode': 404,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': f'Endpoint not found: {http_method} {path}'})
        }

    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
