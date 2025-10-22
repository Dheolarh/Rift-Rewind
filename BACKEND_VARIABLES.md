# Backend Analytics Variables by Slide

## 📊 Complete Backend Data Structure

This document shows all variables sent from the backend analytics for each slide in the Rift Rewind application.

---

## 🎯 Slide 2: Time Spent (`slide2_timeSpent`)

```json
{
  "totalGames": 669,
  "totalHours": 312.5,
  "avgGameLength": 28.5,
  "totalMinutes": 18750
}
```

**Variables:**
- `totalGames` (int) - Total number of matches analyzed (all matches fetched)
- `totalHours` (float) - Total hours spent playing
- `avgGameLength` (float) - Average game duration in minutes
- `totalMinutes` (int) - Total minutes played

**Important Notes:**
- **NO SAMPLING** - All matches are fetched and analyzed
- `totalGames` = actual number of matches in the time period
- All calculations based on complete match history
- Matches consistency with all other slides

---

## 🏆 Slide 3: Favorite Champions (`slide3_favoriteChampions`)

```json
[
  {
    "name": "Yasuo",
    "games": 142,
    "wins": 82,
    "winRate": 57.7,
    "avgKills": 8.5,
    "avgDeaths": 5.2,
    "avgAssists": 6.8,
    "kda": 2.94
  },
  {
    "name": "Lee Sin",
    "games": 98,
    "wins": 53,
    "winRate": 54.1,
    "avgKills": 7.2,
    "avgDeaths": 4.9,
    "avgAssists": 7.1,
    "kda": 2.92
  }
  // ... up to 5 champions
]
```

**Variables (per champion):**
- `name` (string) - Champion name
- `games` (int) - Games played with this champion
- `wins` (int) - Wins with this champion
- `winRate` (float) - Win rate percentage
- `avgKills` (float) - Average kills per game
- `avgDeaths` (float) - Average deaths per game
- `avgAssists` (float) - Average assists per game
- `kda` (float) - KDA ratio

**Note:** Returns top 5 champions sorted by games played

---

## ⚔️ Slide 4: Best Match (`slide4_bestMatch`)

```json
{
  "matchId": "KR_1234567890",
  "champion": "Yasuo",
  "kills": 24,
  "deaths": 3,
  "assists": 18,
  "kda": 14.0,
  "result": "Victory",
  "duration": 35,
  "gameMode": "CLASSIC",
  "timestamp": 1697385600000
}
```

**Variables:**
- `matchId` (string) - Riot match ID
- `champion` (string) - Champion name
- `kills` (int) - Kills in that match
- `deaths` (int) - Deaths in that match
- `assists` (int) - Assists in that match
- `kda` (float) - KDA ratio for that match
- `result` (string) - "Victory" or "Defeat"
- `duration` (int) - Match duration in minutes
- `gameMode` (string) - Game mode (CLASSIC, ARAM, etc.)
- `timestamp` (int) - Unix timestamp in milliseconds

**Note:** Best match is determined by highest (KDA + 10 if won)

---

## 💀 Slide 5: KDA Overview (`slide5_kda`)

```json
{
  "avgKills": 7.8,
  "avgDeaths": 5.4,
  "avgAssists": 7.2,
  "kdaRatio": 2.78,
  "totalKills": 2934,
  "totalDeaths": 2034,
  "totalAssists": 2712
}
```

**Variables:**
- `avgKills` (float) - Average kills per game
- `avgDeaths` (float) - Average deaths per game
- `avgAssists` (float) - Average assists per game
- `kdaRatio` (float) - Overall KDA ratio
- `totalKills` (int) - Total kills across all games
- `totalDeaths` (int) - Total deaths across all games
- `totalAssists` (int) - Total assists across all games

---

## 🏅 Slide 6: Ranked Journey (`slide6_rankedJourney`)

```json
{
  "currentRank": "PLATINUM I",
  "tier": "PLATINUM",
  "division": "I",
  "lp": 76,
  "wins": 142,
  "losses": 118,
  "winRate": 54.6
}
```

**Variables:**
- `currentRank` (string) - Full rank (e.g., "DIAMOND IV")
- `tier` (string) - Rank tier only (e.g., "DIAMOND")
- `division` (string) - Division only (e.g., "IV")
- `lp` (int) - League Points
- `wins` (int) - Total ranked wins
- `losses` (int) - Total ranked losses
- `winRate` (float) - Win rate percentage

**Note:** Returns "UNRANKED" if player has no ranked games

