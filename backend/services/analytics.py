"""
Analytics Module: analytics.py
Purpose: Calculate statistics for all 15 Rift Rewind slides

This is NOT a Lambda function - it's a service module used by other Lambdas.
Can be imported by league_data.py or run as a separate analytics Lambda.
"""

from typing import Dict, Any, List, Optional
from collections import Counter, defaultdict
from datetime import datetime, timedelta


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
        Find player's best performing match.
        
        Returns:
            Best match details or None
        """
        best_match = None
        best_score = -1
        
        for match in self.matches:
            stats = self._get_participant_stats(match)
            if not stats:
                continue
            
            # Calculate performance score
            kills = stats.get('kills', 0)
            deaths = stats.get('deaths', 0)
            assists = stats.get('assists', 0)
            won = stats.get('win', False)
            
            # Score = KDA + win bonus
            kda = (kills + assists) / deaths if deaths > 0 else (kills + assists)
            score = kda + (10 if won else 0)
            
            if score > best_score:
                best_score = score
                best_match = {
                    'matchId': match.get('metadata', {}).get('matchId'),
                    'champion': stats.get('championName'),
                    'kills': kills,
                    'deaths': deaths,
                    'assists': assists,
                    'kda': round(kda, 2),
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
            
            total_kills += stats.get('kills', 0)
            total_deaths += stats.get('deaths', 0)
            total_assists += stats.get('assists', 0)
            games += 1
        
        avg_kills = total_kills / games if games > 0 else 0
        avg_deaths = total_deaths / games if games > 0 else 0
        avg_assists = total_assists / games if games > 0 else 0
        kda_ratio = (avg_kills + avg_assists) / avg_deaths if avg_deaths > 0 else 999
        
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
        Get ranked progression (simplified - full timeline requires historical data).
        
        Returns:
            Current rank info
        """
        solo_queue = self.ranked.get('soloQueue')
        
        if not solo_queue:
            return {
                'currentRank': 'UNRANKED',
                'tier': 'UNRANKED',
                'division': '',
                'lp': 0,
                'wins': 0,
                'losses': 0,
                'winRate': 0
            }
        
        wins = solo_queue.get('wins', 0)
        losses = solo_queue.get('losses', 0)
        total_games = wins + losses
        
        return {
            'currentRank': f"{solo_queue.get('tier')} {solo_queue.get('rank')}",
            'tier': solo_queue.get('tier'),
            'division': solo_queue.get('rank'),
            'lp': solo_queue.get('leaguePoints', 0),
            'wins': wins,
            'losses': losses,
            'winRate': round((wins / total_games * 100), 1) if total_games > 0 else 0
        }
    
    # Slide 7: Vision Score
    def calculate_vision_score(self) -> Dict[str, Any]:
        """
        Calculate vision statistics.
        
        Returns:
            Vision score, wards placed, control wards
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
            'totalVisionScore': total_vision
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
        
        return {
            'partnerName': partner_name,
            'gamesTogether': stats['games'],
            'wins': stats['wins'],
            'winRate': round((stats['wins'] / stats['games'] * 100), 1) if stats['games'] > 0 else 0
        }
    
    # Slide 10-11: Strengths & Weaknesses (placeholders for AI)
    def detect_strengths_weaknesses(self) -> Dict[str, Any]:
        """
        Basic strength/weakness detection (AI will enhance this).
        
        Returns:
            Preliminary strengths and weaknesses
        """
        kda_stats = self.calculate_kda()
        vision_stats = self.calculate_vision_score()
        
        strengths = []
        weaknesses = []
        
        # KDA analysis
        if kda_stats['kdaRatio'] > 3.0:
            strengths.append('Excellent KDA control')
        elif kda_stats['kdaRatio'] < 1.5:
            weaknesses.append('KDA needs improvement')
        
        # Vision analysis
        if vision_stats['avgVisionScore'] > 30:
            strengths.append('Good vision control')
        elif vision_stats['avgVisionScore'] < 15:
            weaknesses.append('Low vision score')
        
        # Death rate
        if kda_stats['avgDeaths'] < 4:
            strengths.append('Survives well in fights')
        elif kda_stats['avgDeaths'] > 7:
            weaknesses.append('High death count')
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses
        }
    
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
        Calculate player percentile vs global average.
        
        Returns:
            Percentile and comparison data
        """
        ranked_info = self.get_ranked_journey()
        kda_stats = self.calculate_kda()
        
        # Simplified percentile (would need real global data)
        tier = ranked_info.get('tier', 'UNRANKED')
        
        rank_percentiles = {
            'IRON': 5,
            'BRONZE': 20,
            'SILVER': 40,
            'GOLD': 60,
            'PLATINUM': 80,
            'EMERALD': 90,
            'DIAMOND': 95,
            'MASTER': 98,
            'GRANDMASTER': 99,
            'CHALLENGER': 99.9
        }
        
        percentile = rank_percentiles.get(tier, 50)
        
        return {
            'rankPercentile': percentile,
            'rank': ranked_info.get('currentRank'),
            'kdaRatio': kda_stats['kdaRatio'],
            'comparison': f'Top {100 - percentile}%' if percentile > 50 else f'Bottom {percentile}%'
        }
    
    # Master function: Calculate all analytics
    def calculate_all(self) -> Dict[str, Any]:
        """
        Calculate all analytics for all 15 slides.
        
        Returns:
            Complete analytics dict
        """
        print("Calculating analytics for all 15 slides...")
        
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
            'slide13_achievements': self.detect_achievements(),
            'slide14_percentile': self.calculate_percentile(),
            'metadata': {
                'calculatedAt': datetime.utcnow().isoformat(),
                'totalMatches': len(self.matches)
            }
        }
        
        print("✓ Analytics calculation complete!")
        return analytics


# For testing
if __name__ == "__main__":
    print("Analytics module ready!")
    print("This module should be imported by Lambda functions or run via analytics Lambda")
