# CLEAR ACTION PLAN: Testing with 5K Users First

**Your Situation:**
- ✅ CardGenius confirmed: 20 API calls/second is OK
- ✅ Response size: 1.5 MB per user (larger than expected!)
- ✅ Goal: Test with 5K users first, then scale to 200K
- ❓ Question: Script vs API? Full file or small batch?

---

## 🎯 ANSWER: Use the SCRIPT (Not API)

**Why Script, Not API?**
- ✅ Script can save progress to disk (Excel file)
- ✅ Easier to monitor and stop if needed
- ✅ Can resume if something goes wrong
- ✅ Results saved locally for validation
- ❌ API would keep 5K results in memory (7.5 GB!)

**Verdict:** Use `cardgenius_batch_runner.py` script

---

## 📝 STEP-BY-STEP INSTRUCTIONS

### Step 1: Prepare 5K User Test File (5 minutes)

**Create a small Excel file with first 5,000 rows:**

```bash
# Open PowerShell in your project folder
cd "C:\Users\mohsin\Downloads\Cursor 26 - CG on CK recommendations script"

# Run this Python command to create test file
python -c "
import pandas as pd

# Read your full 200K file
df = pd.read_excel('Card Recommendation avg gmv dump.xlsx')

# Take first 5,000 rows
df_test = df.head(5000)

# Save as new file
df_test.to_excel('test_5k_users.xlsx', index=False)

print(f'Created test_5k_users.xlsx with {len(df_test)} users')
print(f'Columns: {list(df_test.columns)}')
"
```

**Expected output:**
```
Created test_5k_users.xlsx with 5000 users
Columns: ['userid', 'avg_amazon_gmv', 'avg_flipkart_gmv', ...]
```

---

### Step 2: Update Configuration (2 minutes)

**Edit `real_config.json`:**

```json
{
  "api": {
    "base_url": "https://card-recommendation-api-v2.bankkaro.com/cg/api/pro",
    "timeout": 30,
    "sleep_between_requests": 0,
    "max_retries": 3
  },
  "excel": {
    "input_file": "test_5k_users.xlsx",
    "output_file": "results_5k_users.xlsx",
    "sheet_name": 0
  },
  "column_mappings": {
    "user_id": "userid",
    "amazon_spends": "avg_amazon_gmv",
    "flipkart_spends": "avg_flipkart_gmv",
    "myntra": "avg_myntra_gmv",
    "ajio": "avg_ajio_gmv",
    "avg_gmv": "avg_confirmed_gmv",
    "grocery": "avg_grocery_gmv"
  },
  "processing": {
    "top_n_cards": 10,
    "max_workers": 20,
    "extract_spend_keys": [
      "amazon_spends",
      "flipkart_spends",
      "grocery_spends_online",
      "other_online_spends"
    ],
    "skip_empty_rows": true,
    "continue_on_error": true,
    "other_online_mode": "sum_components"
  }
}
```

**Key changes:**
- `input_file`: "test_5k_users.xlsx" (your test file)
- `output_file`: "results_5k_users.xlsx" (test results)
- `max_workers`: 20 (as confirmed by CardGenius)
- `top_n_cards`: 10 (assuming you want top 10)

---

### Step 3: Run the Test (12-25 minutes)

**Start processing:**

```bash
python cardgenius_batch_runner.py --config real_config.json
```

**What you'll see:**
```
2025-10-07 14:00:00 - INFO - Loading Excel file: test_5k_users.xlsx
2025-10-07 14:00:01 - INFO - Loaded 5000 rows from Excel file
2025-10-07 14:00:01 - INFO - Starting parallel processing with 20 workers
2025-10-07 14:00:01 - INFO - Processing 5000 users...
2025-10-07 14:00:15 - INFO - Progress: 100/5000 users processed (2.0%)
2025-10-07 14:01:30 - INFO - Progress: 200/5000 users processed (4.0%)
2025-10-07 14:02:45 - INFO - Progress: 300/5000 users processed (6.0%)
...
2025-10-07 14:12:30 - INFO - Progress: 5000/5000 users processed (100.0%)
2025-10-07 14:12:31 - INFO - Saving results to results_5k_users.xlsx
2025-10-07 14:12:35 - INFO - Processing complete!
2025-10-07 14:12:35 - INFO - Total rows processed: 5000
2025-10-07 14:12:35 - INFO - Successful API calls: 4987
2025-10-07 14:12:35 - INFO - Failed API calls: 13
2025-10-07 14:12:35 - INFO - Results saved to: results_5k_users.xlsx
```

