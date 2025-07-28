#!/usr/bin/env python3

import requests
import json
from urllib.parse import urljoin

def test_kinocheck_api():
    """Test the KinoCheck API with various endpoints and parameters"""
    
    base_url = 'https://api.kinocheck.de'
    language = 'de'
    
    print("🧪 Testing KinoCheck API...")
    print("=" * 50)
    
    # Test cases with IMDB IDs from your Plex collection
    test_cases = [
        {"name": "Ironheart", "imdb_id": "tt13623126"},
        {"name": "Breaking Bad", "imdb_id": "tt0903747"},
        {"name": "The Office", "imdb_id": "tt0386676"},
        {"name": "Yellowstone", "imdb_id": "tt4236770"},
        {"name": "Silo", "imdb_id": "tt14688458"},
    ]
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Plex-Trailer-Checker/1.0'
    }
    
    # Test 1: Basic API connectivity
    print("🔗 Test 1: Basic API connectivity")
    try:
        response = requests.get(f"{base_url}/", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        if response.status_code == 200:
            print("   ✅ API is reachable")
        else:
            print(f"   ❌ API returned: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
    
    print()
    
    # Test 2: Check available endpoints
    print("🔍 Test 2: Checking available endpoints")
    endpoints_to_test = ['/shows', '/movies', '/videos']
    
    for endpoint in endpoints_to_test:
        try:
            url = urljoin(base_url, endpoint)
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   {endpoint}: Status {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   {endpoint}: Response type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"   {endpoint}: Keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"   {endpoint}: List with {len(data)} items")
                except:
                    print(f"   {endpoint}: Non-JSON response")
            else:
                print(f"   {endpoint}: Error: {response.text[:100]}")
        except Exception as e:
            print(f"   {endpoint}: Exception: {e}")
    
    print()
    
    # Test 3: Test with specific IMDB IDs
    print("🎬 Test 3: Testing with specific IMDB IDs")
    
    for test_case in test_cases:
        print(f"\n   Testing: {test_case['name']} (IMDB: {test_case['imdb_id']})")
        
        # Try /shows endpoint with imdb_id
        try:
            params = {
                'imdb_id': test_case['imdb_id'],
                'language': language
            }
            url = urljoin(base_url, '/shows')
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            print(f"     Request URL: {response.url}")
            print(f"     Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"     Response type: {type(data)}")
                
                if isinstance(data, dict):
                    print(f"     Keys: {list(data.keys())}")
                    if 'videos' in data:
                        videos = data['videos']
                        print(f"     Videos found: {len(videos)}")
                        for i, video in enumerate(videos[:3]):  # Show first 3
                            print(f"       Video {i+1}: {video.get('title', 'No title')}")
                            print(f"                   Categories: {video.get('categories', [])}")
                            print(f"                   YouTube ID: {video.get('youtube_video_id', 'No ID')}")
                    else:
                        print(f"     No 'videos' key in response")
                        print(f"     Response: {json.dumps(data, indent=2)[:500]}...")
                elif isinstance(data, list):
                    print(f"     List response with {len(data)} items")
                    if data:
                        print(f"     First item: {json.dumps(data[0], indent=2)[:300]}...")
                else:
                    print(f"     Unexpected response type: {data}")
            else:
                print(f"     Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"     Exception: {e}")
    
    print()
    
    # Test 4: Try different parameter combinations
    print("🔧 Test 4: Testing different parameter combinations")
    
    test_params = [
        {'imdb_id': 'tt13623126', 'language': 'de'},
        {'imdb_id': 'tt13623126', 'language': 'en'},
        {'imdb_id': 'tt13623126', 'categories': 'Trailer'},
        {'imdb_id': 'tt13623126', 'language': 'de', 'categories': 'Trailer'},
        {'tmdb_id': '114695', 'language': 'de'},  # Ironheart TMDB ID if available
    ]
    
    for i, params in enumerate(test_params):
        print(f"\n   Test 4.{i+1}: Parameters: {params}")
        try:
            url = urljoin(base_url, '/shows')
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            print(f"     Request URL: {response.url}")
            print(f"     Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'videos' in data:
                    print(f"     Videos found: {len(data['videos'])}")
                else:
                    print(f"     Response: {str(data)[:200]}...")
            else:
                print(f"     Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"     Exception: {e}")
    
    print()
    print("🏁 Test completed!")
    print("=" * 50)


def test_id_extraction():
    """Test GUID parsing functions"""
    print("\n🔍 Testing ID extraction functions...")
    
    # Sample GUIDs from Plex (common patterns)
    test_guids = [
        "plex://show/5d9c086fe9d5a1001e6aa77a",
        "com.plexapp.agents.thetvdb://321924?lang=en",
        "com.plexapp.agents.imdb://tt13623126?lang=en",
        "com.plexapp.agents.tmdb://114695?lang=en",
        "tv.plex.agents.movie://tmdb/567604?lang=en",
        "tv.plex.agents.series://tmdb/114695?lang=en",
        "imdb://tt13623126",
        "tmdb://114695",
    ]
    
    import re
    
    def extract_tmdb_id(guid_string):
        if not guid_string:
            return None
        # Look for TMDB pattern in various formats
        patterns = [
            r'tmdb://(\d+)',
            r'tmdb/(\d+)',
            r'agents\.tmdb://(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, guid_string)
            if match:
                return int(match.group(1))
        return None

    def extract_imdb_id(guid_string):
        if not guid_string:
            return None
        # Look for IMDB pattern in various formats
        patterns = [
            r'imdb://(tt\d+)',
            r'imdb//(tt\d+)',
            r'agents\.imdb://(tt\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, guid_string)
            if match:
                return match.group(1)
        return None
    
    for guid in test_guids:
        tmdb_id = extract_tmdb_id(guid)
        imdb_id = extract_imdb_id(guid)
        print(f"   GUID: {guid}")
        print(f"     TMDB ID: {tmdb_id}")
        print(f"     IMDB ID: {imdb_id}")
        print()


if __name__ == "__main__":
    test_kinocheck_api()
    test_id_extraction() 