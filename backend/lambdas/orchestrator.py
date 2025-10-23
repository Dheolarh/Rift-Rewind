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
            logger.info(f"AI insights generated: {insights_result.get('status')}")
            
            # Update analytics with AI-generated strengths/weaknesses
            self._update_analytics_with_insights(session_id, insights_result.get('insights', {}))
        except Exception as e:
            logger.error(f"Failed to generate AI insights: {e}")
            # Continue without AI insights - will use placeholder values
        
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
                    logger.info(f"✓ Slide {slide_num} humor generated")
                else:
                    logger.warning(f"⚠ Slide {slide_num} returned no humor")
            except Exception as e:
                logger.error(f"✗ Failed to generate humor for slide {slide_num}: {e}")
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
                        logger.info(f"✓ Slide {slide_num} humor generated")
                    else:
                        logger.warning(f"⚠ Slide {slide_num} returned no humor")
                except Exception as e:
                    logger.error(f"✗ Failed to generate humor for slide {slide_num}: {e}")
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
            
            # Update slide10_11_analysis with AI-generated strengths/weaknesses
            if 'slide10_11_analysis' in analytics:
                analytics['slide10_11_analysis']['strengths'] = insights.get('strengths', ['Analysis complete'])
                analytics['slide10_11_analysis']['weaknesses'] = insights.get('weaknesses', ['Analysis complete'])
                analytics['slide10_11_analysis']['needsAIProcessing'] = False
                
                # Store additional insights for potential future use
                analytics['slide10_11_analysis']['coaching_tips'] = insights.get('coaching_tips', [])
                analytics['slide10_11_analysis']['play_style'] = insights.get('play_style', '')
                analytics['slide10_11_analysis']['personality_title'] = insights.get('personality_title', '')
            
            # Upload updated analytics
            upload_to_s3(s3_key, analytics)
            logger.info(f"Analytics updated with AI insights for session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error updating analytics with insights: {e}")
            raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        game_name = event.get('gameName')
        tag_line = event.get('tagLine')
        region = event.get('region')
        
        if not all([game_name, tag_line, region]):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required parameters'})
            }
        
        orchestrator = ProgressiveOrchestrator()
        result = orchestrator.orchestrate(game_name, tag_line, region)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
