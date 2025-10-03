# Lambda function for fetching League of Legends data from Riot API
# Handles SUMMONER-V4, MATCH-V5, LEAGUE-V4 API calls

import json
import requests

def lambda_handler(event, context):
    """
    Fetches League data from Riot API
    """
    return {
        'statusCode': 200,
        'body': json.dumps('League Data Fetcher Lambda')
    }