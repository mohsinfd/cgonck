# COMPLETE COMMAND LIST - Copy & Paste

**All commands you need to run, in order.**

---

## 🎯 **OPTION A: Easiest (Just 3 Commands)**

### Command 1: Navigate to folder
```powershell
cd "C:\Users\mohsin\Downloads\Cursor 26 - CG on CK recommendations script"
```

### Command 2: Run 5K test
```powershell
python run_5k_test.py
```
*Wait 7-10 minutes for completion*

### Command 3: Run 200K full batch (only if Command 2 succeeds)
```powershell
python run_200k_full.py
```
*Wait 5-7 hours (run overnight)*

---

## 🎯 **OPTION B: Manual Commands (If Scripts Don't Work)**

### Command 1: Navigate to folder
```powershell
cd "C:\Users\mohsin\Downloads\Cursor 26 - CG on CK recommendations script"
```

### Command 2: Create 5K test file
```powershell
python -c "import pandas as pd; df = pd.read_excel('Card Recommendation avg gmv dump.xlsx'); df.head(5000).to_excel('test_5k_users.xlsx', index=False); print('Created test_5k_users.xlsx')"
```

### Command 3: Create config file
```powershell
python -c "import json; config={'api':{'base_url':'https://card-recommendation-api-v2.bankkaro.com/cg/api/pro','timeout':30,'sleep_between_requests':0,'max_retries':3},'excel':{'input_file':'test_5k_users.xlsx','output_file':'results_5k_users.xlsx','sheet_name':0},'column_mappings':{'user_id':'userid','amazon_spends':'avg_amazon_gmv','flipkart_spends':'avg_flipkart_gmv','myntra':'avg_myntra_gmv','ajio':'avg_ajio_gmv','avg_gmv':'avg_confirmed_gmv','grocery':'avg_grocery_gmv'},'processing':{'top_n_cards':10,'max_workers':10,'extract_spend_keys':['amazon_spends','flipkart_spends','grocery_spends_online','other_online_spends'],'skip_empty_rows':True,'continue_on_error':True,'other_online_mode':'sum_components'}}; json.dump(config,open('config_5k_test.json','w'),indent=2); print('Created config_5k_test.json')"
```

### Command 4: Run 5K processing
```powershell
python cardgenius_batch_runner.py --config config_5k_test.json
```
*Wait 7-10 minutes*

### Command 5: Check 5K results
```powershell
python -c "import pandas as pd; df=pd.read_excel('results_5k_users.xlsx'); total=len(df); success=df['top1_card_name'].notna().sum(); errors=df['cardgenius_error'].notna().sum(); print(f'Total: {total} | Success: {success} ({success/total*100:.1f}%) | Errors: {errors}'); print('\nSample results:'); print(df[['userid','top1_card_name','top1_net_savings']].head())"
```

### Command 6: Create 200K config (only if Command 5 shows >99% success)
```powershell
python -c "import json; config={'api':{'base_url':'https://card-recommendation-api-v2.bankkaro.com/cg/api/pro','timeout':30,'sleep_between_requests':0,'max_retries':3},'excel':{'input_file':'Card Recommendation avg gmv dump.xlsx','output_file':'results_200k_users.xlsx','sheet_name':0},'column_mappings':{'user_id':'userid','amazon_spends':'avg_amazon_gmv','flipkart_spends':'avg_flipkart_gmv','myntra':'avg_myntra_gmv','ajio':'avg_ajio_gmv','avg_gmv':'avg_confirmed_gmv','grocery':'avg_grocery_gmv'},'processing':{'top_n_cards':10,'max_workers':10,'extract_spend_keys':['amazon_spends','flipkart_spends','grocery_spends_online','other_online_spends'],'skip_empty_rows':True,'continue_on_error':True,'other_online_mode':'sum_components'}}; json.dump(config,open('config_200k_full.json','w'),indent=2); print('Created config_200k_full.json')"
```

### Command 7: Run 200K processing
```powershell
python cardgenius_batch_runner.py --config config_200k_full.json
```
*Wait 5-7 hours (run overnight)*

### Command 8: Check 200K results
```powershell
python -c "import pandas as pd; df=pd.read_excel('results_200k_users.xlsx'); total=len(df); success=df['top1_card_name'].notna().sum(); errors=df['cardgenius_error'].notna().sum(); print(f'Total: {total:,} | Success: {success:,} ({success/total*100:.1f}%) | Errors: {errors:,}'); print('\nSample results:'); print(df[['userid','top1_card_name','top1_net_savings']].head())"
```

---

## 🔍 **Optional: Monitoring Commands**

### Check progress (while processing)
```powershell
Get-Content cardgenius_batch.log -Wait -Tail 20
```

### Check what files exist
```powershell
ls *.xlsx
```

### Check disk space
```powershell
Get-PSDrive C
```

### Check if test file was created
```powershell
ls test_5k_users.xlsx
```

### Check if config was created
```powershell
ls config_5k_test.json
```

---

## ✅ **RECOMMENDED: Use Option A**

**Just run these 3 commands:**

```powershell
cd "C:\Users\mohsin\Downloads\Cursor 26 - CG on CK recommendations script"
python run_5k_test.py
python run_200k_full.py
```

**That's it!**

---

## 🚨 **If You Get Errors**

### Error: "python not found"
```powershell
python3 run_5k_test.py
```
Or
```powershell
py run_5k_test.py
```

### Error: "module not found"
```powershell
pip install pandas openpyxl requests
```
Then retry.

### Error: "file not found"
Check you're in the right folder:
```powershell
Get-Location
```
Should show: `C:\Users\mohsin\Downloads\Cursor 26 - CG on CK recommendations script`

---

## 📋 **Copy-Paste Ready (Option A)**

Open PowerShell and paste these **one by one**:

```
cd "C:\Users\mohsin\Downloads\Cursor 26 - CG on CK recommendations script"
```
*Press Enter, wait for prompt*

```
python run_5k_test.py
```
*Press Enter, wait 7-10 minutes*

```
python run_200k_full.py
```
*Press Enter, wait 5-7 hours*

**Done!**



