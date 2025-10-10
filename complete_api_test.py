#!/usr/bin/env python3
"""
Complete API test that waits for job completion
"""

import requests
import json
import time
from test_data_generator import TestDataGenerator

def test_complete_workflow(base_url, api_key, batch_size=10):
    """Test complete API workflow including job completion"""
    print(f"Testing complete workflow with {batch_size} users")
    
    # Generate test data
    generator = TestDataGenerator()
    payload = generator.generate_api_payload(batch_size)
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    # Step 1: Submit job
    print("Step 1: Submitting job...")
    start_time = time.time()
    
    response = requests.post(
        f"{base_url}/api/v1/recommendations",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"Failed to submit job: {response.status_code} - {response.text}")
        return False
    
    job_data = response.json()
    job_id = job_data['job_id']
    print(f"Job submitted: {job_id}")
    
    # Step 2: Monitor job status
    print("Step 2: Monitoring job status...")
    max_wait_time = 300  # 5 minutes
    check_interval = 5   # Check every 5 seconds
    
    while time.time() - start_time < max_wait_time:
        status_response = requests.get(
            f"{base_url}/api/v1/status/{job_id}",
            headers={"X-API-Key": api_key},
            timeout=30
        )
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            status = status_data.get('status', 'unknown')
            processed = status_data.get('processed_users', 0)
            total = status_data.get('total_users', batch_size)
            
            print(f"  Status: {status}, Processed: {processed}/{total}")
            
            if status == 'completed':
                # Step 3: Get results
                print("Step 3: Getting results...")
                results_response = requests.get(
                    f"{base_url}/api/v1/results/{job_id}",
                    headers={"X-API-Key": api_key},
                    timeout=30
                )
                
                if results_response.status_code == 200:
                    results = results_response.json()
                    duration = time.time() - start_time
                    
                    print(f"SUCCESS!")
                    print(f"  Total duration: {duration:.2f} seconds")
                    print(f"  Users processed: {len(results.get('results', []))}")
                    print(f"  Throughput: {(batch_size / duration) * 60:.1f} users/min")
                    
                    # Show sample results
                    if results.get('results'):
                        sample_user = results['results'][0]
                        print(f"  Sample user: {sample_user.get('user_id', 'N/A')}")
                        print(f"  Cards recommended: {len(sample_user.get('recommendations', []))}")
                        
                        if sample_user.get('recommendations'):
                            top_card = sample_user['recommendations'][0]
                            print(f"  Top card: {top_card.get('card_name', 'N/A')}")
                            print(f"  Net savings: {top_card.get('net_savings', 'N/A')}")
                    
                    return True
                else:
                    print(f"Failed to get results: {results_response.status_code}")
                    return False
                    
            elif status == 'failed':
                print(f"Job failed: {status_data.get('error', 'Unknown error')}")
                return False
                
        else:
            print(f"Failed to check status: {status_response.status_code}")
            return False
        
        time.sleep(check_interval)
    
    print(f"Job timed out after {max_wait_time} seconds")
    return False

def test_different_batch_sizes():
    """Test different batch sizes"""
    base_url = "https://cardgenius-batch-api.onrender.com"
    api_key = "cgapi_2025_secure_key_12345"
    
    batch_sizes = [5, 10, 50, 200]
    
    for size in batch_sizes:
        print(f"\n{'='*60}")
        print(f"TESTING BATCH SIZE: {size}")
        print(f"{'='*60}")
        
        success = test_complete_workflow(base_url, api_key, size)
        
        if success:
            print(f"✅ Batch size {size}: PASSED")
        else:
            print(f"❌ Batch size {size}: FAILED")
        
        time.sleep(2)  # Brief pause between tests

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test CardGenius API workflow')
    parser.add_argument('--batch-size', type=int, default=10, help='Batch size to test')
    parser.add_argument('--all-sizes', action='store_true', help='Test all batch sizes')
    
    args = parser.parse_args()
    
    base_url = "https://cardgenius-batch-api.onrender.com"
    api_key = "cgapi_2025_secure_key_12345"
    
    if args.all_sizes:
        test_different_batch_sizes()
    else:
        test_complete_workflow(base_url, api_key, args.batch_size)
