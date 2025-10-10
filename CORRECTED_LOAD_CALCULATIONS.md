# CORRECTED LOAD CALCULATIONS (1.5 MB Response Size)

**IMPORTANT UPDATE:** Response size is **1.5 MB per user** (not 35 KB as initially estimated)

This significantly changes bandwidth requirements!

---

## 🔴 CRITICAL: Bandwidth Requirements

### With 1.5 MB Response Size

**Per Second (20 workers):**
```
Concurrent requests: 20
Requests completing: ~20 per second (best case)

Bandwidth:
├─ Outbound:  20 × 500 bytes = 10 KB/s = 80 Kbps
├─ Inbound:   20 × 1.5 MB = 30 MB/s = 240 Mbps (!!)
└─ Total:     30 MB/s sustained

🚨 YOU NEED 250+ Mbps DOWNLOAD SPEED! 🚨
```

**Per Minute:**
```
Requests: 1,200 (best case)
Data transfer: 1,200 × 1.5 MB = 1.8 GB/minute
```

**Per Hour:**
```
Requests: 72,000 (best case)
Data transfer: 72,000 × 1.5 MB = 108 GB/hour
```

---

## 📊 Updated Timelines

### 5K Users Test

**Best Case (API 1.5s, no bandwidth limit):**
```
Duration: 5,000 ÷ 1,200 users/min = 4.2 minutes
Data: 5,000 × 1.5 MB = 7.5 GB
Bandwidth: 30 MB/s for 4 minutes
```

**Realistic Case (bandwidth-limited to 100 Mbps):**
```
Duration: 5,000 × 1.5 MB ÷ (100 Mbps ÷ 8) = 10 minutes
Data: 7.5 GB
Bandwidth: 12.5 MB/s sustained
Workers: Need to reduce to 8-10 workers
```

### 200K Users Full Batch

**Best Case (250+ Mbps bandwidth):**
```
Duration: 200,000 ÷ 1,200 users/min = 167 minutes = 2.8 hours
Data: 200,000 × 1.5 MB = 300 GB (!!!)
Bandwidth: 30 MB/s for 2.8 hours
```

**Realistic Case (100 Mbps bandwidth):**
```
Duration: 200,000 × 1.5 MB ÷ (100 Mbps ÷ 8) = 400 minutes = 6.7 hours
Data: 300 GB
Bandwidth: 12.5 MB/s sustained
Workers: 8-10 workers optimal
```

---

## 🎯 Optimal Worker Configuration

### Based on YOUR Bandwidth

**If you have 250+ Mbps:**
```json
{ "max_workers": 20 }
// Can sustain 20 × 1.5 MB = 30 MB/s = 240 Mbps
```

**If you have 100-200 Mbps:**
```json
{ "max_workers": 8 }
// Can sustain 8 × 1.5 MB = 12 MB/s = 96 Mbps
```

**If you have 50-100 Mbps:**
```json
{ "max_workers": 4 }
// Can sustain 4 × 1.5 MB = 6 MB/s = 48 Mbps
```

**If you have < 50 Mbps:**
```json
{ "max_workers": 2 }
// Can sustain 2 × 1.5 MB = 3 MB/s = 24 Mbps
```

---

## 💾 Disk Space Requirements

### 5K Users Test
```
Input file: ~5 MB
API responses (temp): 7.5 GB
Output Excel: ~50 MB (with all columns)
Logs: ~10 MB

Total needed: 8 GB free space
```

### 200K Users Full
```
Input file: ~100 MB
API responses (temp): 300 GB (!!!)
Output Excel: ~1 GB (with all columns)
Logs: ~200 MB

Total needed: 350 GB free space
```

---

## 🧮 Why Bandwidth is Now the Bottleneck

### Old Estimate (35 KB response):
```
20 workers × 35 KB = 700 KB/s = 5.6 Mbps
✓ Easy for any connection
```

### New Reality (1.5 MB response):
```
20 workers × 1.5 MB = 30 MB/s = 240 Mbps
⚠️ Requires high-speed connection
⚠️ Most likely bottleneck now
```

**What this means:**
- The API can handle 20 req/s
- But YOUR bandwidth might not handle 240 Mbps
- You'll be bandwidth-limited, not API-limited

---

## 🔍 How to Check Your Bandwidth

### Option 1: Speed Test
```
1. Go to https://speedtest.net
2. Click "Go"
3. Check DOWNLOAD speed (not upload)
4. Need: 250+ Mbps for 20 workers
```

### Option 2: Command Line (Windows)
```powershell
# Open PowerShell
Invoke-WebRequest -Uri "http://speedtest.tele2.net/10MB.zip" `
    -OutFile "test.zip" -UseBasicParsing

