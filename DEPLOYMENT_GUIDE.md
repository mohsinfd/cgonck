# CardGenius API Server - Production Deployment Guide

## 🚀 Render Deployment

### Step 1: Prepare Repository
1. Push your code to GitHub/GitLab
2. Ensure all files are committed:
   - `api_server.py` (main server)
   - `cardgenius_batch_runner.py` (V1)
   - `cardgenius_batch_runner_v2.py` (V2)
   - `commissionable_cards.json`
   - `cashkaro_display_names.json`
   - `requirements.txt`
   - `Procfile`

### Step 2: Deploy on Render
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your repository
4. Configure:
   - **Name**: `cardgenius-api-server`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`

### Step 3: Environment Variables
Add these environment variables in Render dashboard:
```
CARDGENIUS_API_KEY=your_secure_api_key_here
PORT=10000
```

### Step 4: Deploy
Click "Create Web Service" and wait for deployment.

## 🔧 Alternative: Railway Deployment

### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

### Step 2: Deploy
```bash
railway login
railway init
railway up
```

## 🌐 Production Usage

### API Endpoints
- **Base URL**: `https://your-app-name.onrender.com`
- **Documentation**: `https://your-app-name.onrender.com/docs`
- **Health Check**: `https://your-app-name.onrender.com/health`

### Example API Call
```bash
curl -X POST "https://your-app-name.onrender.com/api/v1/recommendations" \
  -H "X-API-Key: your_secure_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "users": [
      {
        "user_id": "12345",
        "avg_amazon_gmv": 15000,
        "avg_flipkart_gmv": 10000,
        "avg_myntra_gmv": 3000,
        "avg_ajio_gmv": 5000,
        "avg_confirmed_gmv": 50000,
        "avg_grocery_gmv": 2000
      }
    ],
    "top_n_cards": 3,
    "version": "v2"
  }'
```

## 📊 V1 vs V2 Output

### V1 (Full Output)
- Complete CardGenius data
- All columns and breakdowns
- Detailed rewards/cashback info

### V2 (Simplified Output)
- 8 columns per card:
  - `card_name` (mapped)
  - `total_savings_yearly`
  - `net_savings`
  - `joining_fees`
  - `amazon_breakdown`
  - `flipkart_breakdown`
  - `grocery_breakdown`
  - `other_online_breakdown`

## 🔒 Security Notes
- Change `CARDGENIUS_API_KEY` in production
- Configure CORS origins properly
- Consider rate limiting for production
- Use HTTPS only

## 📈 Monitoring
- Check Render logs for errors
- Monitor API response times
- Set up health check monitoring
- Track job success/failure rates

## 🚨 Troubleshooting
- Check logs in Render dashboard
- Verify environment variables
- Ensure all dependencies are installed
- Test locally first with `python api_server.py`




