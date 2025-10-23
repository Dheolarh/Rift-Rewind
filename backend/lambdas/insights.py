"""
Lambda Function: insights.py
Purpose: Generate insights using AWS Bedrock Claude 3 Sonnet

Environment Variables Required:
- S3_BUCKET_NAME
- BEDROCK_MODEL_ID

Memory: 256 MB
Timeout: 1 minute
"""

import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from services.aws_clients import get_bedrock_client, download_from_s3, upload_to_s3


class InsightsGenerator:
    """
    Generates actionable coaching insights using Bedrock.
    """
    
    def __init__(self):
        self.bedrock_client = get_bedrock_client()
        # Use inference profile ARN for Llama models (required for cross-region inference)
        # OR use Claude if Llama inference profile not available
        self.model_id = os.environ.get(
            'BEDROCK_MODEL_ID',
            'us.meta.llama3-1-70b-instruct-v1:0'  # Cross-region inference profile
        )
    
    def download_analytics(self, session_id: str) -> Dict[str, Any]:
        """
        Download analytics data from S3.
        
        Args:
            session_id: Session ID
        
        Returns:
            Analytics data dict
        """
        s3_key = f"sessions/{session_id}/analytics.json"
        logger.info(f"Downloading analytics from S3: {s3_key}")
        
        analytics = download_from_s3(s3_key)
        if not analytics:
            raise ValueError(f"Analytics not found for session: {session_id}")
        
        return analytics
    
    def create_insights_prompt(self, analytics: Dict[str, Any]) -> str:
        """
        Create comprehensive insights prompt for Bedrock.
        
        Args:
            analytics: Analytics data with aiContext from detect_strengths_weaknesses
        
        Returns:
            Formatted prompt string
        """
        # Extract slide10_11_analysis data
        slide_data = analytics.get('slide10_11_analysis', {})
        ai_context = slide_data.get('aiContext', {})
        perf_metrics = ai_context.get('performanceMetrics', {})
        
        # Extract comprehensive stats
        total_games = ai_context.get('totalGames', 0)
        avg_kda = ai_context.get('avgKDA', 0)
        avg_kills = ai_context.get('avgKills', 0)
        avg_deaths = ai_context.get('avgDeaths', 0)
        avg_assists = ai_context.get('avgAssists', 0)
        
        win_rate = ai_context.get('winRate', 0)
        vision_score = ai_context.get('avgVisionScore', 0)
        avg_wards = ai_context.get('avgWardsPlaced', 0)
        avg_control = ai_context.get('avgControlWards', 0)
        
        current_tier = ai_context.get('currentTier', 'UNRANKED')
        current_div = ai_context.get('currentDivision', '')
        rank_display = f"{current_tier} {current_div}" if current_div else current_tier
        
        top_champions = ai_context.get('topChampions', [])[:3]
        champ_pool_size = ai_context.get('championPoolSize', 0)
        
        # Format top champions list with detailed stats
        champs_list = ', '.join([
            f"{c.get('name', 'Unknown')} ({c.get('games', 0)} games, {c.get('winRate', 0):.1f}% WR, {c.get('kda', 0):.2f} KDA)" 
            for c in top_champions
        ]) if top_champions else 'Not enough data'
        
        prompt = f"""You are a professional League of Legends coach analyzing a player's Season 15 performance. Provide brutally honest, data-driven insights that identify REAL strengths and areas needing improvement.

**Player Statistics:**
- Total Games Played: {total_games}
- Current Rank: {rank_display}
- Win Rate: {win_rate}%

**Combat Performance:**
- Average KDA: {avg_kda:.2f}
- Average K/D/A per game: {avg_kills:.1f} / {avg_deaths:.1f} / {avg_assists:.1f}
- Death Control: {perf_metrics.get('death_control', 'unknown')}
- KDA Performance: {perf_metrics.get('kda_performance', 'unknown')}

**Vision & Map Control:**
- Average Vision Score: {vision_score:.1f} per game
- Average Wards Placed: {avg_wards:.1f} per game
- Average Control Wards: {avg_control:.1f} per game
- Vision Performance: {perf_metrics.get('vision_performance', 'unknown')}
- Ward Placement: {perf_metrics.get('ward_placement', 'unknown')}

**Champion Pool:**
- Pool Size: {champ_pool_size} champions played
- Top 3 Champions: {champs_list}

**CRITICAL ANALYSIS GUIDELINES:**
1. **Identify CONFLICTING patterns** - e.g., high kills but low vision, good KDA but low win rate
2. **Call out BELOW AVERAGE metrics** - compare to typical {rank_display} players
3. **Detect POOR PERFORMANCE indicators** - high deaths, low vision, inconsistent champion picks
4. **Be SPECIFIC with numbers** - "Your 7.2 deaths per game is 40% higher than average for {rank_display}"
5. **Highlight PLAYSTYLE MISMATCHES** - e.g., playing assassins but dying too much

**Task: Generate insights in the following JSON format (respond ONLY with valid JSON):**

{{
  "strengths": [
    "Specific strength with exact numbers (max 3-4 strengths, only if truly deserved)",
    "Another data-backed strength",
    "Third strength if applicable"
  ],
  "weaknesses": [
    "Critical weakness with comparison to rank average (at least 3-4 weaknesses)",
    "Another weakness explaining WHY it's hurting performance",
    "Third weakness with actionable context",
    "Fourth weakness if multiple issues exist"
  ],
  "coaching_tips": [
    "Highest priority tip addressing biggest weakness",
    "Second priority improvement with practice method",
    "Third tip for long-term growth"
  ],
  "play_style": "One sentence HONEST description of their actual playstyle based on data patterns",
  "personality_title": "Creative 3-4 word title reflecting their ACTUAL performance (e.g., 'The Reckless Brawler', 'The Vision-Blind Assassin')"
}}

**IMPORTANT:**
- If KDA < 2.0, it's a major weakness
- If deaths > 6 per game, they're dying too much
- If vision score < 20, they're not warding enough
- If win rate < 48%, something fundamental needs work
- Don't sugarcoat - be direct but constructive
- Strengths must be backed by above-average performance
- Weaknesses should identify root causes, not just symptoms
- Use professional language - NO emojis or excessive punctuation
- Keep tone analytical and coaching-focused, not casual

Respond ONLY with valid JSON - no other text."""
        
        return prompt
    
    def call_bedrock(self, prompt: str) -> Dict[str, Any]:
        """
        Call Bedrock to generate insights using Meta Llama.
        
        Args:
            prompt: Prompt string
        
        Returns:
            Parsed insights dict
        """
        logger.info("Calling Bedrock for insights generation...")
        
        # Meta Llama 3.1 uses chat template format
        system_prompt = """You are a no-bullshit League of Legends coach analyzing gameplay. 
Call out bad plays. If someone's inting, say it. If their vision score is trash, roast it.
Be brutally honest with data. Don't sugarcoat failures. Constructive but savage.
Respond ONLY with valid JSON - no other text."""
        
        llama_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        
        request_body = {
            "prompt": llama_prompt,
            "max_gen_len": 1500,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        # Invoke Bedrock
        response = self.bedrock_client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        insights_text = response_body.get('generation', '').strip()
        
        try:
            # Extract JSON if wrapped in markdown code blocks
            if '```json' in insights_text:
                insights_text = insights_text.split('```json')[1].split('```')[0].strip()
            elif '```' in insights_text:
                insights_text = insights_text.split('```')[1].split('```')[0].strip()
            
            insights_data = json.loads(insights_text)
            logger.info("Insights generated successfully")
            return insights_data
        
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from Bedrock: {e}")
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
        
        logger.info(f"Storing insights to S3: {s3_key}")
        upload_to_s3(s3_key, data)
    
    def generate(self, session_id: str) -> Dict[str, Any]:
        """
        Generate insights for a session.
        
        Args:
            session_id: Session ID
        
        Returns:
            Result dict with insights
        """
        logger.info(f"Generating insights for session: {session_id}")
        
        analytics = self.download_analytics(session_id)
        prompt = self.create_insights_prompt(analytics)
        insights = self.call_bedrock(prompt)
        self.store_insights(session_id, insights)
        
        logger.info(f"Insights generation complete - Strengths: {len(insights.get('strengths', []))}, "
                   f"Weaknesses: {len(insights.get('weaknesses', []))}, "
                   f"Tips: {len(insights.get('coaching_tips', []))}")
        
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