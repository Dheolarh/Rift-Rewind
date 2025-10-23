"""
Constants for Riot API endpoints, region mappings, and configuration
"""

# Region mappings for Riot API routing
REGIONS = [
    {"label": "North America (NA)", "value": "na1", "flag": "🇺🇸", "regional": "americas"},
    {"label": "Europe West (EUW)", "value": "euw1", "flag": "🇪🇺", "regional": "europe"},
    {"label": "Europe Nordic & East (EUNE)", "value": "eun1", "flag": "🇪🇺", "regional": "europe"},
    {"label": "Korea (KR)", "value": "kr", "flag": "🇰🇷", "regional": "asia"},
    {"label": "Brazil (BR)", "value": "br1", "flag": "🇧🇷", "regional": "americas"},
    {"label": "Japan (JP)", "value": "jp1", "flag": "🇯🇵", "regional": "asia"},
    {"label": "Latin America North (LAN)", "value": "la1", "flag": "🇲🇽", "regional": "americas"},
    {"label": "Latin America South (LAS)", "value": "la2", "flag": "🇦🇷", "regional": "americas"},
    {"label": "Oceania (OCE)", "value": "oc1", "flag": "🇦🇺", "regional": "americas"},
    {"label": "Turkey (TR)", "value": "tr1", "flag": "🇹🇷", "regional": "europe"},
    {"label": "Russia (RU)", "value": "ru", "flag": "🇷🇺", "regional": "europe"},
    {"label": "Philippines (PH)", "value": "ph2", "flag": "🇵🇭", "regional": "sea"},
    {"label": "Singapore (SG)", "value": "sg2", "flag": "🇸🇬", "regional": "sea"},
    {"label": "Thailand (TH)", "value": "th2", "flag": "🇹🇭", "regional": "sea"},
    {"label": "Taiwan (TW)", "value": "tw2", "flag": "🇹🇼", "regional": "sea"},
    {"label": "Vietnam (VN)", "value": "vn2", "flag": "🇻🇳", "regional": "sea"},
]

# Platform to Regional routing mapping
PLATFORM_TO_REGIONAL = {
    "na1": "americas",
    "br1": "americas",
    "la1": "americas",
    "la2": "americas",
    "oc1": "americas",
    "euw1": "europe",
    "eun1": "europe",
    "tr1": "europe",
    "ru": "europe",
    "kr": "asia",
    "jp1": "asia",
    "ph2": "sea",
    "sg2": "sea",
    "th2": "sea",
    "tw2": "sea",
    "vn2": "sea",
}

# Valid platform codes
VALID_PLATFORMS = list(PLATFORM_TO_REGIONAL.keys())

# Valid regional codes
VALID_REGIONAL = ["americas", "europe", "asia", "sea"]

# Region to Platform mapping (reverse lookup)
REGION_TO_PLATFORM = {region["value"]: region for region in REGIONS}

# Riot API base URLs
RIOT_API_PLATFORM_BASE = "https://{platform}.api.riotgames.com"
RIOT_API_REGIONAL_BASE = "https://{regional}.api.riotgames.com"

# Riot API endpoints
RIOT_API_ENDPOINTS = {
    # ACCOUNT-V1 (Regional routing) - Modern API for Riot IDs
    "account_by_riot_id": "/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}",
    
    # SUMMONER-V4 (Platform routing)
    "summoner_by_name": "/lol/summoner/v4/summoners/by-name/{summonerName}",
    "summoner_by_puuid": "/lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}",
    
    # LEAGUE-V4 (Platform routing)
    "league_by_summoner": "/lol/league/v4/entries/by-summoner/{encryptedSummonerId}",
    "league_by_puuid": "/lol/league/v4/entries/by-puuid/{encryptedPUUID}",
    
    # MATCH-V5 (Regional routing)
    "match_ids_by_puuid": "/lol/match/v5/matches/by-puuid/{puuid}/ids",
    "match_by_id": "/lol/match/v5/matches/{matchId}",
}

# Data Dragon CDN (No API key required)
DATA_DRAGON_BASE = "https://ddragon.leagueoflegends.com"
DATA_DRAGON_VERSION_URL = f"{DATA_DRAGON_BASE}/api/versions.json"
DATA_DRAGON_CHAMPION_DATA = f"{DATA_DRAGON_BASE}/cdn/{{version}}/data/en_US/champion.json"
DATA_DRAGON_SPLASH_ART = f"{DATA_DRAGON_BASE}/cdn/img/champion/splash/{{champion}}_0.jpg"
DATA_DRAGON_SQUARE_ICON = f"{DATA_DRAGON_BASE}/cdn/{{version}}/img/champion/{{champion}}.png"
DATA_DRAGON_PROFILE_ICON = f"{DATA_DRAGON_BASE}/cdn/{{version}}/img/profileicon/{{icon_id}}.png"

# Champion name normalization (Riot API uses different names for some champions)
CHAMPION_NAME_MAP = {
    'Wukong': 'MonkeyKing',
    'Renata Glasc': 'Renata',
    'Nunu & Willump': 'Nunu',
    "K'Sante": 'KSante',
    "Kai'Sa": 'Kaisa',
    "Kha'Zix": 'Khazix',
    "Vel'Koz": 'Velkoz',
    "Cho'Gath": 'Chogath',
    "Kog'Maw": 'KogMaw',
    "Rek'Sai": 'RekSai',
    "Bel'Veth": 'Belveth',
}

# Rate limiting
RIOT_API_RATE_LIMIT_PER_SECOND = 20  # Development key limit
RIOT_API_RATE_LIMIT_PER_2_MINUTES = 100  # Development key limit

# AWS Configuration (loaded from environment variables)
import os

# Note: AWS_REGION is reserved in Lambda, use AWS_DEFAULT_REGION or detect from context
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "rift-rewind-sessions")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
SAGEMAKER_ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT_NAME", "rift-rewind-insights")  # Optional

# Session configuration
SESSION_EXPIRY_HOURS = 24
MAX_MATCHES_TO_FETCH = 100

# Rank percentiles (approximate global distribution)
RANK_PERCENTILES = {
    "IRON": {"IV": 0, "III": 1, "II": 2, "I": 3},
    "BRONZE": {"IV": 4, "III": 8, "II": 12, "I": 16},
    "SILVER": {"IV": 20, "III": 28, "II": 36, "I": 44},
    "GOLD": {"IV": 52, "III": 60, "II": 68, "I": 76},
    "PLATINUM": {"IV": 84, "III": 88, "II": 90, "I": 92},
    "EMERALD": {"IV": 94, "III": 95, "II": 96, "I": 97},
    "DIAMOND": {"IV": 98, "III": 98.5, "II": 99, "I": 99.3},
    "MASTER": {"I": 99.5},
    "GRANDMASTER": {"I": 99.8},
    "CHALLENGER": {"I": 99.99},
}
