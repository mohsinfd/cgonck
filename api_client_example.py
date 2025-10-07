#!/usr/bin/env python3
"""
Example client code for Data Team to use the CardGenius API
"""

import requests
import time
import json

# API Configuration
API_URL = "http://localhost:8000"  # Change to your production URL
API_KEY = "YOUR_SECRET_API_KEY_HERE"

def submit_batch(users_data):
    """
    Submit a batch of users for card recommendations
    
    Args:
        users_data: List of user spending data
        
    Returns:
        job_id for tracking the request
    """
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "users": users_data,
        "top_n_cards": 10
    }
    
    response = requests.post(
        f"{API_URL}/api/v1/recommendations",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

def check_status(job_id):
    """Check the status of a job"""
    headers = {"X-API-Key": API_KEY}
    
    response = requests.get(
        f"{API_URL}/api/v1/status/{job_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

def get_results(job_id):
    """Get results of a completed job"""
    headers = {"X-API-Key": API_KEY}
    
    response = requests.get(
        f"{API_URL}/api/v1/results/{job_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

def process_batch_with_polling(users_data, poll_interval=5):
    """
    Submit batch and wait for results with polling
    
    Args:
        users_data: List of user spending data
        poll_interval: Seconds between status checks
        
    Returns:
        Results data
    """
    # Submit batch
    print(f"📤 Submitting batch of {len(users_data)} users...")
    job_response = submit_batch(users_data)
    job_id = job_response['job_id']
    print(f"✅ Job created: {job_id}")
    print(f"   Status: {job_response['status']}")
    print()
    
    # Poll for completion
    while True:
        status = check_status(job_id)
        progress = status['progress_percentage']
        
        print(f"⏳ Progress: {progress:.1f}% ({status['processed_users']}/{status['total_users']} users)")
        
        if status['status'] == 'completed':
            print(f"✅ Job completed!")
            print(f"   Successful: {status['successful']}")
            print(f"   Failed: {status['failed']}")
            break
        elif status['status'] == 'failed':
            print(f"❌ Job failed!")
            return None
        
        time.sleep(poll_interval)
    
    # Get results
    print(f"\n📥 Fetching results...")
    results = get_results(job_id)
    print(f"✅ Retrieved {len(results['results'])} user results")
    
    return results

# Example usage
if __name__ == "__main__":
    # Example: Process 3 users
    sample_users = [
        {
            "user_id": "user_001",
            "avg_amazon_gmv": 5000,
            "avg_flipkart_gmv": 3000,
            "avg_myntra_gmv": 2000,
            "avg_ajio_gmv": 1000,
            "avg_confirmed_gmv": 5000,
            "avg_grocery_gmv": 8000,
            "total_gmv": 24000
        },
        {
            "user_id": "user_002",
            "avg_amazon_gmv": 10000,
            "avg_flipkart_gmv": 5000,
            "avg_myntra_gmv": 3000,
            "avg_ajio_gmv": 2000,
            "avg_confirmed_gmv": 8000,
            "avg_grocery_gmv": 12000,
            "total_gmv": 40000
        },
        {
            "user_id": "user_003",
            "avg_amazon_gmv": 2000,
            "avg_flipkart_gmv": 1500,
            "avg_myntra_gmv": 1000,
            "avg_ajio_gmv": 500,
            "avg_confirmed_gmv": 3000,
            "avg_grocery_gmv": 5000,
            "total_gmv": 13000
        }
    ]
    
    # Process the batch
    results = process_batch_with_polling(sample_users)
    
    if results:
        # Save to file
        with open('api_results_example.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to api_results_example.json")
        
        # Display sample result
        print(f"\n📊 Sample Result (User 1):")
        print(json.dumps(results['results'][0], indent=2)[:500] + "...")


