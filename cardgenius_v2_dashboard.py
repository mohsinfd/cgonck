#!/usr/bin/env python3
"""
CardGenius V2 Dashboard - Streamlit Interface
Simplified dashboard for V2 card recommendations with 8-column output
"""

import streamlit as st
import pandas as pd
import requests
import json
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="CardGenius V2 Dashboard",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "cgapi_2025_secure_key_12345"

def get_api_headers():
    return {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

def test_api_connection():
    """Test if API server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/versions", headers=get_api_headers(), timeout=5)
        return response.status_code == 200
    except:
        return False

def create_recommendation_job(users_data, version="v2"):
    """Create a recommendation job"""
    payload = {
        "users": users_data,
        "top_n_cards": 10,
        "version": version
    }
    
    response = requests.post(
        f"{API_BASE_URL}/recommendations", 
        headers=get_api_headers(), 
        data=json.dumps(payload)
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to create job: {response.text}")
        return None

def get_job_status(job_id):
    """Get job status"""
    response = requests.get(f"{API_BASE_URL}/status/{job_id}", headers=get_api_headers())
    if response.status_code == 200:
        return response.json()
    return None

def get_job_results(job_id):
    """Get job results"""
    response = requests.get(f"{API_BASE_URL}/results/{job_id}", headers=get_api_headers())
    if response.status_code == 200:
        return response.json()
    return None

def main():
    st.title("💳 CardGenius V2 Dashboard")
    st.markdown("**Simplified Card Recommendations with 8-Column Output**")
    
    # Sidebar
    st.sidebar.header("Configuration")
    
    # API Status
    st.sidebar.subheader("API Status")
    if test_api_connection():
        st.sidebar.success("✅ API Server Connected")
    else:
        st.sidebar.error("❌ API Server Not Connected")
        st.sidebar.info("Please start the API server: `python api_server.py`")
        return
    
    # Version Selection
    version = st.sidebar.selectbox(
        "Select Version",
        ["v2", "v1"],
        help="V2: Simplified 8-column output | V1: Full detailed output"
    )
    
    st.sidebar.markdown("---")
    
    # Main Content
    tab1, tab2, tab3 = st.tabs(["📊 Upload Data", "🔄 Process Jobs", "📈 View Results"])
    
    with tab1:
        st.header("Upload User Spending Data")
        
        # Sample data format
        st.subheader("Expected Data Format")
        sample_data = {
            "userid": ["user_001", "user_002"],
            "avg_confirmed_gmv": [50000, 75000],
            "avg_amazon_gmv": [15000, 20000],
            "avg_flipkart_gmv": [10000, 15000],
            "avg_ajio_gmv": [5000, 8000],
            "avg_myntra_gmv": [3000, 5000],
            "avg_grocery_gmv": [8000, 12000],
            "active_months": [12, 12],
            "total_gmv": [96000, 135000]
        }
        
        sample_df = pd.DataFrame(sample_data)
        st.dataframe(sample_df, use_container_width=True)
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Excel file",
            type=['xlsx', 'xls'],
            help="Upload an Excel file with user spending data"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)
                st.success(f"✅ File uploaded successfully! {len(df)} rows loaded")
                
                # Show preview
                st.subheader("Data Preview")
                st.dataframe(df.head(), use_container_width=True)
                
                # Convert to API format
                users_data = []
                for _, row in df.iterrows():
                    user_data = {
                        "user_id": str(row.get('userid', '')),
                        "avg_amazon_gmv": float(row.get('avg_amazon_gmv', 0)),
                        "avg_flipkart_gmv": float(row.get('avg_flipkart_gmv', 0)),
                        "avg_myntra_gmv": float(row.get('avg_myntra_gmv', 0)),
                        "avg_ajio_gmv": float(row.get('avg_ajio_gmv', 0)),
                        "avg_confirmed_gmv": float(row.get('avg_confirmed_gmv', 0)),
                        "avg_grocery_gmv": float(row.get('avg_grocery_gmv', 0))
                    }
                    users_data.append(user_data)
                
                # Store in session state
                st.session_state.users_data = users_data
                st.session_state.uploaded_df = df
                
                st.success(f"✅ {len(users_data)} users ready for processing")
                
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
    
    with tab2:
        st.header("Process Recommendations")
        
        if 'users_data' not in st.session_state:
            st.warning("⚠️ Please upload data first in the 'Upload Data' tab")
            return
        
        users_data = st.session_state.users_data
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Job Configuration")
            top_n_cards = st.slider("Top N Cards", 1, 20, 10)
            st.info(f"Processing {len(users_data)} users with {version.upper()} format")
        
        with col2:
            st.subheader("Actions")
            if st.button("🚀 Start Processing", type="primary"):
                with st.spinner("Creating recommendation job..."):
                    job_response = create_recommendation_job(users_data, version)
                    
                    if job_response:
                        st.session_state.job_id = job_response['job_id']
                        st.success(f"✅ Job created: {job_response['job_id']}")
                        st.info(f"Processing {job_response['total_users']} users with {job_response['version'].upper()} format")
        
        # Job Status
        if 'job_id' in st.session_state:
            st.subheader("Job Status")
            job_id = st.session_state.job_id
            
            if st.button("🔄 Refresh Status"):
                status = get_job_status(job_id)
                if status:
                    st.session_state.job_status = status
            
            if 'job_status' in st.session_state:
                status = st.session_state.job_status
                
                # Progress bar
                progress = status['progress_percentage'] / 100
                st.progress(progress)
                
                # Status info
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Status", status['status'].upper())
                with col2:
                    st.metric("Progress", f"{status['progress_percentage']:.1f}%")
                with col3:
                    st.metric("Processed", f"{status['processed_users']}/{status['total_users']}")
                with col4:
                    st.metric("Success Rate", f"{status['successful']}/{status['processed_users']}")
                
                if status['status'] == 'completed':
                    st.success("🎉 Job completed successfully!")
                    st.session_state.job_completed = True
                elif status['status'] == 'failed':
                    st.error("❌ Job failed")
    
    with tab3:
        st.header("View Results")
        
        if 'job_completed' not in st.session_state:
            st.warning("⚠️ Please complete a job first in the 'Process Jobs' tab")
            return
        
        if st.button("📥 Download Results"):
            job_id = st.session_state.job_id
            results = get_job_results(job_id)
            
            if results and 'results' in results:
                # Convert to DataFrame
                results_df = pd.DataFrame(results['results'])
                
                # Show results
                st.subheader("Recommendation Results")
                st.dataframe(results_df, use_container_width=True)
                
                # Download button
                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="📊 Download CSV",
                    data=csv,
                    file_name=f"cardgenius_v2_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                # V2 specific columns explanation
                if version == "v2":
                    st.subheader("V2 Output Columns")
                    st.info("""
                    **V2 Simplified Output (8 columns per card):**
                    - `card_name`: Mapped to CashKaro display names
                    - `total_savings_yearly`: Total annual savings in ₹
                    - `net_savings`: Net savings after fees in ₹
                    - `joining_fees`: Card joining fees in ₹
                    - `amazon_breakdown`: Amazon savings in ₹
                    - `flipkart_breakdown`: Flipkart savings in ₹
                    - `grocery_breakdown`: Grocery savings in ₹
                    - `other_online_breakdown`: Other online savings in ₹
                    """)
            else:
                st.error("❌ No results available")

if __name__ == "__main__":
    main()