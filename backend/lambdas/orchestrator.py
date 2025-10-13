"""Progressive Orchestrator for Rift Rewind"""

import os
import sys
import json
import time
from typing import Dict, Any, Optional

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

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
        from lambdas.league_data import LeagueDataFetcher
        from lambdas.humor_context import HumorGenerator
        
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
        
        humor_generator = HumorGenerator()
        
        if elapsed < self.priority_humor_trigger:
            humor_generator.generate_priority_slides(session_id)
        
        humor_generator.generate_background_slides(session_id)
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
        from lambdas.league_data import LeagueDataFetcher
        from lambdas.humor_context import HumorGenerator
        
        session_id = existing_session['sessionId']
        
        fetcher = LeagueDataFetcher()
        checkpoint_callback = self._create_checkpoint_callback()
        
        resume_result = fetcher._resume_from_checkpoint(
            existing_session=existing_session,
            region=region,
            checkpoint_callback=checkpoint_callback
        )
        
        humor_generator = HumorGenerator()
        existing_humor = existing_session.get('aiHumor', {})
        missing_slides = [i for i in range(1, 16) if not existing_humor.get(f"slide{i}")]
        
        if missing_slides:
            for slide_num in missing_slides:
                try:
                    result = humor_generator.generate(session_id, slide_num)
                    if result.get('humor'):
                        self.session_manager.update_humor(session_id, slide_num, result['humor'])
                except Exception as e:
                    pass
        
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
