"""
Analytics Module: analytics.py
Purpose: Calculate statistics for all slides
"""

import logging
from typing import Dict, Any, List, Optional
from collections import Counter, defaultdict
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)

CHAMPION_CLASSES = {
    'Assassin': [
        {'name': 'Akali', 'secondary': []},
        {'name': 'Akshan', 'secondary': ['Marksman']},
        {'name': 'Diana', 'secondary': ['Fighter']},
        {'name': 'Ekko', 'secondary': ['Fighter']},
        {'name': 'Evelynn', 'secondary': ['Mage']},
        {'name': 'Fizz', 'secondary': ['Fighter']},
        {'name': 'Kassadin', 'secondary': ['Mage']},
        {'name': 'Katarina', 'secondary': ['Mage']},
        {'name': 'KhaZix', 'secondary': []},
        {'name': 'LeBlanc', 'secondary': ['Mage']},
        {'name': 'MasterYi', 'secondary': ['Fighter']},
        {'name': 'Naafiri', 'secondary': []},
        {'name': 'Nidalee', 'secondary': ['Mage']},
        {'name': 'Nocturne', 'secondary': ['Fighter']},
        {'name': 'Pyke', 'secondary': ['Support']},
        {'name': 'Qiyana', 'secondary': ['Fighter']},
        {'name': 'Rengar', 'secondary': ['Fighter']},
        {'name': 'Shaco', 'secondary': []},
        {'name': 'Talon', 'secondary': []},
        {'name': 'Viego', 'secondary': ['Fighter']},
        {'name': 'Yone', 'secondary': ['Fighter']},
        {'name': 'Zed', 'secondary': []}
    ],
    'Fighter': [
        {'name': 'Aatrox', 'secondary': ['Tank']},
        {'name': 'Ambessa', 'secondary': ['Assassin']},
        {'name': 'BelVeth', 'secondary': []},
        {'name': 'Briar', 'secondary': ['Assassin']},
        {'name': 'Camille', 'secondary': ['Tank']},
        {'name': 'Darius', 'secondary': ['Tank']},
        {'name': 'DrMundo', 'secondary': ['Tank']},
        {'name': 'Fiora', 'secondary': ['Assassin']},
        {'name': 'Gangplank', 'secondary': []},
        {'name': 'Garen', 'secondary': ['Tank']},
        {'name': 'Gnar', 'secondary': ['Tank']},
        {'name': 'Gragas', 'secondary': ['Mage']},
        {'name': 'Gwen', 'secondary': ['Assassin']},
        {'name': 'Hecarim', 'secondary': ['Tank']},
        {'name': 'Illaoi', 'secondary': ['Tank']},
        {'name': 'Irelia', 'secondary': ['Assassin']},
        {'name': 'Jax', 'secondary': ['Assassin']},
        {'name': 'Jayce', 'secondary': ['Marksman']},
        {'name': 'Kayle', 'secondary': ['Support']},
        {'name': 'Kayn', 'secondary': ['Assassin']},
        {'name': 'Kled', 'secondary': ['Tank']},
        {'name': 'LeeSin', 'secondary': ['Assassin']},
        {'name': 'Lillia', 'secondary': ['Mage']},
        {'name': 'Mordekaiser', 'secondary': ['Mage']},
        {'name': 'Nasus', 'secondary': ['Tank']},
        {'name': 'Nilah', 'secondary': ['Assassin']},
        {'name': 'Olaf', 'secondary': ['Tank']},
        {'name': 'Pantheon', 'secondary': ['Assassin']},
        {'name': 'RekSai', 'secondary': ['Tank']},
        {'name': 'Renekton', 'secondary': ['Tank']},
        {'name': 'Riven', 'secondary': ['Assassin']},
        {'name': 'Rumble', 'secondary': ['Mage']},
        {'name': 'Sett', 'secondary': ['Tank']},
        {'name': 'Shyvana', 'secondary': ['Tank']},
        {'name': 'Skarner', 'secondary': ['Tank']},
        {'name': 'Trundle', 'secondary': ['Tank']},
        {'name': 'Tryndamere', 'secondary': ['Assassin']},
        {'name': 'Udyr', 'secondary': ['Tank']},
        {'name': 'Urgot', 'secondary': ['Tank']},
        {'name': 'Vi', 'secondary': ['Assassin']},
        {'name': 'Volibear', 'secondary': ['Tank']},
        {'name': 'Warwick', 'secondary': ['Tank']},
        {'name': 'Wukong', 'secondary': ['Tank']},
        {'name': 'XinZhao', 'secondary': ['Assassin']},
        {'name': 'Yasuo', 'secondary': ['Assassin']},
        {'name': 'Yorick', 'secondary': ['Tank']}
    ],
    'Mage': [
        {'name': 'Ahri', 'secondary': ['Assassin']},
        {'name': 'Anivia', 'secondary': ['Support']},
        {'name': 'Annie', 'secondary': ['Support']},
        {'name': 'AurelionSol', 'secondary': []},
        {'name': 'Aurora', 'secondary': ['Assassin']},
        {'name': 'Azir', 'secondary': ['Marksman']},
        {'name': 'Brand', 'secondary': []},
        {'name': 'Cassiopeia', 'secondary': []},
        {'name': 'Elise', 'secondary': ['Fighter']},
        {'name': 'Fiddlesticks', 'secondary': ['Support']},
        {'name': 'Heimerdinger', 'secondary': ['Support']},
        {'name': 'Hwei', 'secondary': []},
        {'name': 'Karthus', 'secondary': []},
        {'name': 'Kennan', 'secondary': ['Marksman']},
        {'name': 'KogMaw', 'secondary': ['Marksman']},
        {'name': 'LeBlanc', 'secondary': ['Assassin']},
        {'name': 'Lissandra', 'secondary': []},
        {'name': 'Lux', 'secondary': ['Support']},
        {'name': 'Malzahar', 'secondary': ['Assassin']},
        {'name': 'Mel', 'secondary': []},
        {'name': 'Morgana', 'secondary': ['Support']},
        {'name': 'Neeko', 'secondary': ['Support']},
        {'name': 'Orianna', 'secondary': ['Support']},
        {'name': 'Ryze', 'secondary': ['Fighter']},
        {'name': 'Seraphine', 'secondary': ['Support']},
        {'name': 'Swain', 'secondary': ['Fighter']},
        {'name': 'Sylas', 'secondary': ['Assassin']},
        {'name': 'Syndra', 'secondary': []},
        {'name': 'Taliyah', 'secondary': ['Support']},
        {'name': 'TwistedFate', 'secondary': []},
        {'name': 'Veigar', 'secondary': []},
        {'name': 'VelKoz', 'secondary': ['Support']},
        {'name': 'Vex', 'secondary': []},
        {'name': 'Viktor', 'secondary': []},
        {'name': 'Vladimir', 'secondary': ['Tank']},
        {'name': 'Xerath', 'secondary': ['Support']},
        {'name': 'Ziggs', 'secondary': []},
        {'name': 'Zoe', 'secondary': ['Support']},
        {'name': 'Zyra', 'secondary': ['Support']}
    ],
    'Marksman': [
        {'name': 'Aphelios', 'secondary': []},
        {'name': 'Ashe', 'secondary': ['Support']},
        {'name': 'Caitlyn', 'secondary': []},
        {'name': 'Corki', 'secondary': []},
        {'name': 'Draven', 'secondary': []},
        {'name': 'Ezreal', 'secondary': ['Mage']},
        {'name': 'Graves', 'secondary': []},
        {'name': 'Jhin', 'secondary': ['Mage']},
        {'name': 'Jinx', 'secondary': []},
        {'name': 'KaiSa', 'secondary': ['Assassin']},
        {'name': 'Kalista', 'secondary': []},
        {'name': 'Kindred', 'secondary': []},
        {'name': 'Lucian', 'secondary': []},
        {'name': 'MissFortune', 'secondary': []},
        {'name': 'Quinn', 'secondary': ['Assassin']},
        {'name': 'Samira', 'secondary': []},
        {'name': 'Senna', 'secondary': ['Support']},
        {'name': 'Sivir', 'secondary': []},
        {'name': 'Smolder', 'secondary': []},
        {'name': 'Teemo', 'secondary': ['Assassin']},
        {'name': 'Tristana', 'secondary': ['Assassin']},
        {'name': 'Twitch', 'secondary': ['Assassin']},
        {'name': 'Varus', 'secondary': ['Mage']},
        {'name': 'Vayne', 'secondary': ['Assassin']},
        {'name': 'Xayah', 'secondary': []},
        {'name': 'Zeri', 'secondary': []}
    ],
    'Support': [
        {'name': 'Bard', 'secondary': ['Mage']},
        {'name': 'Braum', 'secondary': ['Tank']},
        {'name': 'Ivern', 'secondary': ['Mage']},
        {'name': 'Janna', 'secondary': ['Mage']},
        {'name': 'Karma', 'secondary': ['Mage']},
        {'name': 'Lulu', 'secondary': ['Mage']},
        {'name': 'Milio', 'secondary': ['Mage']},
        {'name': 'Nami', 'secondary': ['Mage']},
        {'name': 'Rakan', 'secondary': []},
        {'name': 'Renata', 'secondary': ['Mage']},
        {'name': 'Sona', 'secondary': ['Mage']},
        {'name': 'Soraka', 'secondary': ['Mage']},
        {'name': 'TahmKench', 'secondary': ['Tank']},
        {'name': 'Taric', 'secondary': ['Fighter']},
        {'name': 'Thresh', 'secondary': ['Fighter']},
        {'name': 'Yuumi', 'secondary': ['Mage']},
        {'name': 'Zilean', 'secondary': ['Mage']}
    ],
    'Tank': [
        {'name': 'Alistar', 'secondary': ['Support']},
        {'name': 'Amumu', 'secondary': ['Mage']},
        {'name': 'Blitzcrank', 'secondary': ['Fighter']},
        {'name': 'ChoGath', 'secondary': ['Mage']},
        {'name': 'Galio', 'secondary': ['Mage']},
        {'name': 'JarvanIV', 'secondary': ['Fighter']},
        {'name': 'KSante', 'secondary': ['Fighter']},
        {'name': 'Leona', 'secondary': ['Support']},
        {'name': 'Malphite', 'secondary': ['Fighter']},
        {'name': 'Maokai', 'secondary': ['Mage']},
        {'name': 'Nautilus', 'secondary': ['Fighter']},
        {'name': 'Nunu', 'secondary': ['Fighter']},
        {'name': 'Ornn', 'secondary': ['Fighter']},
        {'name': 'Poppy', 'secondary': ['Fighter']},
        {'name': 'Rammus', 'secondary': ['Fighter']},
        {'name': 'Rell', 'secondary': ['Support']},
        {'name': 'Sejuani', 'secondary': ['Fighter']},
        {'name': 'Shen', 'secondary': ['Fighter']},
        {'name': 'Singed', 'secondary': ['Fighter']},
        {'name': 'Sion', 'secondary': ['Fighter']},
        {'name': 'Zac', 'secondary': ['Fighter']}
    ]
}



