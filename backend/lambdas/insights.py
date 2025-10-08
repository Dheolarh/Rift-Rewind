"""
Lambda Function: insights.py
Purpose: Generate actionable coaching insights using AWS Bedrock Claude 3 Sonnet

Environment Variables Required:
- S3_BUCKET_NAME
- BEDROCK_MODEL_ID
- AWS_REGION

Memory: 256 MB
Timeout: 1 minute
"""

import os
import sys
import json
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path for local imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.aws_clients import get_bedrock_client, download_from_s3, upload_to_s3


class InsightsGenerator:
    """
    Generates actionable coaching insights using Bedrock.
    """
    
    def __init__(self):
        self.bedrock_client = get_bedrock_client()
        self.model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
    
    def download_analytics(self, session_id: str) -> Dict[str, Any]:
        """
        Download analytics data from S3.
        
        Args:
            session_id: Session ID
        
        Returns:
            Analytics data dict
        """
        s3_key = f"sessions/{session_id}/analytics.json"
        print(f"Downloading analytics from S3: {s3_key}")
        
        analytics = download_from_s3(s3_key)
        if not analytics:
            raise ValueError(f"Analytics not found for session: {session_id}")
        
        return analytics
    
    def create_insights_prompt(self, analytics: Dict[str, Any]) -> str:
        """
        Create comprehensive insights prompt for Bedrock.
        
        Args:
            analytics: Analytics data
        
        Returns:
            Formatted prompt string
        """
        # Extract key metrics (with safe defaults)
        total_games = analytics.get('totalGames', 0)
        avg_kda = analytics.get('avgKDA', 0)
        rank = analytics.get('rank', 'UNRANKED')
        win_rate = analytics.get('winRate', 0)
        avg_cs = analytics.get('avgCS', 0)
        vision_score = analytics.get('avgVisionScore', 0)
        top_champions = analytics.get('topChampions', [])[:3]
        avg_deaths = analytics.get('avgDeaths', 0)
        
        # Format top champions list
        champs_list = ', '.join([f"{c.get('name', 'Unknown')} ({c.get('games', 0)} games)" for c in top_champions])
        
        prompt = f"""You are a professional League of Legends coach analyzing a player's Season 15 performance. Provide actionable, specific insights.

**Player Statistics:**
- Total Games: {total_games}
- Average KDA: {avg_kda}
- Current Rank: {rank}
- Win Rate: {win_rate}%
- Average CS/Min: {avg_cs}
- Average Vision Score: {vision_score}
- Average Deaths per Game: {avg_deaths}
- Top 3 Champions: {champs_list if champs_list else 'Not enough data'}

**Task: Generate insights in the following JSON format (respond ONLY with valid JSON):**

{{
  "strengths": [
    "Specific strength #1 with data example",
    "Specific strength #2 with data example",
    "Specific strength #3 with data example"
  ],
  "weaknesses": [
    "Specific weakness #1 with data example",
    "Specific weakness #2 with data example",
    "Specific weakness #3 with data example"
  ],
  "coaching_tips": [
    "Actionable tip #1 - be specific about what to practice",
    "Actionable tip #2 - include how to improve",
    "Actionable tip #3 - prioritize by impact"
  ],
  "play_style": "One sentence describing their playstyle based on data",
  "personality_title": "Creative 3-4 word player title (e.g., 'The Calculated Assassin')"
}}

**Guidelines:**
- Be encouraging but honest
- Use specific numbers from stats
- Reference champion pool and playstyle
- Make coaching tips actionable (not generic)
- Personality title should be creative and match their playstyle
- Keep each point concise (1-2 sentences)
- Use League terminology (CS, vision control, objectives, etc.)

Respond ONLY with valid JSON - no other text."""
        
        return prompt
    
    def call_bedrock(self, prompt: str) -> Dict[str, Any]:
        """
        Call Bedrock to generate insights.
        
        Args:
            prompt: Prompt string
        
        Returns:
            Parsed insights dict
        """
        print(f"Calling Bedrock for insights generation...")
        
        # Prepare request body
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": 0.7,  # Balanced creativity
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Invoke Bedrock
        response = self.bedrock_client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        insights_text = response_body['content'][0]['text']
        
        # Parse JSON from response
        try:
            # Extract JSON if wrapped in markdown code blocks
            if '```json' in insights_text:
                insights_text = insights_text.split('```json')[1].split('```')[0].strip()
            elif '```' in insights_text:
                insights_text = insights_text.split('```')[1].split('```')[0].strip()
            
            insights_data = json.loads(insights_text)
            print(f"✓ Insights generated successfully")
            return insights_data
        
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from Bedrock: {e}")
            print(f"Raw response: {insights_text}")
            # Return fallback structure
            return {
                "strengths": ["Data analysis in progress"],
                "weaknesses": ["More matches needed for accurate analysis"],
                "coaching_tips": ["Keep playing ranked games for better insights"],
                "play_style": "Developing player profile",
                "personality_title": "The Rising Summoner"
            }
    
    def store_insights(self, session_id: str, insights: Dict[str, Any]):
        """
        Store insights in S3.
        
        Args:
            session_id: Session ID
            insights: Generated insights dict
        """
        s3_key = f"sessions/{session_id}/insights.json"
        
        data = {
            'sessionId': session_id,
            'insights': insights,
            'generatedAt': datetime.utcnow().isoformat(),
            'status': 'complete'
        }
        
        print(f"Storing insights to S3: {s3_key}")
        upload_to_s3(s3_key, data)
    
    def generate(self, session_id: str) -> Dict[str, Any]:
        """
        Generate insights for a session.
        
        Args:
            session_id: Session ID
        
        Returns:
            Result dict with insights
        """
        print(f"\n{'='*60}")
        print(f"GENERATING INSIGHTS")
        print(f"Session ID: {session_id}")
        print(f"{'='*60}\n")
        
        # Step 1: Download analytics
        analytics = self.download_analytics(session_id)
        
        # Step 2: Create prompt
        prompt = self.create_insights_prompt(analytics)
        
        # Step 3: Generate insights
        insights = self.call_bedrock(prompt)
        
        # Step 4: Store results
        self.store_insights(session_id, insights)
        
        print(f"\n{'='*60}")
        print(f"INSIGHTS GENERATION COMPLETE!")
        print(f"Strengths: {len(insights.get('strengths', []))}")
        print(f"Weaknesses: {len(insights.get('weaknesses', []))}")
        print(f"Tips: {len(insights.get('coaching_tips', []))}")
        print(f"Title: {insights.get('personality_title', 'N/A')}")
        print(f"{'='*60}\n")
        
        return {
            'sessionId': session_id,
            'insights': insights,
            'status': 'success'
        }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function.
    
    Expected event format:
    {
        "sessionId": "abc123xyz"
    }
    
    Returns:
    {
        "sessionId": "abc123xyz",
        "insights": { ... },
        "status": "success"
    }
    """
    try:
        # Extract parameters
        session_id = event.get('sessionId')
        
        # Validate required parameters
        if not session_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameter: sessionId'
                })
            }
        
        # Generate insights
        generator = InsightsGenerator()
        result = generator.generate(session_id)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    
    except Exception as e:
        print(f"Error generating insights: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }


# For local testing
if __name__ == "__main__":
    # Test insights generation
    test_event = {
        'sessionId': 'test-session-123'
    }
    
    result = lambda_handler(test_event, None)
    print(f"\nResult: {json.dumps(json.loads(result['body']), indent=2)}")