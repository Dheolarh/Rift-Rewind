"""
Lambda Function: humor_context.py
Purpose: Generate AI humor for each slide using AWS Bedrock Claude 3 Sonnet

Environment Variables Required:
- S3_BUCKET_NAME
- BEDROCK_MODEL_ID
- AWS_REGION

Memory: 256 MB
Timeout: 30 seconds
"""

import os
import sys
import json
from typing import Dict, Any, Optional

# Add parent directory to path for local imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.aws_clients import get_bedrock_client, download_from_s3, upload_to_s3


# Slide-specific prompt templates - COMEDY EDITION
# Reframed as "witty commentary" for Claude content policy compliance
# Still uses League memes and self-deprecating humor players love!
SLIDE_PROMPTS = {
    1: None,  # Player Details - No humor needed
    
    2: """You're a witty League of Legends comedian writing for a year-in-review app (like Spotify Wrapped for gaming).

Player's time investment this year:
- Total Games: {totalGames}
- Total Hours: {totalHours} hours  
- Average Game Length: {avgGameLength} minutes

Write 1-2 funny, sarcastic sentences about their time spent playing. Use popular League memes like:
- "Just one more game" addiction
- "Touch grass" jokes
- Time management humor
- Self-deprecating gaming jokes

Keep it playful and entertaining - this is meant to make players laugh at themselves!

Example style: "You spent 120 hours in the Rift this year. Grass is still there waiting for you whenever you're ready! 🌱"

Your turn:""",
    
    3: """You're a witty League comedian analyzing champion choices for a fun year-in-review app.

Their top champions this year:
{championsList}

Write 1-2 funny sentences about their champion pool using League community memes:
- Yasuo/Yone: "0/10 powerspike" jokes
- Yuumi: "AFK cat" / "Netflix while playing"
- Master Yi: "Right-click champion"
- Lux: "Ability to miss everything"
- Champion stereotypes League players find hilarious

Keep it lighthearted and self-deprecating!

Example: "A Yasuo main with 142 games? The 0/10 powerspike is a lifestyle, not a phase. 🌪️"

Your turn:""",
    
    4: """You're a League comedy writer creating funny match commentary.

Their best/most memorable match:
- Result: {win}
- KDA: {kills}/{deaths}/{assists}
- Champion: {championName}
- Duration: {gameDuration} minutes

Write 1-2 entertaining sentences about this match using League humor:
- Epic win? Celebrate with sarcasm
- Lots of deaths? "Running it down" jokes  
- Long game? "Can't close games" humor
- Clutch performance? Hype it up
- Use "FF15", "mental boom", etc.

Example: "Your 18/2/12 Zed game was clean! The enemy team probably FF'd at 15 and went next. 😎"

Your turn:""",
    
    5: """You're a witty League analyst writing funny KDA commentary.

Their average KDA this year:
- Kills: {avgKills}
- Deaths: {avgDeaths}
- Assists: {avgAssists}
- KDA Ratio: {kdaRatio}

Write 1-2 sarcastic sentences about their KDA using League memes:
- High deaths? "Professional practice tool dummy"
- Low KDA? Self-deprecating jokes
- Good KDA? "KDA player won't teamfight" jokes
- "0/10 powerspike", "running it down", "jungle diff"

Example: "A 2.8 KDA is respectable! Though your death count suggests you're still searching for that mythical 0/10 powerspike. ⚡"

Your turn:""",
    
    6: """You're a League comedian writing about ranked journeys.

Their ranked stats:
- Current Rank: {currentRank}
- LP: {leaguePoints}
- Win Rate: {winRate}%
- Total Games: {totalGames}

Write 1-2 funny sentences about their ranked experience using community memes:

IF they are ranked (currentRank != "Unranked"):
- "Hardstuck" jokes
- "Elo hell doesn't exist - it's a skill issue"
- "One more game to promos" addiction
- Ranked anxiety / mental boom
- Climb struggles everyone relates to

IF they are UNRANKED:
- "Normals only" lifestyle
- "Ranked anxiety too real"
- "Why stress when you can chill?"
- "Avoiding the toxicity" jokes
- "Just for fun" mentality

Examples:
- Ranked: "377 wins and still climbing! That's dedication... or maybe just really good mental after 292 losses. 🎯"
- Unranked: "Unranked? That's the galaxy brain move. Why deal with LP anxiety when you can just vibe in normals? Ranked is overrated anyway. ✌️"

Your turn:""",
    
    7: """You're a League comedian writing about vision control.

Their vision stats:
- Avg Vision Score: {avgVisionScore}
- Wards Placed: {avgWardsPlaced}
- Control Wards: {avgControlWardsPurchased}

Write 1-2 funny sentences about their warding using League jokes:
- Low vision? "Wards exist in the shop" jokes
- Supports with low vision? Funny contradiction
- "That 75g pink ward lost us the game" culture
- Map awareness memes
- Vision diff jokes

Example: "Vision score of 21... The minimap is there for decoration AND information, just so you know! 👁️"

Your turn:""",
    
    8: """You're a League comedian analyzing champion diversity.

Their champion pool:
- Unique Champions: {uniqueChampions}
- Total Games: {totalGames}
- Diversity: {diversityScore}%

Write 1-2 funny sentences using League memes:
- One-trick? "One champ away from ARAM account"
- Too many champs? "Can't decide which to int on"
- Meta slave? Following pro builds blindly
- Off-meta? Hipster or troll?

Example: "14 different champions! That's impressive diversity... or an identity crisis. Your mains are having an existential debate. 🎭"

Your turn:""",
    
    9: """You're a League comedian writing about duo queue dynamics.

Their duo stats:
- Partner: {partnerName}
- Games Together: {gamesTogether}
- Win Rate Together: {winRate}%

Write 1-2 funny sentences about duo queue using community memes:

IF they have a duo partner (gamesTogether > 0):
- "Duo abuse" jokes
- "Duo bot getting gapped" culture
- Friend carrying / being carried
- Synergy or feeding together?

IF they're a solo player (gamesTogether = 0 or Partner = "Solo Player"):
- "True solo queue warrior" jokes
- "Can't trust anyone in soloQ"
- "1v9 every game" humor
- "No one to blame but yourself"

Examples:
- With duo: "You played 2 games with DRX and won both! Either great synergy or they hard carried. We know which one. 🤝"
- Solo player: "Zero duo games? That's the true solo queue experience! You can't get held back by teammates if you refuse to trust anyone. 🗿"

Your turn:""",
    
    10: """You're a League comedian giving backhanded compliments about strengths.

Their top strengths:
{strengths}

Write 1-2 sarcastic but funny sentences that highlight their strength while being playful:
- Good at ONE thing? "Your only redeeming quality"
- Early game god? "Too bad games last 30+ minutes"
- Mechanical skill? "Shame about the macro"
- Good farming? "PvE player in a PvP game"

Example: "You survive teamfights well! Now if only you could actually win them instead of just not dying. 🛡️"

Your turn:""",
    
    11: """You're a League comedian offering constructive (but funny) criticism.

Their main weaknesses:
{weaknesses}

Write 1-2 playful sentences about areas to improve using League humor:
- Bad CS? "Last-hitting tutorial needed"
- Die a lot? "Map awareness DLC not installed"
- Late game? "How to close games: YouTube tutorial"
- Mechanics? "Skill issue (jokingly)"

Example: "Your CS could use some work - those minions aren't going to last-hit themselves! Maybe practice in Practice Tool? 📚"

Your turn:""",
    
    12: """You're a League comedian analyzing player progress over time.

Their stats:
- Total Games This Period: {totalGames}
- Current KDA: {kdaRatio}

Write 1-2 funny sentences about their journey using memes:

IF they have progress data (games increasing, stats changing):
- Improved? "Glow up but still room to grow"
- Declined? "Washed up" humor (playful)
- Stagnant? "Hardstuck definition"
- Streaky? "Mental boom then mental zoom"

IF this is their first season / no historical data:
- "Welcome to the Rift!" energy
- "Everyone starts somewhere"
- "First season hype"
- "The grind begins now"
- "Fresh account who dis?"

Examples:
- With progress: "Your KDA went from 2.1 to 2.9 this year! That's what we call a redemption arc. Next stop: not dying to jungle ganks. 📈"
- First season: "First season on the Rift? Welcome! You're about to discover what 'one more game' addiction feels like. Buckle up! 🎮"

Your turn:""",
    
    13: """You're a League comedian hyping up player achievements.

Their achievements:
{achievements}

Write 1-2 fun sentences celebrating (or playfully teasing) their accomplishments:

IF they have achievements:
- Pentakill? Hype it up!
- Big milestone? Celebrate with sarcasm
- Win streak? "Smurf or lucky?"
- Impressive feat? Give credit where due

IF they have NO achievements ("No special achievements yet"):
- "Participation trophy" jokes
- "There's always next season!"
- "Stats don't define you" humor
- "Hidden achievements" jokes

Examples:
- With achievements: "A pentakill on Katarina? The enemy team must have been trying out their new 'standing still' strategy! Still impressive though. ⚔️"
- No achievements: "No pentakills this year? That's okay, participating is its own reward! There's always next season to unlock that 'Not AFK' achievement. 🏆"

Your turn:""",
    
    14: """You're a League comedian comparing the player to the global average.

Their stats vs the world:
- Rank Percentile: Top {percentile}%
- Current Rank: {currentRank}
- KDA: {kdaRatio}

Write 1-2 funny sentences about where they stand using League culture:
- High rank? "Grass has filed a missing person report"
- Average rank? "Perfectly balanced, as all things should be"
- Low rank? "Room for improvement!" (optimistic)
- Top percentile? Celebrate with sarcasm

Example: "You're in the top 0.1% of players! That's CHALLENGER tier. Touch grass? Never heard of her. 👑"

Your turn:""",
    
    15: """You're a League comedian writing a fun year-end summary.

Their season in review:
- Total Games: {totalGames}
- Final Rank: {currentRank}
- Top Champion: {topChampion}

Write 1-2 entertaining closing sentences that wrap up their year with humor:
- Celebrate their journey
- Self-deprecating jokes welcome
- "See you on the Rift next season"
- Fun, upbeat, memorable

Example: "You played 377 games, hit Challenger, and became an Azir main. What a journey! Same time next year? 🎮"

Your turn:""",
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
        
        # Prepare request body - ROAST MASTER 3000 SETTINGS
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 250,  # Allow slightly longer roasts
            "temperature": 0.9,  # HIGH creativity for savage roasts
            "top_p": 0.95,  # Allow diverse vocabulary
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
        humor_text = response_body['content'][0]['text']
        
        print(f"✓ Generated humor: {humor_text[:100]}...")
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
        print(f"Session ID: {session_id}")
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
        
        print(f"✓ Priority generation complete ({len([r for r in results.values() if r])}/5 slides)")
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
        
        print(f"✓ Background generation complete ({len([r for r in results.values() if r])}/10 slides)")
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
        
        print(f"✓ Full regeneration complete ({len([r for r in results.values() if r])}/15 slides)")
        
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