# If downloads at 10+ MB/s, you have 80+ Mbps
# If downloads at 30+ MB/s, you have 240+ Mbps
```

---

## 📈 Throughput vs Bandwidth

| Your Bandwidth | Max Workers | Throughput | Time for 5K | Time for 200K |
|----------------|-------------|------------|-------------|---------------|
| **250+ Mbps** | 20 | 1,200/min | 4 min | 2.8 hours |
| **200 Mbps** | 16 | 960/min | 5 min | 3.5 hours |
| **150 Mbps** | 12 | 720/min | 7 min | 4.6 hours |
| **100 Mbps** | 8 | 480/min | 10 min | 6.9 hours |
| **50 Mbps** | 4 | 240/min | 21 min | 13.9 hours |

---

## ⚙️ Recommended Configuration

### For 5K Test

**If bandwidth > 200 Mbps:**
```json
{
  "processing": {
    "max_workers": 20
  }
}
```

**If bandwidth 100-200 Mbps:**
```json
{
  "processing": {
    "max_workers": 10
  }
}
```

**If bandwidth < 100 Mbps:**
```json
{
  "processing": {
    "max_workers": 5
  }
}
```

### For 200K Full Batch

**Start conservative, then tune:**
```json
{
  "processing": {
    "max_workers": 10
  }
}
```

**Monitor throughput for first 10 minutes:**
- If getting 800+ users/min → can increase to 15-20
- If getting 400-600 users/min → keep at 10
- If getting < 300 users/min → reduce to 5

---

## 🚨 Warning Signs

### Bandwidth Bottleneck
```
Symptoms:
- Slow progress (< 10 users/minute with 20 workers)
- Network usage at 100%
- Requests timing out
- "Connection reset" errors

Fix:
- Reduce max_workers
- Run during off-peak hours
- Use faster internet connection
```

### Memory Issues
```
Symptoms:
- Python crashes
- "Out of memory" errors
- Computer becomes very slow

Fix:
- Reduce max_workers
- Close other applications
- Process in smaller batches
```

### Disk Space Issues
```
Symptoms:
- "No space left on device"
- Excel file corrupted
- Can't save results

Fix:
- Free up disk space (need 350 GB)
- Save to external drive
- Process in smaller batches
```

---

## 💡 Pro Tips

### 1. Test Your Bandwidth First
```powershell
# Run this to see actual throughput
python -c "
import time
import requests

url = 'https://card-recommendation-api-v2.bankkaro.com/cg/api/pro'
# Make 5 test calls and measure time
# This will tell you realistic throughput
"
```

### 2. Start Conservative
```
First run: 5 workers, 100 users (test)
Second run: 10 workers, 1K users (validate)
Third run: 15 workers, 5K users (performance check)
Fourth run: 20 workers, 200K users (full batch)
```

### 3. Monitor Network Usage
```
Windows: Task Manager → Performance → Network
Watch: Should see sustained 12-30 MB/s during processing
```

### 4. Process in Chunks if Needed
```
Instead of 200K at once:
- Chunk 1: Rows 1-50,000 (75 GB, ~2 hours)
- Chunk 2: Rows 50,001-100,000
- Chunk 3: Rows 100,001-150,000  
- Chunk 4: Rows 150,001-200,000

Benefits:
- Easier to manage
- Can stop/resume
- Less memory usage
```

---

## 📊 Updated Summary Table

| Metric | Old Estimate | New Reality |
|--------|-------------|-------------|
| **Response size** | 35 KB | 1.5 MB (43x larger!) |
| **Bandwidth per worker** | 280 Kbps | 12 Mbps (43x more) |
| **Bandwidth for 20 workers** | 5.6 Mbps | 240 Mbps (43x more) |
| **5K data transfer** | 175 MB | 7.5 GB (43x more) |
| **200K data transfer** | 7 GB | 300 GB (43x more) |
| **Main bottleneck** | API rate limits | **Your bandwidth** |

---

## ✅ Action Items

**Before starting 5K test:**

1. **Check bandwidth:**
   ```
   Go to speedtest.net
   Note download speed
   If < 100 Mbps: Use 5-8 workers
   If 100-200 Mbps: Use 10-15 workers
   If > 200 Mbps: Use 20 workers
   ```

2. **Check disk space:**
   ```powershell
   Get-PSDrive C | Select-Object Used,Free
   Need: 10+ GB for 5K test, 350+ GB for 200K
   ```

3. **Update config accordingly:**
   ```json
   { "max_workers": [YOUR NUMBER BASED ON BANDWIDTH] }
   ```

4. **Run 5K test and monitor:**
   ```
   Watch: Network usage, progress rate, errors
   Expected: 400-1,200 users/minute depending on bandwidth
   ```

---

**Bottom line: With 1.5 MB responses, your internet bandwidth is now the main limitation, not the CardGenius API!**



