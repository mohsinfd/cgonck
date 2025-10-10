# Processing 200K Users: Execution Plan

**Date:** October 7, 2025  
**Task:** Process 200K users from data team  
**Timeline:** Before building server-side logic  
**Question:** API vs Batch Processing?

---

## Quick Answer

**Use BATCH PROCESSING (not API)** - Here's why and how:

---

## Option 1: Via API (NOT RECOMMENDED)

### How It Would Work
```
Data Team → 200K users via API endpoint
           ↓
API creates background job
           ↓
Processes all 200K users
           ↓
Returns results via /results endpoint
```

### Problems

1. **Single Job Timeout Risk**
   - 200K users in one job = high risk of failure
   - If job fails halfway, lose all progress
   - Render may timeout/restart

2. **Memory Issues**
   - 200K results in memory = ~2-3 GB
   - Render free tier = 512 MB (will crash)
   - Paid tier = 2 GB (will be tight)

3. **No Resume Capability**
   - If it fails at user 150K, must restart from beginning
   - Wastes hours of processing

4. **Result Retrieval Issues**
   - Getting 200K results via API = huge JSON payload
   - May timeout on download
   - Browser may crash

### Estimated Time
```
Current (Sequential): 200K × 2.7s = 540,000s = 150 hours = 6.25 days ❌

With Approach A (Parallel, 20 workers): 
200K ÷ 400 users/min = 500 minutes = 8.3 hours

BUT: High risk of failure, no progress saved
```

**Verdict:** ❌ **DO NOT USE API** - Too risky for 200K users

---

## Option 2: Batch Processing Script (RECOMMENDED ✅)

### How It Works
```
Excel File (200K users)
           ↓
cardgenius_batch_runner.py (with parallel processing)
           ↓
Processes in chunks of 1,000 users
           ↓
Saves progress after each chunk
           ↓
Final Excel output with all results
```

### Advantages

1. **Progress Saved**
   - Processes 1,000 users at a time
   - Saves to Excel after each chunk
   - If crashes, resume from last checkpoint

2. **Memory Efficient**
   - Only loads 1,000 users in memory at once
   - Writes to disk incrementally
   - Works on any machine

3. **Easy to Monitor**
   - See real-time progress in logs
   - Can estimate completion time
   - Can pause/resume anytime

4. **Reliable**
   - Proven system (already tested)
   - Local execution (no network issues)
   - Full error logging

### Estimated Time

**Current Code (Sequential):**
```
200,000 users × 2.7s/user = 540,000 seconds
= 9,000 minutes
= 150 hours
= 6.25 days ❌
```

**With Parallel Processing (20 workers):**
```
200,000 users ÷ 400 users/min = 500 minutes
= 8.3 hours ✅
```

**With Chunking (Safety Buffer):**
```
200 chunks of 1,000 users each
Each chunk: 1,000 ÷ 400 = 2.5 minutes processing + 0.5 min saving
Total: 200 × 3 minutes = 600 minutes = 10 hours
```

**Verdict:** ✅ **USE BATCH PROCESSING** - Safe, reliable, proven

---

## Recommended Execution Plan

### Step 1: Prepare (30 minutes)

**A. Implement Parallel Processing**
```python
# I'll modify cardgenius_batch_runner.py to add:
- ThreadPoolExecutor for parallel API calls
- Progress tracking with chunk saving
- Resume capability from last checkpoint
- Rate limiting for CardGenius API
```

**B. Configure for 200K Users**
```json
{
  "processing": {
    "chunk_size": 1000,        // Process 1,000 at a time
    "parallel_workers": 20,    // 20 concurrent API calls
    "checkpoint_interval": 1000 // Save after every 1,000
  }
}
```

**C. Prepare Infrastructure**
- Ensure stable internet connection
- Have backup power/connection
- Reserve dedicated machine for processing

### Step 2: Test Run (1 hour)

**Test with First 5,000 Users:**
```bash
# Extract first 5,000 rows from Excel
python split_excel.py --input 200k_users.xlsx --rows 5000 --output test_5k.xlsx

# Run batch processor
python cardgenius_batch_runner.py --config config.json --input test_5k.xlsx

# Expected: ~12-15 minutes for 5,000 users
# Validate: Check output quality, accuracy, error rate
```

**Success Criteria:**
- [ ] Completes in ~12-15 minutes
- [ ] All 5,000 users processed
- [ ] Output format correct
- [ ] Error rate < 1%
- [ ] Net savings calculations correct

### Step 3: Full Run (10 hours)

