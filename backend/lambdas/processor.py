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
from services.aws_clients import download_from_s3, upload_to_s3
from lambdas.league_data import LeagueDataFetcher
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

        # Ensure we have full match data. Orchestrator uploads only initial fetcher data
        # (account/summoner/ranked). If `matches` is missing or empty, fetch them now
        # using the same LeagueDataFetcher flow used in the orchestrator local worker.
        if not raw_data.get('matches'):
            logger.info(' No matches in raw_data - fetching match history and details now')
            try:
                fetcher = LeagueDataFetcher()
                # Rehydrate fetcher state from raw_data
                fetcher.data = raw_data
                puuid = raw_data.get('account', {}).get('puuid')
                if not puuid:
                    raise RuntimeError('PUUID missing from raw_data; cannot fetch matches')

                match_ids = fetcher.fetch_match_history(puuid, region)
                total_matches = len(match_ids)

                if total_matches == 0:
                    logger.warning(f' No ranked matches found for PUUID {puuid} (region={region})')
                    # Continue with analytics - it will compute zeros - but persist updated raw_data
                # Fetch full match details (no sampling) to ensure complete analytics
                matches = fetcher.fetch_match_details_batch(match_ids, region, use_sampling=False)

                # Update raw_data with fetched matches and metadata
                raw_data['matches'] = matches
                raw_data['allMatchIds'] = match_ids
                raw_data['metadata'] = raw_data.get('metadata', {})
                raw_data['metadata'].update({'totalMatches': len(matches), 'fetchedAt': raw_data.get('metadata', {}).get('fetchedAt')})

                # Re-upload enriched raw_data so other tools can access it
                try:
                    upload_to_s3(raw_key, raw_data)
                    logger.info(' Enriched raw_data uploaded back to S3')
                except Exception as e:
                    logger.warning(f' Failed to re-upload enriched raw_data: {e}')

            except Exception as e:
                logger.exception(f' Failed while fetching matches in processor: {e}')

        # Build analytics
        analytics_engine = RiftRewindAnalytics(raw_data)
        analytics = analytics_engine.calculate_all()

        # This preserves profile icon and other player data after raw_data cleanup
        from services.riot_api_client import RiotAPIClient
        profile_icon_id = raw_data.get('summoner', {}).get('profileIconId')
        profile_icon_url = RiotAPIClient.get_profile_icon_url(profile_icon_id) if profile_icon_id else None
        
        analytics['playerInfo'] = {
            'gameName': raw_data.get('account', {}).get('gameName'),
            'tagLine': raw_data.get('account', {}).get('tagLine'),
            'region': region,
            'summonerLevel': raw_data.get('summoner', {}).get('summonerLevel'),
            'profileIconId': profile_icon_id,
            'profileIconUrl': profile_icon_url
        }

        # Upload analytics to S3
        analytics_key = f"sessions/{session_id}/analytics.json"
        upload_to_s3(analytics_key, analytics)
        logger.info(' Analytics uploaded to S3')
        
        # Clean up raw_data.json to optimize storage (saves ~8-10 MB per session)
        try:
            from services.aws_clients import delete_from_s3
            if delete_from_s3(raw_key):
                logger.info(f' Deleted raw_data.json to optimize storage (saved ~8-10 MB)')
            else:
                logger.warning(f' Could not delete raw_data.json: {raw_key}')
        except Exception as e:
            logger.warning(f' Failed to delete raw_data.json: {e}')



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
        # Derive match counts: prefer explicit analytics fields, fall back to raw_data contents
        try:
            match_count = analytics.get('matchCount') if isinstance(analytics, dict) else None
        except Exception:
            match_count = None

        try:
            total_matches = analytics.get('totalMatches') if isinstance(analytics, dict) else None
        except Exception:
            total_matches = None

        # Fallbacks: look in raw_data for common keys
        if not match_count:
            if isinstance(raw_data, dict) and raw_data.get('matches') is not None:
                match_count = len(raw_data.get('matches') or [])
            elif isinstance(raw_data, dict) and raw_data.get('allMatchIds') is not None:
                match_count = len(raw_data.get('allMatchIds') or [])
            else:
                match_count = 0

        if not total_matches:
            # total_matches may be stored in raw_data.metadata.totalMatches or sampling metadata
            total_matches = 0
            if isinstance(raw_data, dict):
                meta = raw_data.get('metadata') or {}
                if isinstance(meta, dict) and meta.get('totalMatches') is not None:
                    total_matches = meta.get('totalMatches')
                elif raw_data.get('allMatchIds') is not None:
                    total_matches = len(raw_data.get('allMatchIds') or [])

        cache_manager.save_session_to_cache(
            game_name, tag_line, region,
            session_id, analytics, humor_data, player_info,
            int(match_count), int(total_matches)
        )

        _update_session_status(session_id, 'complete', 'Your rewind is ready!', player_info)
        logger.info(f' Session {session_id} processing complete!')

        return {'status': 'complete'}

    except Exception as e:
        logger.error(f' Processor failed for session {session_id}: {e}')
        traceback.print_exc()
        _update_session_status(session_id, 'error', str(e))
        return {'status': 'error', 'message': str(e)}
