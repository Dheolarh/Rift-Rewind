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
        
        analytics_str = download_from_s3(s3_key)
        if not analytics_str:
            raise ValueError(f"Analytics not found for session: {session_id}")
        
        # Parse JSON string to dict
        analytics = json.loads(analytics_str)
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
- Average Vision Score: {vision_score:.1f} per game (Excellent: 50+, Good: 30-50, Poor: <25)
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
6. **DIVERSE WEAKNESS ANALYSIS** - Don't focus only on vision! Include:
   - Death rate patterns (aggressive positioning, overextension)
   - Champion pool issues (one-trick limitations, lack of diversity)
   - Farm/economy problems (if data available)
   - Team fight patterns (KDA vs death rate conflicts)
   - Consistency issues (win rate vs games played)

**Task: Generate insights in the following JSON format (respond ONLY with valid JSON):**

{{
  "strengths": [
    "Specific strength with exact numbers (2-3 strengths, only if truly deserved)"
  ],
  "weaknesses": [
    "Critical weakness - NOT just vision! Focus on death patterns, positioning, champion diversity, or other meaningful metrics",
    "Second weakness from a DIFFERENT category than the first",
    "Third weakness if applicable - be diverse in analysis"
  ],
  "coaching_tips": [
    "Highest priority tip addressing biggest weakness",
    "Second priority improvement with practice method",
    "Third tip for long-term growth"
  ],
  "play_style": "One sentence HONEST description of their actual playstyle based on data patterns",
  "personality_title": "Creative 3-4 word title based on CHAMPION STATS and playstyle (e.g., 'The Reckless Yasuo Main', 'The Cautious Support', 'The Solo Carry Hunter', 'The Team Fight Specialist')"
}}

**PERSONALITY TITLE RULES:**
- Base it on their TOP CHAMPION and playstyle patterns, NOT vision score
- Examples: "The {{adjective}} {{champion/role}} {{playstyle}}"
  - "The Fearless Darius Diver"
  - "The Calculated Mage Sniper"
  - "The Overeager Assassin"
  - "The Patient Farm King"
  - "The One-Trick Wonder" (if champion pool is tiny)
