"""
Lambda Function: humor_context.py
Purpose: Generate AI humor for each slide using AWS Bedrock Claude 3 Sonnet

Environment Variables Required:
- S3_BUCKET_NAME
- BEDROCK_MODEL_ID

Memory: 256 MB
Timeout: 30 seconds
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from services.aws_clients import get_bedrock_client, download_from_s3, upload_to_s3

SLIDE_PROMPTS = {
    1: None,
    
    2: """You're roasting a player's gaming habits.

Stats:
- Total Games: {totalGames}
- Total Hours: {totalHours} hours
- Total Minutes: {totalMinutes} minutes
- Average Game Length: {avgGameLength} minutes

Write ONE savage but funny hilarious sentence (max 30 words) roasting their time investment. Use the EXACT numbers from the stats. NO EMOJIS.

Examples:
"{totalMinutes} minutes of play?! if you took up knitting, you might actually create something useful in that time. Ever heard of a thing called a job?"
"{totalGames} games? Your poor keyboard deserves hazard pay at this point!"
"Spent {totalHours} hours this year. The grass outside filed a missing persons report!"


Max 30 words. Be SAVAGE but hilarious. Use actual stats. NO EMOJIS:""",
    
    3: """You're roasting a player's champion choice.

Their champions:
{championsList}

Write ONE savage sentence (max 30 words) roasting their champion pool. Use ACTUAL champion names and stats. NO EMOJIS.

Examples:
"Yasuo main with 142 games at 45% winrate? The 0/10 powerspike isn't a meme, it's your lifestyle!"
"84 games on Yuumi? That's not playing League, that's watching Netflix with extra steps!"
"Master Yi one-trick with 38% winrate? Right-click harder, surely that'll work eventually!"

Max 30 words. ROAST them using real champion names and stats. NO EMOJIS:""",
    
    4: """You're commenting on someone's best match performance.

Match stats:
- Result: {win}
- KDA: {kills}/{deaths}/{assists}
- Champion: {championName}
- Duration: {gameDuration} minutes

Write ONE savage but funny sentence (max 30 words) about this match. Use EXACT stats. NO EMOJIS.

Examples:
"18/2/12 {championName} game? Okay smurf, we see you! The enemy team probably FF'd at 15!"
"3/9/5? Well... you tried. That's what participation trophies are for, right?"
"{kills}/{deaths}/{assists} on {championName}? That KDA is definitely... a set of numbers that happened!"

Max 30 words. Roast their performance using actual stats. NO EMOJIS:""",
    
    5: """You're roasting someone's KDA stats.

Stats:
- Average Kills: {avgKills}
- Average Deaths: {avgDeaths}
- Average Assists: {avgAssists}
- KDA Ratio: {kdaRatio}

Write ONE savage sentence (max 30 words) about their KDA. Use EXACT numbers. NO EMOJIS.

Examples:
"{kdaRatio} KDA with {avgDeaths} average deaths? You're not running it down, just speedwalking to the fountain!"
"7.2 deaths per game? The grey screen sees you more than your teammates do!"
"That {kdaRatio} KDA screams 'I play for the team!' Translation: professional feeder!"

Max 30 words. Be SAVAGE with the actual stats. NO EMOJIS:""",
    
    6: """You're roasting someone's ranked journey.

Ranked stats:
- Current Rank: {currentRank}
- LP: {leaguePoints}
- Win Rate: {winRate}%
- Total Games: {totalGames}

Write ONE savage sentence (max 30 words) about their rank. Use EXACT rank and stats. NO EMOJIS.

Examples (ranked):
"{currentRank} with {winRate}% winrate after {totalGames} games? Hardstuck isn't a rank, it's a lifestyle!"
"Gold 2? So close to Platinum yet so far. The climb is real! Or... is it?"
"Silver with 200 games played? Elo hell doesn't exist, it's a skill issue!"

Examples (unranked):
"Unranked after all those games? Normals warrior protecting that mental!"

Max 30 words. Use actual rank and stats. NO EMOJIS:""",
    
    7: """You're roasting someone's vision score.

Stats:
- Avg Vision Score: {avgVisionScore}
- Wards Placed: {avgWardsPlaced}

Write ONE savage sentence (max 30 words) about their warding. Use EXACT numbers.

Examples:
"Vision score {avgVisionScore}? The minimap must be decorative for you! Have you heard of Control Wards? �️"
"{avgWardsPlaced} wards per game? So generous! That's almost one every 5 minutes! 🔍"
"Average {avgVisionScore} vision? The fog of war is your best friend apparently! Buy wards! 🎯"

