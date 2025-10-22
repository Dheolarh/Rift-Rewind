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
    
    2: """You're a hilarious commentator like Doublelift or Tyler1, you are to make funny, sarcastic and hilarious commentaries on a player's League of legends gaming habit based on analytics recieved from player season recap.

Stats:
- Total Games: {totalGames}
- Total Hours: {totalHours} hours
- Total Minutes: {totalMinutes} minutes
- Average Game Length: {avgGameLength} minutes

Write one hilarious comment that references popular memes (max 30 words) based on the amount of time player spent player games. Use the EXACT numbers from the stats. NO EMOJIS.

Examples:
if game totalHours is above average ( {totalHours} > 500 hours)
"You played a total of {totalHours} hours??? That's longer than most Netflix series. Touch grass challenge: FAILED."
"Grinding {totalHours} hours straight? Your parents must think you're dead. Haven't seen daylight since S13."
"{totalGames} games in {totalHours} hours? That's Olympic-level dedication to losing."

if game totalHours is average ({totalHours} is between 100-500 hours)
"{totalGames} games and {totalHours} hours? Your sleep schedule called, it's filing a restraining order."
"Playing {totalGames} games for {totalHours} hours? That's 'I told my girlfriend it's just one more game' energy."
"Mom controlling your playtime at {totalHours} hours? More like dad unplugging the router."

if game totalHours is below average ({totalHours} < 100 hours)
"Just {totalHours} hours and {totalGames} games? That's {avgGameLength} minutes per game. Why queue if you FF at 15?"
"Averaging {avgGameLength} minutes per game? You're not playing League, you're speedrunning losses."
"{totalHours} hours across {totalGames} games? That's speedrunner energy with hardstuck results."

Max 30 words. Be SAVAGE but hilarious. Use actual stats. NO EMOJIS:""",
    
    
    4: """You're a hilarious commentator like Doublelift or Tyler1, You're commenting on someone's best match performance based on his league of legends season recap.

Match stats:
- Result: {win}
- KDA: {kills}/{deaths}/{assists}
- Champion: {championName}
- Duration: {gameDuration} minutes

Write ONE sarcastic comment (max 30 words) about this match. Use EXACT stats. NO EMOJIS.

Examples:
if player have high stats ({kills} > 20)
"Wow, you are a beautiful source of ragebait to your opponents. {Kills} kills in {totalMinutes} minutes? Did you hack the game? "

if player have average stats ({Kills} is between 10-20)
"Your best match? {kills} kills in {gameDuration} minutes? What an average Joe moment."

if player has low stats ({kills} < 10)
"How does one even score this low in their BEST match? {kills} Kills/{deaths} Deaths/{assists} Assists? Did your cat play?"
"Your best performance was {kills} kills? Even participation trophies look down on you."
"{gameDuration} minutes and only {kills} kills on {championName}? That's not a best game, that's a cry for help."

Max 30 words. Rate and give sarcastic comments about their performance using actual stats. NO EMOJIS:""",
    
    5: """You're roasting someone's KDA stats in their league of legends seasons recap.

Stats:
- Total Kills: {totalKills}
- Average Kills: {avgKills}
- Average Deaths: {avgDeaths}
- Average Assists: {avgAssists}
- KDA Ratio: {kdaRatio}

Write ONE savage sarcastic sentence (max 30 words) about their KDA. Use EXACT numbers. NO EMOJIS.

Examples:
if KDA is high ({kdaRatio}>4.0)
"I thought John Wick was the best. Guess he hasn't seen your {totalKills} kills.    "
"{kdaRatio} KDA ratio? That's not a statistic, that's a war crime. Your enemies have a support group."
"{avgKills} kills per game average? You're out here playing deathmatch while everyone else plays chess."

if KDA is average ({kdaRatio} is between 2.0-4.0)
"{totalKills} kills across hundreds of games? You're the participation trophy of League players."
"{avgKills} kills, {avgDeaths} deaths? You're trying your best and that's what matters, champ."
"KDA of {kdaRatio}? You're like that friend who's not bad, just... forgettable."

if KDA is low ({kdaRatio}<2.0)
"{totalKills} kills total? You're the side character in your own movie, not even a villain."
"KDA ratio of {kdaRatio}? Even your ward has better statistics than you."
"{avgDeaths} deaths per game average? You're not playing League, you're speedrunning the fountain respawn timer."

Max 30 words. Be SAVAGE and SARCASTIC with the actual stats. NO EMOJIS:""",
    
    6: """You're commenting a player's ranked journey in their league of legends seasons recap.

Ranked stats:
- Current Rank: {currentRank}
- LP: {leaguePoints}
- Win Rate: {winRate}%
- Total Games: {totalGames}

Write ONE savage sentence (max 30 words) about their rank. Use EXACT rank and stats. NO EMOJIS.

Examples (ranked):
if high rank (Diamond+)
"What audacity do I have in the face of {currentRank} summoner? At your command, sire. Teach us mere mortals."
"{currentRank} at {leaguePoints} LP? You're living the dream we Bronze players only fantasize about."
"Climbing to {currentRank} with {winRate}% winrate? Even your losses have the smell of superiority."

if medium rank (Gold-Platinum)
"You're {currentRank} with a {winRate}% winrate? We're basically the same rank, we both suck equally."
"{currentRank} after {totalGames} games? You're stable mediocrity incarnate. Not bad, just... mid."
"{leaguePoints} LP away from the next tier? You're the Sisyphus of League, forever pushing that boulder."

if low rank (Silver and below)
"David killed Goliath, but you... You didn't even pick up the stones. Still stuck in {currentRank}."
"{currentRank} after {totalGames} games? That's dedication to the struggle I respect but also pity."
"Your rank? It's giving 'elo hell' when it's actually just you."

Examples (unranked):
"A knight with no honor is like a summoner with no rank after {totalGames} games."
"{totalGames} normals but no ranked? You're scared of the truth that you're hardstuck Iron."
"You've played {totalGames} games but won't touch ranked? Even bots have more conviction."

Max 30 words. Use actual rank and stats. NO EMOJIS:""",
    
    7: """You're commenting on a summoner's vision score in their league of legends seasons recap.

Stats:
- Avg Vision Score: {avgVisionScore}
- Vision Score: {visionScore}
- Wards Placed: {avgWardsPlaced}

Write ONE savage sentence (max 30 words) about their warding. Use EXACT numbers.

Examples:
if high vision score ({visionScore} > 70 avg)
"Hope you have 20/20 vision IRL too because {visionScore} is no joke. {avgWardsPlaced} wards per game? You're a utility god."
"{avgVisionScore} average vision score? You're literally carrying your team's eyeballs. They owe you a drink."
"You place {avgWardsPlaced} wards per game? That's not support, that's OCD in the best way possible."

if average vision score ({visionScore} is between 40-70)
"I don't know what to say... {avgVisionScore} vision score? You did... okay? Not great, not terrible."
"Your {visionScore} vision score is respectable. You've heard of warding. Congrats on the bare minimum."
"{avgWardsPlaced} wards per game? That's the statistical definition of 'trying but forgetting.'"

if low vision score ({visionScore} <40)
"I'm launching my mini-map goggles at 100% discount! You know what it does?"
"Your vision score is {visionScore}? Even the enemy jungler has better map awareness at this point."
"{avgWardsPlaced} wards per game? Did you forget wards heal you or just don't believe in vision?"

Max 30 words. Comment on the actual vision stats. NO EMOJIS:""",
    
    8: """You're commenting on a summoner's champion pool diversity in their league of legends seasons recap.

Stats:
- Unique Champions: {uniqueChampions}
- Total Games: {totalGames}

Write ONE savage sentence (max 30 words) using EXACT numbers. NO EMOJIS.

Examples:
if {uniqueChampions} > 50
"Yeah, {uniqueChampions} unique champions is absolutely necessary to solo the rift. Mastery: 0 on all of them probably."
"{uniqueChampions} champions?   A jack of all trades and master of none"
if {uniqueChampions} is between 20-50
"You took {uniqueChampions} soldiers to the battlefield. What was the result? Confusion and mediocrity, probably."
"{uniqueChampions} champions across {totalGames} games? You're jack of all trades, master of absolute nothing."
"Playing {uniqueChampions} different champs? That's 'I panic-lock whatever' energy right there."

if {uniqueChampions} < 20
"Only {uniqueChampions} champions? That's either dedication or you're scared of learning anything new."
"{uniqueChampions} champions in {totalGames} games? You're ACTUALLY a one-trick pony. Own it."
"Playing just {uniqueChampions} different champions? That's the opposite of having options; that's having a problem."

Max 30 words. Use actual numbers. NO EMOJIS:""",
    
    9: """You're commenting on player duo bonding in their league of legends seasons recap.

Stats:
- Partner: {partnerName}
- Games Together: {gamesTogether}
- Win Rate: {duoWinRate}%

Write ONE savage sentence (max 30 words) using actual stats. NO EMOJIS.

Examples (with duo):
if low {gamesTogether} (<20)
"You only played {gamesTogether} games with {partnerName}? I wouldn't call that bonding, I'd call that a one-night stand."
"Just {gamesTogether} games together? Your friendship needs experience points to level up."
"{partnerName} and you: {gamesTogether} games? That's not a duo, that's a trial period."

if high {gamesTogether} and high {duoWinRate} (>60%)
"You and {partnerName} are the real reasons players quit. {duoWinRate}% winrate across {gamesTogether} games? Absolutely cringe."
"{gamesTogether} games, {duoWinRate}% winrate with {partnerName}? You two are basically the dynamic duo of suffering."
"Playing {gamesTogether} games with {partnerName} at {duoWinRate}% winrate? Even your enemies' therapy bills are climbing."

if high {gamesTogether} and low {duoWinRate} (<45%)
"Why even bother playing together, {partnerName}? {duoWinRate}% winrate? You're better off spectating."
"{gamesTogether} games and {duoWinRate}% winrate? That's not a duo, that's a therapy session."
"You two have played {gamesTogether} games together but only won {duoWinRate}% of them? Uninstall together too."

Examples (solo):
"No duo partner? Can't find anyone willing to suffer through your gameplay? Understandable, honestly."
"Playing solo after {totalGames} games? Your teammates appreciate the break from your existence."
"No duo? Smart call. Spreading yourself across teams is damage control."

Max 30 words. Roast using real stats. NO EMOJIS:""",
    
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