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

SYSTEM_PROMPT = """
You are a toxic, sarcastic, and brutally honest League of Legends streamer reviewing a viewer's year-in-review. 
Your persona is "The Sleazy Roaster" — you are mean, funny, and use Twitch/League slang.

RULES:
1. Be direct and roast/sarcastically compliment them based on their stats.
2. Do NOT be polite. Do NOT be encouraging unless it's backhanded.
3. Use short, punchy sentences.
4. If they are GOOD: Sarcastically praise them with a backhanded compliment and roast them.
5. If they are AVERAGE: Roast them for being mediocre/boring/NPC, your everyday player.
6. If they are BAD: Roast them for being terrible/griefing/blind.
7. Don't start responses with Congrats/Congratulations.
8. Strictly diverse from given Examples when generating response, think of something unique or different but goes with the context.

WRITING STYLE:
- write it in a conversational, human voice, with a friendly tone that isn’t colloquial. Use short sentences and simple words. Remove academic language, transition phrases, and corporate jargon. Make it sound like someone talking to a friend in simple terms. Keep the key points but strip away any unnecessary words.
- NO EMOJIS. NO EM DASHES (—) or EM SPACES (\u2003). NO HYPHENS (-), NO NEW LINES.
"""

SLIDE_PROMPTS = {

    2: """
CONTEXT: The player's total time spent on League this season.

STATS: {totalGames} games, {totalHours} hours, {avgGameLength} min/game

LOGIC (Select ONE based on stats):
- **HIGH (300+ hours):** They have no life. Roast them for crazy addiction.
- **AVERAGE (100-299 hours):** They are stuck in the middle. Roast them for being a "casual" or tell them to run away while they can.
- **LOW (<100 hours):** They barely played. Roast them for being a "casual" or tell them to run away while they can.

TASK: Write a 1 sentence roast based on the logic above with a maximum of 15 words.
Examples:
Good (High Hours): "That's like the entire season of Game of Thrones. Imagine if you put that time into a job, or a relationship, or literally anything else. You're not a pro, you're just unemployed."
Average: "You played 150 hours I hope that's not a terrible ROI. You're wasting your life for +14 LP."
Poor (Low Hours): "You barely played. Honestly? Good. Save yourself. Uninstall now before you end up like the degenerates in this chat."
Note that examples are just guidelines, not rules.
""",

    3: None,

    4: """
CONTEXT: The player's best match of the season.

STATS: {win}, {kills}/{deaths}/{assists} on {championName} ({gameDuration} min)

LOGIC (Select ONE based on stats):
- **HIGH (Victory + High KDA):** Give them sarcastic backhanded compliment, roast them for believing they are pro.
- **AVERAGE:** It was a fluke. Roast them for having only one good game all year.
- **LOW (Defeat or Poor KDA):** They got carried. Roast them for being a "glorified minion" or "backpack".

TASK: Write a 1 sentence roast based on the logic above with a maximum of 15 words.
""",

    5: """
CONTEXT: The player's Total kills.

STATS: {totalKills} total kills

LOGIC (Select ONE based on stats):
- **HIGH (>1500 kills):** They basically cleared the rift. Roast them for being a pain in the ass to their opponents, try to give your opponents a break.
- **AVERAGE (200-1500 kills):** That's an average player. Let them know they are just like everyone average player.
- **LOW (<200 kills):** They are feeding. Roast them for even playing when they will just keep dying then ragequit.

TASK: Write a 1 sentence roast based on the logic above with a maximum of 15 words.
""",

    6: """
CONTEXT: The player's ranked performance.

STATS: {currentRank}, {winRate}% Win Rate, {totalGames} games

LOGIC (Select ONE based on stats):
- **HIGH (Challenger):** They are a "Challenger". Sarcastically compliment them for the hardwork and sweat put in.
- **ALMOST A CHALLENGER(Diamond++):** They are a "high ranked player but not challenger". Tell them they are close but not close enough in a sarcastic tone.
- **AVERAGE (Gold/Plat):** They are "hardstuck". Roast them for playing hundreds of games to stay in the same average rank.
- **LOW (Iron/Bronze/Silver):** They are bad. Roast them for having "no hands" or playing with their monitor off.

TASK: Write a 1 sentence roast based on the logic above with a maximum of 15 words.
""",

    7: """
CONTEXT: The player's vision score and warding habits.

STATS: {avgVisionScore} vision score, {avgWardsPlaced} wards/game, {avgControlWardsPurchased} control wards

LOGIC (Select ONE based on stats):
- **HIGH (45+ score):** They are paranoid. Roast them for being scared of the dark or having zero mechanics so they just ward.
- **AVERAGE (20-44 score):** They ward the same bush every game. Roast their lack of map awareness.
- **LOW (<20 score):** They are blind. Roast them for saving gold on control wards like a cheapskate.

TASK: Write a 1 sentence roast based on the logic above with a maximum of 15 words.
""",

    8: """
CONTEXT: The player's champion pool diversity.

STATS: {uniqueChampions} unique champs, {totalGames} total games, {diversityScore} diversity score

LOGIC (Select ONE based on stats):
- **HIGH (One-trick / Low Diversity):** They are a one-champion spammer. Roast them for being unable to play anything else, fear of loss?.
- **AVERAGE:** They are a "meta slave". Roast them for just copying what pros play.
- **LOW (High Diversity):** They have an identity crisis. Roast them for playing 50 champs and mastering none.

TASK: Write a 1 sentence roast based on the logic above with a maximum of 15 words.
""",

    9: """
CONTEXT: The player's performance with their duo partner.

STATS: Duo with {partnerName}, {gamesTogether} games, {winRate}% Win Rate

LOGIC (Select ONE based on stats):
- **HIGH (>70% WR):** They are boosted. Roast them for being a menace to other players.
- **AVERAGE (50-70% WR):** They are like every average duo trying to be the cool duo. Roast them for not finding the perfect chemistry, they should keep on trying.
- **LOW (<50% WR):** They are a bad combination but still play together. Roast them for being an NPC duo.

TASK: Write a 1 sentence roast based on the logic above with a maximum of 15 words.
""",

    10: None,
    11: None,

    "10_HEADLINE": """
CONTEXT: Analyze the player's stats to find their biggest STRENGTH.
STATS: {stats_summary}

TASK: Identify player's stenghts and write a clear sentence identifying it.
OUTPUT: Just the sentence. Max 10 words.
""",

    "10_BODY": """
CONTEXT: The player's strength is "{headline}".
STATS: {stats_summary}

TASK: Write 1-2 sentences of coaching advice on prospective utilization of this strength.
Make it sound sarcastic but genuine.
""",

    "11_HEADLINE": """
CONTEXT: Analyze the player's stats to find their biggest WEAKNESS.
STATS: {stats_summary}

TASK: Identify player's weakness and write a clear sentence identifying it.

OUTPUT: Just the title. Max 10 words.
""",

    "11_BODY": """
CONTEXT: The player's weakness is "{headline}".
STATS: {stats_summary}

TASK: Write 1-2 sentences of coaching advice based on this weakness.
Tell them how to fix it but be strict about it and also give them a little movtivation.
""",

    12: None,

    14: """
CONTEXT: The player's global percentile rank.

STATS: {currentRank}, Top {percentile}% of players

LOGIC (Select ONE based on stats):
- **HIGH (Top 10%):** They are the "King of Nerds". Roast them for being proud of a number nobody cares about.
- **AVERAGE:** They are an average player. Sarcastically roast/praise them for their contributing to the leaderboard.
- **LOW (Bottom 20%):** They are the content. Roast them for being the players that streamers laugh at.

TASK: Write a 1 sentence roast based on the logic above with a maximum of 15 words.
""",

    15: """
CONTEXT: The final farewell and season wrap-up also it's christmas season.

STATS: {totalGames} games, {totalHours} hours, {currentRank}, {topChampion}

LOGIC (Select ONE based on stats):
- **GOOD Season:** Tell them to "get a life" now that the season is over but we miss them so they should come back quickly and a happy holidays.
- **AVERAGE Season:** Tell them that was a good season, quite enjoyable and you'll see them next year for another season of mediocrity and happy holidays.
- **BAD Season:** Beg them to uninstall for the sake of the community or if they don't feel tortured they can come for a redemption arc but still you enjoyed the season with them and happy holidays.

TASK: Write a 2-3 sentence closing write-up minimum of 30 words and maximum of 40 words.
""",

    16: """
CONTEXT: Analyze the player's stats to find a fitting title.
STATS: {stats_summary}

TASK: Generate a creative, funny, 2,3,or 4-word title for this player based on League of Legends lore or their playstyle.
Examples: "The Rift Lord", "Lord of the Rift", "Feeder of Legends", "The Rift Seeker", "The Guide to freedom, "KDA Saver" These examples just serve as guide I'm not asking you to use them.

OUTPUT: Just the title. Max 4 words.
"""
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
        
        analytics_str = download_from_s3(s3_key)
        if not analytics_str:
            raise ValueError(f"Analytics not found for session: {session_id}")
        
        # Parse JSON string to dict
        analytics = json.loads(analytics_str) if isinstance(analytics_str, str) else analytics_str
        
        return analytics
    
    def create_prompt(self, slide_number: Any, analytics: Dict[str, Any], headline: str = None) -> Optional[str]:
        """
        Create slide-specific prompt for Bedrock.
        
        Args:
            slide_number: Slide number (int) or Key (str) like "10_HEADLINE"
            analytics: Analytics data
            headline: Optional headline for body generation
        
        Returns:
            Formatted prompt string or None if no humor needed
        """
        if slide_number not in SLIDE_PROMPTS or SLIDE_PROMPTS[slide_number] is None:
            return None
        
        template = SLIDE_PROMPTS[slide_number]
        
        # Map analytics to template variables for each slide
        template_data = {}
        
        try:
            # Special handling for Strengths/Weaknesses (Headline & Body) AND Player Title (Slide 16)
            if str(slide_number).startswith("10_") or str(slide_number).startswith("11_") or slide_number == 16:
                # Gather full stats summary
                ranked = analytics.get('slide6_rankedJourney', {})
                kda = analytics.get('slide5_kda', {})
                vision = analytics.get('slide7_visionScore', {})
                pool = analytics.get('slide8_championPool', {})
                
                # Advanced Analytics (from slide10_11_analysis aiContext)
                adv_analysis = analytics.get('slide10_11_analysis', {}).get('aiContext', {})
                patterns = adv_analysis.get('championPatterns', {})
                classes = adv_analysis.get('classPerformance', {})
                playstyle = adv_analysis.get('playstyle', {})
                duo = adv_analysis.get('duoStats', {})
                
                stats_summary = (
                    f"Rank: {ranked.get('currentRank', 'Unranked')} ({ranked.get('winRate', 0)}% WR). "
                    f"KDA: {round(kda.get('kdaRatio') or 0, 2)}. "
                    f"Vision: {round(vision.get('avgVisionScore') or 0, 1)}. "
                    f"Playstyle: {playstyle.get('avgKP', 0)}% KP, {playstyle.get('avgDmgShare', 0)}% Dmg Share. "
                )
                
                # Add Pattern Insights
                if patterns.get('highestWinRate') is not None:
                    stats_summary += f"Best Champ: {patterns['highestWinRate']['name']} ({round(patterns['highestWinRate']['winRate'])}% WR). "
                if patterns.get('highestDeathAvg') is not None:
                    stats_summary += f"Feeder Champ: {patterns['highestDeathAvg']['name']} ({round(patterns['highestDeathAvg']['avgDeaths'], 1)} deaths/game). "
                
                # Add Class Insights
                if classes.get('bestClass') is not None:
                    stats_summary += f"Best Class: {classes['bestClass']['class']} ({classes['bestClass']['winRate']}% WR). "
                
                # Add Win/Loss Correlations
                win_stats = playstyle.get('winStats', {})
                loss_stats = playstyle.get('lossStats', {})
                if win_stats and loss_stats:
                    stats_summary += f"In Wins: {win_stats.get('kp')}% KP, {win_stats.get('dmgShare')}% Dmg. "
                    stats_summary += f"In Losses: {loss_stats.get('kp')}% KP, {loss_stats.get('dmgShare')}% Dmg. "
                
                # Add Duo Context
                if duo.get('partner') != 'None':
                    stats_summary += f"Duo: {duo.get('partner')} ({duo.get('winRateWithDuo')}% WR). "
                
                # Add Objective Control Metrics
                objectives = adv_analysis.get('objectiveControl', {})
                if objectives:
                    stats_summary += f"Objectives: {objectives.get('dragonParticipation', 0)}% Dragons, {objectives.get('towerDamageShare', 0)}% Tower Dmg. "
                
                # Add Farming Metrics
                farming = adv_analysis.get('farming', {})
                if farming:
                    stats_summary += f"Farming: {farming.get('csPerMin', 0)} CS/min, {farming.get('goldPerMin', 0)} GPM. "
                
                template_data = {
                    'stats_summary': stats_summary,
                    'headline': headline or "Unknown"
                }
            elif slide_number == 2:  # Time Spent
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
            return template  # Return unformatted template as fallback
        except Exception as e:
            return template
    
    def call_bedrock(self, prompt: str) -> str:
        """
        Call Bedrock to generate humor using Meta Llama.
        
        Args:
            prompt: Prompt string
        
        Returns:
            Generated humor text
        """
        
        # Meta Llama 3.1 chat template
        llama_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{SYSTEM_PROMPT}<|eot_id|><|start_header_id|>user<|end_header_id|>

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
        
        logger.info(f" Generated humor: {humor_text}")
        return humor_text
    
    def store_humor(self, session_id: str, slide_number: int, humor_text: str, headline: str = None):
        """
        Store humor in S3.
        
        Args:
            session_id: Session ID
            slide_number: Slide number
            humor_text: Generated humor text
            headline: Optional generated headline (for slides 10/11)
        """
        s3_key = f"sessions/{session_id}/humor/slide_{slide_number}.json"
        
        data = {
            'sessionId': session_id,
            'slideNumber': slide_number,
            'humorText': humor_text,
            'generatedAt': json.dumps({"timestamp": "now"}) 
        }

        # If headline is provided (AI generated), use it.
        if headline:
            data['headline'] = headline
            if slide_number == 10:
                data['headlineType'] = 'strength'
            elif slide_number == 11:
                data['headlineType'] = 'weakness'
        
        # Special handling for Slide 16 (Player Title)
        if slide_number == 16:
            data['headline'] = humor_text
            data['headlineType'] = 'personality_title'

        upload_to_s3(s3_key, data)
        logger.info(f"Stored humor for session {session_id} slide {slide_number} (headline: {headline})")
    
    def generate(self, session_id: str, slide_number: int) -> Dict[str, Any]:
        """
        Generate humor for a specific slide.
        
        Args:
            session_id: Session ID
            slide_number: Slide number (1-15)
        
        Returns:
            Result dict with humor text
        """
        
        # Step 1: Download analytics
        analytics = self.download_analytics(session_id)

        # Step 2: Special Two-Step Generation for Slides 10 & 11
        if slide_number in (10, 11):
            # 2a. Generate Headline
            headline_prompt = self.create_prompt(f"{slide_number}_HEADLINE", analytics)
            headline = self.call_bedrock(headline_prompt) if headline_prompt else "Generic Player"
            
            # 2b. Generate Body using Headline
            body_prompt = self.create_prompt(f"{slide_number}_BODY", analytics, headline=headline)
            humor_text = self.call_bedrock(body_prompt) if body_prompt else "Keep playing."
            
            # 2c. Store both
            self.store_humor(session_id, slide_number, humor_text, headline=headline)
            
            return {
                'sessionId': session_id,
                'slideNumber': slide_number,
                'humorText': humor_text,
                'headline': headline,
                'status': 'success'
            }

        # Step 3: Standard Generation for other slides
        prompt = self.create_prompt(slide_number, analytics)
        
        if not prompt:
            return {
                'sessionId': session_id,
                'slideNumber': slide_number,
                'humorText': None,
                'status': 'no_humor_needed'
            }
        
        # Step 4: Generate humor
        humor_text = self.call_bedrock(prompt)
        
        # Step 5: Store result
        self.store_humor(session_id, slide_number, humor_text)
        
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
        
        
        priority_slides = [1, 2, 3, 4, 5]
        results = {}
        session_manager = SessionManager()
        
        for slide_num in priority_slides:
            
            try:
                result = self.generate(session_id, slide_num)
                humor_text = result.get('humor', '')
                
                # Save to session checkpoint
                if humor_text:
                    session_manager.update_humor(session_id, slide_num, humor_text)
                    results[f"slide{slide_num}"] = humor_text
                else:
                    results[f"slide{slide_num}"] = None
                    
            except Exception as e:
                results[f"slide{slide_num}"] = None
        
        logger.info(f" Priority generation complete ({len([r for r in results.values() if r])}/5 slides)")
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
        
        
        background_slides = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        results = {}
        session_manager = SessionManager()
        
        for slide_num in background_slides:
            
            try:
                result = self.generate(session_id, slide_num)
                humor_text = result.get('humor', '')
                
                # Save to session checkpoint
                if humor_text:
                    session_manager.update_humor(session_id, slide_num, humor_text)
                    results[f"slide{slide_num}"] = humor_text
                else:
                    results[f"slide{slide_num}"] = None
                    
            except Exception as e:
                results[f"slide{slide_num}"] = None
        
        logger.info(f" Background generation complete ({len([r for r in results.values() if r])}/10 slides)")
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
        
        
        all_slides = range(1, 16)  # Slides 1-15
        results = {}
        session_manager = SessionManager()
        
        for slide_num in all_slides:
            
            try:
                result = self.generate(session_id, slide_num)
                humor_text = result.get('humor', '')
                
                # Save to session checkpoint
                if humor_text:
                    session_manager.update_humor(session_id, slide_num, humor_text)
                    results[f"slide{slide_num}"] = humor_text
                else:
                    results[f"slide{slide_num}"] = None
                    
            except Exception as e:
                results[f"slide{slide_num}"] = None
        
        logger.info(f" Full regeneration complete ({len([r for r in results.values() if r])}/15 slides)")
        
        # Notify that regeneration is complete
        
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
                    'message': 'Full regeneration complete'
                })
            }
        
        # Default: Single slide generation
        if not slide_number:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameter: slideNumber'
                })
            }
            
        result = generator.generate(session_id, slide_number)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }