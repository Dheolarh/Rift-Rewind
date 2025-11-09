"""
Analytics Module: analytics.py
Purpose: Calculate statistics for all slides
"""

import logging
from typing import Dict, Any, List, Optional
from collections import Counter, defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


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
    
    # Slide 10-11: Strengths & Weaknesses (prepared for AI analysis)
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
        
        # Prepare comprehensive stats for AI prompt
        ai_context = {
            # Combat stats
            'avgKDA': kda_stats['kdaRatio'],
            'avgKills': kda_stats['avgKills'],
            'avgDeaths': kda_stats['avgDeaths'],
            'avgAssists': kda_stats['avgAssists'],
            'totalKills': kda_stats['totalKills'],
            'totalDeaths': kda_stats['totalDeaths'],
            
            # Vision stats
            'avgVisionScore': vision_stats['avgVisionScore'],
            'avgWardsPlaced': vision_stats['avgWardsPlaced'],
            'avgControlWards': vision_stats['avgControlWards'],
            
            # Game stats
            'totalGames': time_stats['totalGames'],
            'totalHours': time_stats['totalHours'],
            'avgGameLength': time_stats['avgGameLength'],
            'winRate': self._calculate_win_rate(),
            
            # Ranked stats
            'currentTier': ranked_stats.get('tier', 'UNRANKED'),
            'currentDivision': ranked_stats.get('division', ''),
            'currentLP': ranked_stats.get('lp', 0),
            
            # Champion pool
            'topChampions': top_champs[:3],
            'championPoolSize': len(self.analyze_champion_pool().get('championList', [])),
            
            # Performance indicators for AI to analyze
            'performanceMetrics': {
                'kda_performance': 'excellent' if kda_stats['kdaRatio'] > 3.0 else 'poor' if kda_stats['kdaRatio'] < 1.5 else 'average',
                'vision_performance': 'excellent' if vision_stats['avgVisionScore'] > 30 else 'poor' if vision_stats['avgVisionScore'] < 15 else 'average',
                'death_control': 'excellent' if kda_stats['avgDeaths'] < 4 else 'poor' if kda_stats['avgDeaths'] > 7 else 'average',
                'ward_placement': 'excellent' if vision_stats['avgWardsPlaced'] > 20 else 'poor' if vision_stats['avgWardsPlaced'] < 10 else 'average',
                'champion_diversity': 'excellent' if len(self.analyze_champion_pool().get('championList', [])) > 15 else 'poor' if len(self.analyze_champion_pool().get('championList', [])) < 5 else 'average',
                'death_rate_severity': 'critical' if kda_stats['avgDeaths'] > 8 else 'concerning' if kda_stats['avgDeaths'] > 6 else 'acceptable',
                'consistency': 'inconsistent' if abs(kda_stats['kdaRatio'] - 2.0) > 1.5 else 'stable',
            }
        }
        
        # Return placeholder + AI context
        return {
            'strengths': [],
            'weaknesses': [],
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
