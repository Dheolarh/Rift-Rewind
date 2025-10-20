# Backend Analytics Variables by Slide

## 📊 Complete Backend Data Structure

This document shows all variables sent from the backend analytics for each slide in the Rift Rewind application.

---

## 🎯 Slide 2: Time Spent (`slide2_timeSpent`)

```json
{
  "totalGames": 377,
  "totalHours": 312.5,
  "avgGameLength": 28.5,
  "totalMinutes": 18750
}
```

**Variables:**
- `totalGames` (int) - Total number of games played
- `totalHours` (float) - Total hours spent playing (rounded to 1 decimal)
- `avgGameLength` (float) - Average game duration in minutes
- `totalMinutes` (float) - Total minutes played

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

```json
{
  "strengths": [
    "Excellent KDA control",
    "Good vision control",
    "Survives well in fights"
  ],
  "weaknesses": [
    "High death count",
    "Low vision score"
  ]
}
```

**Variables:**
- `strengths` (array of strings) - List of detected strengths
- `weaknesses` (array of strings) - List of detected weaknesses

**Strength Detection Rules:**
- KDA > 3.0 → "Excellent KDA control"
- Avg Vision Score > 30 → "Good vision control"
- Avg Deaths < 4 → "Survives well in fights"

**Weakness Detection Rules:**
- KDA < 1.5 → "KDA needs improvement"
- Avg Vision Score < 15 → "Low vision score"
- Avg Deaths > 7 → "High death count"

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
  "comparison": "Top 20%"
}
```

**Variables:**
- `rankPercentile` (float) - Player's rank percentile (0-100)
- `rank` (string) - Current rank
- `kdaRatio` (float) - KDA ratio
- `comparison` (string) - Comparative description

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

## 📝 Notes

1. **Slide 1 (Welcome)** has no analytics - it's just the input form
2. **Slide 15 (Final Recap)** combines data from multiple slides
3. All numeric values are rounded for frontend display
4. `null` values indicate missing or unavailable data
5. Arrays may be empty if no data matches criteria
6. Humor is generated for ALL slides (2-15) before marking session complete
7. Some features (like progress tracking) are limited without historical data

---

**Last Updated:** October 20, 2025  
**Backend Version:** Analytics v1.0  
**Frontend Integration:** React + TypeScript
