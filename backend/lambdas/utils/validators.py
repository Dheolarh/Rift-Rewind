"""
Input validation utilities for Rift Rewind
"""

import re
from typing import Dict, Any, Tuple
from .constants import VALID_PLATFORMS


def validate_summoner_name(summoner_name: str) -> Tuple[bool, str]:
    """
    Validate summoner name format.
    
    Args:
        summoner_name: The summoner name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not summoner_name:
        return False, "Summoner name is required"
    
    if not isinstance(summoner_name, str):
        return False, "Summoner name must be a string"
    
    # Trim whitespace
    summoner_name = summoner_name.strip()
    
    # Length check (Riot allows 3-16 characters)
    if len(summoner_name) < 3:
        return False, "Summoner name must be at least 3 characters"
    
    if len(summoner_name) > 16:
        return False, "Summoner name must be 16 characters or less"
    
    # Riot allows alphanumeric characters and spaces
    # Note: Some regions allow special characters, but basic validation here
    if not re.match(r'^[a-zA-Z0-9 ]+$', summoner_name):
        return False, "Summoner name contains invalid characters"
    
    return True, ""


def validate_region(region: str) -> Tuple[bool, str]:
    """
    Validate region/platform code.
    
    Args:
        region: The region/platform code to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not region:
        return False, "Region is required"
    
    if not isinstance(region, str):
        return False, "Region must be a string"
    
    region = region.lower().strip()
    
    if region not in VALID_PLATFORMS:
        return False, f"Invalid region. Must be one of: {', '.join(VALID_PLATFORMS)}"
    
    return True, ""


def validate_request_body(body: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validate the request body for generate-rewind endpoint.
    
    Args:
        body: The request body dictionary
        
    Returns:
        Tuple of (is_valid, error_message, validated_data)
    """
    if not body:
        return False, "Request body is required", {}
    
    # Validate summoner name
    summoner_name = body.get('summonerName') or body.get('summoner_name')
    if not summoner_name:
        return False, "summonerName is required", {}
    
    is_valid, error = validate_summoner_name(summoner_name)
    if not is_valid:
        return False, error, {}
    
    # Validate region
    region = body.get('region')
    if not region:
        return False, "region is required", {}
    
    is_valid, error = validate_region(region)
    if not is_valid:
        return False, error, {}
    
    # Optional: match count (default 100, max 100)
    match_count = body.get('matchCount', 100)
    try:
        match_count = int(match_count)
        if match_count < 1:
            match_count = 1
        if match_count > 100:
            match_count = 100
    except (ValueError, TypeError):
        match_count = 100
    
    validated_data = {
        'summoner_name': summoner_name.strip(),
        'region': region.lower().strip(),
        'match_count': match_count
    }
    
    return True, "", validated_data


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for S3 storage.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename.strip('-').lower()
