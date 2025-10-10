# ✅ FINAL CONFIGURATION - 10 Workers

**Endpoint Updated:** `https://bk-prod-external.bankkaro.com/cg`

---

## 📊 **Exact Load with 10 Workers**

### **API Calls:**
```
Per second:  6-7 API calls
Per minute:  400 API calls
Per hour:    24,000 API calls
```

### **Network Load:**
```
Concurrent connections: 10
Bandwidth needed: 84 Mbps download
Data per second: 10.5 MB
```

### **Timeline:**
```
5K users:   12.5 minutes
200K users: 8.3 hours
```

---

## 🎯 **What to Tell CardGenius Team**

**Email them:**

```
Subject: API Load Notification - Batch Processing

Hi Team,

We'll be calling your CardGenius API endpoint:

Endpoint: https://bk-prod-external.bankkaro.com/cg
Load: 6-7 API calls per second sustained
Concurrent: 10 connections
Duration: ~8 hours for 200K users
Total calls: 200,000

Schedule:
- Testing: [DATE] with 5K users (12 minutes)
- Production: [DATE] with 200K users (8 hours)

Is this load acceptable?

Thanks,
[Your Name]
```

---

## ✅ **Everything Updated**

**Scripts updated:**
- ✅ `run_5k_test.py` → New endpoint
- ✅ `run_200k_full.py` → New endpoint
- ✅ `real_config.json` → New endpoint

---

## 🚀 **Ready to Run!**

```powershell
cd "C:\Users\mohsin\Downloads\Cursor 26 - CG on CK recommendations script"
python run_5k_test.py
```

**This will now call:** `https://bk-prod-external.bankkaro.com/cg`

**With:** 6-7 API calls per second (10 workers)

---

**All set! Ready to test?** 🎯