- Make it reflect their ACTUAL performance patterns

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
    
    def call_bedrock(self, prompt: str, ai_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call Bedrock to generate insights using Meta Llama with retries and guaranteed fallback.
        
        Args:
            prompt: Prompt string
            ai_context: Context data for generating data-driven fallbacks
        
        Returns:
            Parsed insights dict (ALWAYS returns valid insights)
        """
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Calling Bedrock for insights generation (attempt {attempt + 1}/{max_retries})...")
                
                # Meta Llama 3.1 uses chat template format
                system_prompt = """You are a professional League of Legends coach analyzing gameplay with brutal honesty. 
Focus on ACTUAL WEAKNESSES from the data - don't default to vision criticism unless it's truly poor (avg vision score < 25).
A vision score of 40+ is GOOD - don't roast it! Instead focus on deaths, KDA, champion pool, consistency, positioning.
Be data-driven and specific. If someone has good stats in an area, acknowledge it and find REAL weaknesses elsewhere.
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
                
                # Log the raw AI response for debugging
                logger.info(f"==> Bedrock raw response (attempt {attempt + 1}):")
                logger.info(f"    Full response length: {len(insights_text)} chars")
                logger.info(f"    First 300 chars: {insights_text[:300]}")
                
                # Extract JSON if wrapped in markdown code blocks
                if '```json' in insights_text:
                    insights_text = insights_text.split('```json')[1].split('```')[0].strip()
                elif '```' in insights_text:
                    insights_text = insights_text.split('```')[1].split('```')[0].strip()
                
                insights_data = json.loads(insights_text)
                
                # Log what we got from parsing
                logger.info(f"==> Parsed JSON successfully")
                logger.info(f"    Fields present: {list(insights_data.keys())}")
                logger.info(f"    Strengths count: {len(insights_data.get('strengths', []))}")
                logger.info(f"    Weaknesses count: {len(insights_data.get('weaknesses', []))}")
                logger.info(f"    Tips count: {len(insights_data.get('coaching_tips', []))}")
                
                # Validate that all required fields exist
                required_fields = ['strengths', 'weaknesses', 'coaching_tips', 'play_style', 'personality_title']
                if all(field in insights_data for field in required_fields):
                    # Ensure arrays have at least one item
                    if (insights_data['strengths'] and 
                        insights_data['weaknesses'] and 
                        insights_data['coaching_tips']):
                        logger.info("==> AI insights generated successfully with all required fields")
                        return insights_data
                    else:
                        logger.warning(f"==> AI returned empty arrays, retrying (attempt {attempt + 1})")
                        logger.warning(f"    Strengths: {len(insights_data.get('strengths', []))}, Weaknesses: {len(insights_data.get('weaknesses', []))}, Tips: {len(insights_data.get('coaching_tips', []))}")
                else:
                    missing_fields = [f for f in required_fields if f not in insights_data]
                    logger.warning(f"==> AI response missing fields: {missing_fields}, retrying (attempt {attempt + 1})")
                
            except json.JSONDecodeError as e:
                logger.error(f"==> JSON parsing error on attempt {attempt + 1}: {e}")
                logger.error(f"    Raw AI response (first 200 chars): {insights_text[:200]}")
                if attempt < max_retries - 1:
                    continue
            except Exception as e:
                logger.error(f"==> Bedrock API error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    continue
        
        # All retries failed - generate data-driven fallback
        logger.warning("==> All Bedrock attempts failed, using data-driven fallback insights")
        return self._generate_fallback_insights(ai_context)
    
    def _generate_fallback_insights(self, ai_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate data-driven fallback insights when AI fails.
        Uses actual player stats to create meaningful insights.
        
        Args:
            ai_context: Player statistics and metrics
        
        Returns:
            Valid insights dict with data-driven content
        """
        logger.info(" Generating data-driven fallback insights...")
        
        # Extract key metrics
        avg_kda = ai_context.get('avgKDA', 0)
        avg_deaths = ai_context.get('avgDeaths', 0)
        win_rate = ai_context.get('winRate', 0)
        vision_score = ai_context.get('avgVisionScore', 0)
        champ_pool = ai_context.get('championPoolSize', 0)
        top_champs = ai_context.get('topChampions', [])
        perf = ai_context.get('performanceMetrics', {})
        
        # Determine strengths based on data
        strengths = []
        if avg_kda > 3.0:
            strengths.append(f"Excellent KDA ratio of {avg_kda:.1f} shows strong mechanical skill")
        elif avg_kda > 2.0:
            strengths.append(f"Solid {avg_kda:.1f} KDA demonstrates consistent gameplay")
        
        if win_rate >= 55:
            strengths.append(f"Strong {win_rate}% win rate reflects good decision-making")
        elif win_rate >= 50:
            strengths.append("Maintaining positive win rate shows competitive performance")
        
        if vision_score > 40:
            strengths.append(f"Good vision control with {vision_score:.0f} average vision score")
        
        if not strengths:
            strengths.append("Active ranked participation boosts skill development")
            strengths.append("Consistent play shows dedication to improvement")
        
        # Determine weaknesses based on data
        weaknesses = []
        if avg_deaths > 7:
            weaknesses.append(f"High death rate of {avg_deaths:.1f} per game suggests aggressive positioning")
        elif avg_deaths > 5.5:
            weaknesses.append("Death count could be reduced with better map awareness")
        
        if champ_pool < 5:
            weaknesses.append(f"Limited champion pool of {champ_pool} champions may hurt flexibility")
        elif champ_pool > 20:
            weaknesses.append("Very diverse champion pool may prevent mastery of specific picks")
        
        if vision_score < 25:
            weaknesses.append(f"Vision score of {vision_score:.0f} needs improvement for better map control")
        
        if win_rate < 45:
            weaknesses.append("Win rate indicates need for strategic adjustments")
        
        if not weaknesses:
            weaknesses.append("Focus on consistency to climb higher")
            weaknesses.append("Small optimizations in positioning can increase win rate")
        
        # Generate coaching tips
        coaching_tips = []
        if avg_deaths > 6:
            coaching_tips.append("Focus on positioning - ask 'where are my teammates?' before engaging")
        if vision_score < 30:
            coaching_tips.append("Buy 2+ control wards per back and place them in river/jungle")
        if champ_pool < 5:
            coaching_tips.append("Master 3-5 champions deeply rather than playing everything")
        
        if not coaching_tips:
            coaching_tips.append("Review your deaths after each game to identify patterns")
            coaching_tips.append("Focus on objectives over kills for consistent wins")
            coaching_tips.append("Practice one champion extensively to learn matchups")
        
        # Generate play style description
        if avg_deaths > 7:
            play_style = "Aggressive player who takes risks for high-reward plays"
        elif avg_deaths < 4:
            play_style = "Cautious player who prioritizes survival and consistent performance"
        elif avg_kda > 3:
            play_style = "Skilled player who balances aggression with smart decision-making"
        else:
            play_style = "Developing player working to refine their strategic approach"
        
        # Generate personality title based on top champion
        if top_champs and len(top_champs) > 0:
            top_champ = top_champs[0].get('name', 'Champion')
            if avg_deaths > 7:
                personality_title = f"The Fearless {top_champ} Player"
            elif avg_kda > 3:
                personality_title = f"The Skilled {top_champ} Main"
            else:
                personality_title = f"The Dedicated {top_champ} Enthusiast"
        else:
            personality_title = "The Determined Competitor"
        
        fallback_result = {
            "strengths": strengths[:3],  # Limit to 3
            "weaknesses": weaknesses[:3],  # Limit to 3
            "coaching_tips": coaching_tips[:3],  # Limit to 3
            "play_style": play_style,
            "personality_title": personality_title
        }
        
        # Log the fallback that was generated
        logger.info(f"==> Generated fallback insights:")
        logger.info(f"    Strengths: {fallback_result['strengths']}")
        logger.info(f"    Weaknesses: {fallback_result['weaknesses']}")
        logger.info(f"    Title: {fallback_result['personality_title']}")
        
        return fallback_result
    
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
            Result dict with insights (ALWAYS succeeds with valid insights)
        """
        logger.info(f"Generating insights for session: {session_id}")
        
        try:
            analytics = self.download_analytics(session_id)
            
            # Extract aiContext for fallback generation if needed
            slide_data = analytics.get('slide10_11_analysis', {})
            ai_context = slide_data.get('aiContext', {})
            
            prompt = self.create_insights_prompt(analytics)
            insights = self.call_bedrock(prompt, ai_context)  # Pass ai_context for fallback
            
            # Validate insights structure
            if not insights.get('strengths') or not insights.get('weaknesses'):
                logger.warning("  AI returned incomplete insights, using fallback")
                insights = self._generate_fallback_insights(ai_context)
            
            self.store_insights(session_id, insights)
            
            logger.info(f" Insights generation complete - Strengths: {len(insights.get('strengths', []))}, "
                       f"Weaknesses: {len(insights.get('weaknesses', []))}, "
                       f"Tips: {len(insights.get('coaching_tips', []))}")
            
            return {
                'sessionId': session_id,
                'insights': insights,
                'status': 'success'
            }
        except Exception as e:
            # Log full stack trace for debugging (helps identify NameError / template issues)
            logger.exception("Critical error in insights generation")
            # Last resort fallback
            fallback_insights = {
                "strengths": ["Active ranked participation", "Commitment to competitive play"],
                "weaknesses": ["Continue playing for deeper analysis", "Focus on consistency"],
                "coaching_tips": ["Review replays after losses", "Master 3-5 champions", "Prioritize objectives"],
                "play_style": "Developing competitive player",
                "personality_title": "The Rising Competitor"
            }
            
            try:
                self.store_insights(session_id, fallback_insights)
            except:
                pass  # If S3 fails, at least return insights
            
            return {
                'sessionId': session_id,
                'insights': fallback_insights,
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