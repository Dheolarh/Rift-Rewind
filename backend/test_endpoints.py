"""
Quick API endpoint test
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing GET /api/health...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_regions():
    """Test regions endpoint"""
    print("Testing GET /api/regions...")
    response = requests.get(f"{BASE_URL}/api/regions")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Regions available: {len(data['regions'])}")
    print(f"Sample: {data['regions'][0]}")
    print()

def test_start_rewind():
    """Test start rewind endpoint"""
    print("Testing POST /api/rewind...")
    payload = {
        "gameName": "Hide on bush",
        "tagLine": "KR1",
        "region": "kr"
    }
    print(f"Request: {payload}")
    response = requests.post(f"{BASE_URL}/api/rewind", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Session created: {data.get('sessionId', '')[:20]}...")
        print(f"✓ Player: {data.get('player', {}).get('gameName')}#{data.get('player', {}).get('tagLine')}")
        print(f"✓ Rank: {data.get('player', {}).get('rank')}")
        print(f"✓ Matches: {data.get('matchCount')}")
        print(f"✓ Test Mode: {data.get('testMode')}")
        return data.get('sessionId')
    else:
        print(f"✗ Error: {response.json()}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("  RIFT REWIND API - ENDPOINT TEST")
    print("=" * 60)
    print()
    
    try:
        test_health()
        test_regions()
        session_id = test_start_rewind()
        
        print("=" * 60)
        print("✓ All endpoints working!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Is it running on port 8000?")
    except Exception as e:
        print(f"✗ Error: {e}")
