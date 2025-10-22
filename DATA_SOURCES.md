# Data Sources & Calculations

## ✅ **ALL DATA IS FROM RIOT API - NO HARDCODING**

This document explains where each piece of data comes from and what calculations are derived.

---

## 📊 **Data Flow**

```
Riot API → riot_api_client.py → analytics.py → api.py → Frontend
```

---

## 🎮 **Slide-by-Slide Data Sources**

### **Slide 2: Time Spent**
| Field | Source | Type |
|-------|--------|------|
| `totalGames` | `len(matches)` - ALL matches analyzed | **DIRECT COUNT** |
| `totalHours` | Sum of `match.info.gameDuration` | **API DATA** |
| `totalMinutes` | `totalHours * 60` | **DERIVED** |
| `avgGameLength` | `total_seconds / total_games / 60` | **DERIVED** |

**✅ Raw Data:** Each match duration from `match['info']['gameDuration']`

**⚡ NO SAMPLING:** All matches are fetched and analyzed (no statistical sampling)

---

### **Slide 3: Favorite Champions**
| Field | Source | Type |
|-------|--------|------|
| `champion.name` | `participant.championName` | **API DATA** |
| `champion.games` | Count per champion | **DIRECT COUNT** |
| `champion.wins` | Count where `participant.win == True` | **API DATA** |
| `champion.winRate` | `(wins / games) * 100` | **DERIVED** |
| `champion.avgKills` | Sum of `participant.kills` / games | **API DATA** |
| `champion.avgDeaths` | Sum of `participant.deaths` / games | **API DATA** |
| `champion.avgAssists` | Sum of `participant.assists` / games | **API DATA** |
| `champion.kda` | `(avgKills + avgAssists) / avgDeaths` | **DERIVED** |

**✅ Raw Data:** Every match's `participant.championName`, `kills`, `deaths`, `assists`, `win`

---

### **Slide 4: Best Match** ⭐ **UPDATED**
| Field | Source | Type |
|-------|--------|------|
| `champion` | `participant.championName` | **API DATA** |
| `kills` | `participant.kills` | **API DATA** |
| `deaths` | `participant.deaths` | **API DATA** |
| `assists` | `participant.assists` | **API DATA** |
| `kda` | `participant.challenges.kda` OR calculated | **API FIRST, FALLBACK** |
| `result` | `participant.win` | **API DATA** |
| `duration` | `match.info.gameDuration / 60` | **API DATA** |
| `timestamp` | `match.info.gameCreation` | **API DATA** |

**✅ Raw Data:** Single best match's participant stats

**🔧 Selection Logic:**
```python
score = (KDA × kill_participation) + win_bonus
where kill_participation = kills + (assists / 2)
```
This finds matches with **high KDA AND high impact** (not just perfect KDA with low kills)

---

### **Slide 5: KDA Overview**
| Field | Source | Type |
|-------|--------|------|
| `totalKills` | Sum of `participant.kills` | **API DATA** |
| `totalDeaths` | Sum of `participant.deaths` | **API DATA** |
| `totalAssists` | Sum of `participant.assists` | **API DATA** |
| `avgKills` | `totalKills / totalGames` | **DERIVED** |
| `avgDeaths` | `totalDeaths / totalGames` | **DERIVED** |
| `avgAssists` | `totalAssists / totalGames` | **DERIVED** |
| `kdaRatio` | `(avgKills + avgAssists) / avgDeaths` | **DERIVED** |

**✅ Raw Data:** All matches' kills/deaths/assists summed

**📐 KDA Formula:** Standard League formula `(K + A) / D`

---

### **Slide 6: Ranked Journey**
| Field | Source | Type |
|-------|--------|------|
| `currentRank` | `soloQueue.tier + " " + soloQueue.rank` | **API DATA** |
| `tier` | `soloQueue.tier` | **API DATA** |
| `division` | `soloQueue.rank` | **API DATA** |
| `lp` | `soloQueue.leaguePoints` | **API DATA** |
| `wins` | `soloQueue.wins` | **API DATA** |
| `losses` | `soloQueue.losses` | **API DATA** |
| `winRate` | `(wins / (wins + losses)) * 100` | **DERIVED** |