Max 30 words. Roast the actual vision stats:""",
    
    8: """You're roasting champion pool diversity.

Stats:
- Unique Champions: {uniqueChampions}
- Total Games: {totalGames}

Write ONE savage sentence (max 30 words) using EXACT numbers. NO EMOJIS.

Examples:
"Played {uniqueChampions} different champions in {totalGames} games? That's not versatility, that's a full-blown identity crisis!"
"One-trick with {uniqueChampions} champions? Master of none! Jack of... well, nothing really!"
"{uniqueChampions} champions means you're equally bad at all of them! Congrats on the consistency!"

Max 30 words. Use actual numbers. NO EMOJIS:""",
    
    9: """You're commenting on duo queue habits.

Stats:
- Partner: {partnerName}
- Games Together: {gamesTogether}
- Win Rate: {duoWinRate}%

Write ONE savage sentence (max 30 words) using actual stats. NO EMOJIS.

Examples (with duo):
"{gamesTogether} games with {partnerName} at {duoWinRate}% winrate? Either perfect synergy or they're carrying you. Probably the latter!"
"Your duo carried you {gamesTogether} games. We both know it. Admit it!"

Examples (solo):
"No duo partner? Can't find anyone willing to suffer through your gameplay? Understandable!"

Max 30 words. Roast using real stats. NO EMOJIS:""",
    
    10: """You're giving a backhanded compliment about their strengths.

Top Strength: {strengths}

Write ONE savage sentence (max 30 words) that sounds like praise but is actually a roast. NO EMOJIS.

Examples:
"Great at not dying in teamfights! Now if only you could contribute kills or assists while hiding!"
"Excellent CS! Too bad this isn't Farming Simulator. Kills win games, not creeps!"
"Highest damage dealer! Turns out hitting minions all game does that! Who knew?"

Max 30 words. Compliment that's secretly an insult. NO EMOJIS:""",
    
    11: """You're pointing out a weakness with 'helpful' advice.

Top Weakness: {weaknesses}

Write ONE savage sentence (max 30 words) that sounds helpful but is actually brutal. NO EMOJIS.

Examples:
"Your CS per minute needs work. Minions don't last-hit themselves! Maybe watch a YouTube tutorial? Or three?"
"Map awareness: 2/10. Good news: vision is free! Bad news: you still won't look at it!"
"Positioning in teamfights? Flash is for escaping danger, not running into 1v5s! Just a tip!"

Max 30 words. Savage advice disguised as help. NO EMOJIS:""",
    
    12: """You're commenting on player progress over the year.

Stats:
- Total Games: {totalGames}
- Current KDA: {kdaRatio}

Write ONE savage sentence (max 30 words) about their journey using actual numbers. NO EMOJIS.

Examples (with improvement):
"KDA went from 1.8 to {kdaRatio}? That's progress! Only took {totalGames} games to figure out dying is bad!"
"Your winrate improved 5%! At this rate you'll hit Challenger in 2043! Keep grinding!"

Examples (first season):
"Welcome to League of Legends! {totalGames} games in and you've discovered true pain! Enjoy your stay!"

Max 30 words. Progress roast with real stats. NO EMOJIS:""",
    
    13: """You're roasting their achievements (or lack thereof).

Achievements: {achievements}

Write ONE savage sentence (max 30 words). NO EMOJIS.

Examples (with achievements):
"ONE pentakill all year? Congrats! The enemy team's 'stand completely still' strategy finally paid off!"
"Triple kill! Not a quadra, not a penta, just... triple. Baby steps!"

Examples (no achievements):
"No pentakills all year? There's always next season! Or the one after. Or never. Probably never!"
"Zero achievements? At least you showed up! Participation trophy incoming!"

Max 30 words. Achievement roast. NO EMOJIS:""",
    
    14: """You're commenting on their rank percentile.

Stats:
- Rank: {currentRank}
- Percentile: Top {percentile}%

Write ONE savage sentence (max 30 words) using EXACT percentile. NO EMOJIS.

Examples:
"Top {percentile}%? So you're better than {percentile}% of players! That's... technically above average! Congrats!"
"Top 30%? Average with extra steps! But hey, better than the bottom 70%! Silver linings!"
"Challenger - Top 0.01%?! Grass filed a missing persons report for you months ago!"
"Bronze - Bottom 15%? Hey, someone has to be down there! Thanks for your service!"

Max 30 words. Use actual percentile. NO EMOJIS:""",
    
    15: """You're writing a final season wrap-up roast.

Stats:
- Total Games: {totalGames}
- Final Rank: {currentRank}
- Top Champion: {topChampion}

Write ONE memorable closing line (max 30 words) using actual stats. Make it savage but funny. NO EMOJIS.

Examples:
"{totalGames} games playing {topChampion} to end in {currentRank}. What a journey! Same addiction next year? See you soon!"
"Another year, another {totalGames} games of pain, glory, and questionable decisions. Can't wait for next season's suffering!"
"{currentRank} after all that grinding? Well... there's always next year! Maybe touch some grass first though?"

Max 30 words. Epic savage farewell using real stats. NO EMOJIS:""",
}


