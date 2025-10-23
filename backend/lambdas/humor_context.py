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
    
    2: """Roast this League player's time commitment. BE CONTEXT AWARE.

Stats: {totalGames} games, {totalHours} hours, {avgGameLength} min/game

HARDCORE (500+ hours): Sarcastic compliment or "get a life" roast
AVERAGE (100-500 hours): Light roast, modest mockery  
CASUAL (<100 hours): "Why even bother" energy

Examples by tier:
HARDCORE: "{totalHours} hours? At this point League IS your job. Unpaid, but still."
HARDCORE: "Touch grass? You played {totalGames} games. Grass is a myth to you now."
AVERAGE: "{totalHours} hours of ranked. Not casual, not addicted. Just... sad."
CASUAL: "{totalGames} games? {totalHours} hours? You barely even tried to ruin your life."

Context-aware roast. Under 30 words. No emojis:""",
    
    
    4: """Roast (or compliment) this player's BEST SINGLE MATCH performance. BE CONTEXT AWARE.

This is about their HIGHEST-KILL GAME, not overall stats.
Stats: {kills}/{deaths}/{assists} on {championName}, {gameDuration} min, Result: {win}

GODLIKE (20+ kills in one game): Sarcastic compliment or "touch grass" roast
GOOD (10-19 kills): Backhanded compliment
AVERAGE (5-9 kills): Light mockery
TERRIBLE (<5 kills): Absolute destruction

Examples by tier:
GODLIKE: "{kills} kills on {championName}? Okay we see you. The enemy team rage quit."
GOOD: "{kills} kills in one game. Not bad. Solid pop-off moment."
AVERAGE: "Your best game ever is {kills}/{deaths}/{assists}? Mid recognizes mid."
TERRIBLE: "{kills} kills in your BEST GAME EVER? That's not a highlight, that's embarrassing."

Roast THIS SPECIFIC MATCH. Under 30 words. No emojis:""",
    
    5: """Roast (or acknowledge) this player's OVERALL SEASON KDA. BE CONTEXT AWARE.

This is about their AVERAGE performance across ALL GAMES, not one match.
Stats: {avgKills}/{avgDeaths}/{avgAssists} per game, {kdaRatio} KDA ratio, {totalKills} total kills all season

ELITE (4.0+ KDA): Sarcastic respect or jealous roast
GOOD (2.5-3.9 KDA): Solid acknowledgment with shade
AVERAGE (1.5-2.4 KDA): Mid-tier mockery  
TRASH (<1.5 KDA): Nuclear destruction

Examples by tier:
ELITE: "{kdaRatio} KDA ratio? Alright calm down. You're good. We get it."
GOOD: "{kdaRatio} KDA across all games. Solid. Not cracked, just consistent."
AVERAGE: "{avgKills}/{avgDeaths}/{avgAssists} average. You're aggressively mid and that's okay."
TRASH: "{kdaRatio} KDA? You're inting every game. That's the consistency we don't need."

Roast their SEASON-LONG KDA performance. Under 30 words. No emojis:""",
    
    
    6: """Roast (or respect) this player's rank. BE CONTEXT AWARE.

Stats: {currentRank}, {leaguePoints} LP, {winRate}% winrate, {totalGames} games

HIGH ELO (Diamond+): Genuine respect or jealous roast
MID ELO (Gold-Plat): Backhanded compliment, "not bad" energy
LOW ELO (Silver-Bronze): Harsh reality check
UNRANKED: Why are you hiding?

Examples by tier:
HIGH: "{currentRank}? Actually impressive. Must be nice being better than 95% of us."
MID: "{currentRank} at {winRate}% WR. You're decent. Barely. Don't let it go to your head."
LOW: "{currentRank} after {totalGames} games. The climb is real. The struggle is... also real."
UNRANKED: "Unranked after {totalGames} games? Ranked anxiety or just scared of the truth?"

Context-aware response. Under 30 words. No emojis:""",
    7: """Roast (or acknowledge) this player's vision control. BE CONTEXT AWARE.

Stats: {avgVisionScore} avg vision score, {avgWardsPlaced} wards/game, {avgControlWardsPurchased} control wards/game

EXCELLENT (45+ vision): Sarcastic respect, "support main" jokes
GOOD (30-44 vision): Solid acknowledgment
AVERAGE (20-29 vision): Light roasting
TERRIBLE (<20 vision): Nuclear destruction for no vision

Examples by tier:
EXCELLENT: "{avgVisionScore} vision score per game? Okay support main, we see you. Your team owes you LP."
GOOD: "{avgVisionScore} vision score per game. Not bad. You actually know wards exist."
AVERAGE: "{avgVisionScore} average vision score? You ward sometimes. When you remember. Maybe."
TERRIBLE: "{avgVisionScore} average vision score? You're playing League with a blindfold. Map awareness who?"

Context-aware response. Under 30 words. No emojis:""",
    
    8: """Roast (or acknowledge) this player's champion pool. BE CONTEXT AWARE.

Stats: {uniqueChampions} unique champions across {totalGames} games

ONE-TRICK (1-10 champs): "Dedication or fear?" roasts
FOCUSED (11-25 champs): Balanced commentary
DIVERSE (26-50 champs): "Jack of all trades" mockery
CHAOS (50+ champs): "Master of none" destruction

Examples by tier:
ONE-TRICK: "{uniqueChampions} champions in {totalGames} games. You found your main and never looked back. Respect."
FOCUSED: "{uniqueChampions} champions. Solid roster. Not spam-clicking in champ select."
DIVERSE: "{uniqueChampions} different champions? That's variety or indecision. Can't tell which."
CHAOS: "{uniqueChampions} champions played? You're not versatile, you're just lost."

Context-aware response. Under 30 words. No emojis:""",
    
    9: """Roast this duo partnership.

Duo stats:
- Partner: {partnerName}
- Games together: {gamesTogether}
- Combined winrate: {winRate}%

Write ONE savage roast about their duo performance. Be brutal. Under 30 words. No emojis.

Examples:
"You and {partnerName} played {gamesTogether} games at {winRate}% winrate. Two negatives don't make a positive."
"{gamesTogether} games with {partnerName}, {winRate}% winrate. You're not a duo, you're a liability multiplier."
"{partnerName} and you: {gamesTogether} games together. Friendship goals. Winning games? Not so much."
"{winRate}% winrate across {gamesTogether} games. You two share one brain cell and it's permanently AFK."
"Playing {gamesTogether} games with {partnerName}. That's not teamwork, that's synchronized inting."

Destroy their duo. Under 30 words:""",
    
    10: """You're giving a backhanded compliment about the players strengths derived from analysis result from their league of legends seasons recap.

Top Strength: {strengths}

Write ONE sarcastic and witty sentence (max 30 words) that sounds like praise but is actually a roast. NO EMOJIS.

Examples:
if strength is map awareness
"Your map awareness is {strengths}? Wow, you occasionally glance at the minimap. Revolutionary gameplay right here."
"Your strength is map awareness? That's not a strength, that's just playing the game correctly."

if strength is teamfighting
"Wow, your {strengths} in teamfights is admirable. Finally, someone who shows up and presses buttons with intent!"
"Your strength is teamfighting? Congratulations on doing the bare minimum and actually participating."

if strength is mechanics
"Your mechanical skill is {strengths}? That's great, shame the mental game doesn't exist."
"Strong mechanics you say? Now if only your decision-making caught up."

if strength is farming/CS
"Your {strengths} CS per minute is incredible. You're basically a creep farming simulator with legs."
"Excellent farming stats! Too bad you die immediately after."

if strength is engaging
"Your strength is engaging? You sure are engaging... the enemy team and losing fights."

Max 30 words. Compliment that's secretly a roast. NO EMOJIS:""",
    
    11: """You're pointing out a weakness with 'helpful' advice from analysis result from their league of legends seasons recap.

Top Weakness: {weaknesses}

Write ONE savage and sarcastic sentence (max 30 words) that sounds helpful but is actually canny. NO EMOJIS.

Examples:
if weakness is CS/farming
"Your CS needs work. Minions don't last-hit themselves. Maybe watch a YouTube tutorial? Or three? Or all of them?"
"Farm more, you say? Revolutionary advice. Minions are free gold, but apparently so is gold for you."

if weakness is map awareness
"Map awareness: critical failure. Good news: vision is free! Bad news: you still won't look at the minimap anyway."
"Can't see the jungler? That's what the minimap is for. Try opening your eyes? Just a thought!"

if weakness is positioning
"Positioning in teamfights? Flash is for escaping danger, not running solo 1v5. Just a helpful tip!"
"Your positioning is rough. Try staying behind your team instead of in the enemy fountain."

if weakness is warding
"You don't ward? Wards are literally free gold sense at minute 3. Even support understands this concept."
"Vision score too low? Buy wards. It's cheaper than therapy for your teammates."

if weakness is mechanics
"Your mechanics need work. Practice in Practice Tool for once instead of bleeding LP in ranked."
"Clunky mechanics? That's okay, start with a 2-button champion and work your way up."

if weakness is decision making
"Decision-making? Rough. Pro tip: not everything needs to be a fight. Sometimes running away is winning."
"Your macro is atrocious. Here's a wild thought: don't fight when down 5k gold."

Max 30 words. Savage advice disguised as help. NO EMOJIS:""",

    12: """You're commenting on year overview from analysis result from their league of legends seasons recap.

Stats:
- Total Games: {totalGames}
- Current KDA: {kdaRatio}

Write ONE savage sentence (max 30 words) about their journey using actual numbers. NO EMOJIS.

Examples (with improvement):
"After {totalGames} games, your KDA is {kdaRatio}? That's not a journey, that's a hostage situation."
"A pitiful {kdaRatio} KDA after {totalGames} games? At this rate, you'll hit average in 2030."
"{totalGames} games later and your KDA is still {kdaRatio}? Even your

Max 30 words. Progress roast with real stats. NO EMOJIS:""",
    
    13: """You're commenting on their achievements (or lack thereof).

Achievements: {achievements}

Write ONE savage sentence (max 30 words). NO EMOJIS.

Examples (with achievements):
"Congratulations on your achievements! Now if only wins were an achievement too."
"Look at you, collecting achievements like participation trophies. Truly impressive."
"Your achievements: {achievements}. Your rank: still stuck. Priorities unclear."

Examples (no achievements):
"No achievements? Not even trying for goals? That's just speedrunning irrelevance."
"Zero achievements recorded. Were you even playing or just afk farming?"
"No special achievements? Even bots aim for something. What's your excuse?"

Examples (mid-tier achievements):
"Some modest achievements here. Baby steps, I respect the effort."
"Your achievements are respectable. Not exciting, but respectable in a 'participation' way."
"Got some achievements! Now graduate to actually being good."

Max 30 words. Achievement roast. NO EMOJIS:""",
    
    14: """You're commenting on their rank percentile and their position on the leaderboard from analysis result from their league of legends seasons recap.

Stats:
- Rank: {currentRank}
- Percentile: Top {percentile}%

Write ONE savage sentence (max 30 words) using EXACT percentile. NO EMOJIS.

Examples:
if percentile is high (Top 1-5%)
"Top {percentile}%? You're basically royalty. Everyone else is peasants. Enjoy the view from up there."
"Only top {percentile}% of players reached your rank? That's elite. That's also unreachable for the 99.9% watching."

if percentile is medium (Top 10-30%)
"Top {percentile}% players? Congrats, you beat the casuals. Now beat the actual players."
"In the top {percentile}%? You're better than average, which isn't saying much."
"Top {percentile}% rank? You're basically a middle manager of League."

if percentile is low (Top 50%+)
"Top {percentile}%? Buddy, that's not an achievement, that's an average Tuesday."
"Top {percentile}%? You and roughly half the server are equally mid."
"Congratulations on being better than exactly half of everyone. You're median."

Max 30 words. Use actual percentile. NO EMOJIS:""",
    
    15: """You're writing a final season wrap-up roast.

Stats:
- Total Games: {totalGames}
- Final Rank: {currentRank}
- Top Champion: {topChampion}

Write ONE memorable closing line (max 30 words) using actual stats. Make it savage but funny. NO EMOJIS.

Examples:
if positive conclusion
"That's {totalGames} games, {currentRank} rank, and one {topChampion} one-trick away from actual competence. Until next season!"
"What a year: {totalGames} games, {currentRank} rank, and a {topChampion} obsession. Same time next year?"
"Here's to {totalGames} games of trying. You reached {currentRank}. Growth is growth, even if it's microscopic."

if neutral/average conclusion
"{totalGames} games. {currentRank} rank. {topChampion} addiction. That's your legacy this season. Thrilling stuff."
"Final verdict: {totalGames} games didn't change much. You're still you, just more tired and slightly older."
"Year summary: {totalGames} grinding sessions = {currentRank}. Mathematically concerning but emotionally relatable."

if hard roast conclusion
"{totalGames} games and you're still {currentRank}? The only thing grinding harder than you are your enemies' teeth."
"After {totalGames} games spamming {topChampion}, you reached {currentRank}? That's not a season, that's a cry for help."
"Wrap up: {totalGames} games, {currentRank} rank, zero self-respect. See you next season for round two!"

Max 30 words. Epic savage farewell using real stats. NO EMOJIS:"""
}

