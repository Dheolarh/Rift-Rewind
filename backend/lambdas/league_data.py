"""
Lambda Function: league_data.py
Purpose: Fetch all player data from Riot APIs and store in S3

Environment Variables Required:
- RIOT_API_KEY
- S3_BUCKET_NAME

Memory: 512 MB
Timeout: 5 minutes
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from services.riot_api_client import RiotAPIClient
from services.aws_clients import upload_to_s3
from services.validators import validate_riot_id, validate_region
from services.constants import PLATFORM_TO_REGIONAL, SEASON_14_START_TIMESTAMP
from services.match_analyzer import IntelligentSampler
from services.session_manager import SessionManager


class LeagueDataFetcher:
    """
    Fetches complete League of Legends player data from Riot APIs.
    Supports progressive checkpoint-based loading for large datasets.
    """
    
    def __init__(self):
        self.riot_client = RiotAPIClient()
        self.sampler = IntelligentSampler()
        self.session_manager = SessionManager()
        self.session_id = None
        self.data = {}
        self.sampling_metadata = {}
        self.checkpoint_batch_size = 100  # Matches per checkpoint
    
    def validate_input(self, game_name: str, tag_line: str, region: str) -> Dict[str, Any]:
        """
        Validate input parameters.
        
        Args:
            game_name: Riot ID game name (e.g., "Hide on bush")
            tag_line: Riot ID tag line (e.g., "KR1")
            region: Region code (e.g., "kr")
        
        Returns:
            Validation result with success status and errors
        """
        errors = []
        
        # Validate Riot ID format
        riot_id_validation = validate_riot_id(game_name, tag_line)
        if not riot_id_validation['valid']:
            errors.extend(riot_id_validation['errors'])
        
        # Validate region
        region_validation = validate_region(region)
        if not region_validation['valid']:
            errors.extend(region_validation['errors'])
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def fetch_account_data(self, game_name: str, tag_line: str, region: str) -> Dict[str, Any]:
        """
        Fetch account data using ACCOUNT-V1 API (Riot ID lookup).
        
        Args:
            game_name: Riot ID game name
            tag_line: Riot ID tag line
            region: Region code (for regional routing)
        
        Returns:
            Account data including PUUID
        """
        logger.info(f"[1/5] Fetching account data for {game_name}#{tag_line} in {region}...")
        
        regional = PLATFORM_TO_REGIONAL.get(region, region)
        logger.info(f"   Platform '{region}' → Regional routing '{regional}'")
        
        account_data = self.riot_client.get_account_by_riot_id(
            game_name=game_name,
            tag_line=tag_line,
            regional=regional
        )
        
        if not account_data:
            raise ValueError(f"Account not found: {game_name}#{tag_line}")
        
        self.data['account'] = {
            'puuid': account_data.get('puuid'),
            'gameName': account_data.get('gameName'),
            'tagLine': account_data.get('tagLine'),
            'region': region
        }
        
        logger.info(f" Account found - PUUID: {account_data.get('puuid')[:10]}...")
        return account_data
    
    def fetch_summoner_data(self, puuid: str, region: str) -> Dict[str, Any]:
        """
        Fetch summoner data using SUMMONER-V4 API.
        
        Args:
            puuid: Player PUUID
            region: Platform region code
        
        Returns:
            Summoner data including level, profile icon
        """
        logger.info(f"[2/5] Fetching summoner data...")
        
        summoner_data = self.riot_client.get_summoner_by_puuid(
            puuid=puuid,
            platform=region
        )
        
        if not summoner_data:
            raise ValueError(f"Summoner not found for PUUID: {puuid}")
        
        self.data['summoner'] = {
            'puuid': summoner_data.get('puuid'),
            'summonerLevel': summoner_data.get('summonerLevel'),
            'profileIconId': summoner_data.get('profileIconId'),
            'revisionDate': summoner_data.get('revisionDate')
        }
        
        logger.info(f" Summoner Level: {summoner_data.get('summonerLevel')}")
        return summoner_data
    
    def fetch_ranked_info(self, puuid: str, region: str) -> Dict[str, Any]:
        """
        Fetch ranked information using LEAGUE-V4 API (by PUUID).
        
        Args:
            puuid: Player PUUID
            region: Platform region code
        
        Returns:
            Ranked queue information
        """
        logger.info(f"[3/5] Fetching ranked information...")
        
        league_entries = self.riot_client.get_league_entries_by_puuid(
            puuid=puuid,
            platform=region
        )
        
        # Find RANKED_SOLO_5x5 queue
        ranked_solo = None
        ranked_flex = None
        
        for entry in league_entries:
            if entry.get('queueType') == 'RANKED_SOLO_5x5':
                ranked_solo = entry
            elif entry.get('queueType') == 'RANKED_FLEX_SR':
                ranked_flex = entry
        
        self.data['ranked'] = {
            'soloQueue': ranked_solo,
            'flexQueue': ranked_flex
        }
        
        if ranked_solo:
            tier = ranked_solo.get('tier', 'UNRANKED')
            rank = ranked_solo.get('rank', '')
            lp = ranked_solo.get('leaguePoints', 0)
            logger.info(f" Rank: {tier} {rank} ({lp} LP)")
        else:
            logger.info(" Rank: UNRANKED")
        
        return league_entries
    
    def fetch_match_history(self, puuid: str, region: str, start_time: Optional[int] = None) -> List[str]:
        """
        Fetch match IDs using MATCH-V5 API for the full year.
        
        Args:
            puuid: Player PUUID
            region: Platform region (will be converted to regional routing)
            start_time: Unix timestamp for start of year (default: January 1, 2025)
        
        Returns:
            List of match IDs from 2025
        """
        if start_time is None:
            start_time = SEASON_14_START_TIMESTAMP
        
        logger.info(f"[4/5] Fetching match history since 2025 start ({datetime.fromtimestamp(start_time).date()})...")
        
        # First, try to get ANY matches at all (no queue filter, no time filter) to verify the account has match history
        logger.info(f"    Checking if account has ANY match history (no filters)...")
        test_any_matches = self.riot_client.get_match_ids(
            puuid=puuid,
            platform=region,
            count=10,
            start=0
        )
        logger.info(f"   Total matches (all modes, all time): {len(test_any_matches) if test_any_matches else 0}")
        if test_any_matches:
            logger.info(f"   Sample match IDs: {test_any_matches[:3]}")
        else:
            logger.error(f" CRITICAL: This PUUID has NO match history at all in the match-v5 API!")
            logger.error(f"   This could mean:")
            logger.error(f"   - Account has match history privacy enabled")
            logger.error(f"   - Account transferred from another region")
            logger.error(f"   - Riot API sync issue for this region")
            logger.error(f"   - This is not the correct account")
        
        # Fetch ALL ranked queues: Solo/Duo (420), Flex (440), and Clash (700)
        all_match_ids = []
        queue_counts = {}  # Track per-queue counts for debugging
        
        for queue_id, queue_name in [(420, "Solo/Duo"), (440, "Flex"), (700, "Clash")]:
            logger.info(f"   Fetching {queue_name} ranked matches...")
            start_index = 0
            batch_size = 100
            queue_matches = []
            
            while True:
                match_ids = self.riot_client.get_match_ids(
                    puuid=puuid,
                    platform=region,
                    count=batch_size,
                    start=start_index,
                    start_time=start_time,
                    queue=queue_id
                )
                
                logger.info(f"      {queue_name}: API returned {len(match_ids) if match_ids else 0} match IDs (start_index={start_index})")
                
                if not match_ids:
                    # If no matches found with time filter, try without it to debug
                    if start_index == 0 and start_time:
                        logger.warning(f"  No {queue_name} matches found with 2025 filter. Trying without time filter to check if ANY matches exist...")
                        test_matches = self.riot_client.get_match_ids(
                            puuid=puuid,
                            platform=region,
                            count=20,
                            start=0,
                            queue=queue_id
                        )
                        logger.info(f"      {queue_name} without filter: {len(test_matches) if test_matches else 0} matches found")
                        if test_matches:
                            logger.warning(f"      Sample match IDs: {test_matches[:3]}")
                            # If matches exist without filter but not with filter, timestamp might be wrong
                            logger.error(f" CRITICAL: Found {len(test_matches)} {queue_name} matches WITHOUT time filter, but 0 WITH filter!")
                            logger.error(f"   This means the timestamp {start_time} is filtering out all matches.")
                            logger.error(f"   The player's matches might be from 2024 or earlier.")
                    break  # No more matches for this queue
                
                queue_matches.extend(match_ids)
                
                # If we got less than batch_size, we've reached the end
                if len(match_ids) < batch_size:
                    break
                
                start_index += batch_size
            
            # Deduplicate within this queue (pagination duplicates)
            queue_matches_before = len(queue_matches)
            queue_matches = list(dict.fromkeys(queue_matches))
            queue_duplicates = queue_matches_before - len(queue_matches)
            
            if queue_duplicates > 0:
                logger.warning(f"        {queue_name}: Removed {queue_duplicates} pagination duplicates within queue")
            
            queue_counts[queue_name] = len(queue_matches)
            all_match_ids.extend(queue_matches)
            logger.info(f"    {queue_name}: {len(queue_matches)} unique matches")
        
        # Remove duplicates (in case of any overlap between queues)
        matches_before_dedup = len(all_match_ids)
        all_match_ids = list(dict.fromkeys(all_match_ids))
        cross_queue_duplicates = matches_before_dedup - len(all_match_ids)
        
        # Log detailed breakdown
        logger.info("")
        logger.info("==> Match Fetching Summary:")
        for queue_name, count in queue_counts.items():
            logger.info(f"    {queue_name}: {count} ranked matches")
        logger.info(f"    Combined total: {matches_before_dedup} matches")
        if cross_queue_duplicates > 0:
            logger.warning(f"    Cross-queue duplicates removed: {cross_queue_duplicates}")
        logger.info(f"    Final unique ranked matches: {len(all_match_ids)}")
        logger.info("")
        
        self.data['matchIds'] = all_match_ids
        logger.info(f"Total ranked matches for 2025: {len(all_match_ids)}")
        
        return all_match_ids
    
    def fetch_match_details_batch(self, match_ids: List[str], region: str, use_sampling: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch match details using intelligent sampling for efficiency.
        
        Args:
            match_ids: List of match IDs
            region: Platform region
            use_sampling: Whether to use intelligent sampling (default: True)
        
        Returns:
            List of match detail objects
        """
        total_matches = len(match_ids)
        
        # Apply intelligent sampling
        if use_sampling and total_matches > 0:
            logger.info(f"[5/6] Applying intelligent sampling...")
            
            sampling_result = self.sampler.sample_matches(match_ids)
            sampled_ids = sampling_result['sampled_match_ids']
            
            # Store sampling metadata
            self.sampling_metadata = {
                'total_matches': sampling_result['total_matches'],
                'sample_count': sampling_result['sample_count'],
                'sample_percentage': sampling_result['sample_percentage'],
                'sampling_tier': sampling_result['metadata']['sampling_tier'],
                'statistical_confidence': sampling_result['metadata']['statistical_confidence'],
                'is_full_analysis': sampling_result['metadata']['is_full_analysis'],
                'monthly_breakdown': sampling_result['monthly_breakdown']
            }
            
            logger.info(f" Sampling Strategy: {sampling_result['metadata']['sampling_tier']}")
            logger.info(f" Analyzing {len(sampled_ids)}/{total_matches} matches ({sampling_result['sample_percentage']:.1f}%)")
            logger.info(f" Statistical Confidence: {sampling_result['metadata']['statistical_confidence']}")
            logger.info(f" Speed Improvement: {sampling_result['metadata']['efficiency_gain']}")
            
            match_ids_to_fetch = sampled_ids
        else:
            logger.info(f"[5/6] Sampling disabled - fetching all matches...")
            match_ids_to_fetch = match_ids
            self.sampling_metadata = {
                'total_matches': total_matches,
                'sample_count': total_matches,
                'sample_percentage': 100.0,
                'sampling_tier': 'No Sampling',
                'statistical_confidence': 'Complete',
                'is_full_analysis': True,
                'monthly_breakdown': {}
            }
        
        # Fetch match details (with parallel processing)
        logger.info(f"[6/6] Fetching {len(match_ids_to_fetch)} match details in parallel...")
        
        matches = self.riot_client.get_matches_batch(
            match_ids=match_ids_to_fetch,
            platform=region,
            batch_size=10,  # 10 parallel workers
            parallel=True   # Enable parallel processing
        )
        
        self.data['matches'] = matches
        self.data['allMatchIds'] = match_ids  # Store all IDs for reference
        self.data['sampledMatchIds'] = match_ids_to_fetch  # Store sampled IDs
        
        logger.info(f" Retrieved {len(matches)}/{len(match_ids_to_fetch)} match details")
        
        return matches
    
    def store_to_s3(self) -> str:
        """
        Store collected data to S3 with sampling metadata.
        
        Returns:
            S3 key where data was stored
        """
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        
        # Add metadata including sampling information
        self.data['metadata'] = {
            'sessionId': self.session_id,
            'fetchedAt': datetime.utcnow().isoformat(),
            'totalMatches': len(self.data.get('matches', [])),
            'status': 'raw_data_complete',
            'sampling': self.sampling_metadata  # Include sampling details
        }
        
        # Store in S3
        s3_key = f"sessions/{self.session_id}/raw_data.json"
        
        upload_to_s3(s3_key, self.data)
        
        logger.info(f" Data stored successfully!")
        return s3_key
    
    # ========================================================================
    # PROGRESSIVE CHECKPOINT METHODS
    # ========================================================================
    
    def fetch_progressive(
        self,
        game_name: str,
        tag_line: str,
        region: str,
        checkpoint_callback=None
    ) -> Dict[str, Any]:
        """
        Fetch player data with progressive 100-match checkpoints.
        This is the NEW main method for progressive data loading.
        
        Args:
            game_name: Riot ID game name
            tag_line: Riot ID tag line
            region: Platform region code
            checkpoint_callback: Optional callback function(checkpoint_num, data)
        
        Returns:
            Complete data payload with checkpoint metadata
        """
        from services.analytics import RiftRewindAnalytics
        
        
        # Check for existing session (returning player)
        existing_session = self.session_manager.load_checkpoint(game_name, tag_line, region)
        
        if existing_session and existing_session['status'] == 'partial':
            return self._resume_from_checkpoint(existing_session, region, checkpoint_callback)
        
        # NEW SESSION MODE
        
        # Step 1: Fetch instant data (5-10 seconds)
        
        validation = self.validate_input(game_name, tag_line, region)
        if not validation['valid']:
            raise ValueError(f"Invalid input: {', '.join(validation['errors'])}")
        
        account_data = self.fetch_account_data(game_name, tag_line, region)
        puuid = account_data['puuid']
        
        self.fetch_summoner_data(puuid, region)
        self.fetch_ranked_info(puuid, region)
        
        # Step 2: Fetch ALL match IDs (instant)
        all_match_ids = self.fetch_match_history(puuid, region)
        total_matches = len(all_match_ids)
        
        logger.info(f" Found {total_matches} matches")
        
        # Create session ID
        self.session_id = self.session_manager.create_session_id(game_name, tag_line, region)
        
        # Step 3: Progressive match fetching (100-match checkpoints)
        
        checkpoint_num = 0
        analyzed_ids = []
        all_matches = []
        
        for i in range(0, total_matches, self.checkpoint_batch_size):
            checkpoint_num += 1
            batch_ids = all_match_ids[i:i + self.checkpoint_batch_size]
            
            
            # Fetch this batch of match details
            batch_matches = self.riot_client.get_matches_batch(
                match_ids=batch_ids,
                platform=region,
                batch_size=10,
                parallel=True
            )
            
            all_matches.extend(batch_matches)
            analyzed_ids.extend(batch_ids)
            remaining_ids = all_match_ids[len(analyzed_ids):]
            
            logger.info(f" Fetched {len(batch_matches)} matches")
            
            # Calculate analytics for current checkpoint
            checkpoint_data = {
                'account': self.data.get('account'),
                'summoner': self.data.get('summoner'),
                'ranked': self.data.get('ranked'),
                'matches': all_matches,
                'metadata': {
                    'sessionId': self.session_id,
                    'checkpoint': checkpoint_num
                }
            }
            
            analytics_engine = RiftRewindAnalytics(checkpoint_data)
            checkpoint_analytics = analytics_engine.calculate_checkpoint_analytics(
                checkpoint_num=checkpoint_num,
                total_matches=total_matches
            )
            
            # Save checkpoint to S3
            player_info = {
                'gameName': game_name,
                'tagLine': tag_line,
                'region': region,
                'puuid': puuid,
                'summonerLevel': self.data.get('summoner', {}).get('summonerLevel'),
                'rank': self.data.get('ranked', {}).get('tier'),
                'tier': self.data.get('ranked', {}).get('rank'),
                'lp': self.data.get('ranked', {}).get('leaguePoints')
            }
            
            match_data = {
                'totalMatches': total_matches,
                'analyzedMatchIds': analyzed_ids,
                'unanalyzedMatchIds': remaining_ids,
                'lastCheckpoint': checkpoint_num
            }
            
            # Initialize aiHumor with all slides as None
            ai_humor = {f"slide{i}": None for i in range(1, 16)}
            
            self.session_manager.save_checkpoint(
                session_id=self.session_id,
                player_info=player_info,
                match_data=match_data,
                analytics=checkpoint_analytics,
                ai_humor=ai_humor,
                status='partial' if remaining_ids else 'complete'
            )
            
            
            # Call checkpoint callback if provided
            if checkpoint_callback:
                checkpoint_callback(checkpoint_num, checkpoint_analytics)
        
        # Mark as complete
        if not remaining_ids:
            self.session_manager.mark_complete(self.session_id)
        
        # Store final complete data
        self.data['matches'] = all_matches
        s3_key = self.store_to_s3()
        
        
        return {
            'sessionId': self.session_id,
            'status': 'complete',
            's3Key': s3_key,
            'totalMatches': total_matches,
            'checkpoints': checkpoint_num
        }
    
    def _resume_from_checkpoint(
        self,
        existing_session: Dict[str, Any],
        region: str,
        checkpoint_callback=None
    ) -> Dict[str, Any]:
        """
        Resume progressive fetch from existing checkpoint.
        
        Args:
            existing_session: Loaded session data from S3
            region: Platform region code
            checkpoint_callback: Optional callback function
        
        Returns:
            Updated session data
        """
        from services.analytics import RiftRewindAnalytics
        
        
        self.session_id = existing_session['sessionId']
        player_info = existing_session['playerInfo']
        match_data = existing_session['matchData']
        
        # Restore existing data
        self.data = {
            'account': {'puuid': player_info['puuid']},
            'summoner': {'summonerLevel': player_info['summonerLevel']},
            'ranked': {
                'tier': player_info['rank'],
                'rank': player_info['tier'],
                'leaguePoints': player_info['lp']
            }
        }
        
        # Get unanalyzed match IDs
        remaining_ids = match_data['unanalyzedMatchIds']
        total_matches = match_data['totalMatches']
        checkpoint_num = match_data['lastCheckpoint']
        
        
        # Continue fetching remaining matches
        all_analyzed_ids = match_data['analyzedMatchIds'].copy()
        
        # Load previously fetched matches from S3
        # (In production, we'd load from S3 raw_data.json)
        # For now, we'll just continue from where we left off
        
        for i in range(0, len(remaining_ids), self.checkpoint_batch_size):
            checkpoint_num += 1
            batch_ids = remaining_ids[i:i + self.checkpoint_batch_size]
            
            
            batch_matches = self.riot_client.get_matches_batch(
                match_ids=batch_ids,
                platform=region,
                batch_size=10,
                parallel=True
            )
            
            all_analyzed_ids.extend(batch_ids)
            still_remaining = remaining_ids[len(all_analyzed_ids) - len(match_data['analyzedMatchIds']):]
            
            logger.info(f" Fetched {len(batch_matches)} matches")
            
            # Update checkpoint
            match_data['analyzedMatchIds'] = all_analyzed_ids
            match_data['unanalyzedMatchIds'] = still_remaining
            match_data['lastCheckpoint'] = checkpoint_num
            
            self.session_manager.save_checkpoint(
                session_id=self.session_id,
                player_info=player_info,
                match_data=match_data,
                analytics=existing_session['analytics'],  # Keep existing analytics
                ai_humor=existing_session['aiHumor'],  # Keep existing humor
                status='partial' if still_remaining else 'complete'
            )
            
            if checkpoint_callback:
                checkpoint_callback(checkpoint_num, None)
        
        # Mark complete if finished
        if not still_remaining:
            self.session_manager.mark_complete(self.session_id)
        
        return {
            'sessionId': self.session_id,
            'status': 'complete' if not still_remaining else 'partial',
            'totalMatches': total_matches,
            'checkpoints': checkpoint_num
        }
    
    # ========================================================================
    # END PROGRESSIVE CHECKPOINT METHODS
    # ========================================================================
    
    def fetch_all(self, game_name: str, tag_line: str, region: str) -> Dict[str, Any]:
        """
        Fetch all player data (orchestration method).
        **DEPRECATED**: Use fetch_progressive() instead for production.
        This method is kept for backwards compatibility and testing.
        
        Args:
            game_name: Riot ID game name
            tag_line: Riot ID tag line
            region: Platform region code
        
        Returns:
            Complete data payload with session ID
        """
        
        
        # Step 1: Validate input
        validation = self.validate_input(game_name, tag_line, region)
        if not validation['valid']:
            raise ValueError(f"Invalid input: {', '.join(validation['errors'])}")
        
        # Step 2: Fetch account data (ACCOUNT-V1)
        account_data = self.fetch_account_data(game_name, tag_line, region)
        puuid = account_data['puuid']
        
        # Step 3: Fetch summoner data (SUMMONER-V4)
        self.fetch_summoner_data(puuid, region)
        
        # Step 4: Fetch ranked info (LEAGUE-V4)
        self.fetch_ranked_info(puuid, region)
        
        # Step 5: Fetch match history (FULL YEAR)
        match_ids = self.fetch_match_history(puuid, region)
        
        # Step 6: Fetch match details for ALL matches (no sampling)
        self.fetch_match_details_batch(match_ids, region, use_sampling=False)
        
        # Step 7: Store to S3
        s3_key = self.store_to_s3()
        
        
        return {
            'sessionId': self.session_id,
            'status': 'success',
            's3Key': s3_key,
            'matchCount': len(self.data.get('matches', []))
        }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function.
    
    Expected event format:
    {
        "gameName": "Hide on bush",
        "tagLine": "KR1",
        "region": "kr"
    }
    
    Returns:
    {
        "sessionId": "uuid",
        "status": "success",
        "matchCount": 100
    }
    """
    try:
        # Extract parameters
        game_name = event.get('gameName')
        tag_line = event.get('tagLine')
        region = event.get('region')
        
        # Validate required parameters
        if not all([game_name, tag_line, region]):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameters: gameName, tagLine, region'
                })
            }
        
        # Fetch all data
        fetcher = LeagueDataFetcher()
        result = fetcher.fetch_all(game_name, tag_line, region)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    
    except ValueError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': str(e)
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }


# For local testing
if __name__ == "__main__":
    # Test with Faker's account
    test_event = {
        'gameName': 'Hide on bush',
        'tagLine': 'KR1',
        'region': 'kr'
    }
    
    result = lambda_handler(test_event, None)
    print(f"\nResult: {json.dumps(json.loads(result['body']), indent=2)}")