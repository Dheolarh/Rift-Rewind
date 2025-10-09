"""
Simple test to verify API wrapper and Flask server work
"""

import os
from dotenv import load_dotenv

load_dotenv()

from api import RiftRewindAPI

def test_api_wrapper():
    """Test the API wrapper functionality"""
    api = RiftRewindAPI()
    
    print("=" * 60)
    print("API WRAPPER TEST")
    print("=" * 60)
    print(f"Test Mode: {api.test_mode}")
    print(f"Max Matches: {api.max_matches}")
    print(f"Humor Slides: {api.humor_slides}")
    print()
    
    # Test regions endpoint
    print("Testing GET /api/regions...")
    response = api.get_regions()
    print(f"Status: {response['statusCode']}")
    body = response.get('body')
    print(f"Regions count: {len(body['regions'])}")
    print()
    
    print("✓ API wrapper is working!")

if __name__ == "__main__":
    test_api_wrapper()
