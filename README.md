# CardGenius Batch Recommendations

A Streamlit-based web application for generating credit card recommendations using the CardGenius API.

## Features

- 📁 **Excel File Upload**: Upload user spending data in Excel format
- 🔄 **Batch Processing**: Process multiple users simultaneously
- 📊 **Real-time Progress**: Live updates during processing
- 💾 **File Management**: Automatic file generation and download
- 🎯 **Smart Recommendations**: Top 3 card recommendations per user
- 📈 **Net Savings Calculation**: Proper ranking by net savings (total_savings - joining_fees + extra_benefits)

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Dashboard**:
   ```bash
   streamlit run cardgenius_dashboard.py
   ```

3. **Access the App**:
   - Open your browser to `http://localhost:8501`

## Configuration

The app uses a configuration system for:
- API endpoints
- Column mappings
- Output file settings

## File Storage

- **Local Development**: Files saved to current working directory
- **Production**: Files saved to app's working directory (varies by platform)
- **Recent Files**: Dashboard shows last 5 generated files with download links

## API Integration

Integrates with CardGenius API to:
- Generate personalized card recommendations
- Calculate savings and benefits
- Handle redemption options and conversion rates

## Output Format

Generated Excel files include:
- User ID and spending data
- Top 3 card recommendations per user
- Net savings calculations
- Card details and benefits
- Redemption options with conversion rates
- Error tracking for failed requests

## Production Deployment

### For Cloud Platforms:
- Files are automatically saved to the platform's working directory
- No additional configuration needed
- Recent files section provides easy access to generated outputs

### Supported Platforms:
- Heroku
- Railway
- Streamlit Cloud
- Any Python hosting platform

## Requirements

- Python 3.8+
- Streamlit
- Pandas
- Requests
- OpenPyXL

See `requirements.txt` for complete dependency list.