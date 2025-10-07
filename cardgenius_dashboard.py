#!/usr/bin/env python3
"""
CardGenius Batch Recommendation Dashboard

A Streamlit-based web interface for uploading Excel files and processing
CardGenius recommendations with real-time progress tracking.
"""

import streamlit as st
import pandas as pd
import json
import os
import tempfile
import time
from datetime import datetime
import subprocess
import sys
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="CardGenius Batch Recommendations",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
            "continue_on_error": True
        }
    }

def create_config_file(config, output_file):
    """Create configuration file"""
    config["excel"]["input_file"] = "temp_input.xlsx"
    config["excel"]["output_file"] = output_file
    
    with open("temp_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    return "temp_config.json"

def run_batch_processing(config_file, progress_bar, status_text, log_container):
    """Run the batch processing with progress updates"""
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
        
        # Read output line by line
        output_lines = []
        log_content = []
        
        for line in iter(process.stdout.readline, ''):
            output_lines.append(line.strip())
            log_content.append(line.strip())
            
            # Update progress based on log messages
            if "Processing row" in line and "/" in line:
                try:
                    # Extract progress from log line
                    parts = line.split("Processing row ")[1].split("/")[0]
                    current = int(parts.split()[0])
                    total = int(parts.split("/")[1].split()[0])
                    progress = current / total
                    progress_bar.progress(progress)
                    status_text.text(f"Processing row {current}/{total}")
                except:
                    pass
            
            # Update log display
            log_container.text("\n".join(log_content[-20:]))  # Show last 20 lines
        
        process.wait()
        
        if process.returncode == 0:
            return True, "Processing completed successfully!"
        else:
            error_output = "\n".join(output_lines[-10:])  # Show last 10 lines for debugging
            return False, f"Processing failed with return code {process.returncode}\nLast output:\n{error_output}"
            
    except Exception as e:
        return False, f"Error running batch processing: {str(e)}"

def show_recent_files():
    """Show recently generated files"""
    try:
        # Find all cardgenius recommendation files
        import glob
        files = glob.glob("cardgenius_recommendations_*.xlsx")
        files.sort(key=os.path.getmtime, reverse=True)
        
        if files:
            st.subheader("📂 Recent Output Files")
            for i, file in enumerate(files[:5]):  # Show last 5 files
                if os.path.exists(file):
                    file_size = os.path.getsize(file)
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file))
                    
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.text(f"{file}")
                    with col2:
                        st.text(f"{file_size:,} bytes")
                    with col3:
                        if st.button("📥", key=f"download_{i}"):
                            with open(file, "rb") as f:
                                st.download_button(
                                    label="Download",
                                    data=f.read(),
                                    file_name=file,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key=f"dl_{i}"
                                )
                        st.text(mod_time.strftime("%m/%d %H:%M"))
        else:
            st.info("No output files found yet.")
    except Exception as e:
        st.warning(f"Could not list recent files: {str(e)}")

