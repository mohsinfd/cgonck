#!/usr/bin/env python3
"""
Test script for CardGenius API Server V1 and V2
Demonstrates both version capabilities
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"
API_KEY = "cgapi_2025_secure_key_12345"

def test_api_versions():
    """Test both V1 and V2 API versions"""
    
    # Test data
    test_users = [
        {
            "user_id": "test_user_001",
            "avg_amazon_gmv": 15000,
            "avg_flipkart_gmv": 10000,
            "avg_myntra_gmv": 3000,
            "avg_ajio_gmv": 5000,
            "avg_confirmed_gmv": 50000,
            "avg_grocery_gmv": 2000
        },
        {
            "user_id": "test_user_002", 
            "avg_amazon_gmv": 8000,
            "avg_flipkart_gmv": 6000,
            "avg_myntra_gmv": 1500,
            "avg_ajio_gmv": 2000,
            "avg_confirmed_gmv": 30000,
            "avg_grocery_gmv": 1000
        }
    ]
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print("🚀 Testing CardGenius API Server V2.0")
    print("=" * 50)
    
    # Test V1
    print("\n📊 Testing V1 (Full Output)...")
    v1_payload = {
        "users": test_users,
        "top_n_cards": 3,
        "version": "v1"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/recommendations", 
                           headers=headers, 
                           json=v1_payload)
    
    if response.status_code == 200:
        v1_job = response.json()
        print(f"✅ V1 Job Created: {v1_job['job_id']}")
        print(f"   Version: {v1_job['version']}")
        print(f"   Users: {v1_job['total_users']}")
    else:
        print(f"❌ V1 Job Failed: {response.status_code} - {response.text}")
        return
    
    # Test V2
    print("\n📊 Testing V2 (Simplified Output)...")
    v2_payload = {
        "users": test_users,
        "top_n_cards": 3,
        "version": "v2"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/recommendations", 
                           headers=headers, 
                           json=v2_payload)
    
    if response.status_code == 200:
        v2_job = response.json()
        print(f"✅ V2 Job Created: {v2_job['job_id']}")
        print(f"   Version: {v2_job['version']}")
        print(f"   Users: {v2_job['total_users']}")
    else:
        print(f"❌ V2 Job Failed: {response.status_code} - {response.text}")
        return
    
    # Monitor both jobs
    print("\n⏳ Monitoring job progress...")
    jobs = [v1_job['job_id'], v2_job['job_id']]
    
    while True:
        all_completed = True
        
        for job_id in jobs:
            status_response = requests.get(f"{API_BASE_URL}/api/v1/status/{job_id}", 
                                        headers=headers)
            
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"   {status['version'].upper()}: {status['status']} - {status['progress_percentage']:.1f}%")
                
                if status['status'] not in ['completed', 'failed']:
                    all_completed = False
            else:
                print(f"   Error checking status for {job_id}")
                all_completed = False
        
        if all_completed:
            break
            
        time.sleep(2)
    
    # Get results
    print("\n📋 Getting Results...")
    
    for job_id in jobs:
        results_response = requests.get(f"{API_BASE_URL}/api/v1/results/{job_id}", 
                                      headers=headers)
        
        if results_response.status_code == 200:
            results = results_response.json()
            print(f"\n✅ {results['version'].upper()} Results:")
            print(f"   Total Users: {results['total_users']}")
            print(f"   Successful: {results['successful']}")
            print(f"   Failed: {results['failed']}")
            
            # Show sample result structure
            if results['results']:
                sample = results['results'][0]
                print(f"   Sample columns: {list(sample.keys())[:5]}...")
        else:
            print(f"❌ Failed to get results for {job_id}: {results_response.status_code}")

if __name__ == "__main__":
    try:
        test_api_versions()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")




