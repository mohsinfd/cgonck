# NO-CODE-EDITING ACTION PLAN: 5K Test

**For users who want to run commands only, no file editing needed!**

---

## ✅ **What You'll Do**

1. Run commands (copy-paste)
2. Watch progress
3. Check results

**No file editing required!**

---

## 📋 **STEP-BY-STEP (Just Copy-Paste)**

### **Step 1: Create Test File (2 minutes)**

Open PowerShell in your project folder and run:

```powershell
# Create 5K test file
python -c "import pandas as pd; df = pd.read_excel('Card Recommendation avg gmv dump.xlsx'); df.head(5000).to_excel('test_5k_users.xlsx', index=False); print('✅ Created test_5k_users.xlsx with 5000 users')"
```

**Expected output:**
```
✅ Created test_5k_users.xlsx with 5000 users
```

---

### **Step 2: Create Config File (Automated)**

**Copy-paste this entire command** (it creates the config file for you):

```powershell
python -c "
import json

config = {
    'api': {
        'base_url': 'https://card-recommendation-api-v2.bankkaro.com/cg/api/pro',
        'timeout': 30,
        'sleep_between_requests': 0,
        'max_retries': 3
    },
    'excel': {
        'input_file': 'test_5k_users.xlsx',
        'output_file': 'results_5k_users.xlsx',
        'sheet_name': 0
    },
    'column_mappings': {
        'user_id': 'userid',
        'amazon_spends': 'avg_amazon_gmv',
        'flipkart_spends': 'avg_flipkart_gmv',
        'myntra': 'avg_myntra_gmv',
        'ajio': 'avg_ajio_gmv',
        'avg_gmv': 'avg_confirmed_gmv',
        'grocery': 'avg_grocery_gmv'
    },
    'processing': {
        'top_n_cards': 10,
        'max_workers': 10,
        'extract_spend_keys': [
            'amazon_spends',
            'flipkart_spends',
            'grocery_spends_online',
            'other_online_spends'
        ],
        'skip_empty_rows': True,
        'continue_on_error': True,
        'other_online_mode': 'sum_components'
    }
}

with open('config_5k_test.json', 'w') as f:
    json.dump(config, f, indent=2)

print('✅ Created config_5k_test.json')
"
```

**Expected output:**
```
✅ Created config_5k_test.json
```

---

### **Step 3: Run the Processing (7-10 minutes)**

**Copy-paste this command:**

```powershell
python cardgenius_batch_runner.py --config config_5k_test.json
```

**What you'll see:**
```
2025-10-07 14:00:00 - INFO - Loading Excel file: test_5k_users.xlsx
2025-10-07 14:00:01 - INFO - Loaded 5000 rows from Excel file
2025-10-07 14:00:01 - INFO - Starting parallel processing with 10 workers
2025-10-07 14:00:01 - INFO - Processing 5000 users...
2025-10-07 14:01:00 - INFO - Progress: 100/5000 users processed (2.0%)
2025-10-07 14:02:00 - INFO - Progress: 200/5000 users processed (4.0%)
2025-10-07 14:03:00 - INFO - Progress: 300/5000 users processed (6.0%)
...
2025-10-07 14:07:30 - INFO - Progress: 5000/5000 users processed (100.0%)
2025-10-07 14:07:31 - INFO - Saving results to results_5k_users.xlsx
2025-10-07 14:07:35 - INFO - Processing complete!
```

**Expected duration:** 7-10 minutes

**To monitor in another window (optional):**
```powershell
# Open a second PowerShell window
Get-Content cardgenius_batch.log -Wait -Tail 20
```

---

### **Step 4: Check Results (1 minute)**

**Copy-paste this command:**

```powershell
python -c "
import pandas as pd
import os

# Check if output file exists
if os.path.exists('results_5k_users.xlsx'):
    df = pd.read_excel('results_5k_users.xlsx')
    
    total = len(df)
    with_results = df['top1_card_name'].notna().sum()
    with_errors = df['cardgenius_error'].notna().sum()
    success_rate = (with_results / total * 100) if total > 0 else 0
    
    print('=' * 50)
    print('📊 RESULTS SUMMARY')
    print('=' * 50)
    print(f'✅ Total users: {total}')
    print(f'✅ Successfully processed: {with_results} ({success_rate:.1f}%)')
    print(f'❌ Errors: {with_errors}')
    print()
    print('Sample results:')
    print(df[['userid', 'top1_card_name', 'top1_net_savings']].head(5).to_string(index=False))
    print()
    print('=' * 50)
    print('✅ Test complete! File: results_5k_users.xlsx')
    print('=' * 50)
else:
    print('❌ Output file not found. Check if processing completed.')
"
```

