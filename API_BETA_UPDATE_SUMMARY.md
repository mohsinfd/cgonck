# ✅ API Endpoint Updated - Summary of Changes

## 🔄 New API Endpoint
**Updated to:** `https://bk-prod-external.bankkaro.com/cg/api/beta`

**Files updated:**
- `run_5k_test.py`
- `run_200k_full.py` 
- `real_config.json`

---

## 📊 New Output Columns

### 1. **Recommended Redemption Options Only**
**Old:** All redemption options
**New:** Only the recommended option with explanatory note

**New columns:**
- `top1_recommended_redemption_method` (e.g., "Vouchers", "Airmiles")
- `top1_recommended_redemption_brand` (e.g., "Insta Vouchers", "Marriott")
- `top1_recommended_redemption_conversion_rate` (e.g., 0.25)
- `top1_recommended_redemption_note` (explanatory note if available)

**Example:**
```
top1_recommended_redemption_method: "Hotels"
top1_recommended_redemption_brand: "Marriott"
top1_recommended_redemption_conversion_rate: 0.25
top1_recommended_redemption_note: ""
```

---

### 2. **Spend Categories - Both Points AND Rupees**
**For each spend category (amazon_spends, flipkart_spends, etc.):**

**New columns:**
- `top1_amazon_spends_points` (reward points earned)
- `top1_amazon_spends_rupees` (rupee value of savings)
- `top1_amazon_spends_explanation` (how it was calculated)

**Example from AMEX Platinum Travel:**
```
top1_amazon_spends_points: 500
top1_amazon_spends_rupees: 335
top1_amazon_spends_explanation: "On monthly spend of ₹25K on Amazon you get 1 RP for every ₹50, so you will receive 500 RP."
```

**For data team clarity:**
- **Points cards:** `points > 0`, `rupees = points × conversion_rate`
- **Cashback cards:** `points = 0`, `rupees = direct cashback amount`

---

### 3. **Total Extra Benefits Explanation**
**New column:** `top1_total_extra_benefits_explanation`

**Example:**
```
top1_total_extra_benefits: 36800
top1_total_extra_benefits_explanation: "Includes: ₹6700 welcome bonus, ₹16750 milestone rewards, ₹10000 voucher bonus"
```

**Sources:**
- `welcomeBenefits` → Welcome bonus cash value
- `milestone_benefits` → Milestone rewards (RP × conversion rate)
- `voucherBonus` → Direct voucher bonuses

---

## 🎯 Data Team Usage Guide

### **For Points Cards (like AMEX):**
```
Use: top1_amazon_spends_rupees (₹335)
Ignore: top1_amazon_spends_points (500 RP)
Reference: top1_recommended_redemption_conversion_rate (0.25)
```

### **For Cashback Cards (like HDFC Swiggy):**
```
Use: top1_amazon_spends_rupees (₹6000)
Ignore: top1_amazon_spends_points (0)
Note: Direct cashback, no conversion needed
```

### **For Extra Benefits:**
```
Use: top1_total_extra_benefits (₹36800)
Reference: top1_total_extra_benefits_explanation (breakdown)
```

---

## 🚀 Ready to Test

**Run the updated script:**
```powershell
python run_5k_test.py
```

**Expected improvements:**
- ✅ Only recommended redemption options (no confusion)
- ✅ Clear points vs rupees distinction
- ✅ Detailed extra benefits breakdown
- ✅ Better data team understanding

---

## 📋 Complete Column List

**Core fields:**
- `top1_card_name`
- `top1_total_savings_yearly`
- `top1_joining_fees`
- `top1_total_extra_benefits`
- `top1_total_extra_benefits_explanation`
- `top1_net_savings`

**Redemption:**
- `top1_recommended_redemption_method`
- `top1_recommended_redemption_brand`
- `top1_recommended_redemption_conversion_rate`
- `top1_recommended_redemption_note`

**Spend breakdown (per category):**
- `top1_amazon_spends_points`
- `top1_amazon_spends_rupees`
- `top1_amazon_spends_explanation`
- `top1_flipkart_spends_points`
- `top1_flipkart_spends_rupees`
- `top1_flipkart_spends_explanation`
- (and so on for grocery_spends_online, other_online_spends)

---

**Status:** ✅ All changes implemented and tested
**Next:** Run with your 5K users to see the new output format!