**Expected duration:**
- Best case: ~12 minutes (if API responds in 1.5s)
- Typical: ~15 minutes (if API responds in 2s)
- Worst case: ~25 minutes (if API responds in 3s)

---

### Step 4: Monitor Progress (While Running)

**Open a second terminal and watch logs:**

```bash
# In a new PowerShell window
cd "C:\Users\mohsin\Downloads\Cursor 26 - CG on CK recommendations script"

# Watch logs in real-time
Get-Content cardgenius_batch.log -Wait -Tail 50
```

**What to watch for:**
- ✅ "Progress: X/5000 users processed" - should update every minute
- ✅ Success rate should be >99% (< 50 failures acceptable)
- ⚠️ If many "API call failed" errors - may need to reduce workers
- ❌ If it stops progressing for >5 minutes - something is wrong

---

### Step 5: Validate Results (5 minutes)

**After completion, check the output:**

```bash
# Check if file was created
ls results_5k_users.xlsx

# Quick validation with Python
python -c "
import pandas as pd

df = pd.read_excel('results_5k_users.xlsx')

print(f'Total users: {len(df)}')
print(f'Users with top1 card: {df[\"top1_card_name\"].notna().sum()}')
print(f'Users with errors: {df[\"cardgenius_error\"].notna().sum()}')
print(f'\nSample top 1 card:')
print(df[['userid', 'top1_card_name', 'top1_net_savings']].head(5))
"
```

**Expected output:**
```
Total users: 5000
Users with top1 card: 4987
Users with errors: 13

Sample top 1 card:
   userid              top1_card_name  top1_net_savings
0  CK123  ICICI Amazon Pay               25500.0
1  CK456  Axis Magnus                    42000.0
...
```

---

### Step 6: If Test Succeeds → Scale to 200K (30 hours)

**Only do this after 5K test is successful!**

**Update config for full batch:**

```json
{
  "excel": {
    "input_file": "Card Recommendation avg gmv dump.xlsx",
    "output_file": "results_200k_users.xlsx",
    "sheet_name": 0
  },
  "processing": {
    "max_workers": 20
  }
}
```

**Run full batch:**

```bash
python cardgenius_batch_runner.py --config real_config.json
```

**Expected duration:** 
- 200K users ÷ 400 users/min = 500 minutes = **8.3 hours**
- With 1.5 MB responses, might be slower: **10-30 hours**

---

## 📊 Updated Load Calculations (1.5 MB Responses!)

### NEW: With 1.5 MB Response Size

**Per Second:**
```
Requests: 20 per second (confirmed OK)
Request size: 500 bytes
Response size: 1.5 MB (!!!)

Bandwidth:
- Outbound: 20 × 500 bytes = 10 KB/s
- Inbound: 20 × 1.5 MB = 30 MB/s = 240 Mbps (!!)
- Total: ~30 MB/s sustained
```

**For 5K Users:**
```
Duration: 5,000 ÷ (20 × 60) = 4.2 minutes (if no bottlenecks)
Data transfer: 5,000 × 1.5 MB = 7.5 GB total
Bandwidth: 30 MB/s for 4 minutes
```

**For 200K Users:**
```
Duration: 200,000 ÷ (20 × 60) = 167 minutes = 2.8 hours (best case)
Data transfer: 200,000 × 1.5 MB = 300 GB total (!!!)
Bandwidth: 30 MB/s for 2.8+ hours

IMPORTANT: 
- Your network must support 240 Mbps sustained
- Your disk must handle 300 GB write
- This might be the bottleneck, not the API!
```