---

## 👁️ Slide 7: Vision Score (`slide7_visionScore`)

```json
{
  "avgVisionScore": 28.5,
  "avgWardsPlaced": 15.2,
  "avgControlWards": 3.8,
  "totalVisionScore": 10735
}
```

**Variables:**
- `avgVisionScore` (float) - Average vision score per game
- `avgWardsPlaced` (float) - Average wards placed per game
- `avgControlWards` (float) - Average control wards bought per game
- `totalVisionScore` (int) - Total vision score across all games

---

## 🎮 Slide 8: Champion Pool (`slide8_championPool`)

```json
{
  "uniqueChampions": 47,
  "totalGames": 377,
  "diversityScore": 12.5,
  "championList": ["Yasuo", "Lee Sin", "Thresh", "Ahri", ...]
}
```

**Variables:**
- `uniqueChampions` (int) - Number of unique champions played
- `totalGames` (int) - Total games played
- `diversityScore` (float) - Diversity percentage (unique/total * 100)
- `championList` (array) - List of all unique champion names

---

## 👥 Slide 9: Duo Partner (`slide9_duoPartner`)

```json
{
  "partnerName": "SummonerX",
  "gamesTogether": 87,
  "wins": 56,
  "winRate": 64.4
}
```

**Variables:**
- `partnerName` (string) - Duo partner's Riot ID or summoner name
- `gamesTogether` (int) - Games played together
- `wins` (int) - Wins together
- `winRate` (float) - Win rate percentage when playing together

**Note:** Returns `null` if no frequent duo partner found

---

## ⚡ Slide 10-11: Strengths & Weaknesses (`slide10_11_analysis`)

**🤖 AI-POWERED ANALYSIS** - Generated by AWS Bedrock Claude 3 Sonnet

```json
{
  "strengths": [
    "Exceptional vision control with 35.2 vision score (45% above Gold average)",
    "Strong KDA of 4.2 showing excellent trade efficiency",
    "Consistent performance on Ahri (72% win rate over 25 games)"
  ],
  "weaknesses": [
    "High death count of 7.8 per game hurts overall impact",
    "Low control ward usage (0.8 per game) leaves objectives vulnerable",
    "Win rate of 46% suggests macro decision-making issues",
    "Inconsistent champion pool makes you predictable in draft"
  ],
  "coaching_tips": [
    "Focus on reducing deaths - trade 2 kills for 1 death less to climb faster",
    "Buy control wards on every back (aim for 3+ per game)",
    "Master 2-3 champions instead of playing 8+ randomly"
  ],
  "play_style": "Aggressive laner who dominates early but struggles to close games",
  "personality_title": "The Reckless Carry",
  "needsAIProcessing": false,
  "aiContext": {
    "avgKDA": 4.2,
    "avgDeaths": 7.8,
    "avgVisionScore": 35.2,
    "winRate": 46.0,
    "currentTier": "GOLD",
    "performanceMetrics": {
      "kda_performance": "excellent",
      "vision_performance": "excellent", 
      "death_control": "poor",
      "ward_placement": "poor"
    }
  }
}
```

**Variables:**
- `strengths` (array of strings) - **AI-generated** personalized strength descriptions with specific data
- `weaknesses` (array of strings) - **AI-generated** critical weakness analysis with comparisons
- `coaching_tips` (array of strings) - **AI-generated** actionable improvement suggestions
- `play_style` (string) - **AI-generated** one-sentence playstyle description
- `personality_title` (string) - **AI-generated** creative 3-4 word title (e.g., "The Vision-Blind Assassin")
- `needsAIProcessing` (boolean) - Flag indicating if AI analysis is complete
- `aiContext` (object) - Comprehensive stats used for AI analysis

**AI Analysis Features:**
- ✅ Compares to rank-specific averages (e.g., "45% above Gold average")
- ✅ Identifies conflicting patterns (high kills but low win rate)
- ✅ Calls out below-average metrics with specific numbers
- ✅ Detects poor performance indicators (deaths, vision, inconsistency)
- ✅ Highlights playstyle mismatches (champion pick vs. performance)
- ✅ Uses exact statistics in every point
- ✅ Brutally honest but constructive feedback

**Performance Indicators:**
- `kda_performance`: "excellent" (>3.0) | "average" (1.5-3.0) | "poor" (<1.5)
- `vision_performance`: "excellent" (>30) | "average" (15-30) | "poor" (<15)
- `death_control`: "excellent" (<4) | "average" (4-7) | "poor" (>7)
- `ward_placement`: "excellent" (>20) | "average" (10-20) | "poor" (<10)

