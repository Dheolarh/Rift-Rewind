"""
Lambda Function: league_data.py
Purpose: Fetch all player data from Riot APIs and store in S3

Environment Variables Required:
- RIOT_API_KEY
- S3_BUCKET_NAME
- AWS_REGION

Memory: 512 MB
Timeout: 5 minutes
"""

import os
import sys
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

# Add parent directory to path for local imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.riot_api_client import RiotAPIClient
from services.aws_clients import upload_to_s3
from services.validators import validate_riot_id, validate_region
from services.constants import PLATFORM_TO_REGIONAL
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
        print(f"[1/5] Fetching account data for {game_name}#{tag_line} in {region}...")
        
        # Convert platform to regional routing
        regional = PLATFORM_TO_REGIONAL.get(region, region)
        
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
        
        print(f"✓ Account found - PUUID: {account_data.get('puuid')[:10]}...")
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
        print(f"[2/5] Fetching summoner data...")
        
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
        
        print(f"✓ Summoner Level: {summoner_data.get('summonerLevel')}")
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
        print(f"[3/5] Fetching ranked information...")
        
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
            print(f"✓ Rank: {tier} {rank} ({lp} LP)")
        else:
            print("✓ Rank: UNRANKED")
        
        return league_entries
    
    def fetch_match_history(self, puuid: str, region: str, start_time: Optional[int] = None) -> List[str]:
        """
        Fetch match IDs using MATCH-V5 API for the full year.
        
        Args:
            puuid: Player PUUID
            region: Platform region (will be converted to regional routing)
            start_time: Unix timestamp for start of year (default: 1 year ago)
        
        Returns:
            List of match IDs from the past year
        """
        # Calculate 1 year ago timestamp if not provided
        if start_time is None:
            from datetime import datetime, timedelta
            one_year_ago = datetime.utcnow() - timedelta(days=365)
            start_time = int(one_year_ago.timestamp())
        
        print(f"[4/5] Fetching FULL YEAR match history (starting from {datetime.fromtimestamp(start_time).date()})...")
        
        # Riot API returns max 100 matches per call, so we need to paginate
        all_match_ids = []
        start_index = 0
        batch_size = 100
        
        while True:
            print(f"   Fetching matches {start_index} to {start_index + batch_size}...")
            
            match_ids = self.riot_client.get_match_ids(
                puuid=puuid,
                platform=region,
                count=batch_size,
                start=start_index,
                start_time=start_time
            )
            
            if not match_ids:
                break  # No more matches
            
            all_match_ids.extend(match_ids)
            
            # If we got less than batch_size, we've reached the end
            if len(match_ids) < batch_size:
                break
            
            start_index += batch_size
            
            # Safety limit: max 1000 matches (should be enough for a year)
            if len(all_match_ids) >= 1000:
                print(f"   Reached safety limit of 1000 matches")
                break
        
        print(f"✓ Found {len(all_match_ids)} matches from the past year")
        
        self.data['matchIds'] = all_match_ids
        print(f"✓ Total matches for the year: {len(all_match_ids)}")
        
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
            print(f"[5/6] Applying intelligent sampling...")
            
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
            
            print(f"✓ Sampling Strategy: {sampling_result['metadata']['sampling_tier']}")
            print(f"✓ Analyzing {len(sampled_ids)}/{total_matches} matches ({sampling_result['sample_percentage']:.1f}%)")
            print(f"✓ Statistical Confidence: {sampling_result['metadata']['statistical_confidence']}")
            print(f"✓ Speed Improvement: {sampling_result['metadata']['efficiency_gain']}")
            
            match_ids_to_fetch = sampled_ids
        else:
            print(f"[5/6] Sampling disabled - fetching all matches...")
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
        print(f"[6/6] Fetching {len(match_ids_to_fetch)} match details in parallel...")
        
        matches = self.riot_client.get_matches_batch(
            match_ids=match_ids_to_fetch,
            platform=region,
            batch_size=10,  # 10 parallel workers
            parallel=True   # Enable parallel processing
        )
        
        self.data['matches'] = matches
        self.data['allMatchIds'] = match_ids  # Store all IDs for reference
        self.data['sampledMatchIds'] = match_ids_to_fetch  # Store sampled IDs
        
        print(f"✓ Retrieved {len(matches)}/{len(match_ids_to_fetch)} match details")
        
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
        
        print(f"\nStoring data to S3: {s3_key}")
        upload_to_s3(s3_key, self.data)
        
        print(f"✓ Data stored successfully!")
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
        
        print(f"\n{'='*60}")
        print(f"PROGRESSIVE FETCH: {game_name}#{tag_line}")
        print(f"{'='*60}\n")
        
        # Check for existing session (returning player)
        existing_session = self.session_manager.load_checkpoint(game_name, tag_line, region)
        
        if existing_session and existing_session['status'] == 'partial':
            print(f"↻ RESUME MODE: Found existing session")
            return self._resume_from_checkpoint(existing_session, region, checkpoint_callback)
        
        # NEW SESSION MODE
        print(f"✦ NEW SESSION MODE")
        
        # Step 1: Fetch instant data (5-10 seconds)
        print(f"\n[1/3] Fetching instant data...")
        
        validation = self.validate_input(game_name, tag_line, region)
        if not validation['valid']:
            raise ValueError(f"Invalid input: {', '.join(validation['errors'])}")
        
        account_data = self.fetch_account_data(game_name, tag_line, region)
        puuid = account_data['puuid']
        
        self.fetch_summoner_data(puuid, region)
        self.fetch_ranked_info(puuid, region)
        
        # Step 2: Fetch ALL match IDs (instant)
        print(f"\n[2/3] Fetching match IDs...")
        all_match_ids = self.fetch_match_history(puuid, region)
        total_matches = len(all_match_ids)
        
        print(f"✓ Found {total_matches} matches")
        
        # Create session ID
        self.session_id = self.session_manager.create_session_id(game_name, tag_line, region)
        
        # Step 3: Progressive match fetching (100-match checkpoints)
        print(f"\n[3/3] Progressive match analysis...")
        
        checkpoint_num = 0
        analyzed_ids = []
        all_matches = []
        
        for i in range(0, total_matches, self.checkpoint_batch_size):
            checkpoint_num += 1
            batch_ids = all_match_ids[i:i + self.checkpoint_batch_size]
            
            print(f"\n--- Checkpoint {checkpoint_num} ---")
            print(f"Fetching matches {i+1} to {min(i+self.checkpoint_batch_size, total_matches)}...")
            
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
            
            print(f"✓ Fetched {len(batch_matches)} matches")
            print(f"Progress: {len(analyzed_ids)}/{total_matches} ({len(analyzed_ids)/total_matches*100:.1f}%)")
            
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
            
            print(f"✓ Checkpoint {checkpoint_num} saved to S3")
            
            # Call checkpoint callback if provided
            if checkpoint_callback:
                checkpoint_callback(checkpoint_num, checkpoint_analytics)
        
        # Mark as complete
        if not remaining_ids:
            self.session_manager.mark_complete(self.session_id)
            print(f"\n✓ All matches analyzed!")
        
        # Store final complete data
        self.data['matches'] = all_matches
        s3_key = self.store_to_s3()
        
        print(f"\n{'='*60}")
        print(f"PROGRESSIVE FETCH COMPLETE!")
        print(f"Session ID: {self.session_id}")
        print(f"Checkpoints: {checkpoint_num}")
        print(f"{'='*60}\n")
        
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
        
        print(f"↻ Resuming from checkpoint {existing_session['matchData']['lastCheckpoint']}")
        
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
        
        print(f"Remaining matches: {len(remaining_ids)}/{total_matches}")
        
        # Continue fetching remaining matches
        all_analyzed_ids = match_data['analyzedMatchIds'].copy()
        
        # Load previously fetched matches from S3
        # (In production, we'd load from S3 raw_data.json)
        # For now, we'll just continue from where we left off
        
        for i in range(0, len(remaining_ids), self.checkpoint_batch_size):
            checkpoint_num += 1
            batch_ids = remaining_ids[i:i + self.checkpoint_batch_size]
            
            print(f"\n--- Checkpoint {checkpoint_num} (Resume) ---")
            print(f"Fetching matches {len(all_analyzed_ids)+1} to {len(all_analyzed_ids)+len(batch_ids)}...")
            
            batch_matches = self.riot_client.get_matches_batch(
                match_ids=batch_ids,
                platform=region,
                batch_size=10,
                parallel=True
            )
            
            all_analyzed_ids.extend(batch_ids)
            still_remaining = remaining_ids[len(all_analyzed_ids) - len(match_data['analyzedMatchIds']):]
            
            print(f"✓ Fetched {len(batch_matches)} matches")
            print(f"Progress: {len(all_analyzed_ids)}/{total_matches} ({len(all_analyzed_ids)/total_matches*100:.1f}%)")
            
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
            print(f"\n✓ Resume complete! All matches analyzed.")
        
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
        print(f"\n⚠️  WARNING: Using legacy fetch_all() method")
        print(f"    Consider using fetch_progressive() for better UX\n")
        
        print(f"\n{'='*60}")
        print(f"FETCHING LEAGUE DATA FOR {game_name}#{tag_line}")
        print(f"{'='*60}\n")
        
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
        
        # Step 6: Fetch match details for ALL matches
        self.fetch_match_details_batch(match_ids, region)
        
        # Step 7: Store to S3
        s3_key = self.store_to_s3()
        
        print(f"\n{'='*60}")
        print(f"DATA FETCH COMPLETE!")
        print(f"Session ID: {self.session_id}")
        print(f"S3 Key: {s3_key}")
        print(f"{'='*60}\n")
        
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
        print(f"Validation error: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': str(e)
            })
        }
    
    except Exception as e:
        print(f"Unexpected error: {e}")
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