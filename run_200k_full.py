#!/usr/bin/env python3
"""
ONE-CLICK FULL 200K BATCH SCRIPT
Run this after successful 5K test
"""

import json
import os
import subprocess
import sys
import pandas as pd
from datetime import datetime

def create_config():
    """Create config for full 200K batch"""
    print("=" * 60)
    print("CREATING CONFIG FOR 200K USERS")
    print("=" * 60)
    
    config = {
        'api': {
            'base_url': 'https://bk-prod-external.bankkaro.com/cg/api/beta',
            'timeout': 30,
            'sleep_between_requests': 0,
            'max_retries': 3
        },
        'excel': {
            'input_file': 'Card Recommendation avg gmv dump.xlsx',
            'output_file': 'results_200k_users.xlsx',
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
    
    with open('config_200k_full.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Created config_200k_full.json")
    print(f"   Workers: {config['processing']['max_workers']}")
    print(f"   Input: {config['excel']['input_file']}")
    print(f"   Output: {config['excel']['output_file']}")

def check_prerequisites():
    """Check if we're ready to run"""
    print("\n" + "=" * 60)
    print("PRE-FLIGHT CHECKS")
    print("=" * 60)
    
    # Check input file
    if not os.path.exists('Card Recommendation avg gmv dump.xlsx'):
        print("❌ Input file not found: Card Recommendation avg gmv dump.xlsx")
        return False
    
    df = pd.read_excel('Card Recommendation avg gmv dump.xlsx')
    print(f"✅ Input file found: {len(df)} users")
    
    # Check disk space (need ~350 GB)
    import shutil
    total, used, free = shutil.disk_usage(".")
    free_gb = free // (2**30)
    print(f"✅ Free disk space: {free_gb} GB")
    
    if free_gb < 350:
        print(f"⚠️  WARNING: Need 350 GB, you have {free_gb} GB")
        print("   Consider processing in smaller batches")
        response = input("Continue anyway? (yes/no): ")
        if response.lower() != 'yes':
            return False
    
    # Check if 5K test was successful
    if os.path.exists('results_5k_users.xlsx'):
        test_df = pd.read_excel('results_5k_users.xlsx')
        success_rate = test_df['top1_card_name'].notna().sum() / len(test_df) * 100
        print(f"✅ 5K test success rate: {success_rate:.1f}%")
        
        if success_rate < 99:
            print("⚠️  WARNING: 5K test had low success rate")
            response = input("Continue anyway? (yes/no): ")
            if response.lower() != 'yes':
                return False
    else:
        print("⚠️  No 5K test results found")
        print("   Recommended: Run run_5k_test.py first")
        response = input("Continue anyway? (yes/no): ")
        if response.lower() != 'yes':
            return False
    
    return True

def run_processing():
    """Run the batch processing"""
    print("\n" + "=" * 60)
    print("STARTING 200K BATCH PROCESSING")
    print("=" * 60)
    print("⏱️  Expected duration: 5-7 hours")
    print("💡 Tip: Leave laptop plugged in and don't close!")
    print("📊 Check cardgenius_batch.log for progress")
    print()
    
    start_time = datetime.now()
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, 'cardgenius_batch_runner.py', '--config', 'config_200k_full.json'],
            check=True
        )
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print()
        print("=" * 60)
        print("✅ PROCESSING COMPLETE!")
        print("=" * 60)
        print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {duration}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Processing failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_results():
    """Check final results"""
    print("\n" + "=" * 60)
    print("CHECKING RESULTS")
    print("=" * 60)
    
    if not os.path.exists('results_200k_users.xlsx'):
        print("❌ Output file not found!")
        return False
    
    try:
        df = pd.read_excel('results_200k_users.xlsx')
        
        total = len(df)
        with_results = df['top1_card_name'].notna().sum()
        with_errors = df['cardgenius_error'].notna().sum()
        success_rate = (with_results / total * 100) if total > 0 else 0
        
        print(f"✅ Total users: {total:,}")
        print(f"✅ Successfully processed: {with_results:,} ({success_rate:.1f}%)")
        print(f"❌ Errors: {with_errors:,} ({with_errors/total*100:.1f}%)")
        
        # File size
        file_size = os.path.getsize('results_200k_users.xlsx') / (1024**3)
        print(f"📁 Output file size: {file_size:.2f} GB")
        
        print()
        print("Sample results:")
        print(df[['userid', 'top1_card_name', 'top1_net_savings']].head(5).to_string(index=False))
        
        print("\n" + "=" * 60)
        print("🎉 BATCH COMPLETE!")
        print("=" * 60)
        print(f"Results saved: results_200k_users.xlsx")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading results: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("🚀 FULL 200K BATCH PROCESSING")
    print("=" * 60)
    print()
    
    # Create config
    create_config()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Pre-flight checks failed")
        return
    
    # Confirm to proceed
    print("\n" + "=" * 60)
    print("READY TO START")
    print("=" * 60)
    print("This will take 5-7 hours")
    print("Make sure:")
    print("  - Laptop is plugged in")
    print("  - Good internet connection")
    print("  - Won't need laptop for next few hours")
    print()
    
    response = input("Start processing? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled")
        return
    
    # Run processing
    if not run_processing():
        print("\n❌ Processing failed")
        return
    
    # Check results
    if not check_results():
        print("\n❌ Failed to validate results")
        return
    
    print("\n" + "=" * 60)
    print("✅ ALL DONE!")
    print("=" * 60)

if __name__ == "__main__":
    main()

