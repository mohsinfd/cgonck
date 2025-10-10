# Technical PRD Summary: Server-Side Card Recommendation Engine

**Quick Reference Guide for Engineering Team**

---

## What We're Building

**Goal:** Replace external CardGenius API with internal recommendation engine

**Why:** 
- 50x faster processing
- No external dependencies
- Process 1M users in 8 hours (vs 31 days)

---

## The Approach: Reverse Engineering as Black Box

We DON'T need CardGenius source code. We'll reverse engineer by:

1. **Collect API samples** (1000+ users)
2. **Analyze patterns** (reward rates, formulas)
3. **Build card catalog** (100+ cards with rules)
4. **Replicate logic** (points → savings → ranking)
5. **Validate** (95%+ accuracy match)

---

## Input Format (From Data Team)

**Excel/CSV with these columns:**

```
user_id, avg_amazon_gmv, avg_flipkart_gmv, avg_myntra_gmv, 
avg_ajio_gmv, avg_grocery_gmv, avg_confirmed_gmv
```

**Example:**
```csv
CK7186246,50000,30000,10000,5000,15000,100000
```

---

## Output Format (To Data Team)

**Excel/CSV with top 10 cards per user:**

```
user_id, rank, card_name, net_savings, total_savings_yearly, 
joining_fees, total_extra_benefits, amazon_points, flipkart_points, ...
```

**Example:**
```csv
CK7186246,1,ICICI Amazon Pay,25500,25000,500,1000,5000,300,...
CK7186246,2,Axis Magnus,27000,22000,10000,15000,2200,1200,...
```

---

## Core Components

### 1. Card Catalog (JSON Database)
```json
{
  "card_name": "ICICI Amazon Pay",
  "joining_fees": 500,
  "reward_rates": {
    "amazon": 0.05,  // 5% cashback
    "flipkart": 0.01,
    "caps": {"amazon": 5000}  // Monthly cap
  },
  "redemption": [
    {"method": "Vouchers", "rate": 1.0},
    {"method": "Cashback", "rate": 0.9}
  ],
  "extra_benefits": 1000
}
```

### 2. Points Calculator
```python
# For each category (Amazon, Flipkart, etc.):
points = spending × reward_rate
if cap exists:
    points = min(points, cap)
```

### 3. Redemption Calculator
```python
# Pick best redemption method (Vouchers vs Cashback)
best_rate = max(redemption_options, key=rate)
total_savings = total_points × best_rate × 12  # Annualize
```

### 4. Net Savings Calculator
```python
net_savings = total_savings_yearly - joining_fees + extra_benefits
```

### 5. Ranking Engine
```python
# Sort by net_savings (descending), return top 10
sorted_cards = sorted(cards, key=lambda x: -x['net_savings'])
return sorted_cards[:10]
```

---

## Implementation Timeline

### Week 1-2: Data Collection
- Collect 1000+ API request-response pairs
- Identify patterns (reward rates, caps, formulas)
- **Output:** Pattern analysis document

### Week 3: Card Catalog
- Build card database schema
- Populate 100+ cards with rules
- **Output:** `card_catalog.json`

### Week 4-5: Engine Development
- Build PointsCalculator
- Build RedemptionCalculator
- Build NetSavingsCalculator
- Build RankingEngine
- **Output:** Working engine + tests

### Week 6: Validation
- Test with 1000 users
- Compare with API results
- Fix discrepancies
- **Output:** 95%+ accuracy achieved

### Week 7: Integration
- Integrate with batch processor
- Production deployment
- **Output:** Live system

**Total: 7 weeks**

---

## Key Formulas (Reverse Engineered)

### Points Calculation
```
Category Points = Spending × Reward Rate
(Apply monthly/yearly caps if exist)
```

### Total Savings
```
Total Savings = Σ(Category Points) × Best_Redemption_Rate × 12
```

### Net Savings
```
Net Savings = Total Savings - Joining Fees + Extra Benefits
```

### Other Online Spend
```
Other Online = Confirmed GMV - (Amazon + Flipkart + Myntra + Ajio + Grocery)
```

---

## Example Calculation

**User Spending:**
- Amazon: ₹50,000/month
- Flipkart: ₹30,000/month
- Other: ₹20,000/month