**Process All 200K Users:**
```bash
# Start processing
python cardgenius_batch_runner.py --config config.json --input 200k_users.xlsx

# Monitor progress (separate terminal)
tail -f cardgenius_batch.log

# Expected output:
2025-10-07 10:00:00 - INFO - Starting batch: 200,000 users
2025-10-07 10:00:01 - INFO - Chunk 1/200: Processing users 1-1000
2025-10-07 10:03:00 - INFO - Chunk 1/200: Complete (2.5 min) - Saved checkpoint
2025-10-07 10:03:01 - INFO - Chunk 2/200: Processing users 1001-2000
...
2025-10-07 20:00:00 - INFO - All chunks complete! Total time: 10 hours
```

**Timeline:**
- Start: Day 1, 10:00 AM
- Finish: Day 1, 8:00 PM (same day!)
- Buffer: 2-3 hours for any issues

### Step 4: Validation (1 hour)

**Verify Output Quality:**
```bash
# Check output file
python validate_results.py --input cardgenius_recommendations_output.xlsx

# Validation checks:
- Total users: 200,000 ✓
- All users have recommendations ✓
- Top 10 cards per user ✓
- Net savings calculated ✓
- No negative net_savings in top cards ✓
- Ranking order correct ✓
```

**Sample Validation:**
- Randomly pick 100 users
- Compare with manual CardGenius API calls
- Verify accuracy matches

---

## Can Our Code Handle 200K? YES (with modifications)

### Current Limitations

1. **Sequential Processing**
   - ❌ Takes 6.25 days (unacceptable)

2. **No Chunking**
   - ❌ Loads entire file in memory
   - ❌ If crashes, loses all progress

3. **No Rate Limiting**
   - ❌ May hit CardGenius API limits
   - ❌ Could get blocked

### Required Modifications (I'll implement these)

1. **Add Parallel Processing**
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_users_parallel(users, max_workers=20):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_user = {
            executor.submit(process_single_user, user): user 
            for user in users
        }
        
        results = []
        for future in as_completed(future_to_user):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"User failed: {e}")
        
        return results
```

2. **Add Chunking with Checkpoints**
```python
def process_in_chunks(df, chunk_size=1000):
    total_chunks = len(df) // chunk_size + 1
    
    for i in range(0, len(df), chunk_size):
        chunk = df[i:i+chunk_size]
        chunk_num = i // chunk_size + 1
        
        logger.info(f"Processing chunk {chunk_num}/{total_chunks}")
        
        # Process chunk
        results = process_users_parallel(chunk, max_workers=20)
        
        # Save checkpoint
        save_checkpoint(results, chunk_num)
        
        logger.info(f"Chunk {chunk_num} complete - checkpoint saved")
```

3. **Add Rate Limiting**
```python
import time
from threading import Semaphore

class RateLimiter:
    def __init__(self, max_calls_per_second=10):
        self.semaphore = Semaphore(max_calls_per_second)
        self.min_interval = 1.0 / max_calls_per_second
        self.last_call = 0
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            with self.semaphore:
                elapsed = time.time() - self.last_call
                if elapsed < self.min_interval:
                    time.sleep(self.min_interval - elapsed)
                
                result = func(*args, **kwargs)
                self.last_call = time.time()
                return result
        return wrapper

@rate_limiter
def call_cardgenius_api(user_data):
    # Your existing API call
    pass
```

4. **Add Resume Capability**
```python
def resume_from_checkpoint(checkpoint_file):
    if os.path.exists(checkpoint_file):
        logger.info(f"Resuming from checkpoint: {checkpoint_file}")
        processed = pd.read_excel(checkpoint_file)
        return len(processed)
    return 0

