"""
Lambda Function: orchestrator.py
Purpose: Coordinate all Lambda functions in the Rift Rewind pipeline

Environment Variables Required:
- AWS_REGION

Memory: 128 MB
Timeout: 10 seconds
"""

import os
import json
import boto3
from typing import Dict, Any


class RiftRewindOrchestrator:
    """
    Orchestrates the complete Rift Rewind data processing pipeline.
    """
    
    def __init__(self):
        self.lambda_client = boto3.client('lambda', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
        self.session_id = None
    
    def invoke_league_data(self, game_name: str, tag_line: str, region: str) -> Dict[str, Any]:
        """
        Invoke league_data Lambda to fetch player data.
        
        Args:
            game_name: Riot ID game name
            tag_line: Riot ID tag line
            region: Region code
        
        Returns:
            Response from league_data Lambda
        """
        print(f"[1/4] Invoking league_data Lambda...")
        
        payload = {
            'gameName': game_name,
            'tagLine': tag_line,
            'region': region
        }
        
        response = self.lambda_client.invoke(
            FunctionName='rift-rewind-league-data',  # Lambda function name
            InvocationType='RequestResponse',  # Synchronous
            Payload=json.dumps(payload)
        )
        
        result = json.loads(response['Payload'].read())
        
        if result.get('statusCode') != 200:
            raise Exception(f"league_data failed: {result.get('body')}")
        
        body = json.loads(result['body'])
        self.session_id = body.get('sessionId')
        
        print(f"✓ league_data complete - Session ID: {self.session_id}")
        return body
    
    def invoke_analytics(self) -> Dict[str, Any]:
        """
        Invoke analytics Lambda to calculate statistics.
        
        Returns:
            Response from analytics Lambda
        """
        print(f"[2/4] Invoking analytics Lambda...")
        
        payload = {
            'sessionId': self.session_id
        }
        
        response = self.lambda_client.invoke(
            FunctionName='rift-rewind-analytics',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        result = json.loads(response['Payload'].read())
        
        if result.get('statusCode') != 200:
            raise Exception(f"analytics failed: {result.get('body')}")
        
        print(f"✓ analytics complete")
        return json.loads(result['body'])
    
    def invoke_humor_parallel(self) -> Dict[str, Any]:
        """
        Invoke humor_context Lambda for all 15 slides in parallel.
        
        Returns:
            Summary of humor generation
        """
        print(f"[3/4] Invoking humor_context Lambda (15 slides in parallel)...")
        
        # Slides that need humor (excluding slide 1)
        slides_with_humor = list(range(2, 16))  # Slides 2-15
        
        # Invoke all slides asynchronously
        for slide_num in slides_with_humor:
            payload = {
                'sessionId': self.session_id,
                'slideNumber': slide_num
            }
            
            self.lambda_client.invoke(
                FunctionName='rift-rewind-humor-context',
                InvocationType='Event',  # Asynchronous
                Payload=json.dumps(payload)
            )
        
        print(f"✓ humor_context invoked for {len(slides_with_humor)} slides (async)")
        return {
            'slidesProcessing': len(slides_with_humor),
            'status': 'processing'
        }
    
    def invoke_insights(self) -> Dict[str, Any]:
        """
        Invoke insights Lambda to generate coaching insights.
        
        Returns:
            Response from insights Lambda
        """
        print(f"[4/4] Invoking insights Lambda...")
        
        payload = {
            'sessionId': self.session_id
        }
        
        response = self.lambda_client.invoke(
            FunctionName='rift-rewind-insights',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        result = json.loads(response['Payload'].read())
        
        if result.get('statusCode') != 200:
            raise Exception(f"insights failed: {result.get('body')}")
        
        print(f"✓ insights complete")
        return json.loads(result['body'])
    
    def orchestrate(self, game_name: str, tag_line: str, region: str) -> Dict[str, Any]:
        """
        Orchestrate the complete pipeline.
        
        Args:
            game_name: Riot ID game name
            tag_line: Riot ID tag line
            region: Region code
        
        Returns:
            Orchestration result with session ID
        """
        print(f"\n{'='*60}")
        print(f"RIFT REWIND ORCHESTRATION START")
        print(f"Player: {game_name}#{tag_line}")
        print(f"Region: {region}")
        print(f"{'='*60}\n")
        
        try:
            # Step 1: Fetch league data
            league_result = self.invoke_league_data(game_name, tag_line, region)
            
            # Step 2: Calculate analytics
            analytics_result = self.invoke_analytics()
            
            # Step 3: Generate humor (parallel)
            humor_result = self.invoke_humor_parallel()
            
            # Step 4: Generate insights
            insights_result = self.invoke_insights()
            
            print(f"\n{'='*60}")
            print(f"ORCHESTRATION COMPLETE!")
            print(f"Session ID: {self.session_id}")
            print(f"Status: All Lambdas invoked successfully")
            print(f"{'='*60}\n")
            
            return {
                'sessionId': self.session_id,
                'status': 'processing',  # Humor is still async
                'stages': {
                    'leagueData': 'complete',
                    'analytics': 'complete',
                    'humor': 'processing',  # Async
                    'insights': 'complete'
                },
                'matchCount': league_result.get('matchCount', 0)
            }
        
        except Exception as e:
            print(f"Orchestration failed: {e}")
            raise


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
        "status": "processing",
        "stages": { ... }
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
        
        # Orchestrate pipeline
        orchestrator = RiftRewindOrchestrator()
        result = orchestrator.orchestrate(game_name, tag_line, region)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    
    except Exception as e:
        print(f"Orchestration error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }


# For local testing (mock Lambda invocations)
if __name__ == "__main__":
    print("Note: Local testing requires actual Lambda functions deployed")
    print("For local testing, run individual Lambda functions separately\n")
    
    test_event = {
        'gameName': 'Hide on bush',
        'tagLine': 'KR1',
        'region': 'kr'
    }
    
    # This will fail locally unless Lambdas are deployed
    # result = lambda_handler(test_event, None)
    # print(f"\nResult: {json.dumps(json.loads(result['body']), indent=2)}")
    
    print("Orchestrator code is ready for AWS deployment!")