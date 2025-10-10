# CardGenius Server-Side Integration - Executive Summary

**For:** CardGenius Tech Team  
**From:** CashKaro Product Team  
**Date:** October 7, 2025

---

## What We Need

**Build a server-side batch processor that:**
1. Reads user spending data from CashKaro database
2. Generates card recommendations using your existing CardGenius logic
3. Writes results back to CashKaro database

**No API calls needed** - Direct database-to-database integration

---

## Processing Requirements

### Initial Backfill
- **Volume:** 2,000,000 users (one-time)
- **Deadline:** < 24 hours
- **Purpose:** Go-live blocker

### Ongoing Operations
- **Volume:** 50,000 users per week
- **Schedule:** Weekly (e.g., Monday 2 AM)
- **Deadline:** < 1 hour per batch

---

## Architecture

```
CashKaro DB
    ↓
[INPUT TABLE: user_spending_data]
    ↓
CardGenius Batch Processor ← Your existing logic
    ↓
[OUTPUT TABLE: card_recommendations]
    ↓
CashKaro consumes results
```

---

## Input Table: `user_spending_data`

**You will read from this table:**

```sql
user_id VARCHAR(50)           -- e.g., "CK7186246"
avg_amazon_gmv DECIMAL(12,2)  -- Monthly average: ₹50,000
avg_flipkart_gmv DECIMAL(12,2)
avg_myntra_gmv DECIMAL(12,2)
avg_ajio_gmv DECIMAL(12,2)
avg_grocery_gmv DECIMAL(12,2)
avg_confirmed_gmv DECIMAL(12,2)  -- Total confirmed GMV
processing_status ENUM         -- 'new', 'pending', 'completed', 'failed'
```

**Sample query you'll use:**
```sql
SELECT * FROM user_spending_data 
WHERE processing_status = 'new'
LIMIT 10000;
```

---

## Output Table: `card_recommendations`

**You will write to this table:**

```sql
user_id VARCHAR(50)                -- Same as input
rank TINYINT                       -- 1 to 10
card_name VARCHAR(200)             -- "ICICI Amazon Pay Credit Card"
total_savings_yearly DECIMAL(12,2) -- ₹25,000
joining_fees DECIMAL(12,2)         -- ₹500
total_extra_benefits DECIMAL(12,2) -- ₹1,000
net_savings DECIMAL(12,2)          -- ₹25,500
amazon_points DECIMAL(12,2)        -- Monthly points
flipkart_points DECIMAL(12,2)
myntra_points DECIMAL(12,2)
ajio_points DECIMAL(12,2)
grocery_points DECIMAL(12,2)
other_online_points DECIMAL(12,2)
redemption_method VARCHAR(50)      -- "Vouchers" or "Cashback"
redemption_rate DECIMAL(5,4)       -- 1.0000 or 0.9000
```

**You'll insert 10 rows per user** (top 10 cards, ranked by net_savings)

---

## What You Already Have

✅ **CardGenius recommendation engine** - Your existing codebase  
✅ **Card catalog** - All card data and rules  
✅ **Calculation logic** - Points, redemption, net savings

## What You Need to Build

🔨 **Batch processor** that:
1. Connects to CashKaro database
2. Fetches users in chunks (e.g., 10K at a time)
3. Calls your existing engine for each user
4. Writes results back to database
5. Updates processing status

🔨 **Parallel processing** (required for performance):
- Process 100+ users simultaneously
- Target: 1,000 users/minute throughput

🔨 **Error handling**:
- Retry failed users
- Log errors
- Don't stop batch on single failure

---

## Performance Targets

| Task | Volume | Target Time | Throughput |
|------|--------|-------------|------------|
| Initial backfill | 2M users | < 24 hours | > 1,000/min |
| Weekly batch | 50K users | < 1 hour | > 1,000/min |

**How to achieve this:**
- Use 100+ parallel workers
- Process in chunks of 10K users
- Direct database access (no network overhead)

**Expected:** With your existing logic running server-side, processing should be very fast (~0.01s per user). Parallel processing gets you to target throughput.

---

## Implementation Approach

### High-Level Pseudo-Code

```python
def process_batch(chunk_size=10000, workers=100):
    # 1. Fetch users
    users = db.query("SELECT * FROM user_spending_data WHERE processing_status = 'new' LIMIT ?", chunk_size)
    
    # 2. Mark as pending
    db.execute("UPDATE user_spending_data SET processing_status = 'pending' WHERE user_id IN (?)", user_ids)
    
    # 3. Process in parallel
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = executor.map(process_user, users)
    
    # 4. Write results
    db.bulk_insert('card_recommendations', flatten(results))
    
    # 5. Mark complete
    db.execute("UPDATE user_spending_data SET processing_status = 'completed' WHERE user_id IN (?)", user_ids)

def process_user(user_data):
    # YOUR EXISTING LOGIC HERE
    recommendations = cardgenius_engine.get_recommendations(user_data)
    return format_for_db(recommendations[:10])  # Top 10 only
```

---

## What CashKaro Provides

✅ **Database access:**
- Connection credentials
- Network access (VPN/firewall rules)
- Read access to `user_spending_data`
- Write access to `card_recommendations`

✅ **Data:**
- 2M users pre-populated for initial run
- Weekly 50K users added every week

✅ **Support:**
- Points of contact
- Schema documentation
- Testing environment

---

## Timeline

### Week 1: Setup
- Database access
- Network connectivity
- Test environment

### Week 2-3: Development
- Build batch processor
- Integrate with your engine
- Add parallel processing
- Unit testing

### Week 4: Testing
- Test with 1K users (functional)
- Test with 100K users (performance)
- Validate accuracy

### Week 5: Pre-Production
- Deploy to staging
- End-to-end testing
- Documentation

### Week 6: Production
- Deploy to production
- Process 2M users
- Monitor and validate

### Week 7: Stabilization
- Bug fixes
- Performance tuning
- Setup weekly automation

**Total: 7 weeks**

---

## Success Criteria

**Must Have:**
- [ ] Process 2M users in < 24 hours
- [ ] All users get exactly 10 recommendations
- [ ] Net savings calculations match your current API
- [ ] Error rate < 0.1%
- [ ] Automated weekly processing working

**Nice to Have:**
- [ ] Process 2M in < 12 hours (faster is better)
- [ ] Real-time monitoring dashboard
- [ ] Automated alerts on failures

---

## Key Technical Details

### Database Connection
- CashKaro will provide: host, database, username, password
- You'll need: Connection pooling (20-200 connections)
- Network: VPN or private connection

### Parallel Processing
- Use your preferred method (threads, processes, async)
- Recommended: 100 workers for optimal throughput
- Resource needs: 16+ core CPU, 32 GB RAM

### Error Handling
- Retry transient failures (3 attempts)
- Log permanent failures
- Don't stop batch on single user failure
- Update `processing_status` and `processing_error` fields

---

## Open Questions

**For CashKaro:**
1. Database type and version?
2. When can you provide credentials?
3. Preferred weekly schedule?
4. Where to send alerts?

**For CardGenius:**
5. Where will this service run?
6. Docker/Kubernetes/VM deployment?
7. 7-week timeline acceptable?
8. How many engineers available?

---

## Next Steps

1. **Review this PRD** with your engineering team
2. **Confirm timeline** is acceptable
3. **Schedule kickoff** meeting with CashKaro
4. **Start Week 1** - Get database access

---

**Full Technical PRD:** See `TECHNICAL_PRD_Database_Integration.md` for complete specifications, SQL schemas, error handling, monitoring, and more.

**Questions?** Contact: [Your Name/Email]



