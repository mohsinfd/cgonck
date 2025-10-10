#!/usr/bin/env python3
"""
Simple API test script for CardGenius recommendations
Tests both local and production APIs with realistic data
"""

import requests
import json
import time
from test_data_generator import TestDataGenerator

def test_api(base_url, api_key="test-api-key-123", batch_size=10):
    """Test API with realistic data"""
    print(f"Testing API at: {base_url}")
    print(f"Batch size: {batch_size} users")
    
    # Generate test data
    generator = TestDataGenerator()
    payload = generator.generate_api_payload(batch_size)
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    print("Sending request...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/recommendations",
            headers=headers,
            json=payload,
            timeout=300
        )
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            users_processed = len(result.get('results', []))
            
            print(f"SUCCESS!")
            print(f"  Duration: {duration:.2f} seconds")
            print(f"  Users processed: {users_processed}")
            print(f"  Throughput: {(batch_size / duration) * 60:.1f} users/min")
            
            # Show sample results
            if result.get('results'):
                sample_user = result['results'][0]
                print(f"  Sample user: {sample_user['user_id']}")
                print(f"  Cards recommended: {len(sample_user.get('recommendations', []))}")
                
                if sample_user.get('recommendations'):
                    top_card = sample_user['recommendations'][0]
                    print(f"  Top card: {top_card.get('card_name', 'N/A')}")
                    print(f"  Net savings: {top_card.get('net_savings', 'N/A')}")
            
            return True
            
        else:
            print(f"FAILED: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        duration = time.time() - start_time
        print(f"TIMEOUT after {duration:.2f} seconds")
        return False
        
    except Exception as e:
        duration = time.time() - start_time
        print(f"ERROR: {str(e)}")
        return False

def main():
    """Test both local and production APIs"""
    
    # Test production API
    print("=" * 60)
    print("TESTING PRODUCTION API")
    print("=" * 60)
    
    production_success = test_api(
        base_url="https://cardgenius-batch-api.onrender.com",
        api_key="test-api-key-123",
        batch_size=10
    )
    
    print("\n" + "=" * 60)
    print("TESTING LOCAL API")
    print("=" * 60)
    
    local_success = test_api(
        base_url="http://localhost:8000",
        api_key="test-api-key-123",
        batch_size=10
    )
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Production API: {'PASS' if production_success else 'FAIL'}")
    print(f"Local API: {'PASS' if local_success else 'FAIL'}")
    
    if production_success:
        print("\nProduction API is working! You can test larger batches:")
        print("python simple_api_test.py --url https://cardgenius-batch-api.onrender.com --batch-size 200")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test CardGenius API')
    parser.add_argument('--url', help='API URL to test')
    parser.add_argument('--batch-size', type=int, default=10, help='Batch size')
    parser.add_argument('--api-key', default='test-api-key-123', help='API key')
    
    args = parser.parse_args()
    
    if args.url:
        test_api(args.url, args.api_key, args.batch_size)
    else:
        main()

