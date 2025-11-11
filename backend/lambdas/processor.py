"""
Processor Lambda
----------------
This Lambda is invoked asynchronously by the orchestrator (start_rewind).
It reads raw session data from S3 (provided key), runs analytics, generates insights
and humor, uploads results to S3 and updates session status.json.

Expected event:
{
  "session_id": "<uuid>",
  "raw_data_s3_key": "sessions/<session_id>/raw_data.json",
  "game_name": "...",
  "tag_line": "...",
  "region": "na1"
}

Note: This module re-uses existing services: RiftRewindAnalytics, InsightsGenerator, HumorGenerator
"""
import json
import logging
import traceback
from typing import Any, Dict

from services.aws_clients import download_from_s3, upload_to_s3
from services.analytics import RiftRewindAnalytics
from lambdas.humor_context import HumorGenerator
from lambdas.insights import InsightsGenerator
from services.session_cache import SessionCacheManager
from services.aws_clients import download_from_s3
from services.riot_api_client import RiotAPIClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _update_session_status(session_id: str, status: str, message: str = '', player_info: dict = None, fetcher_data: dict = None):
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


def lambda_handler(event: Dict[str, Any], context: Any):
    logger.info(f"Processor invoked with event: {json.dumps(event)}")

    session_id = event.get('session_id')
    raw_key = event.get('raw_data_s3_key')
    game_name = event.get('game_name')
    tag_line = event.get('tag_line')
    region = event.get('region')

    if not session_id or not raw_key:
        logger.error('Missing session_id or raw_data_s3_key in event')
        return {'status': 'error', 'message': 'missing parameters'}

    try:
        _update_session_status(session_id, 'analyzing', 'Analyzing your match history...')

        # Download raw fetcher data
        raw_str = download_from_s3(raw_key)
        if not raw_str:
            raise RuntimeError(f'Raw data not found in S3 at {raw_key}')

        raw_data = json.loads(raw_str)

        # Build analytics
        analytics_engine = RiftRewindAnalytics(raw_data)
        analytics = analytics_engine.calculate_all()

        # Upload analytics to S3
        analytics_key = f"sessions/{session_id}/analytics.json"
        upload_to_s3(analytics_key, analytics)
        logger.info(' Analytics uploaded to S3')

        # Update status
        _update_session_status(session_id, 'generating', 'Generating personalized insights...')

        # Generate humor for slides 2-15
        humor_generator = HumorGenerator()
        for slide_num in range(2, 16):
            try:
                humor_generator.generate(session_id, slide_num)
                logger.info(f'   Slide {slide_num} humor generated')
            except Exception as e:
                logger.warning(f'    Slide {slide_num} humor failed: {e}')

        # Generate insights and merge into analytics
        try:
            insights_generator = InsightsGenerator()
            insights_result = insights_generator.generate(session_id)
            insights = insights_result.get('insights', {})

            if 'slide10_11_analysis' in analytics:
                analytics['slide10_11_analysis'].update({
                    'strengths': insights.get('strengths', []),
                    'weaknesses': insights.get('weaknesses', []),
                    'coaching_tips': insights.get('coaching_tips', []),
                    'play_style': insights.get('play_style', ''),
                    'personality_title': insights.get('personality_title', 'The Rising Summoner')
                })
                upload_to_s3(analytics_key, analytics)
                logger.info(' Insights integrated into analytics')
        except Exception as e:
            logger.exception(' Insights generation failed')

        # Collect humor outputs and build player_info for cache
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

        # Build player info from raw_data
        from services.riot_api_client import RiotAPIClient
        profile_icon_id = raw_data.get('summoner', {}).get('profileIconId')
        profile_icon_url = RiotAPIClient.get_profile_icon_url(profile_icon_id) if profile_icon_id else None

        player_info = {
            'gameName': raw_data.get('account', {}).get('gameName'),
            'tagLine': raw_data.get('account', {}).get('tagLine'),
            'region': region,
            'summonerLevel': raw_data.get('summoner', {}).get('summonerLevel'),
            'profileIconId': profile_icon_id,
            'profileIconUrl': profile_icon_url,
            'rank': analytics.get('slide6_rankedJourney', {}).get('currentRank', 'UNRANKED')
        }

        # Save to cache
        cache_manager = SessionCacheManager(cache_expiry_days=7)
        cache_manager.save_session_to_cache(
            game_name, tag_line, region,
            session_id, analytics, humor_data, player_info,
            analytics.get('matchCount', 0), analytics.get('totalMatches', 0)
        )

        _update_session_status(session_id, 'complete', 'Your rewind is ready!', player_info)
        logger.info(f' Session {session_id} processing complete!')

        return {'status': 'complete'}

    except Exception as e:
        logger.error(f' Processor failed for session {session_id}: {e}')
        traceback.print_exc()
        _update_session_status(session_id, 'error', str(e))
        return {'status': 'error', 'message': str(e)}