# Usage
start_index = resume_from_checkpoint('checkpoint_latest.xlsx')
df_remaining = df[start_index:]
process_in_chunks(df_remaining)
```

---

## Detailed Timeline

### Before Implementation (Current State)
- **Time for 200K:** 6.25 days
- **Risk:** Very high (crashes, no checkpoints)
- **Verdict:** ❌ Not viable

### After Implementation (With Parallel + Chunking)

| Phase | Duration | Activity |
|-------|----------|----------|
| **Preparation** | 30 min | Implement code changes |
| **Testing** | 1 hour | Test with 5K users |
| **Full Run** | 10 hours | Process 200K users |
| **Validation** | 1 hour | QA and verification |
| **Buffer** | 2 hours | Handle any issues |
| **TOTAL** | **~14-15 hours** | Complete end-to-end |

**You can finish in 1 day!** ✅

---

## Risk Assessment

### High Risk Factors

1. **CardGenius API Rate Limits**
   - **Risk:** Unknown limits may block us
   - **Mitigation:** Contact CardGenius, implement rate limiting
   - **Fallback:** Reduce parallel workers from 20 → 10 (doubles time to 20 hours)

2. **Network Instability**
   - **Risk:** Internet drops during processing
   - **Mitigation:** Use stable connection, checkpoints allow resume
   - **Impact:** Minimal (resume from last checkpoint)

3. **CardGenius API Downtime**
   - **Risk:** External API goes down
   - **Mitigation:** Retry logic, exponential backoff
   - **Impact:** Medium (delays completion)

### Low Risk Factors

4. **Memory Issues**
   - **Risk:** Out of memory
   - **Mitigation:** Process in chunks of 1,000
   - **Impact:** None (chunking prevents this)

5. **Disk Space**
   - **Risk:** Not enough disk space
   - **Check:** Need ~500 MB for output file
   - **Mitigation:** Check before starting

---

## Cost Analysis

### Infrastructure Costs
- **None** - Runs on local machine
- Optional: Rent cloud VM if you want 24/7 reliability
  - AWS t3.medium: ~$0.04/hour × 10 hours = **$0.40**
  - Google Cloud e2-medium: ~$0.03/hour × 10 hours = **$0.30**

### API Costs
- CardGenius API: Assumed free/budgeted
- If charged per call: 200K × $X per call

### Developer Time
- Implementation: 4 hours @ $X/hour
- Monitoring: 2 hours @ $X/hour (spot checking)

**Total Cost: Minimal (~$50-100 including dev time)**

---

## Recommended Configuration

### config.json
```json
{
  "cardgenius_api": {
    "url": "https://card-recommendation-api-v2.bankkaro.com/cg/api/pro",
    "timeout": 30,
    "retry_attempts": 3
  },
  "processing": {
    "parallel": {
      "enabled": true,
      "max_workers": 20,
      "chunk_size": 1000
    },
    "rate_limiting": {
      "enabled": true,
      "max_requests_per_second": 10,
      "burst_size": 20
    },
    "checkpoints": {
      "enabled": true,
      "save_every_n_users": 1000,
      "checkpoint_dir": "./checkpoints"
    }
  },
  "excel": {
    "input_file": "200k_users.xlsx",
    "output_file": "200k_recommendations_output.xlsx",
    "append_results": false
  }
}
```

---

## Monitoring & Progress Tracking

### Real-Time Monitoring Script
```python
# monitor_progress.py
import pandas as pd
import time
from datetime import datetime, timedelta

def monitor_progress(output_file, total_users=200000):
    start_time = datetime.now()
    
    while True:
        try:
            df = pd.read_excel(output_file)
            processed = len(df)
            
            # Calculate metrics
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = processed / elapsed * 60  # users per minute
            remaining = total_users - processed
            eta_minutes = remaining / rate if rate > 0 else 0
            eta_time = datetime.now() + timedelta(minutes=eta_minutes)
            
            # Display
            print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                  f"Processed: {processed:,}/{total_users:,} "
                  f"({processed/total_users*100:.1f}%) | "
                  f"Rate: {rate:.0f} users/min | "
                  f"ETA: {eta_time.strftime('%H:%M:%S')}", 
                  end='')
            
            if processed >= total_users:
                print(f"\n✅ Complete! Total time: {elapsed/3600:.1f} hours")
                break
                
        except FileNotFoundError:
            print("Waiting for output file...", end='\r')
        
        time.sleep(10)  # Update every 10 seconds

if __name__ == "__main__":
    monitor_progress("200k_recommendations_output.xlsx", 200000)
```

---

## Final Recommendation

### DO THIS:

1. **Use Batch Processing** (not API)
2. **I'll implement parallel processing** (takes 2-4 hours)
3. **You test with 5K users** (takes 15 minutes)
4. **Then run full 200K** (takes 10 hours)
5. **Complete in 1 day** ✅

### DON'T DO THIS:

- ❌ Use API for 200K users (too risky)
- ❌ Keep sequential processing (6 days too long)
- ❌ Process without checkpoints (lose progress on crash)

---

## Next Steps

**Immediate (Right Now):**
1. ✅ Send me the Excel file structure (column names)
2. ✅ I'll implement parallel processing + chunking
3. ✅ You confirm CardGenius API rate limits (if known)

**Today:**
4. ✅ Test with 5K users (~15 min)
5. ✅ Validate results quality

**Tomorrow:**
6. ✅ Start 200K processing (morning)
7. ✅ Monitor progress (periodic checks)
8. ✅ Complete by evening (~10 hours)

**Shall I start implementing the parallel processing + chunking now?**

This will enable you to process 200K users in 10 hours instead of 6 days.



