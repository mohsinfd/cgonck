#!/usr/bin/env python3
"""
Simplified CardGenius Dashboard - Fixed version
"""

import streamlit as st
import pandas as pd
import json
import os
import tempfile
import time
import re
from datetime import datetime
import subprocess
import sys
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="CardGenius Batch Recommendations",
    page_icon="💳",
    layout="wide"
)

def fuzzy_column_match(target_column: str, available_columns: list) -> str:
    """Find the best matching column using case-insensitive fuzzy matching"""
    target_lower = target_column.lower()
    
    # Exact match (case-insensitive)
    for col in available_columns:
        if col.lower() == target_lower:
            return col
    
    # Partial match
    for col in available_columns:
        if target_lower in col.lower() or col.lower() in target_lower:
            return col
    
    # Regex-based matching for common patterns
    patterns = {
        'amazon': r'amazon.*gmv',
        'flipkart': r'flipkart.*gmv',
        'myntra': r'myntra.*gmv',
        'ajio': r'ajio.*gmv',
        'grocery': r'grocery.*gmv',
        'confirmed_gmv': r'(confirmed|avg_confirmed).*gmv',
        'user_id': r'user.*id'
    }
    
    for key, pattern in patterns.items():
        if key in target_lower:
            for col in available_columns:
                if re.search(pattern, col.lower()):
                    return col
    
    return None

def load_default_config():
    """Load default configuration"""
    return {
        "api": {
            "base_url": "https://card-recommendation-api-v2.bankkaro.com/cg/api/pro",
            "timeout": 30,
            "sleep_between_requests": 1.2,
            "max_retries": 3
        },
        "excel": {
            "sheet_name": 0
        },
        "column_mappings": {
            "user_id": "userid",
            "amazon_spends": " avg_amazon_gmv ",
            "flipkart_spends": " avg_flipkart_gmv ",
            "myntra": " avg_myntra_gmv ",
            "ajio": " avg_ajio_gmv ",
            "avg_gmv": " avg_confirmed_gmv ",
            "grocery": " avg_grocery_gmv ",
            "total_gmv": " total_gmv "
        },
        "processing": {
            "top_n_cards": 10,
            "extract_spend_keys": [
                "amazon_spends",
                "flipkart_spends", 
                "grocery_spends_online",
                "other_online_spends"
            ],
            "skip_empty_rows": True,
            "continue_on_error": True,
            "other_online_mode": "sum_components"
        }
    }

def create_config_file(config, output_file):
    """Create configuration file"""
    config["excel"]["input_file"] = "temp_input.xlsx"
    config["excel"]["output_file"] = output_file
    
    with open("temp_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    return "temp_config.json"

def run_batch_processing(config_file):
    """Run the batch processing"""
    try:
        # Run the batch runner
        cmd = [sys.executable, "cardgenius_batch_runner.py", "--config", config_file]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Read output
        output_lines = []
        for line in iter(process.stdout.readline, ''):
            output_lines.append(line.strip())
        
        process.wait()
        
        if process.returncode == 0:
            return True, "Processing completed successfully!"
        else:
            return False, f"Processing failed with return code {process.returncode}"
            
    except Exception as e:
        return False, f"Error running batch processing: {str(e)}"

def main():
    """Main dashboard function"""
    st.title("💳 CardGenius Batch Recommendations")
    st.markdown("Upload an Excel file with user spending data to generate card recommendations.")
    
    # Load default config
    config = load_default_config()
    
    # File upload
    st.header("📁 File Upload")
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload an Excel file with user spending data"
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_input_path = tmp_file.name
        
        # Preview the uploaded file
        try:
            df_preview = pd.read_excel(temp_input_path)
            st.subheader("📊 File Preview")
            st.dataframe(df_preview.head(10))
            
            st.info(f"📈 File contains {len(df_preview)} rows and {len(df_preview.columns)} columns")
            
            # Show column mapping validation with fuzzy matching
            st.subheader("🔍 Column Mapping Validation")
            available_columns = list(df_preview.columns)
            
            # Resolve column mappings using fuzzy matching
            resolved_mappings = {}
            missing_columns = []
            
            for field, target_column in config["column_mappings"].items():
                resolved_column = fuzzy_column_match(target_column, available_columns)
                if resolved_column:
                    resolved_mappings[field] = resolved_column
                else:
                    missing_columns.append(f"{field} -> '{target_column}'")
            
            # Show resolved mappings
            if resolved_mappings:
                st.success("✅ Column mappings resolved:")
                for field, resolved_col in resolved_mappings.items():
                    st.success(f"  • {field} → '{resolved_col}'")
            
            if missing_columns:
                st.error("❌ Could not resolve these columns:")
                for missing in missing_columns:
                    st.error(f"  • {missing}")
                st.warning("Please ensure your Excel file has the required columns.")
            else:
                st.success("✅ All required columns found!")
                
                # Update config with resolved mappings
                config["column_mappings"] = resolved_mappings
                
                # Processing section
                st.header("🚀 Processing")
                
                if st.button("▶️ Start Processing", type="primary", use_container_width=True):
                    # Create output filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = f"cardgenius_recommendations_{timestamp}.xlsx"
                    
                    # Create config file
                    config_file = create_config_file(config, output_file)
                    
                    # Copy uploaded file to expected location
                    import shutil
                    shutil.copy2(temp_input_path, "temp_input.xlsx")
                    
                    # Show processing status
                    with st.spinner("Processing... This may take several minutes."):
                        success, message = run_batch_processing(config_file)
                    
                    if success:
                        st.success("✅ " + message)
                        
                        # Provide download link
                        if os.path.exists(output_file):
                            with open(output_file, "rb") as f:
                                st.download_button(
                                    label="📥 Download Results",
                                    data=f.read(),
                                    file_name=output_file,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                        
                        # Show summary
                        try:
                            result_df = pd.read_excel(output_file)
                            st.subheader("📊 Results Summary")
                            
                            # Count successful vs failed
                            total_rows = len(result_df)
                            error_rows = len(result_df[result_df['cardgenius_error'] != ''])
                            success_rows = total_rows - error_rows
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Rows", total_rows)
                            with col2:
                                st.metric("Successful", success_rows)
                            with col3:
                                st.metric("Failed", error_rows)
                            
                        except Exception as e:
                            st.warning(f"Could not load results summary: {str(e)}")
                    
                    else:
                        st.error("❌ " + message)
                    
                    # Cleanup
                    try:
                        os.unlink("temp_input.xlsx")
                        os.unlink("temp_config.json")
                    except:
                        pass
                
        except Exception as e:
            st.error(f"Error reading Excel file: {str(e)}")
    else:
        st.info("👆 Please upload an Excel file to get started")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**CardGenius Batch Recommendations** | "
        "Built with Streamlit | "
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

if __name__ == "__main__":
    main()

