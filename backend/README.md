# Rift Rewind - Backend

**AI-Powered League of Legends Year-in-Review**  
AWS + Riot Games Hackathon 2025

---

## 🎯 Overview

Complete serverless backend for Rift Rewind - a Spotify Wrapped-style experience for League of Legends players using AWS Bedrock for AI-generated humor and insights.

### Key Features
- ✅ Full-year match history (365 days)
- ✅ 15 comprehensive analytics slides
- ✅ AI-generated humor (AWS Bedrock Claude 3 Sonnet)
- ✅ Edge case handling (solo players, unranked, new accounts)
- ✅ Modern Riot API architecture (PUUID-based)

---

## 📦 Project Structure

```
backend/
├── lambdas/                      # AWS Lambda Functions
│   ├── league_data.py           # Riot API data fetcher
│   ├── humor_context.py         # Bedrock humor generator
│   ├── insights.py              # Bedrock insights generator
│   └── orchestrator.py          # Pipeline coordinator
│
├── services/                     # Shared Services
│   ├── analytics.py             # Statistics calculator (15 slides)
│   ├── riot_api_client.py       # Riot API integration
│   ├── aws_clients.py           # S3 + Bedrock clients
│   ├── validators.py            # Input validation
│   └── constants.py             # Configuration
│
├── docs/                         # Documentation
│   ├── AWS_SETUP_CHECKLIST.md   # Deployment guide
│   ├── BEDROCK_SETUP.md         # Bedrock configuration
│   ├── LAMBDA_FUNCTIONS_COMPLETE.md
│   ├── FULL_YEAR_IMPLEMENTATION.md
│   ├── ROAST_MASTER_STRATEGY.md # Humor strategy
│   └── SETUP.md
│
├── final_test.py                 # Complete pipeline test
├── test_full_backend_e2e.py     # Detailed E2E test
├── EDGE_CASE_SUMMARY.md         # Edge case handling
├── requirements.txt
└── .env
```

---

## 🚀 Quick Start

### 1. Setup Environment

```powershell
# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials
```

### 2. Required Environment Variables

```env
RIOT_API_KEY=your_riot_api_key_here
S3_BUCKET_NAME=rift-rewind-data
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
AWS_REGION=us-east-1
```

### 3. Run Final Test

```powershell
python final_test.py
```

---

## 🏗️ Architecture

### Lambda Functions

#### 1. **league_data.py** (418 lines)
- Fetches player data from Riot APIs
- Handles full-year match history with pagination
- Stores raw data to S3

**APIs Used:**
- ACCOUNT-V1 (Riot ID lookup)
- SUMMONER-V4 (Player info)
- LEAGUE-V4 (Ranked data)
- MATCH-V5 (Match history + details)

#### 2. **humor_context.py** (663 lines)
- Generates AI humor for 14 slides (2-15)
- Uses AWS Bedrock Claude 3 Sonnet
- Handles all edge cases (solo, unranked, no achievements)

**Key Features:**
- Witty comedian prompts (Claude-friendly)
- League memes ("0/10 powerspike", "touch grass", "duo abuse")
- Complete field mapping system
- 100% edge case coverage

#### 3. **insights.py** (282 lines)
- Generates coaching insights using Bedrock
- Provides strengths, weaknesses, tips
- Creates custom player titles

#### 4. **orchestrator.py** (219 lines)
- Coordinates all Lambda functions
- Manages pipeline execution
- Handles parallel humor generation

### Analytics Engine

**analytics.py** - Calculates statistics for all 15 slides:

| Slide | Component | Metrics |
|-------|-----------|---------|
| 1 | Player Details | Input form |
| 2 | Time Spent | Total games, hours, avg length |
| 3 | Champions | Top 5 champions, winrates, KDA |
| 4 | Best Match | Highest performance game |
| 5 | KDA | Avg kills/deaths/assists, ratio |
| 6 | Ranked Journey | Rank, LP, winrate |
| 7 | Vision Score | Wards, control wards, vision score |
| 8 | Champion Pool | Diversity, unique champions |
| 9 | Duo Partner | Most played partner, winrate |
| 10 | Strengths | AI-detected strengths |
| 11 | Weaknesses | Areas for improvement |
| 12 | Progress | Year-over-year growth |
| 13 | Achievements | Pentakills, milestones |
| 14 | Social Comparison | Rank percentile |
| 15 | Final Recap | Summary + custom title |

