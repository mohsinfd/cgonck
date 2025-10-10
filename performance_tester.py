#!/usr/bin/env python3
"""
Performance testing suite for CardGenius API
Tests real-world scenarios with batches of 200+ users
"""

import requests
import time
import json
import pandas as pd
from datetime import datetime
import concurrent.futures
from test_data_generator import TestDataGenerator
import statistics

class APIPerformanceTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_key = "test-api-key-123"  # Use your actual API key
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }
        self.results = []
        
    def test_single_batch(self, batch_size=200, timeout=300):
        """Test a single batch processing"""
        print(f"Testing batch of {batch_size} users...")
        
        # Generate test data
        generator = TestDataGenerator()
        payload = generator.generate_api_payload(batch_size)
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/recommendations",
                headers=self.headers,
                json=payload,
                timeout=timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                
                # Extract performance metrics
                metrics = {
                    'batch_size': batch_size,
                    'duration_seconds': duration,
                    'status_code': response.status_code,
                    'users_processed': len(result_data.get('results', [])),
                    'avg_time_per_user': duration / batch_size,
                    'throughput_users_per_minute': (batch_size / duration) * 60,
                    'success': True,
                    'timestamp': datetime.now().isoformat()
                }
                
                print(f"Batch completed in {duration:.2f}s ({metrics['throughput_users_per_minute']:.1f} users/min)")
                
            else:
                metrics = {
                    'batch_size': batch_size,
                    'duration_seconds': duration,
                    'status_code': response.status_code,
                    'error': response.text,
                    'success': False,
                    'timestamp': datetime.now().isoformat()
                }
                
                print(f"Batch failed: {response.status_code} - {response.text}")
            
            self.results.append(metrics)
            return metrics
            
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            metrics = {
                'batch_size': batch_size,
                'duration_seconds': duration,
                'status_code': 'TIMEOUT',
                'error': f'Request timed out after {timeout}s',
                'success': False,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"Batch timed out after {timeout}s")
            self.results.append(metrics)
            return metrics
            
        except Exception as e:
            duration = time.time() - start_time
            metrics = {
                'batch_size': batch_size,
                'duration_seconds': duration,
                'status_code': 'ERROR',
                'error': str(e),
                'success': False,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"Batch error: {str(e)}")
            self.results.append(metrics)
            return metrics
    
    def test_concurrent_batches(self, num_batches=3, batch_size=50):
        """Test multiple concurrent batches"""
        print(f"Testing {num_batches} concurrent batches of {batch_size} users each...")
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_batches) as executor:
            futures = [
                executor.submit(self.test_single_batch, batch_size, timeout=180)
                for _ in range(num_batches)
            ]
            
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        
        successful_batches = [r for r in results if r['success']]
        failed_batches = [r for r in results if not r['success']]
        
        print(f"\nConcurrent Test Results:")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Successful batches: {len(successful_batches)}/{num_batches}")
        print(f"   Failed batches: {len(failed_batches)}")
        
        if successful_batches:
            avg_duration = statistics.mean([r['duration_seconds'] for r in successful_batches])
            avg_throughput = statistics.mean([r['throughput_users_per_minute'] for r in successful_batches])
            print(f"   Average duration: {avg_duration:.2f}s per batch")
            print(f"   Average throughput: {avg_throughput:.1f} users/min")
        
        return results
    
    def test_error_scenarios(self):
        """Test various error scenarios"""
        print("Testing error scenarios...")
        
        error_tests = [
            {
                'name': 'Invalid API Key',
                'payload': {'users': [{'user_id': 'test', 'avg_amazon_gmv': 1000}], 'top_n_cards': 10},
                'headers': {'Content-Type': 'application/json', 'X-API-Key': 'invalid-key'}
            },
            {
                'name': 'Malformed Payload',
                'payload': {'users': [{'user_id': 'test'}], 'top_n_cards': 10},  # Missing required fields
                'headers': self.headers
            },
            {
                'name': 'Empty Batch',
                'payload': {'users': [], 'top_n_cards': 10},
                'headers': self.headers
            },
            {
                'name': 'Oversized Batch',
                'payload': self._generate_oversized_payload(),
                'headers': self.headers
            }
        ]
        
        for test in error_tests:
            print(f"   Testing: {test['name']}")
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/recommendations",
                    headers=test['headers'],
                    json=test['payload'],
                    timeout=30
                )
                print(f"   Status: {response.status_code}")
                if response.status_code != 200:
                    print(f"   Error: {response.text[:100]}...")
            except Exception as e:
                print(f"   Exception: {str(e)}")
    
    def _generate_oversized_payload(self):
        """Generate an oversized payload for testing limits"""
        generator = TestDataGenerator()
        return generator.generate_api_payload(1000)  # Very large batch
    
    def run_comprehensive_test(self):
        """Run comprehensive performance test suite"""
        print("Starting comprehensive API performance test...")
        print(f"Target API: {self.base_url}")
        print("=" * 60)
        
        # Test different batch sizes
        batch_sizes = [10, 50, 100, 200]
        
        for size in batch_sizes:
            print(f"\nTesting batch size: {size}")
            self.test_single_batch(size)
            time.sleep(2)  # Brief pause between tests
        
        # Test concurrent batches
        print(f"\nTesting concurrent batches...")
        self.test_concurrent_batches(num_batches=3, batch_size=50)
        
        # Test error scenarios
        print(f"\nTesting error scenarios...")
        self.test_error_scenarios()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate performance test report"""
        if not self.results:
            print("❌ No test results to report")
            return
        
        successful_tests = [r for r in self.results if r['success']]
        failed_tests = [r for r in self.results if not r['success']]
        
        print("\n" + "=" * 60)
        print("PERFORMANCE TEST REPORT")
        print("=" * 60)
        
        print(f"Total tests: {len(self.results)}")
        print(f"Successful: {len(successful_tests)}")
        print(f"Failed: {len(failed_tests)}")
        print(f"Success rate: {len(successful_tests)/len(self.results)*100:.1f}%")
        
        if successful_tests:
            print(f"\nPerformance Metrics:")
            durations = [r['duration_seconds'] for r in successful_tests]
            throughputs = [r['throughput_users_per_minute'] for r in successful_tests]
            
            print(f"   Average duration: {statistics.mean(durations):.2f}s")
            print(f"   Min duration: {min(durations):.2f}s")
            print(f"   Max duration: {max(durations):.2f}s")
            print(f"   Average throughput: {statistics.mean(throughputs):.1f} users/min")
            print(f"   Max throughput: {max(throughputs):.1f} users/min")
        
        if failed_tests:
            print(f"\nFailed Tests:")
            for test in failed_tests:
                print(f"   Batch size {test['batch_size']}: {test.get('error', 'Unknown error')}")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"performance_test_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nDetailed results saved to: {report_file}")

def main():
    """Main testing function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test CardGenius API performance')
    parser.add_argument('--url', default='http://localhost:8000', help='API base URL')
    parser.add_argument('--batch-size', type=int, default=200, help='Batch size to test')
    parser.add_argument('--quick', action='store_true', help='Run quick test only')
    
    args = parser.parse_args()
    
    tester = APIPerformanceTester(args.url)
    
    if args.quick:
        print("Running quick test...")
        tester.test_single_batch(args.batch_size)
    else:
        tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