def main():
    """Main dashboard function"""
    st.title("💳 CardGenius Batch Recommendations")
    st.markdown("Upload an Excel file with user spending data to generate card recommendations.")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Add tab selection
        config_tab = st.radio(
            "Configuration Type",
            ["API & Processing", "Card Name Mapping"],
            label_visibility="collapsed"
        )
        
        # Load default config
        config = load_default_config()
        
        if config_tab == "API & Processing":
            # API Settings
            st.subheader("API Settings")
            config["api"]["sleep_between_requests"] = st.slider(
                "Sleep between requests (seconds)", 
                min_value=0.5, 
                max_value=5.0, 
                value=1.2, 
                step=0.1
            )
            config["api"]["max_retries"] = st.number_input(
                "Max retries per request", 
                min_value=1, 
                max_value=10, 
                value=3
            )
            
            # Processing Settings
            st.subheader("Processing Settings")
            config["processing"]["top_n_cards"] = st.number_input(
                "Number of top cards to extract", 
                min_value=1, 
                max_value=20, 
                value=10
            )
            config["processing"]["skip_empty_rows"] = st.checkbox(
                "Skip empty rows", 
                value=True
            )
            config["processing"]["continue_on_error"] = st.checkbox(
                "Continue on error", 
                value=True
            )
            
            # Column Mappings
            st.subheader("Column Mappings")
            st.markdown("Map your Excel columns to the required fields:")
            
            for field, default_col in config["column_mappings"].items():
                config["column_mappings"][field] = st.text_input(
                    field.replace("_", " ").title(),
                    value=default_col,
                    help=f"Column name for {field}"
                )
        
        elif config_tab == "Card Name Mapping":
            st.subheader("🃏 Card Name Mapping")
            st.markdown("Map CashKaro card names to CardGenius card names")
            
            # Load or create card mappings
            try:
                with open('manual_card_mappings.json', 'r') as f:
                    card_mappings = json.load(f)
            except:
                card_mappings = {}
            
            # Load CardGenius cards
            try:
                with open('cardgenius_all_cards.json', 'r') as f:
                    cardgenius_cards = json.load(f)
            except:
                cardgenius_cards = []
            
            if cardgenius_cards:
                st.info(f"📋 {len(cardgenius_cards)} CardGenius cards available")
                
                # Show current mappings count
                st.metric("Mapped Cards", len(card_mappings))
                
                # Auto-generate mappings button
                if st.button("🤖 Auto-Generate Mappings"):
                    from card_name_mapper import CardNameMapper
                    mapper = CardNameMapper()
                    
                    # Your CashKaro cards list
                    cashkaro_cards = [
                        "Hsbc Bank Travel One Credit Card", "Hsbc Bank Rupay Cashback Credit Card",
                        "Idfc First Bank Power Plus Credit Card", "Idfc First Bank Power Plus Rupay Credit Card",
                        "Idfc First Bank Classic Credit Card", "Idfc First Bank Wow Credit Card",
                        "Axis Bank Magnus Credit Card", "Axis Bank Flipkart Credit Card",
                        "American Express Membership Rewards Credit Card", "American Express Smartearn Credit Card",
                        "Sbi Cashback Credit Card", "Sbi Elite Credit Card",
                        "Hdfc Millenia Credit Card", "Hdfc Infinia Credit Card",
                        "Au Bank Zenith+ Credit Card", "Au Bank Altura Credit Card",
                        # Add more as needed
                    ]
                    
                    # Generate mappings
                    new_mappings = {}
                    for ck_name in cashkaro_cards:
                        match = mapper.find_best_match(ck_name, cardgenius_cards, threshold=0.7)
                        if match and ck_name not in card_mappings:
                            new_mappings[ck_name] = match[0]
                    
                    # Merge with existing
                    card_mappings.update(new_mappings)
                    
                    with open('manual_card_mappings.json', 'w') as f:
                        json.dump(card_mappings, f, indent=2)
                    
                    st.success(f"✅ Auto-generated {len(new_mappings)} new mappings")
                    st.warning("⚠️  Please review and correct the auto-generated mappings below")
                    st.rerun()
                
                # Add new mapping section
                st.subheader("➕ Add/Edit Mapping")
                
                cashkaro_name_input = st.text_input("CashKaro Card Name")
                cardgenius_name_select = st.selectbox(
                    "CardGenius Card Name",
                    [""] + sorted(cardgenius_cards)
                )
                
                if st.button("Save Mapping"):
                    if cashkaro_name_input and cardgenius_name_select:
                        card_mappings[cashkaro_name_input] = cardgenius_name_select
                        with open('manual_card_mappings.json', 'w') as f:
                            json.dump(card_mappings, f, indent=2)
                        st.success(f"✅ Saved: {cashkaro_name_input} → {cardgenius_name_select}")
                        st.rerun()
                
                # Show existing mappings
                st.subheader("📋 Current Mappings")
                
                if card_mappings:
                    # Display with edit/delete options
                    st.markdown(f"**Total: {len(card_mappings)} mappings**")
                    
                    # Create editable table
                    mapping_list = list(card_mappings.items())
                    
                    for i, (ck_name, cg_name) in enumerate(mapping_list):
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.text(ck_name)
                        with col2:
                            st.text(f"→ {cg_name}")
                        with col3:
                            if st.button("🗑️", key=f"del_{i}"):
                                del card_mappings[ck_name]
                                with open('manual_card_mappings.json', 'w') as f:
                                    json.dump(card_mappings, f, indent=2)
                                st.success(f"✅ Deleted mapping for {ck_name}")
                                st.rerun()
                    
                    # Export option
                    st.download_button(
                        "📥 Download manual_card_mappings.json",
                        data=json.dumps(card_mappings, indent=2),
                        file_name="manual_card_mappings.json",
                        mime="application/json",
                        use_container_width=True
                    )
                else:
                    st.info("No mappings yet. Click 'Auto-Generate Mappings' or add manually above.")
            else:
                st.warning("⚠️  CardGenius cards not loaded. Run the application first to fetch cards.")
    
    # Show recent files section
    show_recent_files()
    st.divider()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📁 File Upload")
        
        # File upload
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
                
                # Use the same fuzzy matching logic as the batch runner
                def fuzzy_column_match(target_column: str, available_columns: list) -> str:
                    target_lower = target_column.lower()
                    
                    # Exact match (case-insensitive)
                    for col in available_columns:
                        if col.lower() == target_lower:
                            return col
                    
                    # Partial match
                    for col in available_columns:
                        if target_lower in col.lower() or col.lower() in target_lower:
                            return col
                    
                    return None
                
                # Resolve column mappings using fuzzy matching
                resolved_mappings = {}
                missing_columns_list = []
                
                for field, target_column in config["column_mappings"].items():
                    resolved_column = fuzzy_column_match(target_column, available_columns)
                    if resolved_column:
                        resolved_mappings[field] = resolved_column
                    else:
                        missing_columns_list.append(f"{field} -> '{target_column}'")
                
                # Show resolved mappings
                if resolved_mappings:
                    st.success("✅ Column mappings resolved:")
                    for field, resolved_col in resolved_mappings.items():
                        st.success(f"  • {field} → '{resolved_col}'")
                
                if missing_columns_list:
                    st.error("❌ Could not resolve these columns:")
                    for missing in missing_columns_list:
                        st.error(f"  • {missing}")
                    st.warning("Please ensure your Excel file has the required columns.")
                    has_missing_columns = True
                else:
                    st.success("✅ All required columns found!")
                    has_missing_columns = False
                    
                    # Update config with resolved mappings
                    config["column_mappings"] = resolved_mappings
                        
            except Exception as e:
                st.error(f"Error reading Excel file: {str(e)}")
                temp_input_path = None
                has_missing_columns = True
        else:
            temp_input_path = None
            has_missing_columns = True
            st.info("👆 Please upload an Excel file to get started")
    
    with col2:
        st.header("🚀 Processing")
        
        if temp_input_path is not None and not has_missing_columns:
            if st.button("▶️ Start Processing", type="primary", use_container_width=True):
                # Create output filename with absolute path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"cardgenius_recommendations_{timestamp}.xlsx"
                output_path = os.path.abspath(output_file)
                
                # Create config file
                config_file = create_config_file(config, output_path)
                
                # Copy uploaded file to expected location
                import shutil
                shutil.copy2(temp_input_path, "temp_input.xlsx")
                
                # Processing section
                st.subheader("⚡ Processing Status")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Create a placeholder for logs
                log_placeholder = st.empty()
                
                with log_placeholder.container():
                    st.subheader("📝 Processing Logs")
                    log_container = st.empty()
                
                # Run processing
                success, message = run_batch_processing(config_file, progress_bar, status_text, log_container)
                
                if success:
                    st.success("✅ " + message)
                    
                    # Verify file exists and provide download link
                    if os.path.exists(output_path):
                        file_size = os.path.getsize(output_path)
                        st.info(f"📁 File created successfully: {output_file} ({file_size:,} bytes)")
                        
                        with open(output_path, "rb") as f:
                            st.download_button(
                                label="📥 Download Results",
                                data=f.read(),
                                file_name=output_file,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                    else:
                        st.error(f"❌ Output file not found: {output_path}")
                        st.warning("The processing completed but the output file was not created.")
                    
                    # Show summary
                    try:
                        result_df = pd.read_excel(output_path)
                        st.subheader("📊 Results Summary")
                        
                        # Count successful vs failed
                        total_rows = len(result_df)
                        if 'cardgenius_error' in result_df.columns:
                            error_rows = len(result_df[result_df['cardgenius_error'].notna() & (result_df['cardgenius_error'] != '')])
                        else:
                            error_rows = 0
                        success_rows = total_rows - error_rows
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Rows", total_rows)
                        with col2:
                            st.metric("Successful", success_rows)
                        with col3:
                            st.metric("Failed", error_rows)
                        
                        # Show sample results
                        if success_rows > 0:
                            st.subheader("🎯 Sample Results")
                            sample_cols = [col for col in result_df.columns if col.startswith('top1_')]
                            if sample_cols:
                                display_cols = sample_cols + (['cardgenius_error'] if 'cardgenius_error' in result_df.columns else [])
                                st.dataframe(result_df[display_cols].head(5))
                        
                        # Show file info
                        st.info(f"📁 Results saved to: {output_path}")
                        
                    except Exception as e:
                        st.warning(f"Could not load results summary: {str(e)}")
                        st.info(f"📁 Results file generated: {output_file}")
                
                else:
                    st.error("❌ " + message)
                
                # Cleanup
                try:
                    os.unlink("temp_input.xlsx")
                    os.unlink("temp_config.json")
                    if os.path.exists(output_file):
                        pass  # Keep output file for download
                except:
                    pass
        
        else:
            st.info("Upload a file and configure column mappings to start processing")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**CardGenius Batch Recommendations** | "
        "Built with Streamlit | "
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

if __name__ == "__main__":
    main()


