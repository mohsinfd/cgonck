#!/usr/bin/env python3
"""
QUICK TEST SCRIPT - 15 ROWS ONLY
"""
import json
import pandas as pd
import os
import subprocess
import sys

def create_sample_file():
    """Create 15-row test file"""
    print("=" * 60)
    print("STEP 1: Creating 15-row test file...")
    print("=" * 60)
    
    try:
        # Try to read the file
        df = pd.read_excel('Card Recommendation avg gmv dump.xlsx')
        df_sample = df.head(15)
        df_sample.to_excel('test_sample_15.xlsx', index=False)
        print(f"✅ Created test_sample_15.xlsx with {len(df_sample)} users")
        return True
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        print("Please close the Excel file if it's open and try again")
        return False

def create_config():
    """Create config file for 15-row test"""
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
            'input_file': 'test_sample_15.xlsx',
            'output_file': 'results_sample_15.xlsx',
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
            'top_n_cards': 3,
            'max_workers': 5,  # Reduced for small test
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
    
    with open('config_sample_15.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Created config_sample_15.json")
    return True

def run_test():
    """Run the test"""
    print("\n" + "=" * 60)
    print("STEP 3: Running test...")
    print("=" * 60)
    
    try:
        # Import and run the batch processor
        from cardgenius_batch_runner import CardGeniusBatchRunner
        
        runner = CardGeniusBatchRunner('config_sample_15.json')
        output_file = runner.process_excel()
        
        print(f"✅ Test completed! Results saved to: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def show_results():
    """Show sample results"""
    print("\n" + "=" * 60)
    print("STEP 4: Sample Results")
    print("=" * 60)
    
    try:
        df = pd.read_excel('results_sample_15.xlsx')
        
        print(f"Total users processed: {len(df)}")
        print(f"Columns in output: {len(df.columns)}")
        print()
        
        # Show first few rows
        print("Sample results (first 3 users):")
        sample_cols = ['userid', 'top1_card_name', 'top1_net_savings', 'top1_recommended_redemption_method', 'top1_recommended_redemption_conversion_rate']
        print(df[sample_cols].head(3).to_string(index=False))
        
        print()
        print("All columns:")
        for i, col in enumerate(df.columns, 1):
            print(f"{i:2d}. {col}")
            
    except Exception as e:
        print(f"❌ Error reading results: {e}")

if __name__ == "__main__":
    print("🚀 QUICK TEST - 15 ROWS ONLY")
    print("=" * 60)
    
    # Step 1: Create sample file
    if not create_sample_file():
        sys.exit(1)
    
    # Step 2: Create config
    if not create_config():
        sys.exit(1)
    
    # Step 3: Run test
    if not run_test():
        sys.exit(1)
    
    # Step 4: Show results
    show_results()
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)