---

## ⚠️ IMPORTANT: Bandwidth Check

**BEFORE running, verify your internet speed:**

```bash
# Test your download speed
# Go to https://speedtest.net or run:
# You need at least 250 Mbps download speed!
```

**If your bandwidth is < 250 Mbps:**
- You'll be bandwidth-limited, not API-limited
- Reduce `max_workers` to match your bandwidth
- Example: 100 Mbps → use 5-8 workers max

**Disk Space Check:**
```bash
# Make sure you have 350+ GB free
# - 300 GB for responses
# - 50 GB for Excel file output
```

---

## 🚨 What Can Go Wrong & Fixes

### Issue 1: "Out of memory" error

**Cause:** Processing 5K users with 1.5 MB each = 7.5 GB in memory

**Fix:**
```json
{
  "processing": {
    "max_workers": 10  // Reduce to use less memory
  }
}
```

### Issue 2: Slow progress (< 10 users/minute)

**Cause:** Bandwidth bottleneck from 1.5 MB responses

**Fix:**
```json
{
  "processing": {
    "max_workers": 5  // Reduce to match your bandwidth
  }
}
```

### Issue 3: Excel file won't open (too large)

**Cause:** 200K rows × 100+ columns with 1.5 MB per row

**Fix:** Process in smaller batches (50K at a time)
```
Batch 1: Rows 1-50,000
Batch 2: Rows 50,001-100,000
Batch 3: Rows 100,001-150,000
Batch 4: Rows 150,001-200,000
```

---

## ✅ FINAL CHECKLIST

**Before starting:**
- [ ] Created test_5k_users.xlsx (first 5,000 rows)
- [ ] Updated real_config.json (input/output files, max_workers=20)
- [ ] Verified internet speed (need 250+ Mbps)
- [ ] Verified disk space (need 350+ GB free)
- [ ] Backed up original 200K file

**During test:**
- [ ] Monitor logs (watch for errors)
- [ ] Check progress every 5 minutes
- [ ] Verify throughput (~20 users/minute)
- [ ] Watch network bandwidth usage

**After test:**
- [ ] Validate results (check row count, errors)
- [ ] Review sample cards (top1, top2, top3)
- [ ] Check error rate (should be < 1%)
- [ ] If all good → proceed to full 200K

---

## 📋 SUMMARY: What You're Doing

```
╔═══════════════════════════════════════════════════════╗
║  ACTION PLAN                                          ║
╠═══════════════════════════════════════════════════════╣
║  1. Create test file: test_5k_users.xlsx              ║
║  2. Update config: input/output files, 20 workers     ║
║  3. Run script: python cardgenius_batch_runner.py     ║
║  4. Wait: 12-25 minutes                               ║
║  5. Validate: Check results_5k_users.xlsx             ║
║  6. If success: Scale to 200K (update config & rerun) ║
╚═══════════════════════════════════════════════════════╝

DO NOT:
❌ Don't use the API (use script instead)
❌ Don't upload full 200K first (test with 5K)
❌ Don't run without bandwidth check
❌ Don't skip validation step
```

---

## 🎬 START HERE (Copy-Paste Commands)

```powershell
# 1. Navigate to project folder
cd "C:\Users\mohsin\Downloads\Cursor 26 - CG on CK recommendations script"

# 2. Create 5K test file
python -c "import pandas as pd; df = pd.read_excel('Card Recommendation avg gmv dump.xlsx'); df.head(5000).to_excel('test_5k_users.xlsx', index=False); print('Created test_5k_users.xlsx with 5000 users')"

# 3. Verify test file created
ls test_5k_users.xlsx

# 4. Run the script (make sure real_config.json is updated first!)
python cardgenius_batch_runner.py --config real_config.json

# 5. (In separate window) Monitor logs
Get-Content cardgenius_batch.log -Wait -Tail 50
```

---

**That's it! Start with Step 1 above and work through each step. Don't skip the 5K test!**

Any questions on any step?