**Expected output:**
```
==================================================
📊 RESULTS SUMMARY
==================================================
✅ Total users: 5000
✅ Successfully processed: 4987 (99.7%)
❌ Errors: 13

Sample results:
   userid              top1_card_name  top1_net_savings
  CK12345        ICICI Amazon Pay            25500.0
 USER9876          Axis Magnus                42000.0
 CUST5432         HDFC Regalia               18500.0
  CK77889    SBI Card ELITE                   35000.0
 USER2341         Amex Platinum              28000.0

==================================================
✅ Test complete! File: results_5k_users.xlsx
==================================================
```

---

### **Step 5: If Test Success → Scale to 200K**

**Only do this if Step 4 shows >99% success rate!**

**Create config for full 200K batch:**

```powershell
python -c "
import json

config = {
    'api': {
        'base_url': 'https://card-recommendation-api-v2.bankkaro.com/cg/api/pro',
        'timeout': 30,
        'sleep_between_requests': 0,
        'max_retries': 3
    },
    'excel': {
        'input_file': 'Card Recommendation avg gmv dump.xlsx',
        'output_file': 'results_200k_users.xlsx',
        'sheet_name': 0
    },
    'column_mappings': {
        'user_id': 'userid',
        'amazon_spends': 'avg_amazon_gmv',
        'flipkart_spends': 'avg_flipkart_gmv',
        'myntra': 'avg_myntra_gmv',
        'ajio': 'avg_ajio_gmv',
        'avg_gmv': 'avg_confirmed_gmv',
        'grocery': 'avg_grocery_gmv'
    },
    'processing': {
        'top_n_cards': 10,
        'max_workers': 10,
        'extract_spend_keys': [
            'amazon_spends',
            'flipkart_spends',
            'grocery_spends_online',
            'other_online_spends'
        ],
        'skip_empty_rows': True,
        'continue_on_error': True,
        'other_online_mode': 'sum_components'
    }
}

with open('config_200k_full.json', 'w') as f:
    json.dump(config, f, indent=2)

print('✅ Created config_200k_full.json')
print('⏱️  Expected duration: 5-7 hours')
print('💡 Tip: Run overnight!')
"
```

**Then run:**

```powershell
python cardgenius_batch_runner.py --config config_200k_full.json
```

**Expected duration:** 5-7 hours (run overnight)

---

## 🎛️ **Optional: Adjust Workers**

**If you want to try different worker counts** (after 5K test):

**For 15 workers (faster, needs better internet):**
```powershell
python -c "
import json
with open('config_5k_test.json', 'r') as f: config = json.load(f)
config['processing']['max_workers'] = 15
with open('config_5k_test.json', 'w') as f: json.dump(config, f, indent=2)
print('✅ Updated to 15 workers')
"
```

**For 5 workers (slower, more conservative):**
```powershell
python -c "
import json
with open('config_5k_test.json', 'r') as f: config = json.load(f)
config['processing']['max_workers'] = 5
with open('config_5k_test.json', 'w') as f: json.dump(config, f, indent=2)
print('✅ Updated to 5 workers')
"
```

---

## 🔍 **Troubleshooting Commands**

### Check if test file was created:
```powershell
ls test_5k_users.xlsx
```

### Check if config was created:
```powershell
ls config_5k_test.json
```

### View current config:
```powershell
Get-Content config_5k_test.json
```

### Check log file for errors:
```powershell
Get-Content cardgenius_batch.log -Tail 50
```

### Check how many rows in input file:
```powershell
python -c "import pandas as pd; df = pd.read_excel('test_5k_users.xlsx'); print(f'Rows: {len(df)}')"
```

### Check columns in your file:
```powershell
python -c "import pandas as pd; df = pd.read_excel('Card Recommendation avg gmv dump.xlsx'); print('Columns:', list(df.columns))"
```

---

## ⚠️ **If Something Goes Wrong**

