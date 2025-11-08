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

    2: """Create a short, funny one-liner about how much time this player spent on League. 
Compare their total hours to any real-world activity (watching a show, working a job, running a marathon, etc.).
It should sound playful and slightly concerned — like the game can’t believe their dedication.

Stats: {totalGames} games, {totalHours} hours, {avgGameLength} min/game

TONE GUIDE:
- 500+ hours → Legendary obsession
- 100–500 hours → Balanced addiction
- <100 hours → Barely played

Examples:
"That’s enough time to master piano, but you chose tilt instead."
"You’ve clocked in like League pays salary."
"You played just enough to remember how painful it is."

Keep under 20 words, use humor + exaggeration:""",
    

    4: """Write a short, dramatic reaction to this player's best match — as if the system is shocked, proud, or disappointed.
Focus on emotion, not stats.

Stats: {kills}/{deaths}/{assists} on {championName}, {gameDuration} min, Result: {win}

PERFORMANCE GUIDE:
- 20+ kills → Overpowered energy
- 10–19 kills → Strong but human
- 5–9 kills → Mid-tier flex
- <5 kills → Comic relief

Examples:
"That match was pure chaos — beautiful chaos."
"You peaked there, admit it."
"Painful to watch, but at least memorable."

Under 15 words, cinematic or mocking tone:""",
    

    5: """Write a short reaction to the player's season KDA. 
Be direct — compliment or mock their skill level without listing numbers.

Stats: {totalKills}

TONE GUIDE:
- 1000+ → Overlord energy
- 500–999 → Solid
- 100–499 → Mid
- <100 → Disaster

Examples:
"All hail the dark summoner."
"Well that's good I'll say, you prefer a diplomatic solution"
"You’re a horror to watch."
"After all this time, still a noob."

Under 15 words, confident and punchy:""",
    

    6: """Describe their rank in a funny, personal way — like the system knows them too well.
Avoid stats, just attitude.

Stats: {currentRank}, {leaguePoints}, {winRate}%, {totalGames}

TONE GUIDE:
- Diamond+ → Quiet admiration
- Gold–Plat → Endless grind
- Silver–Bronze → Tragic comedy
- Unranked → Confused soul

Examples:
"You breathe ranked air. Respect."
"Gold again? Eternal purgatory."
"Bronze is a lifestyle, not a rank."
"Still unranked? That’s a talent."

Under 15 words, witty and personal:""",
    

    7: """Make a funny comment about how well this player uses vision — like judging their eyesight.
Use jokes about seeing, blindness, or map awareness.

Stats: {avgVisionScore}, {avgWardsPlaced}, {avgControlWardsPurchased}

TONE GUIDE:
- 45+ → Eagle vision
- 30–44 → Average awareness
- 20–29 → Fog dweller
- <20 → Blind adventurer

Examples:
"You see everything. Creepy."
"You ward for decoration."
"Did you uninstall your eyes?"
"You play like you’ve never seen a minimap."

Under 15 words, pun-based humor preferred:""",
    

    8: """Write a quick, funny line about their champion pool — like you’re judging their identity crisis or loyalty.

Stats: {uniqueChampions}, {totalGames}

TONE GUIDE:
- 1–10 → One-trick devotion
- 11–25 → Consistent but obsessed
- 26–50 → Lost identity
- 50+ → Chaos incarnate

Examples:
"Restraining order from that champ pending."
"One nerf away from existential dread."
"You’re loyal, maybe too loyal."
"That’s not a pool — it’s an ocean of confusion."

Under 15 words, short and character-driven:""",
    

    9: """Write a short, funny line about this player and their duo partner — like you’re narrating a chaotic relationship.

Stats: {partnerName}, {gamesTogether}, {winRate}%

Examples:
"You and {partnerName}? A romantic disaster."
"{partnerName} carried your trauma, not your LP."
"Together, you two redefine throwing."
"Dynamic duo? More like dynamic disaster."

Under 15 words, playful duo energy:""",
    

    10: """You are a professional coach giving a short, specific praise for their best strength.

Top Strength: {strengths}

Examples:
"Excellent map control — you move like you own the Rift."
"Perfect positioning — chaos fears you."
"Teamfights are your stage. Keep performing."

Under 25 words, professional and encouraging:""",
    

    11: """You are a professional coach giving quick, actionable advice for their biggest weakness.

Top Weakness: {weaknesses}

Examples:
"Too aggressive early. Learn patience, win late."
"Low vision — start warding like you mean it."
"Bad CS. Farm gold, not death timers."

Under 25 words, clear and constructive:""",
    

    12: """Write a short, darkly funny line about their overall season progress — like an anime arc gone wrong.

Stats: {totalGames}, {kdaRatio}

Examples:
"{totalGames} games later, still no enlightenment."
"Your journey was 90% filler episodes."
"Growth? Just trauma with stats."

Under 15 words, existential humor tone:""",
    

    14: """Write a short, mock-serious comment about their global percentile, as if it’s from a documentary narrator.

Stats: {currentRank}, {percentile}%

Examples:
"Top {percentile}% — the chosen few."
"Top {percentile}% — respectable mediocrity."
"Top {percentile}% — humanity’s middle child."

Under 15 words, dramatic or deadpan tone:""",
    

    15: """Write a short farewell for their season wrap-up. 
It should sound warm, proud, and a little nostalgic — like the system saying goodbye to a friend.

Stats: {totalGames} games, {totalHours} hours, {currentRank} rank, {topChampion}, {kdaRatio} KDA, {winRate}% win rate

Examples:
"What a season.\n{totalGames} games, countless moments.\n{topChampion} carried your story.\nSee you next season, summoner."

3–5 sentences max, under 100 words:"""
}

