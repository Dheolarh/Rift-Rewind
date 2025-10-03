\# Rift Rewind 🎮

\> AI-powered year-in-review for League of Legends players - Spotify
Wrapped meets the Rift

Built for the \*\*AWS + Riot Games Rift Rewind Hackathon\*\*

\-\--

\## 🎯 What It Does

Transform League of Legends match history into a personalized,
story-driven rewind with:

\- \*\*Dynamic Humor\*\*: AI-generated jokes using champion lore &
League culture

\- \*\*Actionable Insights\*\*: Strengths, weaknesses, and coaching tips

\- \*\*Progress Tracking\*\*: Year-over-year performance analysis

\- \*\*Social Sharing\*\*: Shareable cards with custom player titles

\-\--

\## 🛠️ Tech Stack

\### Frontend

\- \*\*React 18 + TypeScript\*\* - UI framework

\- \*\*Tailwind CSS\*\* - Styling

\- \*\*Framer Motion\*\* - Animations

\- \*\*Recharts\*\* - Data visualizations

\### Backend

\- \*\*AWS Lambda\*\* (Python 3.11) - Serverless compute

\- \*\*AWS API Gateway\*\* - REST API

\- \*\*AWS S3\*\* - Session storage

\- \*\*AWS Bedrock (Claude 3 Sonnet)\*\* - Humor & insights generation

\- \*\*AWS SageMaker\*\* - Player behavior analysis

\### APIs

\- \*\*Riot Games API\*\* - Match history, player stats

\- \*\*Data Dragon CDN\*\* - Champion images & metadata (no key
required)

\-\--

\## 🖼️ Champion Images (No API Key Required!)

\### \*\*Data Dragon CDN - Free & Public\*\*

All 171 champion images are available via Riot\'s \*\*Data Dragon
CDN\*\* - \*\*NO API KEY NEEDED!\*\*