**Typical Strength Examples:**
- "Exceptional KDA of 5.2 places you in top 10% of Platinum players"
- "Vision score of 42 per game shows strong map awareness"
- "78% win rate on Thresh demonstrates champion mastery"
- "Excellent objective control with 15% team damage share"

**Typical Weakness Examples:**
- "Critical death count of 9.2 per game (80% higher than Silver average)"
- "Vision score of 12.1 is severely lacking - you're playing blind"
- "42% win rate indicates fundamental macro issues"
- "Small champion pool (4 champions) makes you predictable in draft"
- "High kills but low win rate suggests poor game closing skills"

**Note:** Analysis is generated ONCE per session and cached. AI uses 15+ metrics including KDA, vision, deaths, assists, wards, champion pool, win rate, rank, and more.

---

## 📈 Slide 12: Progress (`slide12_progress`)

```json
{
  "message": "Progress tracking requires multi-season data",
  "currentSeason": {
    "currentRank": "PLATINUM I",
    "tier": "PLATINUM",
    "division": "I",
    "lp": 76,
    "wins": 142,
    "losses": 118,
    "winRate": 54.6
  }
}
```

**Variables:**
- `message` (string) - Status message
- `currentSeason` (object) - Same structure as `slide6_rankedJourney`

**Note:** Full progress tracking requires historical data not currently available

---

## 🏆 Slide 13: Achievements (`slide13_achievements`)

```json
[
  {
    "type": "Pentakills",
    "count": 3,
    "description": "Legendary! 3 pentakills"
  },
  {
    "type": "Quadrakills",
    "count": 12,
    "description": "12 quadrakills"
  },
  {
    "type": "Dedication",
    "count": 377,
    "description": "377 games played - true dedication!"
  }
]
```

**Variables (per achievement):**
- `type` (string) - Achievement type
- `count` (int) - Number of times achieved
- `description` (string) - Human-readable description

**Achievement Types:**
- `Pentakills` - Total pentakills across all games
- `Quadrakills` - Total quadrakills across all games
- `Dedication` - Milestone for playing 100+ games

---

## 📊 Slide 14: Social Comparison (`slide14_percentile`)

```json
{
  "rankPercentile": 80,
  "rank": "PLATINUM I",
  "kdaRatio": 2.78,
  "comparison": "Top 20%",
  "yourRank": 1247,
  "leaderboard": [
    {
      "rank": 1247,
      "summonerName": "PlayerName#NA1",
      "winRate": 54.6,
      "gamesPlayed": 260,
      "isYou": true
    }
  ]
}
```

**Variables:**
- `rankPercentile` (float) - Player's rank percentile (0-100)
- `rank` (string) - Current rank (e.g., "PLATINUM I")
- `kdaRatio` (float) - KDA ratio
- `comparison` (string) - Comparative description (e.g., "Top 20%")
- `yourRank` (int) - **NEW** - Player's position on the leaderboard
- `leaderboard` (array) - **NEW** - Player's leaderboard entry
  - `rank` (int) - Position number
  - `summonerName` (string) - Player's display name (GameName#TagLine)
  - `winRate` (float) - Win rate percentage
  - `gamesPlayed` (int) - Total ranked games played
  - `isYou` (boolean) - Always true (marks the player)

**Leaderboard Position:**
- Fetched from Riot API `/lol/league/v4/entries/{queue}/{tier}/{division}`
- Shows approximate position within tier/division
- Based on LP (League Points) comparison
- Falls back to 0 if API call fails

**Rank Percentiles:**
- IRON: 5%
- BRONZE: 20%
- SILVER: 40%
- GOLD: 60%
- PLATINUM: 80%
- EMERALD: 90%
- DIAMOND: 95%
- MASTER: 98%
- GRANDMASTER: 99%
- CHALLENGER: 99.9%

---

## 🎭 AI Humor Variables

For each slide (2-15), there's also a humor variable generated by AWS Bedrock:

