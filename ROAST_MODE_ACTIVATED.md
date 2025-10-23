# 🔥 ROAST MODE ACTIVATED - System Roasting Player

## What Changed (From Self-Roasting → System Roasting)

### ❌ OLD STYLE (Self-Roasting):
```
"Bruh I played 336 games? That's 212 hours I'll never get back."
```
Player roasting themselves, self-aware cringe

### ✅ NEW STYLE (System Roasting):
```
"336 games? 212 hours wasted. Your sleep schedule, social life, and hygiene all filed restraining orders."
```
Direct system roast - brutal and savage

---

## Updated Prompts

### Slide 2 - Time Spent
**Before:** "You just finished watching your season recap. Time to roast yourself..."  
**Now:** "You're roasting a League player's time commitment based on their season stats."

**Example Output:**
> "{totalGames} games? {totalHours} hours? Touch grass. Your chair has a permanent ass-print at this point."

---

### Slide 4 - Best Match  
**Before:** "Just watched your 'best match'... Time to be real with yourself"  
**Now:** "Roast this player's 'best match' performance."

**Example Output:**
> "This is your BEST game? {kills}/{deaths}/{assists} on {championName}? You're cooked. Just quit."

---

### Slide 5 - KDA
**Before:** "Looking at your KDA stats. Time for some real talk."  
**Now:** "Roast this player's KDA performance."

**Example Output:**
> "{kdaRatio} KDA? You're not playing League, you're testing how fast you can run it down."

---

### Slide 6 - Rank
**Before:** "Checking your rank. Time to face reality."  
**Now:** "Roast this player's rank."

**Example Output:**
> "{currentRank} after {totalGames} games? You're not climbing, you're rearranging deck chairs on the Titanic."

---

### Slide 9 - Duo Partner
**Before:** "Looking at who you played with most this season."  
**Now:** "Roast this duo partnership."

**Example Output:**
> "You and {partnerName} played {gamesTogether} games at {winRate}% winrate. Two negatives don't make a positive."

---

## System Prompt Update

**humor_context.py:**
```python
system_prompt = """You are a brutal League of Legends roaster. You're the system analyzing gameplay and calling out bad performance.
Be savage, direct, and merciless. Roast players for their mistakes. Use gaming slang. No filter.
NO EMOJIS. Max 30 words. Make it hurt."""
```

**insights.py:**
```python
system_prompt = """You are a no-bullshit League of Legends coach analyzing gameplay. 
Call out bad plays. If someone's inting, say it. If their vision score is trash, roast it.
Be brutally honest with data. Don't sugarcoat failures. Constructive but savage.
Respond ONLY with valid JSON - no other text."""
```

---

## Authentication: IAM (Already Configured ✅)

Your code already uses **IAM authentication** via boto3:

```python
_bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name=AWS_DEFAULT_REGION
)
```

This automatically uses:
- ✅ Lambda execution role (when deployed)
- ✅ AWS credentials from environment/config
- ✅ IAM role attached to EC2/Lambda

**No bearer token needed!** IAM is more secure and doesn't expire.

---

## Model Configuration

**Model:** `meta.llama3-1-70b-instruct-v1:0`

**Settings:**
- Temperature: **0.9** (high creativity for savage roasts)
- Top P: **0.95** (wide vocabulary for brutal insults)
- Max tokens: **100** (30 words ~= 40-50 tokens)

---

## Example Roasts (System → Player)

### Time Spent:
- "Your playtime is {totalHours} hours. That's not dedication, that's unemployment."
- "Touch grass. Your chair has a permanent ass-print at this point."
- "{totalHours} hours and you're STILL hardstuck? That's not dedication, that's insanity."

### Best Match:
- "This is your BEST game? You're cooked. Just quit."
- "Your highlight reel is {kills}/{deaths}/{assists}? Even bots have better career games."
- "If {kills}/{deaths}/{assists} is your best, your worst must be a crime scene."

### KDA:
- "You're not playing League, you're testing how fast you can run it down."
- "Even your ward has better combat stats than you do."
- "You're that teammate everyone dodge queues to avoid."

### Rank:
- "You're not climbing, you're rearranging deck chairs on the Titanic."
- "You're not hardstuck, you're cemented in concrete."
- "Your MMR and your standards are both underground."

### Duo:
- "Two negatives don't make a positive."
- "You're not a duo, you're a liability multiplier."
- "You two share one brain cell and it's permanently AFK."

---

## Key Differences

| Aspect | Self-Roasting (Old) | System Roasting (New) |
|--------|--------------------|-----------------------|
| **Tone** | "I'm trash lol" | "You ARE trash" |
| **Voice** | First person | Third person |
| **Impact** | Self-deprecating humor | Direct brutal roast |
| **Example** | "Bruh I'm inting" | "You're inting. Stop." |
| **Energy** | Cringe/aware | Savage/merciless |

---

## Testing

```bash
# Test humor generation
python backend/lambdas/humor_context.py

# Or invoke Lambda
aws lambda invoke \
  --function-name humor-generator \
  --payload '{"sessionId":"test-123","slideNumber":5}' \
  response.json
```

Expected output style:
```json
{
  "humorText": "2.1 KDA? You're not playing League, you're speedrunning the fountain respawn timer."
}
```

---

## Deployment Checklist

- [x] Updated humor prompts (system roasting style)
- [x] Updated system prompts (brutal/savage)
- [x] Switched to Meta Llama 3.1 70B
- [x] IAM authentication (already configured)
- [x] Temperature set to 0.9 for creativity
- [x] 30-word limit enforced
- [ ] Deploy to AWS Lambda
- [ ] Update `BEDROCK_MODEL_ID` environment variable
- [ ] Test with real player data
- [ ] Verify roasts are brutal enough 🔥

---

## Environment Variable

```bash
BEDROCK_MODEL_ID=meta.llama3-1-70b-instruct-v1:0
```

---

## Summary

**What You Get:**
- 🔥 **System roasts player** - Not self-aware, just brutal
- 💀 **Savage and direct** - "You're cooked. Just quit."
- 🎯 **No sugarcoating** - Calls out bad plays directly
- ⚡ **Meta Llama 3.1** - Won't refuse to roast
- 💰 **14x cheaper** - Than Claude
- 🔒 **IAM auth** - Secure, no token expiration

**Roast Mode: ACTIVATED** 🎮🔥

The system is now ready to absolutely destroy players' egos with data-backed brutality.