\`\`\`typescript

// Get latest version

const versionRes = await
fetch(\'https://ddragon.leagueoflegends.com/api/versions.json\');

const versions = await versionRes.json();

const latestVersion = versions\[0\]; // e.g., \"14.23.1\"

\`\`\`

\### \*\*Image Types:\*\*

\#### 1. \*\*Splash Art\*\* (Full size \~1920x1080) - Best for champion
cards

\`\`\`typescript

// Format:
https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{ChampionName}\_{SkinNumber}.jpg

const yasuoSplash =
\'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Yasuo_0.jpg\';

const luxSplash =
\'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Lux_0.jpg\';

// Use directly in React

\<img src={yasuoSplash} alt=\"Yasuo\" /\>

\`\`\`

\#### 2. \*\*Square Icons\*\* (120x120) - For small displays

\`\`\`typescript

// Format:
https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{ChampionName}.png

const yasuoIcon =
\`https://ddragon.leagueoflegends.com/cdn/\${latestVersion}/img/champion/Yasuo.png\`;

\`\`\`

\#### 3. \*\*Loading Screen\*\* (308x560) - Vertical portraits

\`\`\`typescript

const yasuoLoading =
\'https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Yasuo_0.jpg\';

\`\`\`

\### \*\*Champion Name Normalization\*\*

\`\`\`typescript

const CHAMPION_NAME_MAP: Record\<string, string\> = {

\'Wukong\': \'MonkeyKing\',

\'Renata Glasc\': \'Renata\',

\'Nunu & Willump\': \'Nunu\',

\"K\'Sante\": \'KSante\',

\"Kai\'Sa\": \'Kaisa\',

\"Kha\'Zix\": \'Khazix\',

\"Vel\'Koz\": \'Velkoz\',

\"Cho\'Gath\": \'Chogath\',

\"Kog\'Maw\": \'KogMaw\',

\"Rek\'Sai\": \'RekSai\',

\"Bel\'Veth\": \'Belveth\'

};

function normalizeChampionName(name: string): string {

return CHAMPION_NAME_MAP\[name\] \|\| name;

}

\`\`\`

\### \*\*All Champions Data (JSON)\*\*

\`\`\`typescript

// Get all 171 champions metadata (NO API KEY)

const url =
\`https://ddragon.leagueoflegends.com/cdn/\${latestVersion}/data/en_US/champion.json\`;

const res = await fetch(url);

const data = await res.json();

// Returns: { data: { \"Yasuo\": {\...}, \"Lux\": {\...}, \... } }

\`\`\`

\-\--

\## 📡 Riot API Overview

\### \*\*APIs That Need API Key:\*\*

\| API \| Purpose \| Routing Type \|

\|\-\-\-\--\|\-\-\-\-\-\-\-\--\|\-\-\-\-\-\-\-\-\-\-\-\-\--\|

\| \*\*SUMMONER-V4\*\* \| Get player PUUID \| Platform (na1, euw1) \|

\| \*\*MATCH-V5\*\* \| Match history & details \| Regional (americas,
europe) \|

\| \*\*LEAGUE-V4\*\* \| Ranked information \| Platform (na1, euw1) \|

\### \*\*APIs That DON\'T Need Key:\*\*

\| Resource \| Purpose \| URL \|

\|\-\-\-\-\-\-\-\-\--\|\-\-\-\-\-\-\-\--\|\-\-\-\--\|

\| \*\*Data Dragon\*\* \| Champion images \|
\`ddragon.leagueoflegends.com\` \|

\| \*\*Data Dragon\*\* \| Champion data JSON \|
\`ddragon.leagueoflegends.com\` \|

\### \*\*Routing Types (Important!)\*\*

\#### Platform Routing (for SUMMONER-V4, LEAGUE-V4)

\`\`\`

na1.api.riotgames.com (North America)

euw1.api.riotgames.com (Europe West)

kr.api.riotgames.com (Korea)

br1.api.riotgames.com (Brazil)

\`\`\`

\#### Regional Routing (for MATCH-V5)

\`\`\`

americas.api.riotgames.com (NA, BR, LAN, LAS, OCE)

europe.api.riotgames.com (EUW, EUNE, TR, RU)

asia.api.riotgames.com (KR, JP)

sea.api.riotgames.com (PH, SG, TH, TW, VN)

\`\`\`

\-\--

\## 🎬 Rewind Slides with API Usage

\### \*\*Slide 1: Welcome & Player Input\*\*

\*\*Component:\*\* \`PlayerDetails.tsx\`

\-\--

User Input Requirements

\### \*\*What Players Need to Provide:\*\*

1\. \*\*Summoner Name\*\* (their in-game username)

2\. \*\*Region\*\* (their game server)

That\'s it! No password or login required - all data is fetched from
public Riot APIs.

\### \*\*Region Selector (User-Friendly)\*\*

Players know their server but might not know API codes. Use friendly
names:

\`\`\`typescript

const REGIONS = \[

{ label: \"North America\", value: \"na1\", flag: \"🇺🇸\" },

{ label: \"Europe West\", value: \"euw1\", flag: \"🇪🇺\" },

{ label: \"Europe Nordic & East\", value: \"eun1\", flag: \"🇪🇺\" },

{ label: \"Korea\", value: \"kr\", flag: \"🇰🇷\" },

{ label: \"Brazil\", value: \"br1\", flag: \"🇧🇷\" },

{ label: \"Japan\", value: \"jp1\", flag: \"🇯🇵\" },

{ label: \"Latin America North\", value: \"la1\", flag: \"🇲🇽\" },

{ label: \"Latin America South\", value: \"la2\", flag: \"🇦🇷\" },

{ label: \"Oceania\", value: \"oc1\", flag: \"🇦🇺\" },

{ label: \"Turkey\", value: \"tr1\", flag: \"🇹🇷\" },

{ label: \"Russia\", value: \"ru\", flag: \"🇷🇺\" },

{ label: \"Philippines\", value: \"ph2\", flag: \"🇵🇭\" },

{ label: \"Singapore\", value: \"sg2\", flag: \"🇸🇬\" },

{ label: \"Thailand\", value: \"th2\", flag: \"🇹🇭\" },

{ label: \"Taiwan\", value: \"tw2\", flag: \"🇹🇼\" },

{ label: \"Vietnam\", value: \"vn2\", flag: \"🇻🇳\" }

\];

\`\`\`

\### \*\*UI Component Example:\*\*

\`\`\`tsx

// PlayerDetails.tsx

function PlayerDetails() {

const \[summonerName, setSummonerName\] = useState(\'\');

const \[region, setRegion\] = useState(\'na1\');

return (

\<div className=\"flex flex-col gap-4 max-w-md mx-auto p-8\"\>

\<h1 className=\"text-4xl font-bold\"\>RIFT REWIND\</h1\>

{/\* Summoner Name Input \*/}

\<div\>

\<label className=\"block text-sm mb-2\"\>Summoner Name\</label\>

\<input

type=\"text\"

value={summonerName}

onChange={(e) =\> setSummonerName(e.target.value)}

placeholder=\"Enter your summoner name\"

className=\"w-full px-4 py-3 rounded-lg border\"

/\>

\</div\>

{/\* Region Selector \*/}

\<div\>

\<label className=\"block text-sm mb-2\"\>Region\</label\>

\<select

value={region}

onChange={(e) =\> setRegion(e.target.value)}

className=\"w-full px-4 py-3 rounded-lg border\"

\>

{REGIONS.map(r =\> (

\<option key={r.value} value={r.value}\>

{r.flag} {r.label}

\</option\>

))}

\</select\>

\</div\>

{/\* Start Button \*/}

\<button

onClick={() =\> startRewind(summonerName, region)}

className=\"w-full py-4 bg-purple-600 text-white rounded-lg font-bold\"

\>

START YOUR REWIND

\</button\>

\</div\>

);

}

\`\`\`

\*\*APIs Used:\*\*

\- \*\*SUMMONER-V4\*\*:
\`/lol/summoner/v4/summoners/by-name/{summonerName}\`

\- Returns: \`{ puuid, summonerId, accountId, summonerLevel }\`

\*\*Purpose:\*\* Get player PUUID for subsequent API calls

\-\--

\### \*\*Slide 2: Time Spent & Games Played\*\*

\*\*Component:\*\* \`TimeSpent.tsx\`

\*\*APIs Used:\*\*

\- \*\*MATCH-V5\*\*:
\`/lol/match/v5/matches/by-puuid/{puuid}/ids?count=100\`

\- Returns: Array of match IDs

\- \*\*MATCH-V5\*\*: \`/lol/match/v5/matches/{matchId}\` (×100)

\- Returns: \`{ info: { gameDuration } }\`

\*\*Calculation:\*\* Sum all \`gameDuration\` values

\*\*Humor Example:\*\* \"3,421 minutes in the Rift. That\'s longer than
Teemo stays invisible in a bush.\"

\-\--

\### \*\*Slide 3: Favorite Champions\*\*

\*\*Component:\*\* \`Champions.tsx\`

\*\*APIs Used:\*\*

\- \*\*MATCH-V5\*\*: \`/lol/match/v5/matches/{matchId}\` (×100)

\- Returns: \`{ info: { participants: \[{ championName, kills, deaths,
assists, win }\] } }\`

\- \*\*Data Dragon\*\*: Champion splash art (no key)

\-
\`https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{name}\_0.jpg\`

\*\*Calculation:\*\* Count champion frequency, get top 3

\*\*Humor Example:\*\* \"127 games of Yasuo. Your team banned him 50
times to save themselves. The 0/10 power spike is real.\"

\-\--

\### \*\*Slide 4: Best Match Highlights\*\*

\*\*Component:\*\* \`BestMatch.tsx\`

\*\*APIs Used:\*\*

\- \*\*MATCH-V5\*\*: \`/lol/match/v5/matches/{matchId}\` (×100)

\- Returns: \`{ info: { participants: \[{ kills, deaths, assists,
totalDamageDealtToChampions }\] } }\`

\*\*Calculation:\*\* Find highest KDA ratio \`(kills + assists) /
deaths\`

\*\*Humor Example:\*\* \"23/2/15 KDA on Ahri. Absolute fox energy. The
enemy team reported you for being too good.\"

\-\--

\### \*\*Slide 5: KDA Overview\*\*

\*\*Component:\*\* \`KDA.tsx\`

\*\*APIs Used:\*\*

\- \*\*MATCH-V5\*\*: \`/lol/match/v5/matches/{matchId}\` (×100)

\- Aggregate: \`kills\`, \`deaths\`, \`assists\`

\*\*Calculation:\*\*

\- Total kills = sum of all kills

\- Average KDA = \`(total kills + total assists) / total deaths\`

\- Trend analysis (improving/declining)

\*\*Humor Example:\*\* \"1,823 deaths. Even Inting Sion mains are
judging you. Ward the river next time.\"

\-\--

\### \*\*Slide 6: Ranked Journey\*\*

\*\*Component:\*\* \`RankedJourney.tsx\`

\*\*APIs Used:\*\*

\- \*\*LEAGUE-V4\*\*:
\`/lol/league/v4/entries/by-summoner/{summonerId}\`

\- Returns: \`{ tier, rank, leaguePoints, wins, losses }\`

\- \*\*MATCH-V5\*\*: Match timestamps to infer rank changes over time

\*\*Calculation:\*\* Track rank progression from match history
timestamps

\*\*Humor Example:\*\* \"From Silver II to Gold I. You escaped ELO hell!
Now you\'re slightly less flamed by teammates.\"

\-\--

\### \*\*Slide 7: Vision & Wards\*\*

\*\*Component:\*\* \`VisionScore.tsx\`

\*\*APIs Used:\*\*

\- \*\*MATCH-V5\*\*: \`/lol/match/v5/matches/{matchId}\` (×100)

\- Returns: \`{ info: { participants: \[{ visionScore }\] } }\`

\*\*Calculation:\*\*

\- Total wards = sum of \`visionScore\`

\- Average = total / game count

\*\*Humor Example:\*\* \"10,492 wards placed! That\'s more wards than
Teemo has mushrooms (almost).\"

\-\--

\### \*\*Slide 8: Champion Pool Diversity\*\*

\*\*Component:\*\* \`ChampionPool.tsx\`

\*\*APIs Used:\*\*

\- \*\*MATCH-V5\*\*: \`/lol/match/v5/matches/{matchId}\` (×100)

\- Extract all unique \`championName\` values

\*\*Calculation:\*\* Count unique champions played

\*\*Humor Example:\*\* \"34 different champions. But 127 Yasuo games out
of 287 total? You\'re a Yasuo main with a side hustle.\"

\-\--

\### \*\*Slide 9: Duo Partner Stats\*\*

\*\*Component:\*\* \`DuoPartner.tsx\`

\*\*APIs Used:\*\*

\- \*\*MATCH-V5\*\*: \`/lol/match/v5/matches/{matchId}\` (×100)

\- Returns: \`{ info: { participants: \[{ puuid, summonerName, win }\] }
}\`

\*\*Calculation:\*\*

\- Find most frequent teammate (same team, multiple games)

\- Calculate win rate with that partner

\*\*Humor Example:\*\* \"112 games with DuoMate69. That\'s practically
married. 63% win rate? Power couple energy.\"

\-\--

\### \*\*Slide 10: Strengths Analysis\*\*

\*\*Component:\*\* \`Strengths.tsx\`

\*\*APIs Used:\*\*

\- \*\*MATCH-V5\*\*: All performance metrics from match history

\- \*\*AWS SageMaker\*\*: Statistical analysis (compare to rank average)

\- \*\*AWS Bedrock\*\*: Generate coaching insights

\*\*Calculation:\*\* Compare metrics to rank averages, identify top 3
strengths

\*\*Example Output:\*\*

\`\`\`

Strength: Late Game Scaling ⭐

\"58% win rate after 30 minutes. 12% above Gold average.

Actionable: Prioritize scaling items and vision control.\"

\`\`\`

\-\--

\### \*\*Slide 11: Weaknesses Analysis\*\*

\*\*Component:\*\* \`Weaknesses.tsx\`

\*\*APIs Used:\*\*

\- \*\*MATCH-V5\*\*: All performance metrics

\- \*\*AWS SageMaker\*\*: Pattern detection, weakness identification

\- \*\*AWS Bedrock\*\*: Constructive coaching feedback

\*\*Calculation:\*\* Identify underperforming metrics vs rank average

\*\*Example Output:\*\*

\`\`\`

Weakness: Early Game Pressure 📈

\"45% win rate in first 15 minutes. 6% below Gold average.

Actionable: Focus on level 2/3 trades, watch high-elo VODs.\"

\`\`\`

\-\--

\### \*\*Slide 12: Progress Over Time\*\*

\*\*Component:\*\* \`ProgressTimeline.tsx\`

\*\*APIs Used:\*\*

\- \*\*MATCH-V5\*\*: Match data with timestamps

\- Group by month: \`gameCreation\` (Unix timestamp)

\- \*\*AWS SageMaker\*\*: Trend analysis

\- \*\*AWS Bedrock\*\*: Progress narrative

\*\*Calculation:\*\* Group matches by month, calculate monthly KDA/win
rate trends

\*\*Visualization:\*\* Line chart (Recharts) showing KDA, win rate,
vision score over time

\-\--

\### \*\*Slide 13: Unique Achievements\*\*

\*\*Component:\*\* \`Achievements.tsx\`

\*\*APIs Used:\*\*

\- \*\*MATCH-V5\*\*: \`/lol/match/v5/matches/{matchId}\` (×100)

\- Returns: \`{ info: { participants: \[{ pentaKills, quadraKills }\],
gameDuration } }\`

\*\*Calculations:\*\*

\- Pentakills: \`participant.pentaKills\`

\- Longest game: \`max(info.gameDuration)\`

\- Comeback wins: Games won with gold deficit

\*\*Humor Example:\*\* \"3 pentakills! Your teammates hate you for the
KS. 67-minute game? You could\'ve learned guitar.\"

\-\--

\### \*\*Slide 14: Social Comparison\*\*

\*\*Component:\*\* \`SocialComparison.tsx\`

\*\*APIs Used:\*\*

\- \*\*LEAGUE-V4\*\*:
\`/lol/league/v4/entries/by-summoner/{summonerId}\`

\- Current rank for percentile calculation

\*\*Calculation:\*\* Calculate global percentile based on rank
distribution

\*\*Humor Example:\*\* \"Top 8% globally. You\'re better than 92% of
League players. Flex-worthy.\"

\-\--

\### \*\*Slide 15: Final Recap & Title\*\*

\*\*Component:\*\* \`FinalRecap.tsx\`

\*\*APIs Used:\*\*

\- \*\*AWS Bedrock\*\*: Generate custom player title based on playstyle

\- All previous data aggregated

\*\*Title Examples:\*\*

\- \"The Windwalker of Gold\"

\- \"Herald of Late Game Terror\"

\- \"The Comeback Architect\"

\*\*Final Message:\*\* \"287 games. 3,421 minutes. You survived another
year of Yasuo mains. See you on the Rift in 2026. 🔥\"

\-\--

\## 📊 Architecture Flow

\`\`\`

User Input → API Gateway → Lambda (Orchestrator)

↓

Parallel Processing:

├─ SUMMONER-V4: Get PUUID

├─ MATCH-V5: Get 100 match IDs

├─ MATCH-V5: Get 100 match details (parallel)

├─ LEAGUE-V4: Get ranked info

└─ Data Dragon: Get champion data (cached)

↓

Store Raw Data in S3

↓

Analysis Pipeline:

├─ SageMaker: Trends, patterns, anomalies

└─ Bedrock: Humor, insights, narratives

↓

Store Results in S3

↓

Frontend Polls → Render 15 Slides

\`\`\`

\-\--

\## 📈 API Call Breakdown

\*\*Per User Rewind:\*\*

\`\`\`

SUMMONER-V4: 1 call (Get PUUID)

MATCH-V5: 1 call (Get match IDs)

MATCH-V5: 100 calls (Get match details)

LEAGUE-V4: 1 call (Get rank)

Data Dragon: 2 calls (Version + champion data - cached)

───────────────────────────────────

Total: \~105 calls per user

\`\`\`

\*\*Rate Limits:\*\*

\- Development Key: 20 requests/second, 100 requests/2 minutes

\- Production Key: Higher limits (request via Riot Developer Portal)

\*\*Optimization:\*\*

\- Cache Data Dragon responses (changes every \~2 weeks)

\- Batch process match details (async/parallel)

\- Store raw data in S3 (avoid re-fetching)

\-\--

\## 🚀 Quick Start

\### Prerequisites

\- AWS Account with Bedrock access

\- Riot Games Developer API Key (\[Get one
here\](https://developer.riotgames.com/))

\- Node.js 18+

\- Python 3.11+

\### Frontend Setup

\`\`\`bash

cd frontend

npm install

npm run dev

\`\`\`

\### Backend Setup

\`\`\`bash

\# Deploy Lambda functions

cd backend/lambdas

./deploy.sh

\# Or use CloudFormation

aws cloudformation deploy \\

\--template-file infrastructure/template.yaml \\

\--stack-name rift-rewind

\`\`\`

\### Environment Variables

\`\`\`bash

\# Frontend (.env)

VITE_API_GATEWAY_URL=https://your-api.amazonaws.com

\# Backend (Lambda)

RIOT_API_KEY=RGAPI-your-key-here

BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

S3_BUCKET_SESSIONS=rift-rewind-sessions

\`\`\`

\-\--

\## 📂 Project Structure

\`\`\`

rift-rewind/

├── frontend/

│ ├── src/

│ │ ├── components/

│ │ │ └── slides/

│ │ │ ├── PlayerDetails.tsx

│ │ │ ├── TimeSpent.tsx

│ │ │ ├── Champions.tsx

│ │ │ ├── BestMatch.tsx

│ │ │ ├── KDA.tsx

│ │ │ ├── RankedJourney.tsx

│ │ │ ├── VisionScore.tsx

│ │ │ ├── ChampionPool.tsx

│ │ │ ├── DuoPartner.tsx

│ │ │ ├── Strengths.tsx

│ │ │ ├── Weaknesses.tsx

│ │ │ ├── ProgressTimeline.tsx

│ │ │ ├── Achievements.tsx

│ │ │ ├── SocialComparison.tsx

│ │ │ └── FinalRecap.tsx

│ │ │

│ │ ├── services/

│ │ │ ├── riotApi.ts

│ │ │ ├── championImages.ts

│ │ │ └── awsService.ts

│ │ │

│ │ └── utils/

│ └── package.json

│

├── backend/

│ ├── lambdas/

│ │ ├── orchestrator/

│ │ ├── fetch_league_data/

│ │ ├── generate_humor/

│ │ └── generate_insights/

│ │

│ ├── sagemaker/

│ │ └── scripts/

│ │

│ └── infrastructure/

│ └── cloudformation/

│

└── docs/

\`\`\`

\-\--

\## 💰 Cost Estimate (1000 users/month)

\- \*\*Lambda\*\*: \~\$0.20 (free tier)

\- \*\*Bedrock\*\*: \~\$45 (15M tokens)

\- \*\*SageMaker\*\*: \~\$50-100

\- \*\*S3\*\*: \~\$2.30

\- \*\*API Gateway\*\*: \~\$0.01

\- \*\*Total\*\*: \~\$110-160/month

\-\--

\## 🎯 Hackathon Criteria

✅ \*\*Insight Quality\*\*: Strengths/weaknesses with actionable
coaching

✅ \*\*Technical Execution\*\*: Multi-AWS service integration

✅ \*\*Creativity & UX\*\*: Story-driven, humorous experience

✅ \*\*AWS Integration\*\*: Bedrock (humor) + SageMaker (analytics)

✅ \*\*Unique & Vibes\*\*: Personality-driven narratives

\-\--

\## 🔒 Security

\- API keys in AWS Secrets Manager

\- Rate limiting (10 requests/min per user)

\- Input validation with Pydantic

\- CORS configuration

\- S3 bucket encryption

\-\--

\## 📖 Resources

\- \[Riot Developer Portal\](https://developer.riotgames.com/)

\- \[Data Dragon
Documentation\](https://developer.riotgames.com/docs/lol#data-dragon)

\- \[AWS Bedrock Documentation\](https://docs.aws.amazon.com/bedrock/)

\- \[Hackathon Page\](https://riftrewind.devpost.com/)

\-\--

\## 📄 License

MIT or Apache 2.0 (required for hackathon)

\-\--

\*\*Built with ☕ for Rift Rewind Hackathon 2025\*\*