---

## 🎭 Humor System

### Approach: "Witty Comedian"

All prompts reframed from aggressive roasts to playful comedy for Claude content policy compliance.

**Humor Style:**
- Self-deprecating League jokes
- Community memes (0/10 powerspike, touch grass, hardstuck)
- Stat-based personalization
- Playful sarcasm

### Edge Cases Handled

✅ **Solo Players** (no duo partner)
✅ **Unranked** (normals only)
✅ **No Achievements** (new/casual players)
✅ **First Season** (no historical data)
✅ **Low Activity** (<10 games)
✅ **Zero Vision** (no wards placed)
✅ **Missing Stats** (fallback values)

See: `EDGE_CASE_SUMMARY.md` for details

---

## 🧪 Testing

### Quick Test
```powershell
python final_test.py
```

### Full E2E Test
```powershell
python test_full_backend_e2e.py
```

### Test Profiles

**Default:** Faker (Hide on bush#KR1)
- CHALLENGER I, 1113 LP
- 500+ matches available
- Perfect for full-year testing

---

## 📊 Status

### ✅ Complete & Production-Ready

| Component | Status | Tested |
|-----------|--------|--------|
| Riot API Integration | ✅ | ✅ |
| Full-year history | ✅ | ✅ |
| S3 Storage | ✅ | ✅ |
| Analytics (15 slides) | ✅ | ✅ |
| Bedrock Humor | ✅ | ✅ |
| Edge Case Handling | ✅ | ✅ |
| Documentation | ✅ | N/A |

### Recent Updates (Oct 8, 2025)

✅ **Humor system refactored** - Claude-friendly prompts  
✅ **Edge cases implemented** - 100% coverage  
✅ **Field mapping fixed** - Nested data extraction  
✅ **Duo partner fix** - Riot ID system  

---

## 🚀 Deployment

### Prerequisites
1. AWS Account with permissions:
   - Lambda execution
   - S3 read/write
   - Bedrock access (Claude 3 Sonnet)
2. Riot Games API Key (Developer Portal)

### Steps

See: `docs/AWS_SETUP_CHECKLIST.md` for complete deployment guide

**Quick Deploy:**
1. Create IAM role for Lambda
2. Create S3 bucket
3. Deploy Lambda functions
4. Create API Gateway endpoints
5. Set environment variables

---

## 💰 Cost Estimates

**For 1000 Users:**

| Service | Usage | Cost |
|---------|-------|------|
| Lambda | ~60 seconds/user | ~$0.001 |
| S3 | ~500KB/user | ~$0.01 |
| Bedrock | 14 calls/user | ~$0.08 |
| **Total** | Per user | **~$0.09** |
| **Monthly** | 1000 users | **~$90** |

Well within hackathon budget! 🎯

---

## 🎯 Hackathon Alignment

### Targeting: "Roast Master 3000" Prize

✅ **Witty AI humor** using League memes  
✅ **Stat-based jokes** personalized per player  
✅ **Edge case coverage** - works for everyone  
✅ **Claude 3 Sonnet** - high quality generation  

### Judging Criteria Met

| Criterion | Implementation |
|-----------|---------------|
| Insight Quality | 15 slides of analytics + AI coaching |
| Technical Execution | Multi-Lambda serverless architecture |
| Creativity & UX | Spotify Wrapped style + humor |
| AWS Integration | Bedrock (Claude 3) + S3 + Lambda |
| Unique & Vibes | League memes + personalized comedy |

---

## 📝 License

MIT License - Required for AWS + Riot Games Hackathon

---

## 🔗 Resources

- **Hackathon:** [Rift Rewind on Devpost](https://rift-rewind.devpost.com/)
- **Riot API:** [Developer Portal](https://developer.riotgames.com/)
- **AWS Bedrock:** [Documentation](https://docs.aws.amazon.com/bedrock/)

---

**Built for AWS + Riot Games Hackathon 2025**  
**Deadline:** November 10, 2025  
**Status:** Backend Complete ✅
