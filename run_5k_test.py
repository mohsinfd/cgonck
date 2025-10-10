#!/usr/bin/env python3
"""
ONE-CLICK TEST SCRIPT
Just run this file to test with 5K users!
"""

import json
import pandas as pd
import os
import subprocess
import sys

def create_test_file():
    """Create 5K test file"""
    print("=" * 60)
    print("STEP 1: Creating 5K test file...")
    print("=" * 60)
    
    try:
        df = pd.read_excel('Card Recommendation avg gmv dump.xlsx')
        df_test = df.head(5000)
        df_test.to_excel('test_5k_users.xlsx', index=False)
        print(f"✅ Created test_5k_users.xlsx with {len(df_test)} users")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_config():
    """Create config file"""
    print("\n" + "=" * 60)
    print("STEP 2: Creating config file...")
    print("=" * 60)
    
    config = {
        'api': {
            'base_url': 'https://bk-prod-external.bankkaro.com/cg/api/beta',
            'timeout': 30,
            'sleep_between_requests': 0,
            'max_retries': 3
        },
        'excel': {
            'input_file': 'test_5k_users.xlsx',
            'output_file': 'results_5k_users.xlsx',
            'sheet_name': 0
        },
        'column_mappings': {
            'user_id': 'userid',
            'amazon_spends': 'avg_amazon_gmv',
            'flipkart_spends': 'avg_flipkart_gmv',
            'myntra': 'avg_myntra_gmv',
            'ajio': 'avg_ajio_gmv',
            'avg_gmv': 'avg_confirmed_gmv',
            'grocery': 'avg_grocery_gmv'
        },
        'processing': {
            'top_n_cards': 10,
            'max_workers': 10,
            'extract_spend_keys': [
                'amazon_spends',
                'flipkart_spends',
                'grocery_spends_online',
                'other_online_spends'
            ],
            'skip_empty_rows': True,
            'continue_on_error': True,
            'other_online_mode': 'sum_components'
        }
    }
    
    try:
        with open('config_5k_test.json', 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Created config_5k_test.json")
        print("   Workers: 10")
        print("   Input: test_5k_users.xlsx")
        print("   Output: results_5k_users.xlsx")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_processing():
    """Run the batch processing"""
    print("\n" + "=" * 60)
    print("STEP 3: Running batch processing...")
    print("=" * 60)
    print("⏱️  Expected duration: 7-10 minutes")
    print("📊 Watch for 'Progress: X/5000' messages")
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, 'cardgenius_batch_runner.py', '--config', 'config_5k_test.json'],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Processing failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_results():
    """Check results"""
    print("\n" + "=" * 60)
    print("STEP 4: Checking results...")
    print("=" * 60)
    
    if not os.path.exists('results_5k_users.xlsx'):
        print("❌ Output file not found!")
        return False
    
    try:
        df = pd.read_excel('results_5k_users.xlsx')
        
        total = len(df)
        with_results = df['top1_card_name'].notna().sum()
        with_errors = df['cardgenius_error'].notna().sum()
        success_rate = (with_results / total * 100) if total > 0 else 0
        
        print(f"✅ Total users: {total}")
        print(f"✅ Successfully processed: {with_results} ({success_rate:.1f}%)")
        print(f"❌ Errors: {with_errors} ({with_errors/total*100:.1f}%)")
        print()
        print("Sample results:")
        print(df[['userid', 'top1_card_name', 'top1_net_savings']].head(5).to_string(index=False))
        
        if success_rate > 99:
            print("\n" + "=" * 60)
            print("🎉 TEST SUCCESSFUL!")
            print("=" * 60)
            print("✅ Ready to process full 200K batch")
            print()
            print("Next step: Run full_200k_batch.py")
        else:
            print("\n" + "=" * 60)
            print("⚠️  SUCCESS RATE LOW")
            print("=" * 60)
            print("Check cardgenius_batch.log for errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading results: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("🚀 ONE-CLICK 5K TEST")
    print("=" * 60)
    print()
    
    # Step 1: Create test file
    if not create_test_file():
        print("\n❌ Failed at Step 1")
        return
    
    # Step 2: Create config
    if not create_config():
        print("\n❌ Failed at Step 2")
        return
    
    # Step 3: Run processing
    if not run_processing():
        print("\n❌ Failed at Step 3")
        return
    
    # Step 4: Check results
    if not check_results():
        print("\n❌ Failed at Step 4")
        return
    
    print("\n" + "=" * 60)
    print("✅ ALL DONE!")
    print("=" * 60)

if __name__ == "__main__":
    main()