### Problem: "File not found" error

**Run this to check files:**
```powershell
ls *.xlsx
```

**Make sure you're in the right folder:**
```powershell
cd "C:\Users\mohsin\Downloads\Cursor 26 - CG on CK recommendations script"
```

### Problem: Processing is very slow

**Check progress:**
```powershell
Get-Content cardgenius_batch.log -Tail 5
```

**Reduce workers to 5:**
```powershell
python -c "
import json
with open('config_5k_test.json', 'r') as f: config = json.load(f)
config['processing']['max_workers'] = 5
with open('config_5k_test.json', 'w') as f: json.dump(config, f, indent=2)
print('✅ Reduced to 5 workers - try running again')
"
```

### Problem: Many errors in output

**Check error rate:**
```powershell
python -c "
import pandas as pd
df = pd.read_excel('results_5k_users.xlsx')
errors = df['cardgenius_error'].notna().sum()
total = len(df)
print(f'Errors: {errors}/{total} ({errors/total*100:.1f}%)')
if errors > 50:
    print('⚠️  High error rate - check logs')
else:
    print('✅ Error rate acceptable')
"
```

---

## 📊 **Monitor Progress (Real-Time)**

**Open a second PowerShell window and run:**

```powershell
# Real-time log monitoring
Get-Content cardgenius_batch.log -Wait -Tail 20
```

**Or check progress every minute:**

```powershell
python -c "
import time
import os

print('Monitoring progress... (Ctrl+C to stop)')
print()

while True:
    if os.path.exists('results_5k_users.xlsx'):
        import pandas as pd
        df = pd.read_excel('results_5k_users.xlsx')
        processed = df['top1_card_name'].notna().sum()
        print(f'\r✅ Processed: {processed}/5000 ({processed/5000*100:.1f}%)', end='', flush=True)
    else:
        print('\r⏳ Waiting for results file...', end='', flush=True)
    
    time.sleep(10)
"
```

---

## ✅ **COMPLETE WORKFLOW (Copy-Paste All)**

**Run these commands in order:**

```powershell
# Navigate to project folder
cd "C:\Users\mohsin\Downloads\Cursor 26 - CG on CK recommendations script"

# Step 1: Create test file
python -c "import pandas as pd; df = pd.read_excel('Card Recommendation avg gmv dump.xlsx'); df.head(5000).to_excel('test_5k_users.xlsx', index=False); print('✅ Step 1 complete')"

# Step 2: Create config
python -c "import json; config={'api':{'base_url':'https://card-recommendation-api-v2.bankkaro.com/cg/api/pro','timeout':30,'sleep_between_requests':0,'max_retries':3},'excel':{'input_file':'test_5k_users.xlsx','output_file':'results_5k_users.xlsx','sheet_name':0},'column_mappings':{'user_id':'userid','amazon_spends':'avg_amazon_gmv','flipkart_spends':'avg_flipkart_gmv','myntra':'avg_myntra_gmv','ajio':'avg_ajio_gmv','avg_gmv':'avg_confirmed_gmv','grocery':'avg_grocery_gmv'},'processing':{'top_n_cards':10,'max_workers':10,'extract_spend_keys':['amazon_spends','flipkart_spends','grocery_spends_online','other_online_spends'],'skip_empty_rows':True,'continue_on_error':True,'other_online_mode':'sum_components'}}; json.dump(config,open('config_5k_test.json','w'),indent=2); print('✅ Step 2 complete')"

# Step 3: Run processing (this will take 7-10 minutes)
python cardgenius_batch_runner.py --config config_5k_test.json

# Step 4: Check results
python -c "import pandas as pd; df=pd.read_excel('results_5k_users.xlsx'); print('✅ Total:',len(df),'| Success:',df['top1_card_name'].notna().sum(),'| Errors:',df['cardgenius_error'].notna().sum()); print(df[['userid','top1_card_name','top1_net_savings']].head())"
```

---

## 🎯 **SUMMARY**

**What you're doing:**
1. Create 5K test file → **1 command**
2. Create config file → **1 command**
3. Run processing → **1 command**
4. Check results → **1 command**

**NO FILE EDITING NEEDED!**

**Total time:** ~10 minutes for 5K test

**If success:** Scale to 200K with same process

---

**Ready? Start with Step 1 above!** 🚀



