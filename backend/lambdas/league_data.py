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


class LeagueDataFetcher:
    """
    Fetches complete League of Legends player data from Riot APIs.
    """
    
    def __init__(self):
        self.riot_client = RiotAPIClient()
        self.session_id = None
        self.data = {}
    
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
    
    def fetch_match_details_batch(self, match_ids: List[str], region: str) -> List[Dict[str, Any]]:
        """
        Fetch match details in batches using MATCH-V5 API.
        
        Args:
            match_ids: List of match IDs
            region: Platform region
        
        Returns:
            List of match detail objects
        """
        print(f"[5/5] Fetching match details (this may take a while)...")
        
        matches = self.riot_client.get_matches_batch(
            match_ids=match_ids,
            platform=region,
            batch_size=10  # Process 10 matches at a time
        )
        
        self.data['matches'] = matches
        print(f"✓ Retrieved {len(matches)} match details")
        
        return matches
    
    def store_to_s3(self) -> str:
        """
        Store collected data to S3.
        
        Returns:
            S3 key where data was stored
        """
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        
        # Add metadata
        self.data['metadata'] = {
            'sessionId': self.session_id,
            'fetchedAt': datetime.utcnow().isoformat(),
            'totalMatches': len(self.data.get('matches', [])),
            'status': 'raw_data_complete'
        }
        
        # Store in S3
        s3_key = f"sessions/{self.session_id}/raw_data.json"
        
        print(f"\nStoring data to S3: {s3_key}")
        upload_to_s3(s3_key, self.data)
        
        print(f"✓ Data stored successfully!")
        return s3_key
    
    def fetch_all(self, game_name: str, tag_line: str, region: str) -> Dict[str, Any]:
        """
        Fetch all player data (orchestration method).
        
        Args:
            game_name: Riot ID game name
            tag_line: Riot ID tag line
            region: Platform region code
        
        Returns:
            Complete data payload with session ID
        """
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