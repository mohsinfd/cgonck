#!/usr/bin/env python3
"""
Detailed API test to debug data processing issues
"""

import requests
import json
import time
from test_data_generator import TestDataGenerator

def test_with_debug(base_url, api_key, batch_size=5):
    """Test API with detailed debugging"""
    print(f"Testing API at: {base_url}")
    print(f"Batch size: {batch_size} users")
    
    # Generate test data
    generator = TestDataGenerator()
    payload = generator.generate_api_payload(batch_size)
    
    print("\nGenerated payload:")
    print(f"  Users count: {len(payload['users'])}")
    print(f"  Top N cards: {payload['top_n_cards']}")
    
    # Show first user data
    if payload['users']:
        first_user = payload['users'][0]
        print(f"\nFirst user data:")
        for key, value in first_user.items():
            print(f"  {key}: {value}")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    print(f"\nSending request...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/recommendations",
            headers=headers,
            json=payload,
            timeout=300
        )
        
        duration = time.time() - start_time
        
        print(f"\nResponse:")
        print(f"  Status code: {response.status_code}")
        print(f"  Duration: {duration:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\nResponse data:")
            print(f"  Job ID: {result.get('job_id', 'N/A')}")
            print(f"  Status: {result.get('status', 'N/A')}")
            print(f"  Results count: {len(result.get('results', []))}")
            
            if result.get('results'):
                print(f"\nFirst result:")
                first_result = result['results'][0]
                print(f"  User ID: {first_result.get('user_id', 'N/A')}")
                print(f"  Recommendations count: {len(first_result.get('recommendations', []))}")
                
                if first_result.get('recommendations'):
                    top_card = first_result['recommendations'][0]
                    print(f"  Top card: {top_card.get('card_name', 'N/A')}")
                    print(f"  Net savings: {top_card.get('net_savings', 'N/A')}")
            else:
                print(f"\nNo results returned!")
                print(f"Full response: {json.dumps(result, indent=2)}")
            
            return True
            
        else:
            print(f"  Error: {response.text}")
            return False
            
    except Exception as e:
        duration = time.time() - start_time
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_with_debug(
        base_url="https://cardgenius-batch-api.onrender.com",
        api_key="cgapi_2025_secure_key_12345",
        batch_size=5
    )