class HumorGenerator:
    """
    Generates AI humor for Rift Rewind slides using Bedrock.
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
        
        analytics_str = download_from_s3(s3_key)
        if not analytics_str:
            raise ValueError(f"Analytics not found for session: {session_id}")
        
        # Parse JSON string to dict
        analytics = json.loads(analytics_str) if isinstance(analytics_str, str) else analytics_str
        
        return analytics
    
    def create_prompt(self, slide_number: int, analytics: Dict[str, Any]) -> Optional[str]:
        """
        Create slide-specific prompt for Bedrock.
        
        Args:
            slide_number: Slide number (1-15)
            analytics: Analytics data
        
        Returns:
            Formatted prompt string or None if no humor needed
        """
        if slide_number not in SLIDE_PROMPTS or SLIDE_PROMPTS[slide_number] is None:
            return None
        
        template = SLIDE_PROMPTS[slide_number]
        
        # Map analytics to template variables for each slide
        template_data = {}
        
        try:
            if slide_number == 2:  # Time Spent
                data = analytics.get('slide2_timeSpent', {})
                template_data = {
                    'totalGames': data.get('totalGames', 0),
                    'totalHours': data.get('totalHours', 0),
                    'avgGameLength': data.get('avgGameLength', 0)
                }
            
            elif slide_number == 3:  # Champions
                champions = analytics.get('slide3_favoriteChampions', [])
                champ_list = '\n'.join([
                    f"- {c['name']}: {c['games']} games, {c['winRate']}% WR, {c['kda']} KDA"
                    for c in champions[:3]
                ]) if champions else "No champions played"
                template_data = {'championsList': champ_list}
            
            elif slide_number == 4:  # Best Match
                match = analytics.get('slide4_bestMatch', {})
                template_data = {
                    'win': 'Victory' if match.get('result') == 'Victory' else 'Defeat',
                    'kills': match.get('kills', 0),
                    'deaths': match.get('deaths', 0),
                    'assists': match.get('assists', 0),
                    'championName': match.get('championName', 'Unknown'),
                    'gameDuration': round(match.get('gameDuration', 0))
                }
            
            elif slide_number == 5:  # KDA
                kda = analytics.get('slide5_kda', {})
                template_data = {
                    'avgKills': round(kda.get('avgKills', 0), 1),
                    'avgDeaths': round(kda.get('avgDeaths', 0), 1),
                    'avgAssists': round(kda.get('avgAssists', 0), 1),
                    'kdaRatio': round(kda.get('kdaRatio', 0), 2)
                }
            
            elif slide_number == 6:  # Ranked
                ranked = analytics.get('slide6_rankedJourney', {})
                template_data = {
                    'currentRank': ranked.get('currentRank', 'Unranked'),
                    'leaguePoints': ranked.get('leaguePoints', 0),
                    'winRate': ranked.get('winRate', 0),
                    'totalGames': ranked.get('wins', 0) + ranked.get('losses', 0)
                }
            
            elif slide_number == 7:  # Vision
                vision = analytics.get('slide7_visionScore', {})
                template_data = {
                    'avgVisionScore': round(vision.get('avgVisionScore', 0), 1),
                    'avgWardsPlaced': round(vision.get('avgWardsPlaced', 0), 1),
                    'avgControlWardsPurchased': round(vision.get('avgControlWardsPurchased', 0), 1)
                }
            
            elif slide_number == 8:  # Champion Pool
                pool = analytics.get('slide8_championPool', {})
                template_data = {
                    'uniqueChampions': pool.get('uniqueChampions', 0),
                    'totalGames': pool.get('totalGames', 0),
                    'diversityScore': round(pool.get('diversityScore', 0), 1)
                }
            
            elif slide_number == 9:  # Duo Partner
                duo = analytics.get('slide9_duoPartner', {})
                if duo:
                    template_data = {
                        'partnerName': duo.get('partnerName', 'Unknown'),
                        'gamesTogether': duo.get('gamesTogether', 0),
                        'winRate': duo.get('winRate', 0)
                    }
                else:
                    template_data = {
                        'partnerName': 'Solo Player',
                        'gamesTogether': 0,
                        'winRate': 0
                    }
            
            elif slide_number == 10:  # Strengths
                analysis = analytics.get('slide10_11_analysis', {})
                strengths = analysis.get('strengths', [])
                strengths_text = ', '.join(strengths) if strengths else 'Good game sense'
                template_data = {'strengths': strengths_text}
            
            elif slide_number == 11:  # Weaknesses
                analysis = analytics.get('slide10_11_analysis', {})
                weaknesses = analysis.get('weaknesses', [])
                weaknesses_text = ', '.join(weaknesses) if weaknesses else 'Room for improvement everywhere'
                template_data = {'weaknesses': weaknesses_text}
            
            elif slide_number == 12:  # Progress
                # If no historical data, use current stats as baseline
                time_data = analytics.get('slide2_timeSpent', {})
                kda = analytics.get('slide5_kda', {})
                
                template_data = {
                    'totalGames': time_data.get('totalGames', 0),
                    'kdaRatio': round(kda.get('kdaRatio', 0), 2)
                }
            
            elif slide_number == 13:  # Achievements
                achievements = analytics.get('slide13_achievements', [])
                if achievements:
                    ach_text = '\n'.join([f"- {a['title']}: {a['description']}" for a in achievements])
                else:
                    ach_text = "No special achievements yet"
                template_data = {'achievements': ach_text}
            
            elif slide_number == 14:  # Social Comparison
                percentile = analytics.get('slide14_percentile', {})
                template_data = {
                    'percentile': percentile.get('percentile', 50),
                    'currentRank': percentile.get('rank', 'Unranked'),
                    'kdaRatio': round(percentile.get('kdaRatio', 0), 2)
                }
            
            elif slide_number == 15:  # Final Recap
                time_data = analytics.get('slide2_timeSpent', {})
                ranked = analytics.get('slide6_rankedJourney', {})
                champions = analytics.get('slide3_favoriteChampions', [])
                top_champ = champions[0]['name'] if champions else 'None'
                
                template_data = {
                    'totalGames': time_data.get('totalGames', 0),
                    'currentRank': ranked.get('currentRank', 'Unranked'),
                    'topChampion': top_champ
                }
            
            formatted_prompt = template.format(**template_data)
            return formatted_prompt
            
        except KeyError as e:
            print(f"Warning: Missing analytics field for slide {slide_number}: {e}")
            return template  # Return unformatted template as fallback
        except Exception as e:
            print(f"Error formatting prompt for slide {slide_number}: {e}")
            return template
    
    def call_bedrock(self, prompt: str) -> str:
        """
        Call Bedrock to generate humor.
        
        Args:
            prompt: Prompt string
        
        Returns:
            Generated humor text
        """
        print(f"Calling Bedrock with prompt length: {len(prompt)}")
        
        # Prepare request body - SAVAGE ROAST SETTINGS
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,  # Allow up to 30 words (30 words ≈ 40-50 tokens + buffer)
            "temperature": 0.95,  # VERY HIGH: Maximum creativity for savage roasts
            "top_p": 0.9,  # Allow diverse, unexpected vocabulary
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
        humor_text = response_body['content'][0]['text'].strip()
        
        # Clean up any quotes or extra formatting
        humor_text = humor_text.strip('"').strip("'").strip()
        
        # Remove any emojis that might have been generated
        import re
        # Remove emoji characters (comprehensive regex pattern)
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001F900-\U0001F9FF"  # supplemental symbols
            u"\U0001FA00-\U0001FAFF"  # more symbols
            "]+", flags=re.UNICODE)
        humor_text = emoji_pattern.sub('', humor_text).strip()
        
        logger.info(f"✓ Generated humor: {humor_text}")
        return humor_text
    
    def store_humor(self, session_id: str, slide_number: int, humor_text: str):
        """
        Store humor in S3.
        
        Args:
            session_id: Session ID
            slide_number: Slide number
            humor_text: Generated humor text
        """
        s3_key = f"sessions/{session_id}/humor/slide_{slide_number}.json"
        
        data = {
            'sessionId': session_id,
            'slideNumber': slide_number,
            'humorText': humor_text,
            'generatedAt': json.dumps({"timestamp": "now"})  # Will be replaced with actual timestamp
        }
        
        print(f"Storing humor to S3: {s3_key}")
        upload_to_s3(s3_key, data)
    
    def generate(self, session_id: str, slide_number: int) -> Dict[str, Any]:
        """
        Generate humor for a specific slide.
        
        Args:
            session_id: Session ID
            slide_number: Slide number (1-15)
        
        Returns:
            Result dict with humor text
        """
        print(f"\n{'='*60}")
        print(f"GENERATING HUMOR FOR SLIDE {slide_number}")
        print(f"{'='*60}\n")
        
        # Step 1: Download analytics
        analytics = self.download_analytics(session_id)
        
        # Step 2: Create prompt
        prompt = self.create_prompt(slide_number, analytics)
        
        if not prompt:
            print(f"No humor template for slide {slide_number}")
            return {
                'sessionId': session_id,
                'slideNumber': slide_number,
                'humorText': None,
                'status': 'no_humor_needed'
            }
        
        # Step 3: Generate humor
        humor_text = self.call_bedrock(prompt)
        
        # Step 4: Store result
        self.store_humor(session_id, slide_number, humor_text)
        
        print(f"\n{'='*60}")
        print(f"HUMOR GENERATION COMPLETE!")
        print(f"{'='*60}\n")
        
        return {
            'sessionId': session_id,
            'slideNumber': slide_number,
            'humorText': humor_text,
            'status': 'success'
        }


    # ========================================================================
    # PROGRESSIVE HUMOR GENERATION METHODS
    # ========================================================================
    
    def generate_priority_slides(self, session_id: str) -> Dict[str, Any]:
        """
        Generate humor for priority slides (1-5) rapidly.
        Used at 3:30 mark before loading screen ends.
        
        Args:
            session_id: Session ID
        
        Returns:
            Dict with generated humor for slides 1-5
        """
        from services.session_manager import SessionManager
        
        print(f"🚀 PRIORITY GENERATION: Slides 1-5 for session {session_id}")
        
        priority_slides = [1, 2, 3, 4, 5]
        results = {}
        session_manager = SessionManager()
        
        for slide_num in priority_slides:
            print(f"  Generating slide {slide_num}...")
            
            try:
                result = self.generate(session_id, slide_num)
                humor_text = result.get('humor', '')
                
                # Save to session checkpoint
                if humor_text:
                    session_manager.update_humor(session_id, slide_num, humor_text)
                    results[f"slide{slide_num}"] = humor_text
                    print(f"  ✓ Slide {slide_num} complete")
                else:
                    results[f"slide{slide_num}"] = None
                    print(f"  ⊘ Slide {slide_num} - no humor needed")
                    
            except Exception as e:
                print(f"  ✗ Slide {slide_num} failed: {e}")
                results[f"slide{slide_num}"] = None
        
        logger.info(f"✓ Priority generation complete ({len([r for r in results.values() if r])}/5 slides)")
        return results
    
    def generate_background_slides(self, session_id: str) -> Dict[str, Any]:
        """
        Generate humor for background slides (6-15) during slide viewing.
        Used while user is viewing the first few slides.
        
        Args:
            session_id: Session ID
        
        Returns:
            Dict with generated humor for slides 6-15
        """
        from services.session_manager import SessionManager
        
        print(f"🔄 BACKGROUND GENERATION: Slides 6-15 for session {session_id}")
        
        background_slides = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        results = {}
        session_manager = SessionManager()
        
        for slide_num in background_slides:
            print(f"  Generating slide {slide_num}...")
            
            try:
                result = self.generate(session_id, slide_num)
                humor_text = result.get('humor', '')
                
                # Save to session checkpoint
                if humor_text:
                    session_manager.update_humor(session_id, slide_num, humor_text)
                    results[f"slide{slide_num}"] = humor_text
                    print(f"  ✓ Slide {slide_num} complete")
                else:
                    results[f"slide{slide_num}"] = None
                    
            except Exception as e:
                print(f"  ✗ Slide {slide_num} failed: {e}")
                results[f"slide{slide_num}"] = None
        
        logger.info(f"✓ Background generation complete ({len([r for r in results.values() if r])}/10 slides)")
        return results
    
    def regenerate_all_slides(self, session_id: str) -> Dict[str, Any]:
        """
        Regenerate ALL slide humor with complete analysis data.
        Used when analysis completes while user is viewing slides.
        
        Args:
            session_id: Session ID
        
        Returns:
            Dict with regenerated humor for all slides
        """
        from services.session_manager import SessionManager
        
        print(f"🔁 FULL REGENERATION: All slides with complete data for session {session_id}")
        
        all_slides = range(1, 16)  # Slides 1-15
        results = {}
        session_manager = SessionManager()
        
        for slide_num in all_slides:
            print(f"  Regenerating slide {slide_num}...")
            
            try:
                result = self.generate(session_id, slide_num)
                humor_text = result.get('humor', '')
                
                # Save to session checkpoint
                if humor_text:
                    session_manager.update_humor(session_id, slide_num, humor_text)
                    results[f"slide{slide_num}"] = humor_text
                    print(f"  ✓ Slide {slide_num} regenerated")
                else:
                    results[f"slide{slide_num}"] = None
                    
            except Exception as e:
                print(f"  ✗ Slide {slide_num} failed: {e}")
                results[f"slide{slide_num}"] = None
        
        logger.info(f"✓ Full regeneration complete ({len([r for r in results.values() if r])}/15 slides)")
        
        # Notify that regeneration is complete
        print(f"\n{'='*60}")
        print(f"🔥 REGENERATION COMPLETE!")
        print(f"Frontend should show popup:")
        print(f"'We finally caught up to you! Let's see how much")
        print(f" chaos you ACTUALLY caused 🔥'")
        print(f"{'='*60}\n")
        
        return results
    
    # ========================================================================
    # END PROGRESSIVE HUMOR GENERATION METHODS
    # ========================================================================


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function - PROGRESSIVE GENERATION SUPPORT
    
    Supports multiple generation modes:
    
    1. Single slide (original):
    {
        "sessionId": "uuid",
        "slideNumber": 3
    }
    
    2. Priority slides (1-5):
    {
        "sessionId": "uuid",
        "mode": "priority"
    }
    
    3. Background slides (6-15):
    {
        "sessionId": "uuid",
        "mode": "background"
    }
    
    4. Full regeneration:
    {
        "sessionId": "uuid",
        "mode": "regenerate"
    }
    
    Returns:
    {
        "sessionId": "abc123xyz",
        "slideNumber": 3,
        "humorText": "...",
        "status": "success"
    }
    """
    try:
        # Extract parameters
        session_id = event.get('sessionId')
        mode = event.get('mode', 'single')
        slide_number = event.get('slideNumber')
        
        # Validate session ID
        if not session_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameter: sessionId'
                })
            }
        
        generator = HumorGenerator()
        
        # Route to appropriate generation method
        if mode == 'priority':
            # Generate slides 1-5 rapidly (before loading screen ends)
            results = generator.generate_priority_slides(session_id)
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'mode': 'priority',
                    'slides': results,
                    'message': 'Priority slides (1-5) generated'
                })
            }
        
        elif mode == 'background':
            # Generate slides 6-15 in background (during slide viewing)
            results = generator.generate_background_slides(session_id)
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'mode': 'background',
                    'slides': results,
                    'message': 'Background slides (6-15) generated'
                })
            }
        
        elif mode == 'regenerate':
            # Regenerate all slides with complete analysis
            results = generator.regenerate_all_slides(session_id)
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'mode': 'regenerate',
                    'slides': results,
                    'message': 'All slides regenerated with complete data'
                })
            }
        
        else:  # mode == 'single' (original behavior)
            # Validate slide number for single mode
            if not slide_number:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'error': 'Missing slideNumber for single mode'
                    })
                }
            
            if not (1 <= slide_number <= 15):
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'error': 'slideNumber must be between 1 and 15'
                    })
                }
            
            # Generate humor for single slide
            result = generator.generate(session_id, slide_number)
            
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }
    
    except Exception as e:
        print(f"Error generating humor: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }


# For local testing
if __name__ == "__main__":
    # Test humor generation for slide 3 (Champions)
    test_event = {
        'sessionId': 'test-session-123',
        'slideNumber': 3
    }
    
    result = lambda_handler(test_event, None)
    print(f"\nResult: {json.dumps(json.loads(result['body']), indent=2)}")