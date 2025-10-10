# CardGenius Output Columns - Complete Explanation

## 📊 Overview
Based on the CardGenius API response and our processing logic, here's what each column means:

---

## 🔢 Core Financial Metrics

### 1. **`total_savings_yearly`**
**What it is:** The total annual savings you'll earn from using this card

**Components:**
- Cashback/points earned on Amazon spending
- Cashback/points earned on Flipkart spending
- Cashback/points earned on Grocery spending
- Cashback/points earned on Other Online spending
- **CONVERTED TO RUPEES** using the best redemption rate

**Does it include joining fees?** ❌ **NO** - This is GROSS savings before any costs

**Example from API:**
```json
"total_savings_yearly": 12000  // ₹12,000 in rewards earned
```

---

### 2. **`joining_fees`**
**What it is:** The annual or one-time joining fee for the card

**Source:** Comes directly from CardGenius card database

**Example from API:**
```json
"joining_fees": 500  // ₹500 annual fee
```

**Note:** Some cards have ₹0 joining fees (e.g., ICICI Amazon Pay)

---

### 3. **`total_extra_benefits`**
**What it is:** Milestone rewards, welcome bonuses, or other benefits

**Common examples:**
- Welcome bonus vouchers (e.g., ₹1,500 voucher on first spend)
- Milestone benefits (e.g., ₹10,000 benefit after spending ₹4L)
- Annual fee waivers converted to rupee value
- Lounge access value, etc.

**Example from API:**
```json
"total_extra_benefits": 1500  // ₹1,500 welcome bonus
```

**Does it include joining fees?** ❌ **NO** - These are ADDITIONAL perks

---

### 4. **`net_savings`** ⭐ **MOST IMPORTANT**
**What it is:** The TRUE annual value of the card to you

**Formula:**
```
net_savings = total_savings_yearly - joining_fees + total_extra_benefits
```

**Example calculation:**
- Card: AMEX SMART EARN
- Total savings: ₹10,050
- Joining fees: ₹495
- Extra benefits: ₹1,500
- **Net Savings = 10,050 - 495 + 1,500 = ₹11,055**

**This is what we use for ranking cards!**

---

## 🎯 Points & Rewards Breakdown

### 5. **`amazon_spends_points`**
**What it is:** Reward points earned ONLY from your Amazon spending

**Two formats:**
1. **Direct cashback cards:** Points = 0, but explanation shows cashback in rupees
2. **Points cards:** Shows actual reward points earned

**Example from API:**
```json
// Cashback card (HDFC Swiggy)
"amazon_spends_points": 0
"amazon_spends_explanation": "On spends of ₹1.2L on Amazon you get 5% Cashback, which is ₹6,000."

// Points card (AMEX Smart Earn)
"amazon_spends_points": 250
"amazon_spends_explanation": "On spend of ₹2.5K on Amazon you get 5 RP for every ₹50, so you will receive 250 RP."
```

**Note:** If points = 0 but explanation shows savings, the card gives DIRECT CASHBACK (already included in total_savings_yearly)

---

### 6. **`flipkart_spends_points`**
**What it is:** Reward points earned from Flipkart spending

**Same logic as Amazon:**
- Points = 0 → Direct cashback
- Points > 0 → Reward points that need redemption

---

### 7. **`grocery_spends_online_points`**
**What it is:** Points from online grocery spending (Swiggy Instamart, BigBasket, etc.)

---

### 8. **`other_online_spends_points`**
**What it is:** Points from OTHER online platforms

**What's included in "other online"?**
Based on our column mapping:
```
other_online_spends = avg_myntra_gmv + avg_ajio_gmv + avg_confirmed_gmv
```

**Common brands covered:**
- Myntra, Ajio, Nykaa
- BookMyShow, Uber, Ola
- Food delivery (Swiggy, Zomato)
- Other e-commerce not in Amazon/Flipkart/Grocery

---

## 💳 Redemption Options

### 9. **`redemption_options`**
**What it is:** JSON array of ways to convert your points to value

**Structure:**
```json
[{
  "type": "Vouchers",           // Vouchers, Cashback, or AirMiles
  "conversion_rate": 0.25,      // 1 point = ₹0.25
  "brand": "Insta Vouchers",    // Specific brand if applicable
  "description": ""
}]
```

**Example interpretation:**
- Conversion rate 1.0 = 1 point = ₹1 (best!)
- Conversion rate 0.25 = 1 point = ₹0.25 (4 points = ₹1)
- Conversion rate 0.67 = 1 point = ₹0.67

