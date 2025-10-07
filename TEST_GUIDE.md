# Testing Guide

## Quick Start Testing

### Test 1: Dashboard (5 minutes)

**Step 1 - Start Dashboard:**
```bash
streamlit run cardgenius_dashboard.py
```

**Step 2 - Test in Browser (http://localhost:8501):**

1. **Test Card Mapping Admin:**
   - Click sidebar → Select "Card Name Mapping"
   - Click "🤖 Auto-Generate Mappings" button
   - **Expected**: You should see a list of auto-generated mappings
   - **Action**: Review the list, try deleting one mapping (click 🗑️)
   - **Success**: If mappings appear and you can delete them ✅

2. **Test File Processing:**
   - Click sidebar → Select "API & Processing"
   - Upload `Card Recommendation avg gmv dump.xlsx`
   - **Expected**: File preview appears, shows "✅ All required columns found!"
   - Click "▶️ Start Processing"
   - **Expected**: Progress bar updates, results appear
   - **Success**: If you can download results ✅

---

### Test 2: API Server (10 minutes)

**Terminal 1 - Start API:**
```bash
pip install fastapi uvicorn pydantic
python api_server.py
```

**Expected Output:**
```
🚀 Starting CardGenius Recommendations API Server
📋 API Documentation: http://localhost:8000/docs
🔑 API Key: YOUR_SECRET_API_KEY_HERE

INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Browser - Test Swagger UI (http://localhost:8000/docs):**

1. **Test Health Check:**
   - Click on `GET /health`
   - Click "Try it out"
   - Click "Execute"
   - **Expected**: `{"status": "healthy"}`
   - **Success**: If you see healthy status ✅

2. **Test Create Job:**
   - Click on `POST /api/v1/recommendations`
   - Click "Try it out"
   - In `X-API-Key` field, enter: `YOUR_SECRET_API_KEY_HERE`
   - Keep the default JSON payload (or modify user_id)
   - Click "Execute"
   - **Expected**: Returns `job_id` with status "queued"
   - **Success**: If you get a job_id ✅

3. **Test Status Check:**
   - Copy the `job_id` from step 2
   - Click on `GET /api/v1/status/{job_id}`
   - Click "Try it out"
   - Paste the job_id
   - Enter API key
   - Click "Execute"
   - **Expected**: Shows processing status/progress
   - **Success**: If status changes to "completed" ✅

4. **Test Get Results:**
   - Click on `GET /api/v1/results/{job_id}`
   - Click "Try it out"
   - Paste the same job_id
   - Enter API key
   - Click "Execute"
   - **Expected**: Returns full card recommendations
   - **Success**: If you see card recommendations ✅

---

### Test 3: Python Client (5 minutes)

**Terminal 2 (while API server is running in Terminal 1):**
```bash
python api_client_example.py
```

**Expected Output:**
```
📤 Submitting batch of 3 users...
✅ Job created: <job_id>
   Status: queued

⏳ Progress: 33.3% (1/3 users)
⏳ Progress: 66.7% (2/3 users)
⏳ Progress: 100.0% (3/3 users)
✅ Job completed!
   Successful: 3
   Failed: 0

📥 Fetching results...
✅ Retrieved 3 user results
💾 Results saved to api_results_example.json
```

**Success**: If you see results saved to file ✅

---

## If Something Goes Wrong

### **Dashboard Issues:**
- **Error on load**: Check terminal for Python errors
- **No mappings appear**: Check if `cardgenius_all_cards.json` exists
- **File upload fails**: Check column names match

### **API Issues:**
- **500 Error**: Check the terminal where API is running for error logs
- **401 Error**: API key is wrong
- **Job stuck**: Check if CardGenius API is accessible

### **Common Fixes:**
```bash
# Restart everything
taskkill /f /im python.exe

# Reinstall dependencies
pip install -r requirements.txt

# Test syntax
python -m py_compile api_server.py
python -m py_compile cardgenius_dashboard.py
```

---

## What to Report

If you encounter errors, please share:
1. **Which test** failed (Dashboard, API, Client)
2. **Error message** from the terminal
3. **Step** where it failed

This will help me fix the specific issue quickly!
