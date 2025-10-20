# AI-Powered Strengths & Weaknesses Analysis

## Overview
The strengths/weaknesses analysis has been upgraded from simple if/else rules to **AI-powered analysis using AWS Bedrock Claude 3 Sonnet**.

## What Changed

### ❌ OLD SYSTEM (Rule-Based)
```python
# Simple if/else checks
if kda > 3.0:
    strengths.append('Excellent KDA control')
elif kda < 1.5:
    weaknesses.append('KDA needs improvement')
```

### ✅ NEW SYSTEM (AI-Powered)

#### 1. **Analytics Preparation** (`analytics.py`)
- Collects comprehensive player statistics
- Calculates performance indicators (excellent/average/poor)
- Prepares `aiContext` with 15+ metrics for AI analysis
- Flags data as `needsAIProcessing: true`

**Metrics Sent to AI:**
- Combat: KDA, kills, deaths, assists
- Vision: Vision score, wards placed, control wards
- Game stats: Total games, win rate, avg game length
- Ranked: Current tier, division, LP
- Champion pool: Top 3 champions with detailed stats, pool size
- Performance indicators: KDA performance, vision performance, death control, ward placement

#### 2. **AI Insights Generation** (`insights.py`)
Claude AI analyzes the data with these instructions:
- ✅ Identify **CONFLICTING patterns** (e.g., high kills but low vision)
- ✅ Call out **BELOW AVERAGE metrics** compared to rank
- ✅ Detect **POOR PERFORMANCE indicators** (high deaths, low vision)
- ✅ Be **SPECIFIC with numbers** (e.g., "Your 7.2 deaths is 40% higher than average")
- ✅ Highlight **PLAYSTYLE MISMATCHES** (e.g., playing assassins but dying too much)

**AI Response Format:**
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
    "Win rate of 46% suggests macro decision-making issues"
  ],
  "coaching_tips": [...],
  "play_style": "Aggressive laner who dominates early but struggles to close games",
  "personality_title": "The Reckless Carry"
}
```

#### 3. **Orchestration** (`orchestrator.py`)
- Invokes insights Lambda **AFTER** data fetching
- Updates analytics with AI-generated strengths/weaknesses
- Replaces placeholder values with real AI analysis
- Handles both new sessions and resumed sessions

**Flow:**
1. Fetch player data → 2. Calculate analytics → 3. Generate AI insights → 4. Update analytics → 5. Generate humor → 6. Complete

## Key Features

### 🎯 Context-Aware Analysis
- Compares performance to player's rank (e.g., "above average for Gold")
- Considers champion pool and playstyle
- Identifies contradictions (high KDA but low win rate)

### 🔍 Brutally Honest
- Won't sugarcoat poor performance
- Calls out specific numbers and percentages
- Identifies root causes, not just symptoms

### 📊 Data-Driven
- Every strength/weakness backed by actual stats
- Uses exact numbers from player's matches
- References specific champions and games played

### 🎮 League-Specific
- Uses proper terminology (CS, vision control, objectives)
- Understands champion roles and playstyles
- Contextualizes based on meta and rank

## Example Outputs

### High Performer
**Strengths:**
- "Exceptional KDA of 5.2 places you in top 10% of Platinum players"
- "Vision score of 42.3 per game shows strong map awareness"
- "78% win rate on Thresh demonstrates mastery"

**Weaknesses:**
- "Small champion pool (4 champions) makes you predictable"
- "Low control ward usage leaves Baron vulnerable"

### Struggling Player
**Strengths:**
- "Decent laning phase with 6.5 CS/min"

**Weaknesses:**
- "Critical death count of 9.2 per game (80% higher than Silver average)"
- "Vision score of 12.1 is severely lacking - you're playing blind"
- "42% win rate indicates fundamental macro issues"
- "Inconsistent champion picks show lack of focus"

### Conflicting Performance
**Strengths:**
- "Strong mechanical skill with 8.2 kills per game"
- "Good objective damage output"

**Weaknesses:**
- "High kills but 44% win rate suggests poor game closing"
- "Only 2.1 control wards per game leaves team vulnerable"
- "7.5 deaths per game negates your kill pressure"

## Technical Details

### Performance
- AI generation takes ~2-5 seconds
- Runs in parallel with humor generation
- Cached for 7 days with session data

### Fallback
- If AI fails, placeholder values are used
- System continues to function without AI
- Errors logged but don't block session completion

### Cost
- ~$0.001 per analysis (Bedrock Claude 3 Sonnet pricing)
- Only runs once per session (cached)
- Negligible compared to value provided

## Benefits

1. **Personalized**: Each analysis is unique to the player
2. **Actionable**: Specific feedback players can act on
3. **Contextual**: Considers rank, champions, playstyle
4. **Honest**: Doesn't hide poor performance
5. **Detailed**: Backed by real numbers and statistics

## Frontend Display

The frontend (`StrengthsSlide.tsx`) displays:
- **Main strength** as large hero text
- **Additional strengths** as bullet points
- **AI humor** for personality

Example:
```
YOUR STRENGTHS

[Main Strength - Large]
Exceptional vision control with 35.2 vision score

[Additional Strengths - Bullets]
• Strong KDA of 4.2 showing excellent trades
• Consistent Ahri performance (72% WR)

[AI Humor]
"You ward more than a paranoid support main! 👁️✨"
```

## Deployment Notes

**Required Environment Variables:**
- `BEDROCK_MODEL_ID`: `anthropic.claude-3-sonnet-20240229-v1:0`
- `S3_BUCKET_NAME`: Session storage bucket

**Lambda Configuration:**
- Memory: 256 MB
- Timeout: 60 seconds
- IAM: Bedrock invoke permissions + S3 read/write

## Future Enhancements

Potential additions:
- Compare to friends/region averages
- Track improvement over time (season-to-season)
- Generate coaching roadmap (30-day improvement plan)
- Predict rank potential based on current stats
- Identify "quick wins" (easy improvements with high impact)
