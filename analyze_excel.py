#!/usr/bin/env python3
"""
Quick script to analyze the Excel file structure and column mappings
"""

import pandas as pd
import sys

def analyze_excel(file_path):
    """Analyze Excel file structure and suggest column mappings"""
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        print("=== EXCEL FILE ANALYSIS ===")
        print(f"File: {file_path}")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("\n=== FIRST 5 ROWS ===")
        print(df.head())
        print("\n=== DATA TYPES ===")
        print(df.dtypes)
        print("\n=== SAMPLE DATA VALUES ===")
        for col in df.columns:
            print(f"{col}: {df[col].dropna().head(3).tolist()}")
        
        # Suggest column mappings
        print("\n=== SUGGESTED COLUMN MAPPINGS ===")
        columns_lower = [col.lower().strip() for col in df.columns]
        
        mappings = {}
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'user' in col_lower and 'id' in col_lower:
                mappings['user_id'] = col
            elif 'amazon' in col_lower:
                mappings['amazon_spends'] = col
            elif 'flipkart' in col_lower:
                mappings['flipkart_spends'] = col
            elif 'myntra' in col_lower:
                mappings['myntra'] = col
            elif 'ajio' in col_lower:
                mappings['ajio'] = col
            elif 'avg' in col_lower and 'gmv' in col_lower:
                mappings['avg_gmv'] = col
            elif 'grocery' in col_lower:
                mappings['grocery'] = col
            elif 'total' in col_lower and 'gmv' in col_lower:
                mappings['total_gmv'] = col
        
        print("Detected mappings:")
        for key, value in mappings.items():
            print(f"  {key}: '{value}'")
        
        return df, mappings
        
    except Exception as e:
        print(f"Error analyzing Excel file: {e}")
        return None, None

if __name__ == "__main__":
    file_path = "Card Recommendation avg gmv dump.xlsx"
    df, mappings = analyze_excel(file_path)




