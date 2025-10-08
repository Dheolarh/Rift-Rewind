"""
Input validation utilities for Rift Rewind
"""

import re
from typing import Dict, Any, Tuple
from .constants import VALID_PLATFORMS, REGIONS


def validate_riot_id(game_name: str, tag_line: str) -> Dict[str, Any]:
    """
    Validate Riot ID format (GameName#TagLine).
    
    Args:
        game_name: Riot ID game name
        tag_line: Riot ID tag line
        
    Returns:
        Dict with 'valid' bool and 'errors' list
    """
    errors = []
    
    # Validate game name
    if not game_name:
        errors.append("Game name is required")
    elif not isinstance(game_name, str):
        errors.append("Game name must be a string")
    elif len(game_name.strip()) < 3:
        errors.append("Game name must be at least 3 characters")
    elif len(game_name.strip()) > 16:
        errors.append("Game name must be 16 characters or less")
    
    # Validate tag line
    if not tag_line:
        errors.append("Tag line is required")
    elif not isinstance(tag_line, str):
        errors.append("Tag line must be a string")
    elif len(tag_line.strip()) < 2:
        errors.append("Tag line must be at least 2 characters")
    elif len(tag_line.strip()) > 5:
        errors.append("Tag line must be 5 characters or less")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_region(region: str) -> Dict[str, Any]:
    """
    Validate region/platform code.
    
    Args:
        region: The region/platform code to validate
        
    Returns:
        Dict with 'valid' bool and 'errors' list
    """
    errors = []
    
    if not region:
        errors.append("Region is required")
    elif not isinstance(region, str):
        errors.append("Region must be a string")
    else:
        region_lower = region.lower().strip()
        
        # Check if it's a valid platform code
        valid_codes = VALID_PLATFORMS + [r['value'] for r in REGIONS]
        
        if region_lower not in valid_codes:
            errors.append(f"Invalid region. Must be one of: {', '.join(VALID_PLATFORMS)}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


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
    region_str = body.get('region')
    if not region_str:
        return False, "region is required", {}
    
    region_validation = validate_region(region_str)
    if not region_validation['valid']:
        return False, region_validation['errors'][0], {}
    
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
        'region': region_str.lower().strip(),
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