**Card: ICICI Amazon Pay**
- Amazon rate: 5%
- Other rate: 1%
- Joining fees: ₹500
- Benefits: ₹1,000

**Calculation:**
1. Amazon points = 50,000 × 0.05 = 2,500
2. Flipkart points = 30,000 × 0.01 = 300
3. Other points = 20,000 × 0.01 = 200
4. Total monthly = 2,500 + 300 + 200 = 3,000
5. Annual points = 3,000 × 12 = 36,000
6. Savings (@ 1.0 voucher rate) = ₹36,000
7. Net savings = 36,000 - 500 + 1,000 = **₹36,500**

---

## Validation Strategy

### Accuracy Tests
- **Top 1 card match:** >95% (most critical)
- **Top 5 cards match:** >90%
- **Net savings:** 100% accurate (±₹1)

### Test with:
- 100 users (diverse spending patterns)
- 1000 users (production-like)
- Edge cases (zero spend, extreme spend)

---

## Critical Success Factors

1. **Pattern Accuracy**
   - Must correctly identify all reward rates
   - Must identify all caps and limits
   - Must understand redemption logic

2. **Card Catalog Quality**
   - Complete data for 100+ cards
   - Regularly updated (weekly checks)
   - Version controlled

3. **Continuous Validation**
   - Daily comparison with API
   - Alert if accuracy drops
   - Quick fix process

---

## Performance Targets

| Metric | Target | vs Current |
|--------|--------|------------|
| Time per user | <0.05s | 50x faster |
| 200K users | <1 hour | 150x faster |
| 1M users | <8 hours | 90x faster |
| Memory | <500MB | Same |

---

## Risk Mitigation

**Risk:** Can't identify all patterns  
**Mitigation:** Collect 1000+ diverse samples; continuous validation

**Risk:** Card catalog becomes outdated  
**Mitigation:** Automated weekly checks; monitoring dashboard

**Risk:** Accuracy below 95%  
**Mitigation:** Extensive testing; keep API as fallback

---

## Tech Stack

**Language:** Python 3.10+  
**Libraries:**
- pandas (data processing)
- numpy (calculations)
- pydantic (validation)
- pytest (testing)

**Infrastructure:**
- Runs locally or on server
- No external dependencies
- Self-contained

---

## What Engineering Team Needs to Do

### Phase 1: Understand Current API (Week 1)
1. Read API documentation
2. Analyze sample responses
3. Identify all fields and their meanings

### Phase 2: Collect Data (Week 1-2)
1. Build data collection script
2. Run API for 1000+ diverse users
3. Save request-response pairs

### Phase 3: Pattern Analysis (Week 2)
1. Analyze reward rates per card
2. Identify caps and limits
3. Understand redemption logic
4. Document all patterns

### Phase 4: Build Catalog (Week 3)
1. Create card database schema
2. Populate from pattern analysis
3. Validate against API responses

### Phase 5: Build Engine (Week 4-5)
1. Implement PointsCalculator
2. Implement RedemptionCalculator
3. Implement NetSavingsCalculator
4. Implement RankingEngine
5. Write comprehensive tests

### Phase 6: Validate (Week 6)
1. Test with 100 users
2. Compare with API
3. Fix discrepancies
4. Test with 1000 users
5. Achieve 95%+ accuracy

### Phase 7: Deploy (Week 7)
1. Integrate with batch system
2. Integration testing
3. Production deployment
4. Monitoring setup

---

## Questions for Engineering Team

1. **Timeline:** Is 7 weeks acceptable?
2. **Resources:** How many developers available?
3. **API Access:** Can we make 1000+ test API calls?
4. **Data Storage:** Where should card catalog live?
5. **Maintenance:** Who will own catalog updates?

---

## Success Definition

**We're successful when:**
- ✅ Process 200K users in <1 hour
- ✅ 95%+ accuracy vs CardGenius API
- ✅ Zero external dependencies
- ✅ Automated testing in place
- ✅ Card catalog update process working

---

**Next Steps:**
1. Review this PRD with engineering team
2. Get approval on approach
3. Start Week 1 tasks (data collection)

**Questions?** Refer to full technical PRD: `TECHNICAL_PRD_ServerSide_Implementation.md`