class HumorGenerator:
    """
    Generates AI humor for Rift Rewind slides using Bedrock.
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
                total_minutes = data.get('totalMinutes')
                # Calculate totalMinutes if not present (for old cached data)
                if total_minutes is None:
                    total_hours = data.get('totalHours', 0)
                    total_minutes = int(total_hours * 60)
                
                template_data = {
                    'totalGames': data.get('totalGames', 0),
                    'totalHours': data.get('totalHours', 0),
                    'totalMinutes': total_minutes,
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
                    'championName': match.get('champion', 'Unknown'),
                    'gameDuration': round(match.get('duration', 0)),
                    'totalMinutes': round(match.get('duration', 0))
                }
            
            elif slide_number == 5:  # KDA
                kda = analytics.get('slide5_kda', {})
                template_data = {
                    'avgKills': round(kda.get('avgKills', 0), 1),
                    'avgDeaths': round(kda.get('avgDeaths', 0), 1),
                    'avgAssists': round(kda.get('avgAssists', 0), 1),
                    'kdaRatio': round(kda.get('kdaRatio', 0), 2),
                    'totalKills': kda.get('totalKills', 0)
                }
            
            elif slide_number == 6:  # Ranked
                ranked = analytics.get('slide6_rankedJourney', {})
                template_data = {
                    'currentRank': ranked.get('currentRank', 'Unranked'),
                    'leaguePoints': ranked.get('lp', 0),
                    'winRate': ranked.get('winRate', 0),
                    'totalGames': ranked.get('wins', 0) + ranked.get('losses', 0)
                }
            
            elif slide_number == 7:  # Vision
                vision = analytics.get('slide7_visionScore', {})
                template_data = {
                    'avgVisionScore': round(vision.get('avgVisionScore', 0), 1),
                    'avgWardsPlaced': round(vision.get('avgWardsPlaced', 0), 1),
                    'avgControlWardsPurchased': round(vision.get('avgControlWards', 0), 1)
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
                    'percentile': percentile.get('rankPercentile', 50),
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
        Call Bedrock to generate humor using Meta Llama.
        
        Args:
            prompt: Prompt string
        
        Returns:
            Generated humor text
        """
        print(f"Calling Bedrock with prompt length: {len(prompt)}")
        
        # Meta Llama 3.1 uses chat template format with special tokens
        system_prompt = """You are a CONTEXT-AWARE League of Legends roaster analyzing player performance.

GOOD players: Sarcastic respect, backhanded compliments, "touch grass" jokes
AVERAGE players: Light roasts, modest mockery, "you're trying" energy  
BAD players: Brutal destruction, savage roasts, "why do you even play" vibes

Read the stats. Match your tone to their skill level. Be funny, not generic.
NO EMOJIS. Max 30 words."""
        
        # Llama chat template format
        llama_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        
        # Prepare request body for Meta Llama - SAVAGE ROAST SETTINGS
        request_body = {
            "prompt": llama_prompt,
            "max_gen_len": 100,  # Llama uses different param name
            "temperature": 0.9,  # High creativity for spicy roasts
            "top_p": 0.95  # Wide vocabulary for creative insults
        }
        
        # Invoke Bedrock
        response = self.bedrock_client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body)
        )
        
        # Parse response (Llama has different response format)
        response_body = json.loads(response['body'].read())
        humor_text = response_body.get('generation', '').strip()
        
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