```json
{
  "slide2_humor": "377 games? Your keyboard deserves hazard pay! ⌨️",
  "slide3_humor": "Yasuo main? The 0/10 powerspike is a lifestyle! 😅",
  "slide4_humor": "This match was so epic, even the enemy team was cheering for you! 🎭",
  "slide5_humor": "You've eliminated more champions than there are people in a small village! 🏰",
  "slide6_humor": "You climbed more ranks than a chess grandmaster... but with way more rage quits! ♟️😤",
  "slide7_humor": "You've placed more wards than a hospital has patients! 🏥",
  "slide8_humor": "Talk about champion diversity! You're basically a one-person champion ocean. 🌊",
  "slide9_humor": "You two are like peanut butter and jelly... if jelly could flash-ult and secure pentas! 🥜✨",
  "slide10_humor": "These are the skills that separate the good from the legendary! ⚡",
  "slide11_humor": "Every weakness is just a strength waiting to be discovered! 💪",
  "slide12_humor": "You've grown more than a Cho'Gath with full stacks! 🦖 The grind never stops!",
  "slide13_humor": "Achievement unlocked: Being absolutely legendary! 🏆",
  "slide14_humor": "You're rubbing shoulders with the elite! Just... digitally. And they probably don't know you exist. 😎",
  "slide15_humor": "What a journey! From noob to... well, slightly less noob! 🎮✨"
}
```

**Each humor variable:**
- Generated by Claude 3 Sonnet via AWS Bedrock
- Personalized based on slide analytics
- Stored as `slide{N}_humor` where N is slide number (2-15)

---

## 📦 Complete Response Structure

When frontend calls `/api/rewind`, it receives:

```json
{
  "sessionId": "abc-123-def-456",
  "status": "complete",
  "fromCache": false,
  "testMode": false,
  "matchCount": 300,
  "totalMatches": 377,
  "player": {
    "gameName": "Hide on bush",
    "tagLine": "KR1",
    "region": "kr",
    "summonerLevel": 642,
    "rank": "CHALLENGER"
  }
}
```

Then when calling `/api/rewind/{sessionId}`, it receives all analytics:

```json
{
  "sessionId": "abc-123-def-456",
  "status": "complete",
  "fromCache": false,
  "analytics": {
    "slide2_timeSpent": { ... },
    "slide3_favoriteChampions": [ ... ],
    "slide4_bestMatch": { ... },
    "slide5_kda": { ... },
    "slide6_rankedJourney": { ... },
    "slide7_visionScore": { ... },
    "slide8_championPool": { ... },
    "slide9_duoPartner": { ... },
    "slide10_11_analysis": { ... },
    "slide12_progress": { ... },
    "slide13_achievements": [ ... ],
    "slide14_percentile": { ... },
    "slide2_humor": "...",
    "slide3_humor": "...",
    // ... humor for slides 4-15
    "metadata": {
      "calculatedAt": "2025-10-20T12:00:00Z",
      "totalMatches": 377
    }
  }
}
```

---

## 🔄 Caching System

Cached sessions store the complete structure above in:
- **S3 Path:** `cache/users/{gameName}#{tagLine}-{region}/complete_session.json`
- **Expiration:** 7 days
- **Background Save:** Uploaded asynchronously while user views slides

---

## � ShareCard Component

The ShareCard uses data from multiple slides to generate a downloadable summary:

**Required Data:**
```typescript
{
  summonerName: string,        // From player account
  playerTitle: string,          // From slide10_11_analysis.personality_title
  year: number,                 // Current year (2025)
  stats: {
    gamesPlayed: number,        // From slide2_timeSpent.totalGames
    hoursPlayed: number,        // From slide2_timeSpent.totalHours
    peakRank: string,           // From slide6_rankedJourney.currentRank
    favoriteChampion: string,   // From slide3_favoriteChampions[0].champion
    kdaRatio: number,           // From slide5_kda.kdaRatio
    winRate: number             // From slide6_rankedJourney.winRate
  }
}
```

**Usage:**
- Triggered from Final Recap slide (Slide 15) via "Share" button
- Generates beautiful card with player stats
- Downloads as PNG image using html2canvas
- Filename format: `{summonerName}-RiftRewind-{year}.png`

---

## �📝 Notes

1. **Slide 1 (Welcome)** has no analytics - it's just the input form
2. **Slide 15 (Final Recap)** combines data from multiple slides + ShareCard
3. All numeric values are rounded for frontend display
4. `null` values indicate missing or unavailable data
5. Arrays may be empty if no data matches criteria
6. Humor is generated for ALL slides (2-15) before marking session complete
7. Some features (like progress tracking) are limited without historical data
8. **ShareCard** aggregates 6 different backend sources for downloadable recap

---

**Last Updated:** October 20, 2025  
**Backend Version:** Analytics v1.0  
**Frontend Integration:** React + TypeScript
