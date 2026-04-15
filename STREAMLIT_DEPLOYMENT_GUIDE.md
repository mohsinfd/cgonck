# CardGenius Streamlit Deployment Guide

## 🚀 Streamlit Cloud Deployment

### Option 1: Streamlit Cloud (Recommended)

**Step 1: Prepare Repository**
1. Push your code to GitHub
2. Ensure all files are committed:
   - `cardgenius_combined_dashboard.py` (main dashboard)
   - `cardgenius_v2_dashboard.py` (V2 only)
   - `cardgenius_dashboard.py` (V1 only)
   - `cardgenius_batch_runner.py` (V1)
   - `cardgenius_batch_runner_v2.py` (V2)
   - `commissionable_cards.json`
   - `cashkaro_display_names.json`
   - `requirements.txt`

**Step 2: Deploy on Streamlit Cloud**
1. Go to [Streamlit Cloud](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Configure:
   - **Main file path**: `cardgenius_combined_dashboard.py`
   - **App URL**: `https://your-app-name.streamlit.app`

**Step 3: Deploy**
Click "Deploy!" and wait for deployment.

### Option 2: Render (Streamlit)

**Step 1: Create Procfile for Streamlit**
```bash
web: streamlit run cardgenius_combined_dashboard.py --server.port $PORT --server.address 0.0.0.0
```

**Step 2: Deploy on Render**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your repository
4. Configure:
   - **Name**: `cardgenius-streamlit-dashboard`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run cardgenius_combined_dashboard.py --server.port $PORT --server.address 0.0.0.0`

## 📋 Available Dashboards

### 1. Combined Dashboard (Recommended)
**File**: `cardgenius_combined_dashboard.py`
- **Features**: Choose between V1 and V2
- **URL**: `https://your-app-name.streamlit.app`
- **Use Case**: Production deployment with both options

### 2. V2 Only Dashboard
**File**: `cardgenius_v2_dashboard.py`
- **Features**: V2 simplified output only
- **URL**: `https://your-app-name.streamlit.app`
- **Use Case**: Frontend-focused deployment

### 3. V1 Only Dashboard
**File**: `cardgenius_dashboard.py`
- **Features**: V1 full output only
- **URL**: `https://your-app-name.streamlit.app`
- **Use Case**: Detailed analysis deployment

## 🌐 Production Usage

### Combined Dashboard Features
- **Version Selection**: Radio button to choose V1 or V2
- **File Upload**: Excel file upload with validation
- **Column Mapping**: Automatic fuzzy matching
- **Real-time Processing**: Progress bars and logs
- **Download Results**: Direct download of output files
- **Preview**: Sample output preview

### V2 Specific Features
- **8 columns per card** output
- **Mapped card names** (CashKaro display names)
- **Rupee formatting** for all monetary values
- **Commission filtering** (only commissionable cards)
- **Simplified breakdowns** (Amazon, Flipkart, Grocery, Other Online)

## 🔧 Configuration

### Environment Variables (Optional)
```bash
# For production customization
CARDGENIUS_API_URL=https://your-api-url.com
CARDGENIUS_API_KEY=your_api_key
```

### Requirements.txt
```
streamlit>=1.28.0
pandas>=1.5.0
openpyxl>=3.0.0
requests>=2.28.0
```

## 📊 Output Formats

### V1 Output (Full)
- Complete CardGenius data
- 20+ columns per card
- Detailed rewards/cashback info
- All spending categories

### V2 Output (Simplified)
- 8 columns per card:
  - `card_name` (mapped)
  - `total_savings_yearly`
  - `net_savings`
  - `joining_fees`
  - `amazon_breakdown`
  - `flipkart_breakdown`
  - `grocery_breakdown`
  - `other_online_breakdown`

## 🚨 Troubleshooting

### Common Issues
1. **File upload errors**: Check file format (Excel only)
2. **Column mapping issues**: Verify column names in Excel
3. **Processing failures**: Check API connectivity
4. **Memory issues**: Reduce batch size for large files

### Debug Mode
Add to your Streamlit app:
```python
import streamlit as st
st.set_page_config(page_title="CardGenius Debug")
st.write("Debug mode enabled")
```

## 📈 Monitoring

### Streamlit Cloud
- Check deployment logs
- Monitor usage metrics
- View error reports

### Render
- Check service logs
- Monitor resource usage
- Set up alerts

## 🔒 Security Notes

- **File Upload**: Temporary files are cleaned up
- **API Keys**: Use environment variables
- **Data Privacy**: Files are processed locally
- **Access Control**: Consider adding authentication

## 🎯 Best Practices

1. **Use Combined Dashboard** for production
2. **Test with sample data** first
3. **Monitor processing times** for large files
4. **Keep requirements.txt updated**
5. **Use environment variables** for configuration




