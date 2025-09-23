#!/usr/bin/env python3
"""
Simple test script to verify the dashboard functionality
"""

import streamlit as st
import pandas as pd
import os

def test_excel_loading():
    """Test Excel file loading functionality"""
    print("Testing Excel file loading...")
    
    # Test with the existing file
    try:
        df = pd.read_excel("Card Recommendation avg gmv dump.xlsx")
        print(f"✅ Successfully loaded Excel file: {len(df)} rows, {len(df.columns)} columns")
        print(f"Columns: {list(df.columns)}")
        return True
    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    print("Testing configuration loading...")
    
    try:
        import json
        with open("cardgenius_config.json", "r") as f:
            config = json.load(f)
        print("✅ Successfully loaded configuration")
        print(f"API URL: {config['api']['base_url']}")
        return True
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False

def test_api_connection():
    """Test API connection"""
    print("Testing API connection...")
    
    try:
        import requests
        response = requests.post(
            "https://card-recommendation-api-v2.bankkaro.com/cg/api/pro",
            json={
                "amazon_spends": 1000,
                "flipkart_spends": 500,
                "grocery_spends_online": 200,
                "other_online_spends": 300,
                "selected_card_id": None
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API connection successful: {len(data.get('savings', []))} cards returned")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing CardGenius Dashboard Components...")
    print("=" * 50)
    
    tests = [
        test_excel_loading,
        test_config_loading,
        test_api_connection
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("🎉 All tests passed! Dashboard should work correctly.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")