**✅ Raw Data:** Riot `/lol/league/v4/entries/by-summoner/{summonerId}` endpoint

---

### **Slide 7: Vision Score**
| Field | Source | Type |
|-------|--------|------|
| `avgVisionScore` | Sum of `participant.visionScore` / games | **API DATA** |
| `avgWardsPlaced` | Sum of `participant.wardsPlaced` / games | **API DATA** |
| `avgControlWards` | Sum of `participant.visionWardsBoughtInGame` / games | **API DATA** |

**✅ Raw Data:** Each match's vision stats

---

### **Slide 8: Champion Pool**
| Field | Source | Type |
|-------|--------|------|
| `uniqueChampions` | `len(set(all champion names))` | **DIRECT COUNT** |
| `totalGames` | `len(matches)` | **DIRECT COUNT** |
| `diversityScore` | `(uniqueChampions / totalGames) * 100` | **DERIVED** |
| `champions[]` | List of all unique `participant.championName` | **API DATA** |

**✅ Raw Data:** Set of unique champion names from all matches

---

### **Slide 9: Duo Partner**
| Field | Source | Type |
|-------|--------|------|
| `partnerName` | `participant.riotIdGameName` | **API DATA** |
| `gamesTogether` | Count of matches with same teammate | **DIRECT COUNT** |
| `wins` | Count where both won | **API DATA** |
| `winRate` | `(wins / gamesTogether) * 100` | **DERIVED** |

**✅ Raw Data:** Each match's `participants[]` array filtered by team

---

### **Slide 14: Social Comparison** ⭐ **WITH LEADERBOARD**
| Field | Source | Type |
|-------|--------|------|
| `yourRank` | Position in tier from `/lol/league/v4/entries` | **API DATA** |
| `rankPercentile` | Calculated from global rank distribution | **DERIVED** |
| `leaderboard[]` | Array of summoners from same tier/division | **API DATA** |

**✅ Raw Data:** Riot `/lol/league/v4/entries/{queue}/{tier}/{division}` endpoint

---

## 🤖 **AI-Generated Content**

### **Strengths & Weaknesses (Slides 10 & 11)**
- **Source:** AWS Bedrock Claude 3 Sonnet
- **Input:** 15+ performance metrics from analytics
- **Process:** AI analyzes conflicts, below-average metrics, poor performance
- **Output:** 3-4 strengths, 3-4+ weaknesses, coaching tips, playstyle, personality_title

### **Humor (Slides 2-15)**
- **Source:** AWS Bedrock Claude 3 Sonnet
- **Input:** Slide-specific stats with actual values
- **Process:** Savage roasting with exact numbers
- **Output:** One 30-word max sentence per slide

---

## 🔄 **Caching System**

- **Location:** S3 `cache/users/{gameName}#{tagLine}-{region}/`
- **Expiration:** 7 days
- **Structure:**
  ```
  complete_session.json  # Full analytics + humor
  analytics.json         # Raw analytics
  humor/slide_N.json     # Individual humor per slide
  ```

---

## ✅ **Data Integrity Guarantees**

1. **No Hardcoded Values** - All data comes from Riot API or is mathematically derived
2. **No Mocked Data** - Production code uses real API responses
3. **Proper Fallbacks** - Default values only when API returns null/missing data
4. **Accurate Calculations** - All formulas follow League of Legends standards

---

## 📝 **Key Points**

- **Kills, Deaths, Assists:** Always from `participant.kills`, `participant.deaths`, `participant.assists`
- **Win Rate:** Always calculated from API's `wins` and `losses` counts
- **KDA Ratio:** Preferably from API's `challenges.kda`, fallback to `(K+A)/D`
- **Match Selection:** Scored by algorithm, not random or hardcoded
- **Timestamps:** Direct from `match.info.gameCreation` (milliseconds since epoch)

---

**Last Updated:** October 21, 2025
