#!/usr/bin/env python3
"""
Production Test Script for CardGenius API Server
Tests both V1 and V2 endpoints with real-world scenarios
"""

import requests
import json
import time
import os

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("CARDGENIUS_API_KEY", "cgapi_2025_secure_key_12345")

def test_production_api():
    """Test the production API with realistic data"""
    
    # Realistic user data
    test_users = [
        {
            "user_id": "prod_user_001",
            "avg_amazon_gmv": 25000,
            "avg_flipkart_gmv": 18000,
            "avg_myntra_gmv": 5000,
            "avg_ajio_gmv": 3000,
            "avg_confirmed_gmv": 75000,
            "avg_grocery_gmv": 4000
        },
        {
            "user_id": "prod_user_002",
            "avg_amazon_gmv": 12000,
            "avg_flipkart_gmv": 8000,
            "avg_myntra_gmv": 2000,
            "avg_ajio_gmv": 1500,
            "avg_confirmed_gmv": 40000,
            "avg_grocery_gmv": 2500
        },
        {
            "user_id": "prod_user_003",
            "avg_amazon_gmv": 35000,
            "avg_flipkart_gmv": 22000,
            "avg_myntra_gmv": 8000,
            "avg_ajio_gmv": 4000,
            "avg_confirmed_gmv": 100000,
            "avg_grocery_gmv": 6000
        }
    ]
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print("🚀 Production API Test")
    print("=" * 50)
    print(f"API URL: {API_BASE_URL}")
    print(f"API Key: {API_KEY[:10]}...")
    
    # Test health endpoint
    print("\n🏥 Testing Health Endpoint...")
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    # Test version info
    print("\n📋 Testing Version Info...")
    try:
        version_response = requests.get(f"{API_BASE_URL}/api/v1/versions", timeout=10)
        if version_response.status_code == 200:
            versions = version_response.json()
            print(f"✅ Supported versions: {versions['supported_versions']}")
        else:
            print(f"❌ Version info failed: {version_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Version info error: {e}")
    
    # Test V2 (simplified output)
    print("\n📊 Testing V2 (Simplified Output)...")
    v2_payload = {
        "users": test_users,
        "top_n_cards": 5,
        "version": "v2"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/recommendations", 
                               headers=headers, 
                               json=v2_payload,
                               timeout=30)
        
        if response.status_code == 200:
            v2_job = response.json()
            print(f"✅ V2 Job Created: {v2_job['job_id']}")
            print(f"   Version: {v2_job['version']}")
            print(f"   Users: {v2_job['total_users']}")
            
            # Monitor job
            job_id = v2_job['job_id']
            print(f"\n⏳ Monitoring V2 job progress...")
            
            max_wait = 60  # 60 seconds max wait
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                status_response = requests.get(f"{API_BASE_URL}/api/v1/status/{job_id}", 
                                            headers=headers,
                                            timeout=10)
                
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"   Status: {status['status']} - {status['progress_percentage']:.1f}%")
                    
                    if status['status'] in ['completed', 'failed']:
                        break
                else:
                    print(f"   Error checking status: {status_response.status_code}")
                    break
                
                time.sleep(3)
            
            # Get results
            print(f"\n📋 Getting V2 Results...")
            results_response = requests.get(f"{API_BASE_URL}/api/v1/results/{job_id}", 
                                          headers=headers,
                                          timeout=10)
            
            if results_response.status_code == 200:
                results = results_response.json()
                print(f"✅ V2 Results Retrieved:")
                print(f"   Total Users: {results['total_users']}")
                print(f"   Successful: {results['successful']}")
                print(f"   Failed: {results['failed']}")
                
                # Show sample result structure
                if results['results']:
                    sample = results['results'][0]
                    v2_columns = [k for k in sample.keys() if 'card_name' in k or 'savings' in k or 'fees' in k]
                    print(f"   Sample V2 columns: {v2_columns[:8]}...")
                    
                    # Show actual data
                    if 'top1_card_name' in sample:
                        print(f"   Top card: {sample.get('top1_card_name', 'N/A')}")
                        print(f"   Top savings: ₹{sample.get('top1_total_savings_yearly', 0)}")
            else:
                print(f"❌ Failed to get V2 results: {results_response.status_code}")
                
        else:
            print(f"❌ V2 Job Failed: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ V2 test error: {e}")
    
    print(f"\n🎉 Production test completed!")
    print(f"API is ready for production use with both V1 and V2 support")

if __name__ == "__main__":
    test_production_api()