class RiftRewindAnalytics:
    """
    Calculates comprehensive statistics for all 15 slides.
    """
    
    def __init__(self, raw_data: Dict[str, Any]):
        """
        Initialize with raw data from league_data Lambda.
        
        Args:
            raw_data: Complete raw data dict from S3
        """
        self.raw_data = raw_data
        self.puuid = raw_data.get('account', {}).get('puuid')
        self.matches = raw_data.get('matches', [])
        self.summoner = raw_data.get('summoner', {})
        self.ranked = raw_data.get('ranked', {})
        self.region = raw_data.get('metadata', {}).get('region', 'na1')
    
    def _get_participant_stats(self, match: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get participant stats for the player in a match.
        
        Args:
            match: Match details dict
        
        Returns:
            Participant stats or None if not found
        """
        participants = match.get('info', {}).get('participants', [])
        
        for participant in participants:
            if participant.get('puuid') == self.puuid:
                return participant
        
        return None
    
    # Slide 2: Time Spent & Games Played
    def calculate_time_spent(self) -> Dict[str, Any]:
        """
        Calculate total time played and game counts.
        
        Returns:
            Dict with total games, hours, average game length
        """
        # Count all analyzed matches (no sampling - we fetch everything now)
        total_games = len(self.matches)
        total_seconds = 0
        
        for match in self.matches:
            duration = match.get('info', {}).get('gameDuration', 0)
            total_seconds += duration
        
        total_hours = total_seconds / 3600
        avg_game_length = (total_seconds / total_games / 60) if total_games > 0 else 0
        
        return {
            'totalGames': total_games,
            'totalHours': round(total_hours, 1),
            'avgGameLength': round(avg_game_length, 1),
            'totalMinutes': round(total_seconds / 60, 0)
        }
    
    # Slide 3: Favorite Champions
    def get_favorite_champions(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Get player's most played champions.
        
        Args:
            top_n: Number of top champions to return
        
        Returns:
            List of champion dicts with games, wins, KDA
        """
        champion_stats = defaultdict(lambda: {
            'games': 0,
            'wins': 0,
            'kills': [],
            'deaths': [],
            'assists': []
        })
        
        for match in self.matches:
            stats = self._get_participant_stats(match)
            if not stats:
                continue
            
            champion = stats.get('championName', 'Unknown')
            won = stats.get('win', False)
            
            champion_stats[champion]['games'] += 1
            if won:
                champion_stats[champion]['wins'] += 1
            
            champion_stats[champion]['kills'].append(stats.get('kills', 0))
            champion_stats[champion]['deaths'].append(stats.get('deaths', 0))
            champion_stats[champion]['assists'].append(stats.get('assists', 0))
        
        # Calculate averages and format
        champions = []
        for champ, data in champion_stats.items():
            games = data['games']
            avg_kills = sum(data['kills']) / games if games > 0 else 0
            avg_deaths = sum(data['deaths']) / games if games > 0 else 0
            avg_assists = sum(data['assists']) / games if games > 0 else 0
            
            champions.append({
                'name': champ,
                'games': games,
                'wins': data['wins'],
                'winRate': round((data['wins'] / games * 100), 1) if games > 0 else 0,
                'avgKills': round(avg_kills, 1),
                'avgDeaths': round(avg_deaths, 1),
                'avgAssists': round(avg_assists, 1),
                'kda': round((avg_kills + avg_assists) / avg_deaths, 2) if avg_deaths > 0 else 999
            })
        
        # Sort by games played
        champions.sort(key=lambda x: x['games'], reverse=True)
        
        return champions[:top_n]
    
    # Slide 4: Best Match
    def find_best_match(self) -> Optional[Dict[str, Any]]:
        """
        Find player's best performing match based on HIGHEST KILLS.
        
        Returns:
            Best match details or None
        """
        best_match = None
        highest_kills = -1
        
        for match in self.matches:
            stats = self._get_participant_stats(match)
            if not stats:
                continue
            
            # Get actual stats from API (not calculated)
            kills = stats.get('kills', 0)
            deaths = stats.get('deaths', 0)
            assists = stats.get('assists', 0)
            won = stats.get('win', False)
            
            # Try to get KDA from API challenges, fallback to calculation
            kda = stats.get('challenges', {}).get('kda')
            if kda is None:
                kda = (kills + assists) / deaths if deaths > 0 else (kills + assists)
            
            # PRIORITY: Highest kills (primary), then KDA as tiebreaker
            # If kills are equal, pick the one with better KDA
            is_better = (kills > highest_kills) or (kills == highest_kills and best_match and kda > best_match['kda'])
            
            if is_better:
                highest_kills = kills
                best_match = {
                    'matchId': match.get('metadata', {}).get('matchId'),
                    'champion': stats.get('championName'),
                    'kills': kills,  # Direct from API
                    'deaths': deaths,  # Direct from API
                    'assists': assists,  # Direct from API
                    'kda': round(kda, 2),  # From API or calculated
                    'result': 'Victory' if won else 'Defeat',
                    'duration': round(match.get('info', {}).get('gameDuration', 0) / 60, 0),
                    'gameMode': match.get('info', {}).get('gameMode', 'CLASSIC'),
                    'timestamp': match.get('info', {}).get('gameCreation', 0)
                }
        
        return best_match
    
    # Slide 5: KDA Overview
    def calculate_kda(self) -> Dict[str, Any]:
        """
        Calculate overall KDA statistics.
        
        Returns:
            Dict with avg kills, deaths, assists, KDA ratio
        """
        total_kills = 0
        total_deaths = 0
        total_assists = 0
        games = 0
        
        for match in self.matches:
            stats = self._get_participant_stats(match)
            if not stats:
                continue
            
            kills = stats.get('kills', 0)
            deaths = stats.get('deaths', 0)
            assists = stats.get('assists', 0)
            
            total_kills += kills
            total_deaths += deaths
            total_assists += assists
            games += 1
        
        avg_kills = total_kills / games if games > 0 else 0
        avg_deaths = total_deaths / games if games > 0 else 0
        avg_assists = total_assists / games if games > 0 else 0
        kda_ratio = (avg_kills + avg_assists) / avg_deaths if avg_deaths > 0 else 999
        
        # Debug logging
        logger.info(f"KDA Calculation: {games} games analyzed")
        logger.info(f"  Total: {total_kills} kills, {total_deaths} deaths, {total_assists} assists")
        logger.info(f"  Average: {avg_kills:.1f}K / {avg_deaths:.1f}D / {avg_assists:.1f}A")
        logger.info(f"  KDA Ratio: {kda_ratio:.2f}")
        
        return {
            'avgKills': round(avg_kills, 1),
            'avgDeaths': round(avg_deaths, 1),
            'avgAssists': round(avg_assists, 1),
            'kdaRatio': round(kda_ratio, 2),
            'totalKills': total_kills,
            'totalDeaths': total_deaths,
            'totalAssists': total_assists
        }
    
    # Slide 6: Ranked Journey
    def get_ranked_journey(self) -> Dict[str, Any]:
        """
        Get ranked progression using ACTUAL match data from analyzed games.
        This ensures consistency with other slides (uses same match dataset).
        
        Returns:
            Rank info with wins/losses from analyzed matches
        """
        solo_queue = self.ranked.get('soloQueue')
        
        # Calculate wins/losses from ACTUAL analyzed matches
        wins = 0
        losses = 0
        
        for match in self.matches:
            stats = self._get_participant_stats(match)
            if not stats:
                continue
            
            if stats.get('win'):
                wins += 1
            else:
                losses += 1
        
        total_games = wins + losses
        win_rate = round((wins / total_games * 100), 1) if total_games > 0 else 0
        
        # Get current rank from Riot API (most accurate for rank/tier/LP)
        if not solo_queue:
            return {
                'currentRank': 'UNRANKED',
                'tier': 'UNRANKED',
                'division': '',
                'lp': 0,
                'wins': wins,  # Use match data
                'losses': losses,  # Use match data
                'winRate': win_rate,  # Use match data
                'totalGames': total_games
            }
        
        return {
            'currentRank': f"{solo_queue.get('tier')} {solo_queue.get('rank')}",
            'tier': solo_queue.get('tier'),
            'division': solo_queue.get('rank'),
            'lp': solo_queue.get('leaguePoints', 0),
            'wins': wins,  # Use match data (consistent with other slides)
            'losses': losses,  # Use match data
            'winRate': win_rate,  # Calculated from match data
            'totalGames': total_games  # Total analyzed games
        }
    
    # Slide 7: Vision Score
    def calculate_vision_score(self) -> Dict[str, Any]:
        """
        Calculate vision statistics.
        
        Returns:
            Vision score, wards placed, control wards (both averages and totals)
        """
        total_vision = 0
        total_wards = 0
        total_control_wards = 0
        games = 0
        
        for match in self.matches:
            stats = self._get_participant_stats(match)
            if not stats:
                continue
            
            total_vision += stats.get('visionScore', 0)
            total_wards += stats.get('wardsPlaced', 0)
            total_control_wards += stats.get('visionWardsBoughtInGame', 0)
            games += 1
        
        return {
            'avgVisionScore': round(total_vision / games, 1) if games > 0 else 0,
            'avgWardsPlaced': round(total_wards / games, 1) if games > 0 else 0,
            'avgControlWards': round(total_control_wards / games, 1) if games > 0 else 0,
            'totalVisionScore': total_vision,
            'totalWardsPlaced': total_wards,
            'totalControlWards': total_control_wards
        }
    
    # Slide 8: Champion Pool
    def analyze_champion_pool(self) -> Dict[str, Any]:
        """
        Analyze champion pool diversity.
        
        Returns:
            Unique champions, diversity metrics
        """
        unique_champions = set()
        
        for match in self.matches:
            stats = self._get_participant_stats(match)
            if stats:
                unique_champions.add(stats.get('championName', 'Unknown'))
        
        total_games = len(self.matches)
        
        return {
            'uniqueChampions': len(unique_champions),
            'totalGames': total_games,
            'diversityScore': round((len(unique_champions) / total_games * 100), 1) if total_games > 0 else 0,
            'championList': list(unique_champions)
        }
    
    # Slide 9: Duo Partner
    def find_duo_partner(self) -> Optional[Dict[str, Any]]:
        """
        Find most frequent duo partner.
        
        Returns:
            Duo partner stats or None
        """
        duo_stats = defaultdict(lambda: {'games': 0, 'wins': 0})
        
        for match in self.matches:
            participants = match.get('info', {}).get('participants', [])
            player_stats = self._get_participant_stats(match)
            
            if not player_stats:
                continue
            
            player_team = player_stats.get('teamId')
            won = player_stats.get('win', False)
            
            # Find teammates
            for participant in participants:
                if participant.get('puuid') != self.puuid and participant.get('teamId') == player_team:
                    # Use riotIdGameName (new Riot ID system) or fall back to summonerName (deprecated)
                    partner_name = participant.get('riotIdGameName') or participant.get('summonerName', 'Unknown')
                    duo_stats[partner_name]['games'] += 1
                    if won:
                        duo_stats[partner_name]['wins'] += 1
        
        if not duo_stats:
            return None
        
        # Find most frequent duo
        best_duo = max(duo_stats.items(), key=lambda x: x[1]['games'])
        partner_name, stats = best_duo
        
        # Get player's profile icon URL
        from services.riot_api_client import RiotAPIClient
        profile_icon_id = self.summoner.get('profileIconId')
        player_profile_icon_url = RiotAPIClient.get_profile_icon_url(profile_icon_id) if profile_icon_id else None
        
        return {
            'partnerName': partner_name,
            'gamesTogether': stats['games'],
            'wins': stats['wins'],
            'winRate': round((stats['wins'] / stats['games'] * 100), 1) if stats['games'] > 0 else 0,
            'playerProfileIconUrl': player_profile_icon_url
        }
    
    # Slide 10-11: Strengths & Weaknesses (Advanced Pattern Analysis)
    def analyze_champion_patterns(self) -> Dict[str, Any]:
        """
        Analyze champion performance patterns (Best, Worst, Feeder).
        """
        champ_stats = defaultdict(lambda: {'games': 0, 'wins': 0, 'deaths': 0})
        
        for match in self.matches:
            stats = self._get_participant_stats(match)
            if not stats: continue
            
            name = stats.get('championName', 'Unknown')
            champ_stats[name]['games'] += 1
            champ_stats[name]['deaths'] += stats.get('deaths', 0)
            if stats.get('win'):
                champ_stats[name]['wins'] += 1
        
        # Filter for champs with min 3 games for meaningful patterns
        significant_champs = {k: v for k, v in champ_stats.items() if v['games'] >= 3}
        if not significant_champs:
            significant_champs = champ_stats # Fallback
            
        # Calculate rates
        patterns = []
        for name, data in significant_champs.items():
            wr = (data['wins'] / data['games']) * 100
            avg_deaths = data['deaths'] / data['games']
            patterns.append({
                'name': name,
                'winRate': wr,
                'avgDeaths': avg_deaths,
                'games': data['games']
            })
            
        # Sorts
        best_wr = sorted(patterns, key=lambda x: x['winRate'], reverse=True)
        worst_wr = sorted(patterns, key=lambda x: x['winRate'])
        most_deaths = sorted(patterns, key=lambda x: x['avgDeaths'], reverse=True)
        
        return {
            'highestWinRate': best_wr[0] if best_wr else None,
            'lowestWinRate': worst_wr[0] if worst_wr else None,
            'highestDeathAvg': most_deaths[0] if most_deaths else None
        }

    def analyze_class_performance(self) -> Dict[str, Any]:
        """
        Analyze performance by champion class (Mage, Fighter, etc).
        """
        class_stats = defaultdict(lambda: {'games': 0, 'wins': 0})
        
        # Reverse lookup map
        champ_to_class = {}
        for cls, champs in CHAMPION_CLASSES.items():
            for c in champs:
                champ_to_class[c['name']] = cls
        
        for match in self.matches:
            stats = self._get_participant_stats(match)
            if not stats: continue
            
            name = stats.get('championName')
            # Default to Fighter if unknown, or check secondary logic later
            primary_class = champ_to_class.get(name, 'Unknown')
            
            if primary_class != 'Unknown':
                class_stats[primary_class]['games'] += 1
                if stats.get('win'):
                    class_stats[primary_class]['wins'] += 1
        
        results = []
        for cls, data in class_stats.items():
            if data['games'] > 0:
                results.append({
                    'class': cls,
                    'games': data['games'],
                    'winRate': round((data['wins'] / data['games']) * 100, 1)
                })
        
        results.sort(key=lambda x: x['winRate'], reverse=True)
        return {
            'bestClass': results[0] if results else None,
            'worstClass': results[-1] if results else None,
            'allClasses': results
        }

    def calculate_playstyle_metrics(self) -> Dict[str, Any]:
        """
        Calculate advanced playstyle metrics (KP, Dmg Share, etc).
        """
        total_kp = 0
        total_dmg_share = 0
        total_gold_share = 0
        games = 0
        
        wins_stats = {'kp': 0, 'dmg': 0, 'deaths': 0, 'count': 0}
        loss_stats = {'kp': 0, 'dmg': 0, 'deaths': 0, 'count': 0}
        
        for match in self.matches:
            stats = self._get_participant_stats(match)
            if not stats: continue
            
            # Team totals
            team_id = stats.get('teamId')
            team_kills = 0
            team_dmg = 0
            team_gold = 0
            
            for p in match.get('info', {}).get('participants', []):
                if p.get('teamId') == team_id:
                    team_kills += p.get('kills', 0)
                    team_dmg += p.get('totalDamageDealtToChampions', 0)
                    team_gold += p.get('goldEarned', 0)
            
            # Player stats
            kills = stats.get('kills', 0)
            assists = stats.get('assists', 0)
            deaths = stats.get('deaths', 0)
            dmg = stats.get('totalDamageDealtToChampions', 0)
            gold = stats.get('goldEarned', 0)
            won = stats.get('win', False)
            
            # Metrics
            kp = ((kills + assists) / team_kills) if team_kills > 0 else 0
            dmg_share = (dmg / team_dmg) if team_dmg > 0 else 0
            gold_share = (gold / team_gold) if team_gold > 0 else 0
            
            total_kp += kp
            total_dmg_share += dmg_share
            total_gold_share += gold_share
            games += 1
            
            # Win/Loss Splits
            target = wins_stats if won else loss_stats
            target['kp'] += kp
            target['dmg'] += dmg_share
            target['deaths'] += deaths
            target['count'] += 1
            
        def get_avg(source, key):
            return round((source[key] / source['count']) * 100, 1) if source['count'] > 0 else 0
            
        return {
            'avgKP': round((total_kp / games) * 100, 1) if games > 0 else 0,
            'avgDmgShare': round((total_dmg_share / games) * 100, 1) if games > 0 else 0,
            'avgGoldShare': round((total_gold_share / games) * 100, 1) if games > 0 else 0,
            'winStats': {
                'kp': get_avg(wins_stats, 'kp'),
                'dmgShare': get_avg(wins_stats, 'dmg'),
                'avgDeaths': round(wins_stats['deaths'] / wins_stats['count'], 1) if wins_stats['count'] > 0 else 0
            },
            'lossStats': {
                'kp': get_avg(loss_stats, 'kp'),
                'dmgShare': get_avg(loss_stats, 'dmg'),
                'avgDeaths': round(loss_stats['deaths'] / loss_stats['count'], 1) if loss_stats['count'] > 0 else 0
            }
        }
    
    def calculate_objective_control(self) -> Dict[str, Any]:
        """
        Calculate player's objective control metrics.
        Measures participation in dragons, barons, and tower damage.
        
        Returns:
            Dict with objective participation rates and damage shares
        """
        if not self.matches:
            return {
                'dragonParticipation': 0,
                'baronParticipation': 0,
                'towerDamageShare': 0,
                'avgTowerDamage': 0
            }
        
        total_dragons = 0
        player_dragons = 0
        total_barons = 0
        player_barons = 0
        total_tower_damage = 0
        team_tower_damage = 0
        
        for match in self.matches:
            player_stats = self._get_participant_stats(match)
            if not player_stats:
                continue
            
            # Dragon participation (using objectives from match timeline if available)
            # Note: dragonKills is team stat, we approximate participation
            team_dragons = player_stats.get('dragonKills', 0)
            total_dragons += team_dragons
            # Assume player participated if they were in the game (alive > 50% of time)
            if player_stats.get('timePlayed', 0) > match.get('gameDuration', 0) * 0.5:
                player_dragons += team_dragons
            
            # Baron participation
            team_barons = player_stats.get('baronKills', 0)
            total_barons += team_barons
            if player_stats.get('timePlayed', 0) > match.get('gameDuration', 0) * 0.5:
                player_barons += team_barons
            
            # Tower damage
            player_tower_dmg = player_stats.get('damageDealtToTurrets', 0)
            total_tower_damage += player_tower_dmg
            
            # Calculate team tower damage
            team_id = player_stats.get('teamId')
            team_total = 0
            for participant in match.get('participants', []):
                if participant.get('teamId') == team_id:
                    team_total += participant.get('damageDealtToTurrets', 0)
            team_tower_damage += team_total if team_total > 0 else 1  # Avoid division by zero
        
        dragon_participation = round((player_dragons / total_dragons * 100), 1) if total_dragons > 0 else 0
        baron_participation = round((player_barons / total_barons * 100), 1) if total_barons > 0 else 0
        tower_damage_share = round((total_tower_damage / team_tower_damage * 100), 1) if team_tower_damage > 0 else 0
        avg_tower_damage = round(total_tower_damage / len(self.matches))
        
        return {
            'dragonParticipation': dragon_participation,
            'baronParticipation': baron_participation,
            'towerDamageShare': tower_damage_share,
            'avgTowerDamage': avg_tower_damage
        }
    
    def calculate_cs_efficiency(self) -> Dict[str, Any]:
        """
        Calculate player's CS (Creep Score) efficiency metrics.
        Measures farming efficiency, gold generation, and resource conversion.
        
        Returns:
            Dict with CS/min, GPM, and efficiency ratios
        """
        if not self.matches:
            return {
                'csPerMin': 0,
                'goldPerMin': 0,
                'avgCS': 0,
                'avgGold': 0
            }
        
        total_cs = 0
        total_gold = 0
        total_minutes = 0
        
        for match in self.matches:
            player_stats = self._get_participant_stats(match)
            if not player_stats:
                continue
            
            # CS = minions + neutral minions (jungle camps)
            minions = player_stats.get('totalMinionsKilled', 0)
            jungle = player_stats.get('neutralMinionsKilled', 0)
            cs = minions + jungle
            
            # Gold earned
            gold = player_stats.get('goldEarned', 0)
            
            # Game duration in minutes
            duration_seconds = match.get('info', {}).get('gameDuration', 0)
            duration_minutes = duration_seconds / 60
            
            total_cs += cs
            total_gold += gold
            total_minutes += duration_minutes
        
        cs_per_min = round(total_cs / total_minutes, 1) if total_minutes > 0 else 0
        gold_per_min = round(total_gold / total_minutes) if total_minutes > 0 else 0
        avg_cs = round(total_cs / len(self.matches))
        avg_gold = round(total_gold / len(self.matches))
        
        return {
            'csPerMin': cs_per_min,
            'goldPerMin': gold_per_min,
            'avgCS': avg_cs,
            'avgGold': avg_gold
        }

    def detect_strengths_weaknesses(self) -> Dict[str, Any]:
        """
        Prepare comprehensive data for AI-powered strength/weakness analysis.
        Returns placeholder values - actual analysis done by insights Lambda.
        
        Returns:
            Placeholder strengths/weaknesses + comprehensive stats for AI
        """
        kda_stats = self.calculate_kda()
        vision_stats = self.calculate_vision_score()
        time_stats = self.calculate_time_spent()
        ranked_stats = self.get_ranked_journey()
        top_champs = self.get_favorite_champions()
        
        # New Advanced Analytics
        patterns = self.analyze_champion_patterns()
        classes = self.analyze_class_performance()
        playstyle = self.calculate_playstyle_metrics()
        duo = self.find_duo_partner()
        objectives = self.calculate_objective_control()
        farming = self.calculate_cs_efficiency()
        
        # Prepare comprehensive stats for AI prompt
        ai_context = {
            # Combat stats
            'avgKDA': kda_stats['kdaRatio'],
            'avgKills': kda_stats['avgKills'],
            'avgDeaths': kda_stats['avgDeaths'],
            'avgAssists': kda_stats['avgAssists'],
            
            # Vision stats
            'avgVisionScore': vision_stats['avgVisionScore'],
            'avgWardsPlaced': vision_stats['avgWardsPlaced'],
            'avgControlWards': vision_stats['avgControlWards'],
            
            # Game stats
            'totalGames': time_stats['totalGames'],
            'winRate': self._calculate_win_rate(),
            
            # Ranked stats
            'currentTier': ranked_stats.get('tier', 'UNRANKED'),
            
            # Advanced Patterns (The "Why" Factor)
            'championPatterns': patterns,
            'classPerformance': classes,
            'playstyle': playstyle,
            'duoStats': {
                'partner': duo.get('partnerName', 'None') if duo else 'None',
                'gamesWithDuo': duo.get('gamesTogether', 0) if duo else 0,
                'winRateWithDuo': duo.get('winRate', 0) if duo else 0
            },
            'objectiveControl': objectives,
            'farming': farming
        }
        
        # Return placeholder + AI context
        return {
            'strength': 'Consistent Player',
            'weakness': 'Room for Growth',
            'aiContext': ai_context,
            'needsAIProcessing': True  # Flag for orchestrator to invoke insights Lambda
        }
    
    def _calculate_win_rate(self) -> float:
        """Calculate win rate percentage."""
        if not self.matches:
            return 0.0
        
        wins = 0
        for match in self.matches:
            stats = self._get_participant_stats(match)
            if stats and stats.get('win'):
                wins += 1
        
        return round((wins / len(self.matches)) * 100, 1)
    
    # Slide 12: Progress Timeline (requires historical data)
    def calculate_progress(self) -> Dict[str, Any]:
        """
        Calculate progress metrics (limited without historical data).
        
        Returns:
            Progress indicators
        """
        # This would ideally compare to previous season
        # For now, return current season stats
        return {
            'message': 'Progress tracking requires multi-season data',
            'currentSeason': self.get_ranked_journey()
        }
    
    # Slide 13: Achievements
    def detect_achievements(self) -> List[Dict[str, Any]]:
        """
        Detect special achievements.
        
        Returns:
            List of achievements
        """
        achievements = []
        
        # Check for pentakills
        penta_count = 0
        quadra_count = 0
        
        for match in self.matches:
            stats = self._get_participant_stats(match)
            if not stats:
                continue
            
            if stats.get('pentaKills', 0) > 0:
                penta_count += stats.get('pentaKills', 0)
            if stats.get('quadraKills', 0) > 0:
                quadra_count += stats.get('quadraKills', 0)
        
        if penta_count > 0:
            achievements.append({
                'type': 'Pentakills',
                'count': penta_count,
                'description': f'Legendary! {penta_count} pentakill{"s" if penta_count > 1 else ""}'
            })
        
        if quadra_count > 0:
            achievements.append({
                'type': 'Quadrakills',
                'count': quadra_count,
                'description': f'{quadra_count} quadrakill{"s" if quadra_count > 1 else ""}'
            })
        
        # Check total games milestone
        total_games = len(self.matches)
        if total_games >= 100:
            achievements.append({
                'type': 'Dedication',
                'count': total_games,
                'description': f'{total_games} games played - true dedication!'
            })
        
        return achievements
    
    # Slide 14: Social Comparison
    def calculate_percentile(self) -> Dict[str, Any]:
        """
        Calculate player percentile and leaderboard position.
        
        Returns:
            Percentile, comparison data, and player details for leaderboard display
        """
        from .riot_api_client import RiotAPIClient
        
        ranked_info = self.get_ranked_journey()
        kda_stats = self.calculate_kda()
        time_stats = self.calculate_time_spent()
        
        # Get base percentile from rank
        tier = ranked_info.get('tier', 'UNRANKED')
        division = ranked_info.get('division', 'IV')
        lp = ranked_info.get('lp', 0)
        
        # League of Legends rank distribution (based on Riot's official data)
        # Each tier has 4 divisions (IV, III, II, I)
        tier_ranges = {
            'IRON': (0, 5),           # Bottom 5%
            'BRONZE': (5, 23),        # 5-23% (18% of players)
            'SILVER': (23, 45),       # 23-45% (22% of players)
            'GOLD': (45, 67),         # 45-67% (22% of players)
            'PLATINUM': (67, 84),     # 67-84% (17% of players)
            'EMERALD': (84, 92),      # 84-92% (8% of players)
            'DIAMOND': (92, 97),      # 92-97% (5% of players)
            'MASTER': (97, 98.5),     # 97-98.5% (1.5% of players)
            'GRANDMASTER': (98.5, 99.5),  # 98.5-99.5% (1% of players)
            'CHALLENGER': (99.5, 100)     # Top 0.5%
        }
        
        if tier == 'UNRANKED':
            percentile = 50  # Middle of the pack
        elif tier in ['MASTER', 'GRANDMASTER', 'CHALLENGER']:
            # No divisions, use tier range
            percentile = tier_ranges[tier][0]
        else:
            # Calculate percentile within tier based on division
            tier_min, tier_max = tier_ranges.get(tier, (50, 50))
            tier_width = tier_max - tier_min
            
            # Division progression: IV -> III -> II -> I
            division_map = {'IV': 0, 'III': 1, 'II': 2, 'I': 3}
            division_progress = division_map.get(division, 0)
            
            # Each division is 25% of the tier (4 divisions total)
            # Add LP progress within division (0-100 LP = 0-25% of tier)
            lp_progress = min(lp, 100) / 100  # Normalize LP to 0-1
            total_progress = (division_progress + lp_progress) / 4  # 0 to 1
            
            percentile = tier_min + (tier_width * total_progress)
        
        percentile = round(percentile, 1)  # Round to 1 decimal place
        
        # Try to get actual leaderboard position
        summoner_id = self.summoner.get('id')
        leaderboard_rank = None
        
        if summoner_id and tier != 'UNRANKED':
            try:
                api_client = RiotAPIClient()
                division = ranked_info.get('division', 'IV')
                lp = ranked_info.get('lp', 0)
                
                # Get position within tier/division
                position = api_client.get_league_position_in_tier(
                    queue='RANKED_SOLO_5x5',
                    tier=tier,
                    division=division,
                    lp=lp,
                    platform=self.region
                )
                
                if position:
                    leaderboard_rank = position
                    logger.info(f"Retrieved leaderboard position: {position}")
                    
            except Exception as e:
                logger.error(f"Failed to get leaderboard position: {e}")
        
        # Get player details
        game_name = self.raw_data.get('account', {}).get('gameName', 'Player')
        tag_line = self.raw_data.get('account', {}).get('tagLine', '')
        summoner_name = f"{game_name}#{tag_line}" if tag_line else game_name
        
        # Get player's profile icon URL
        player_icon_id = self.summoner.get('profileIconId', 0)
        player_profile_icon_url = RiotAPIClient.get_profile_icon_url(player_icon_id)
        
        # Get summoner level
        summoner_level = self.summoner.get('summonerLevel', 0)
        
        win_rate = self._calculate_win_rate()
        total_games = time_stats['totalGames']
        total_wins = int(total_games * (win_rate / 100)) if win_rate > 0 else 0
        
        return {
            'rankPercentile': percentile,
            'rank': ranked_info.get('currentRank'),
            'tier': ranked_info.get('tier', 'UNRANKED'),
            'division': ranked_info.get('division', ''),
            'kdaRatio': kda_stats['kdaRatio'],
            'comparison': f'Top {100 - percentile}%' if percentile > 50 else f'Bottom {percentile}%',
            'yourRank': leaderboard_rank,  # None if not available
            'playerProfileIconUrl': player_profile_icon_url,
            'summonerLevel': summoner_level,
            'leaderboard': [{
                'rank': leaderboard_rank,  # None if not available
                'summonerName': summoner_name,
                'summonerLevel': summoner_level,
                'winRate': win_rate,
                'wins': total_wins,
                'gamesPlayed': total_games,
                'rankTier': ranked_info.get('currentRank'),
                'profileIconUrl': player_profile_icon_url,
                'isYou': True
            }]
        }
    
    # Master function: Calculate all analytics
    def calculate_checkpoint_analytics(self, checkpoint_num: int, total_matches: int) -> Dict[str, Any]:
        """
        Calculate analytics for a specific checkpoint (100-match batch).
        Used for progressive data loading.
        
        Args:
            checkpoint_num: Current checkpoint number (1, 2, 3...)
            total_matches: Total number of matches in the dataset
        
        Returns:
            Analytics dict with available data
        """
        
        # Calculate available analytics based on current matches
        analytics = {
            'checkpointNum': checkpoint_num,
            'matchesAnalyzed': len(self.matches),
            'totalMatches': total_matches,
            'isPartial': len(self.matches) < total_matches,
            
            # These can be calculated with any amount of data
            'slide2_timeSpent': self.calculate_time_spent(),
            'slide3_favoriteChampions': self.get_favorite_champions(),
            'slide4_bestMatch': self.find_best_match(),
            'slide5_kda': self.calculate_kda(),
            'slide6_rankedJourney': self.get_ranked_journey(),
            'slide7_visionScore': self.calculate_vision_score(),
            'slide8_championPool': self.analyze_champion_pool(),
            'slide9_duoPartner': self.find_duo_partner(),
            'slide10_11_analysis': self.detect_strengths_weaknesses(),
            'slide12_progress': self.calculate_progress(),
            'slide14_percentile': self.calculate_percentile(),
            
            'metadata': {
                'calculatedAt': datetime.utcnow().isoformat(),
                'checkpoint': checkpoint_num,
                'partialData': len(self.matches) < total_matches
            }
        }
        
        return analytics
    
    def get_slides_for_initial_humor(self) -> List[int]:
        """
        Get list of slide numbers that should have humor generated first.
        These are the slides that will be shown during the initial loading screen.
        
        Returns:
            List of slide numbers [1, 2, 3, 4, 5]
        """
        return [1, 2, 3, 4, 5]
    
    def get_slides_for_background_humor(self) -> List[int]:
        """
        Get list of slide numbers for background humor generation.
        These are generated while the user is viewing the initial slides.
        
        Returns:
            List of slide numbers [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        """
        return [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    
    def merge_analytics(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge new analytics with existing checkpoint analytics.
        Used when continuing analysis from a checkpoint.
        
        Args:
            existing: Existing analytics from checkpoint
            new: Newly calculated analytics
        
        Returns:
            Merged analytics dict
        """
        # New analytics always overwrite existing (they have more data)
        merged = existing.copy()
        merged.update(new)
        
        # Update metadata
        merged['metadata'] = {
            'calculatedAt': datetime.utcnow().isoformat(),
            'totalMatches': new.get('totalMatches', existing.get('totalMatches', 0)),
            'updatedFrom': existing.get('metadata', {}).get('checkpoint', 0),
            'currentCheckpoint': new.get('checkpointNum', 0)
        }
        
        return merged
    
    def calculate_all(self) -> Dict[str, Any]:
        """
        Calculate all analytics for all 15 slides.
        
        Returns:
            Complete analytics dict
        """
        
        analytics = {
            'sessionId': self.raw_data.get('metadata', {}).get('sessionId'),
            'slide2_timeSpent': self.calculate_time_spent(),
            'slide3_favoriteChampions': self.get_favorite_champions(),
            'slide4_bestMatch': self.find_best_match(),
            'slide5_kda': self.calculate_kda(),
            'slide6_rankedJourney': self.get_ranked_journey(),
            'slide7_visionScore': self.calculate_vision_score(),
            'slide8_championPool': self.analyze_champion_pool(),
            'slide9_duoPartner': self.find_duo_partner(),
            'slide10_11_analysis': self.detect_strengths_weaknesses(),
            'slide12_progress': self.calculate_progress(),
            'slide14_percentile': self.calculate_percentile(),
            'metadata': {
                'calculatedAt': datetime.utcnow().isoformat(),
                'totalMatches': len(self.matches)
            }
        }
        
        logger.info(" Analytics calculation complete!")
        return analytics


# For testing
if __name__ == "__main__":
    print("Analytics module ready!")
    print("This module should be imported by Lambda functions or run via analytics Lambda")