class HumorGenerator:
    """
    Generates AI humor for Rift Rewind slides using Bedrock.
    """
    
    def __init__(self):
        self.bedrock_client = get_bedrock_client()
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
                time_data = analytics.get('slide2_timeSpent', {})
                kda = analytics.get('slide5_kda', {})
                
                template_data = {
                    'totalGames': time_data.get('totalGames', 0),
                    'kdaRatio': round(kda.get('kdaRatio', 0), 2)
                }
            
            elif slide_number == 14:  # Social Comparison
                percentile_block = analytics.get('slide14_percentile', {})
                raw_percentile = percentile_block.get('rankPercentile', 50)
                display_percent = round(100 - raw_percentile, 1)

                template_data = {
                    'percentile': display_percent,
                    'currentRank': percentile_block.get('rank', 'Unranked'),
                    'kdaRatio': round(percentile_block.get('kdaRatio', 0), 2)
                }
            
            elif slide_number == 15:  # Final Recap
                time_data = analytics.get('slide2_timeSpent', {})
                ranked = analytics.get('slide6_rankedJourney', {})
                champions = analytics.get('slide3_favoriteChampions', [])
                top_champ = champions[0]['name'] if champions else 'None'
                
                total_hours = time_data.get('totalHours')
                if total_hours is None:
                    total_minutes = time_data.get('totalMinutes')
                    total_hours = round((total_minutes or 0) / 60, 1)

                kda = analytics.get('slide5_kda', {})
                kda_ratio = round(kda.get('kdaRatio', 0), 2)

                win_rate = ranked.get('winRate') if ranked.get('winRate') is not None else analytics.get('slide14_percentile', {}).get('yourWinRate')
                try:
                    win_rate = round(float(win_rate), 1) if win_rate is not None else 0.0
                except Exception:
                    win_rate = 0.0

                duo = analytics.get('slide9_duoPartner', {})
                partner_name = duo.get('partnerName') if duo else None

                template_data = {
                    'totalGames': time_data.get('totalGames', 0),
                    'totalHours': total_hours or 0,
                    'currentRank': ranked.get('currentRank', 'Unranked'),
                    'topChampion': top_champ,
                    'kdaRatio': kda_ratio,
                    'winRate': win_rate,
                    'partnerName': partner_name or 'your duo'
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
        
        # Meta Llama 3.1 chat template
        system_prompt = """You are a CONTEXT-AWARE League of Legends roaster analyzing player performance.

GOOD players: Sarcastic respect, backhanded compliments, "sarcastic" jokes
AVERAGE players: Light roasts, modest mockery, "you're trying" energy  
BAD players: Brutal destruction, savage roasts, "why do you even play" vibes

Read the stats. Match your tone to their skill level. Be funny, not generic.

WRITING STYLE:
Write in a conversational, human voice with a friendly tone that isn't colloquial. 
Use short sentences and simple words. 
Remove academic language, transition phrases, and corporate jargon. 
Make it sound like someone talking to a friend in simple terms. 
Keep the key points but strip away any unnecessary words.

NO EMOJIS. NO EM DASHES (—). Use commas instead and hyphens (-) if necessary. Max 30 words."""
        
        # Llama chat template format
        llama_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        
        request_body = {
            "prompt": llama_prompt,
            "max_gen_len": 100,  
            "temperature": 0.9,  
            "top_p": 0.95  
        }
        
        # Invoke Bedrock
        response = self.bedrock_client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        humor_text = response_body.get('generation', '').strip()
        
        # Clean up any quotes or extra formatting
        humor_text = humor_text.strip('"').strip("'").strip()
        
        # Remove any emojis that might have been generated
        import re
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  
            u"\U0001F300-\U0001F5FF"  
            u"\U0001F680-\U0001F6FF"  
            u"\U0001F1E0-\U0001F1FF"  
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001F900-\U0001F9FF"  
            u"\U0001FA00-\U0001FAFF"  
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
            'generatedAt': json.dumps({"timestamp": "now"}) 
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
        
        print(f"PRIORITY GENERATION: Slides 1-5 for session {session_id}")
        
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
        
        print(f"BACKGROUND GENERATION: Slides 6-15 for session {session_id}")
        
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
        
        print(f"FULL REGENERATION: All slides with complete data for session {session_id}")
        
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
        print(f"GENERATION COMPLETE!")
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