**Our filtering:** We ONLY show Vouchers and Cashback methods (not AirMiles, Hotel Points, etc.)

---

### 10. **`highest_conversion_rate`**
**What it is:** The best conversion rate among ALL redemption options

**Example:**
```json
"highest_conversion_rate": 0.67  // Best rate is 0.67 rupees per point
```

**Used for:** Calculating total_savings_yearly from points

---

### 11. **`all_conversion_rates`**
**What it is:** Human-readable summary of the BEST redemption option

**Format:**
```
"Vouchers: 0.25 (Insta Vouchers)"
```

**If empty/0:** Card gives direct cashback, no point conversion needed

---

## 🔗 Additional Fields

### 12. **`network_url`**
**What it is:** Affiliate tracking link for the card application

**Used for:** CashKaro affiliate commissions when user applies

---

### 13. **`card_name`**
**What it is:** Official name of the credit card

**Note:** We use CardGenius naming (e.g., "AXIS MAGNUS", "ICICI Amazon Pay Credit Card")

---

## 📈 Spending Input Columns (What we send to API)

### User's Spending Data:
1. **`avg_amazon_gmv`** → Maps to `amazon_spends` in API
2. **`avg_flipkart_gmv`** → Maps to `flipkart_spends` in API
3. **`avg_grocery_gmv`** → Maps to `grocery_spends_online` in API
4. **`avg_myntra_gmv + avg_ajio_gmv + avg_confirmed_gmv`** → Maps to `other_online_spends` in API

---

## 🎯 How CardGenius Calculates `total_savings_yearly`

### For DIRECT CASHBACK cards (e.g., HDFC Swiggy, SBI Cashback):
```
total_savings_yearly = 
  Amazon cashback (5% of ₹120K = ₹6,000) +
  Flipkart cashback (5% of ₹120K = ₹6,000) +
  Grocery cashback (10% of ₹0 = ₹0) +
  Other online cashback (5% of ₹0 = ₹0)
  = ₹12,000
```

### For POINTS cards (e.g., AMEX Smart Earn, HDFC Millenia):
```
Step 1: Calculate points earned per category
  Amazon: 250 points (5 RP per ₹50 on ₹2.5K)
  Flipkart: 1,000 points (10 RP per ₹50 on ₹5K)
  Total: 1,250 points

Step 2: Convert to rupees using best redemption rate
  1,250 points × 0.25 (Voucher rate) = ₹312.50

Step 3: But API shows total_savings_yearly = ₹10,050
  (This includes ALL spending categories at their respective rates)
```

**KEY INSIGHT:** CardGenius does ALL this math internally. We just receive the final `total_savings_yearly` figure.

---

## ⚠️ Important Notes

### Why are points sometimes 0 but savings exist?
**Answer:** The card gives DIRECT CASHBACK instead of points

Example:
```json
"amazon_spends_points": 0
"amazon_spends_explanation": "you get 5% Cashback, which is ₹6,000"
```
This ₹6,000 is ALREADY included in `total_savings_yearly`

### Why is `net_savings` different from `total_savings_yearly`?
**Answer:** Because we subtract joining fees and add extra benefits

```
net_savings = total_savings_yearly - joining_fees + total_extra_benefits
```

This is the ACTUAL benefit to the user.

### Does `total_savings_yearly` include any fees?
**Answer:** ❌ **NO** - It's GROSS rewards before any costs

All fees are handled separately in the `joining_fees` field.

---

## 📊 Ranking Logic

**How we rank cards:**
1. Sort by `net_savings` (descending)
2. Top card = highest `net_savings`

**Example:**
```
User 15999:
- Top 1: HDFC Swiggy (net_savings = ₹11,500)
- Top 2: AMEX Smart Earn (net_savings = ₹11,055)
- Top 3: SBI Cashback (net_savings = ₹11,001)
```

---

## 🎓 Summary

| Column | Includes Fees? | What it represents |
|--------|----------------|-------------------|
| `total_savings_yearly` | ❌ NO | Gross rewards earned (before costs) |
| `joining_fees` | N/A | Annual fee you pay |
| `total_extra_benefits` | ❌ NO | Additional perks (welcome bonus, etc.) |
| `net_savings` | ✅ YES | **TRUE VALUE = savings - fees + benefits** |

**Bottom line:** 
- `total_savings_yearly` = What you EARN
- `joining_fees` = What you PAY
- `total_extra_benefits` = What you GET as bonus
- **`net_savings` = What you ACTUALLY SAVE** (most important!)

---

Generated: Based on CardGenius API v2 response structure
Last Updated: Real-world testing with 134 users

