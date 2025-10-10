# Technical PRD: CardGenius Server-Side Recommendation Engine
## Database-to-Database Integration

**Document Version:** 2.0  
**Date:** October 7, 2025  
**Audience:** CardGenius Tech Team  
**Priority:** Critical  
**Type:** Technical Specification

---

## 1. Executive Summary

### Context
CashKaro needs to process **2 million users initially**, then **50,000 users weekly** for card recommendations. Current external API approach takes too long and is not scalable.

### Objective
CardGenius tech team to build **server-side recommendation engine** that:
- Reads user spending data from CashKaro database table
- Processes recommendations using existing CardGenius logic
- Writes results back to CashKaro database table
- Eliminates external API calls and network overhead

### Why Server-Side?
- **Performance:** Process 2M users in hours (not days)
- **Scale:** Handle 50K weekly users easily
- **Reliability:** No network dependencies or API timeouts
- **Efficiency:** Direct database access, no serialization overhead

### Success Criteria
- [ ] Process 2M users in < 24 hours
- [ ] Process 50K users in < 1 hour (weekly batches)
- [ ] 100% accuracy (same logic as current API)
- [ ] Automated weekly execution

---

## 2. Business Requirements

### 2.1 Processing Requirements

#### Initial Backfill
- **Volume:** 2,000,000 users (one-time)
- **Timeline:** Complete in < 24 hours
- **Priority:** High (blocking go-live)

#### Ongoing Operations
- **Volume:** 50,000 users per week
- **Schedule:** Weekly batch (e.g., every Monday)
- **Timeline:** Complete in < 1 hour
- **Priority:** Medium (routine operations)

### 2.2 Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Initial 2M users** | < 24 hours | Enable go-live on schedule |
| **Weekly 50K users** | < 1 hour | Minimize disruption |
| **Throughput** | > 1,000 users/min | Ensure scalability |
| **Accuracy** | 100% | Match current API logic |
| **Availability** | 99.9% | Critical business process |

### 2.3 Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CashKaro Database                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────┐     │
│  │  INPUT TABLE: user_spending_data                 │     │
│  ├──────────────────────────────────────────────────┤     │
│  │  - user_id                                       │     │
│  │  - avg_amazon_gmv                                │     │
│  │  - avg_flipkart_gmv                              │     │
│  │  - avg_myntra_gmv                                │     │
│  │  - avg_ajio_gmv                                  │     │
│  │  - avg_grocery_gmv                               │     │
│  │  - avg_confirmed_gmv                             │     │
│  │  - processing_status (new/pending/complete)      │     │
│  │  - last_processed_at                             │     │
│  └──────────────────────────────────────────────────┘     │
│                         ↓                                   │
│                         ↓                                   │
│              CardGenius Processing Engine                   │
│              (Server-side, direct DB access)                │
│                         ↓                                   │
│                         ↓                                   │
│  ┌──────────────────────────────────────────────────┐     │
│  │  OUTPUT TABLE: card_recommendations              │     │
│  ├──────────────────────────────────────────────────┤     │
│  │  - user_id                                       │     │
│  │  - rank (1-10)                                   │     │
│  │  - card_name                                     │     │
│  │  - total_savings_yearly                          │     │
│  │  - joining_fees                                  │     │
│  │  - total_extra_benefits                          │     │
│  │  - net_savings                                   │     │
│  │  - amazon_points                                 │     │
│  │  - flipkart_points                               │     │
│  │  - myntra_points                                 │     │
│  │  - ajio_points                                   │     │
│  │  - grocery_points                                │     │
│  │  - other_online_points                           │     │
│  │  - redemption_method                             │     │
│  │  - redemption_rate                               │     │
│  │  - processed_at                                  │     │
│  └──────────────────────────────────────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Database Specifications

### 3.1 Input Table: `user_spending_data`

**Table Name:** `cashkaro.user_spending_data`  
**Access:** Read-only for CardGenius  
**Owner:** CashKaro Data Team

#### Schema

```sql
CREATE TABLE user_spending_data (
    -- Primary Key
    user_id VARCHAR(50) PRIMARY KEY,
    
    -- Spending Data (Monthly Averages in INR)
    avg_amazon_gmv DECIMAL(12, 2) NOT NULL DEFAULT 0,
    avg_flipkart_gmv DECIMAL(12, 2) NOT NULL DEFAULT 0,
    avg_myntra_gmv DECIMAL(12, 2) NOT NULL DEFAULT 0,
    avg_ajio_gmv DECIMAL(12, 2) NOT NULL DEFAULT 0,
    avg_grocery_gmv DECIMAL(12, 2) NOT NULL DEFAULT 0,
    avg_confirmed_gmv DECIMAL(12, 2) NOT NULL DEFAULT 0,
    
    -- Processing Metadata
    processing_status ENUM('new', 'pending', 'completed', 'failed') DEFAULT 'new',
    last_processed_at TIMESTAMP NULL,
    processing_error TEXT NULL,
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_processing_status (processing_status),
    INDEX idx_last_processed (last_processed_at)
);
```

#### Sample Data

```sql
-- Sample records
INSERT INTO user_spending_data VALUES
('CK7186246', 50000.00, 30000.00, 10000.00, 5000.00, 15000.00, 120000.00, 'new', NULL, NULL, NOW(), NOW()),
('USER4188152', 120000.00, 20000.00, 5000.00, 2000.00, 8000.00, 160000.00, 'new', NULL, NULL, NOW(), NOW()),
('CUST3267595', 10000.00, 5000.00, 2000.00, 1000.00, 3000.00, 22000.00, 'new', NULL, NULL, NOW(), NOW());
```

#### Data Validation Rules

```sql
-- Constraints that should be enforced
ALTER TABLE user_spending_data
    ADD CONSTRAINT chk_positive_spending CHECK (
        avg_amazon_gmv >= 0 AND
        avg_flipkart_gmv >= 0 AND
        avg_myntra_gmv >= 0 AND
        avg_ajio_gmv >= 0 AND
        avg_grocery_gmv >= 0 AND
        avg_confirmed_gmv >= 0
    );
```

#### Query to Fetch Pending Users

```sql
-- CardGenius will use this query to fetch users to process
SELECT 
    user_id,
    avg_amazon_gmv,
    avg_flipkart_gmv,
    avg_myntra_gmv,
    avg_ajio_gmv,
    avg_grocery_gmv,
    avg_confirmed_gmv
FROM user_spending_data
WHERE processing_status = 'new'
LIMIT 10000;  -- Process in batches of 10K

-- Update status to 'pending' before processing
UPDATE user_spending_data
SET processing_status = 'pending',
    updated_at = NOW()
WHERE user_id IN (...);  -- List of users being processed
```

---

### 3.2 Output Table: `card_recommendations`

**Table Name:** `cashkaro.card_recommendations`  
**Access:** Write (INSERT/UPDATE) for CardGenius  
**Owner:** CashKaro Data Team

#### Schema

```sql
CREATE TABLE card_recommendations (
    -- Primary Key (Composite)
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    rank TINYINT NOT NULL,  -- 1 to 10
    
    -- Card Details
    card_name VARCHAR(200) NOT NULL,
    card_id VARCHAR(100) NULL,  -- Optional: Internal card identifier
    
    -- Savings Breakdown
    total_savings_yearly DECIMAL(12, 2) NOT NULL,
    joining_fees DECIMAL(12, 2) NOT NULL,
    total_extra_benefits DECIMAL(12, 2) NOT NULL,
    net_savings DECIMAL(12, 2) NOT NULL,
    
    -- Category-wise Points (Monthly)
    amazon_points DECIMAL(12, 2) DEFAULT 0,
    flipkart_points DECIMAL(12, 2) DEFAULT 0,
    myntra_points DECIMAL(12, 2) DEFAULT 0,
    ajio_points DECIMAL(12, 2) DEFAULT 0,
    grocery_points DECIMAL(12, 2) DEFAULT 0,
    other_online_points DECIMAL(12, 2) DEFAULT 0,
    
    -- Redemption Details
    redemption_method VARCHAR(50) NULL,  -- e.g., 'Vouchers', 'Cashback'
    redemption_rate DECIMAL(5, 4) NULL,  -- e.g., 1.0000 or 0.9000
    
    -- Metadata
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    batch_id VARCHAR(50) NULL,  -- Track which batch this belongs to
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    UNIQUE KEY unique_user_rank (user_id, rank),
    INDEX idx_user_id (user_id),
    INDEX idx_batch_id (batch_id),
    INDEX idx_processed_at (processed_at),
    INDEX idx_net_savings (net_savings DESC),
    
    -- Foreign Key (if needed)
    FOREIGN KEY (user_id) REFERENCES user_spending_data(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
```

#### Sample Output Data

```sql
-- Sample recommendations for one user
INSERT INTO card_recommendations VALUES
(NULL, 'CK7186246', 1, 'ICICI Amazon Pay Credit Card', 'icici_amazon_pay', 
 25000.00, 500.00, 1000.00, 25500.00,
 5000.00, 300.00, 100.00, 50.00, 150.00, 2000.00,
 'Vouchers', 1.0000, NOW(), 'BATCH_20251007_001', NOW(), NOW()),
 
(NULL, 'CK7186246', 2, 'Axis Magnus Credit Card', 'axis_magnus',
 22000.00, 10000.00, 15000.00, 27000.00,
 2200.00, 1200.00, 500.00, 250.00, 750.00, 3000.00,
 'Vouchers', 1.0000, NOW(), 'BATCH_20251007_001', NOW(), NOW()),
 
(NULL, 'CK7186246', 3, 'HDFC Regalia Credit Card', 'hdfc_regalia',
 18000.00, 2500.00, 5000.00, 20500.00,
 1800.00, 1200.00, 400.00, 200.00, 600.00, 2500.00,
 'Cashback', 0.9000, NOW(), 'BATCH_20251007_001', NOW(), NOW());
```

#### Query to Insert Recommendations

```sql
-- CardGenius will use INSERT or REPLACE
REPLACE INTO card_recommendations (
    user_id, rank, card_name, card_id,
    total_savings_yearly, joining_fees, total_extra_benefits, net_savings,
    amazon_points, flipkart_points, myntra_points, ajio_points, 
    grocery_points, other_online_points,
    redemption_method, redemption_rate,
    processed_at, batch_id
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NOW(), ?);
```

---

## 4. Processing Logic Requirements

### 4.1 Core Calculation Logic

**CardGenius tech team already has this logic in their existing codebase.**  
This section documents what CashKaro expects as output, not how to implement it.

#### Required Calculations

1. **Points Calculation**
   - Calculate points earned per spending category
   - Apply any caps/limits per card rules
   - Handle special cases (bonus points, milestones)

2. **Redemption Value**
   - Convert points to rupee value
   - Select best redemption method (Vouchers vs Cashback)
   - Use highest conversion rate available

3. **Net Savings**
   - Formula: `net_savings = total_savings_yearly - joining_fees + total_extra_benefits`
   - Must be accurate to 2 decimal places

4. **Ranking**
   - Sort cards by `net_savings` (descending)
   - Return top 10 cards per user
   - Assign rank 1-10

#### Expected Behavior

- **No External API Calls:** All logic runs server-side
- **Consistent Results:** Same input always produces same output
- **Handle Edge Cases:**
  - Users with zero spending in all categories
  - Users with extreme spending (>₹10L/month)
  - Missing or NULL values (treat as 0)

---

## 5. Technical Implementation Requirements

### 5.1 Processing Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              CardGenius Processing Service                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────┐           │
│  │  1. Batch Coordinator                       │           │
│  │     - Fetches pending users from DB         │           │
│  │     - Splits into chunks (10K users)        │           │
│  │     - Manages parallel processing           │           │
│  └─────────────────────────────────────────────┘           │
│                      ↓                                      │
│  ┌─────────────────────────────────────────────┐           │
│  │  2. Recommendation Engine (Existing)        │           │
│  │     - Your existing CardGenius logic        │           │
│  │     - Processes 1 user → Returns 10 cards   │           │
│  │     - Pure function (no side effects)       │           │
│  └─────────────────────────────────────────────┘           │
│                      ↓                                      │
│  ┌─────────────────────────────────────────────┐           │
│  │  3. Database Writer                         │           │
│  │     - Batches INSERT statements             │           │
│  │     - Handles duplicates (REPLACE)          │           │
│  │     - Updates processing status             │           │
│  └─────────────────────────────────────────────┘           │
│                      ↓                                      │
│  ┌─────────────────────────────────────────────┐           │
│  │  4. Monitoring & Logging                    │           │
│  │     - Track progress (users processed)      │           │
│  │     - Log errors                            │           │
│  │     - Send alerts on failures               │           │
│  └─────────────────────────────────────────────┘           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Recommended Approach

#### Parallel Processing (Required)

**Current Performance (Sequential):**
- 1 user = ~0.01s (server-side, no network)
- 2M users = 20,000 seconds = 5.5 hours

**Required Performance (Parallel):**
- 100 parallel workers
- 2M users = 200 seconds = 3.3 minutes ✅

**Implementation Pattern:**
```python
# Pseudo-code (use your preferred language/framework)

def process_batch(batch_id, chunk_size=10000, workers=100):
    """
    Main batch processing function
    """
    # 1. Fetch pending users
    users = db.query("""
        SELECT * FROM user_spending_data 
        WHERE processing_status = 'new'
        LIMIT ?
    """, chunk_size)
    
    # 2. Mark as pending
    db.execute("""
        UPDATE user_spending_data 
        SET processing_status = 'pending' 
        WHERE user_id IN (?)
    """, [u.user_id for u in users])
    
    # 3. Process in parallel
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(process_single_user, user, batch_id)
            for user in users
        ]
        
        results = []
        for future in as_completed(futures):
            try:
                result = future.result()
                results.extend(result)  # List of 10 cards
            except Exception as e:
                logger.error(f"User processing failed: {e}")
    
    # 4. Batch insert results
    db.bulk_insert('card_recommendations', results)
    
    # 5. Mark as completed
    db.execute("""
        UPDATE user_spending_data 
        SET processing_status = 'completed',
            last_processed_at = NOW()
        WHERE user_id IN (?)
    """, [u.user_id for u in users])


def process_single_user(user_data, batch_id):
    """
    Process one user using existing CardGenius logic
    """
    # Call your existing recommendation engine
    recommendations = cardgenius_engine.get_recommendations(user_data)
    
    # Format for database
    db_records = []
    for rank, card in enumerate(recommendations[:10], start=1):
        db_records.append({
            'user_id': user_data.user_id,
            'rank': rank,
            'card_name': card.name,
            'total_savings_yearly': card.savings,
            'joining_fees': card.fees,
            'net_savings': card.net_savings,
            # ... all other fields
            'batch_id': batch_id
        })
    
    return db_records
```

### 5.3 Database Connection Requirements

**Connection Pool:**
- Min connections: 10
- Max connections: 200 (for 100 workers + overhead)
- Connection timeout: 30 seconds
- Query timeout: 60 seconds

**Credentials:** CashKaro Data Team will provide:
- Database host
- Database name
- Username/password
- SSL/TLS certificates (if required)

**Network:**
- CardGenius servers must have network access to CashKaro DB
- Firewall rules will be configured by CashKaro DevOps
- VPN or private network connection preferred

---

## 6. Performance Requirements

### 6.1 Processing Targets

#### Initial 2M Users

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Total Time** | < 24 hours | End-to-end batch completion |
| **Throughput** | > 1,000 users/min | Sustained throughput |
| **Chunk Processing** | < 10 min per 10K | Individual chunk time |
| **Memory Usage** | < 16 GB | Peak memory consumption |
| **CPU Usage** | < 80% | Average across cores |

**Strategy:**
- Process in 200 batches of 10K users each
- Run continuously for 24 hours
- 200 batches × 10 minutes = 2,000 minutes = 33 hours (with buffer)
- **OR** increase parallelism to complete faster

#### Weekly 50K Users

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Total Time** | < 1 hour | End-to-end batch completion |
| **Throughput** | > 1,000 users/min | Sustained throughput |
| **Schedule** | Weekly (e.g., Monday 2 AM) | Cron job |

**Strategy:**
- Process in 5 batches of 10K users each
- 5 batches × 10 minutes = 50 minutes ✅

### 6.2 Resource Allocation

**Recommended Server Specs:**
- **CPU:** 16+ cores
- **RAM:** 32 GB
- **Storage:** 100 GB SSD
- **Network:** 1 Gbps+

**Scaling Options:**
1. **Vertical:** Increase cores/RAM for faster processing
2. **Horizontal:** Run multiple servers in parallel (not required for 50K/week)

---

## 7. Error Handling & Recovery

### 7.1 Error Scenarios

#### Database Connection Failures
```python
# Retry logic
@retry(max_attempts=3, backoff=exponential)
def execute_query(query, params):
    try:
        return db.execute(query, params)
    except ConnectionError:
        logger.error("DB connection failed, retrying...")
        raise
```

#### Processing Failures
```python
# Mark failed users
try:
    recommendations = process_single_user(user)
except Exception as e:
    db.execute("""
        UPDATE user_spending_data 
        SET processing_status = 'failed',
            processing_error = ?
        WHERE user_id = ?
    """, str(e), user.user_id)
```

#### Partial Batch Failures
- **Continue processing:** Don't stop entire batch if one user fails
- **Log errors:** Detailed error logs for debugging
- **Retry mechanism:** Automatic retry for transient failures

### 7.2 Recovery Procedures

**Resume from Checkpoint:**
```sql
-- Find last successful batch
SELECT MAX(batch_id) FROM card_recommendations;

-- Count remaining users
SELECT COUNT(*) FROM user_spending_data 
WHERE processing_status IN ('new', 'failed');

-- Restart processing from where it left off
-- (Processing script handles this automatically)
```

**Reprocess Failed Users:**
```sql
-- Reset failed users to retry
UPDATE user_spending_data
SET processing_status = 'new',
    processing_error = NULL
WHERE processing_status = 'failed'
    AND last_processed_at < DATE_SUB(NOW(), INTERVAL 1 HOUR);
```

---

## 8. Monitoring & Alerting

### 8.1 Metrics to Track

#### Real-Time Metrics
```python
metrics = {
    'users_processed': 0,
    'users_pending': 0,
    'users_failed': 0,
    'throughput_per_minute': 0,
    'estimated_completion_time': None,
    'current_batch_id': None,
    'errors_last_hour': 0
}
```

#### Progress Tracking Query
```sql
-- Dashboard query
SELECT 
    processing_status,
    COUNT(*) as count,
    MIN(last_processed_at) as oldest_processed,
    MAX(last_processed_at) as latest_processed
FROM user_spending_data
GROUP BY processing_status;

-- Throughput calculation
SELECT 
    DATE_FORMAT(last_processed_at, '%Y-%m-%d %H:%i:00') as minute_bucket,
    COUNT(*) as users_processed
FROM user_spending_data
WHERE last_processed_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
GROUP BY minute_bucket
ORDER BY minute_bucket DESC;
```

### 8.2 Alerts

**Critical Alerts:**
- Processing stopped (no progress for 15 minutes)
- Error rate > 5%
- Database connection lost
- Throughput < 100 users/min

**Warning Alerts:**
- Error rate > 1%
- Throughput < 500 users/min
- Memory usage > 24 GB
- CPU usage > 90%

---

## 9. Schedule & Automation

### 9.1 Initial 2M User Processing

**One-Time Job:**
```bash
# Manual trigger by CardGenius team
./run_batch_processing.sh --mode initial --chunk-size 10000 --workers 100

# Expected output:
# Starting initial batch processing...
# Target: 2,000,000 users
# Chunk size: 10,000 users
# Parallel workers: 100
# Estimated completion: 24 hours
# Progress: [===>...........................] 15% (300K/2M users)
```

**Monitoring Dashboard:**
- Real-time progress (users processed / total)
- Estimated time remaining
- Current throughput
- Error count and details

### 9.2 Weekly 50K User Processing

**Cron Job:**
```bash
# Run every Monday at 2:00 AM
0 2 * * 1 /path/to/run_batch_processing.sh --mode weekly --chunk-size 10000

# Or use your preferred scheduler (Airflow, Kubernetes CronJob, etc.)
```

**Automated Workflow:**
1. CashKaro Data Team populates `user_spending_data` table (Sunday night)
2. CardGenius processing runs automatically (Monday 2 AM)
3. Results available in `card_recommendations` table (Monday 3 AM)
4. CashKaro consumes results for user-facing features (Monday morning)

---

## 10. Testing & Validation

### 10.1 Pre-Production Testing

#### Phase 1: Functional Testing (1000 users)
```sql
-- Create test dataset
INSERT INTO user_spending_data_test
SELECT * FROM user_spending_data
ORDER BY RAND()
LIMIT 1000;

-- Run processing
./run_batch_processing.sh --mode test --table user_spending_data_test

-- Validate output
SELECT 
    COUNT(DISTINCT user_id) as users_with_recommendations,
    COUNT(*) / COUNT(DISTINCT user_id) as avg_cards_per_user,
    MIN(net_savings) as min_net_savings,
    MAX(net_savings) as max_net_savings,
    AVG(net_savings) as avg_net_savings
FROM card_recommendations_test;

-- Expected: 1000 users, 10 cards each, reasonable net_savings values
```

#### Phase 2: Performance Testing (100K users)
```bash
# Measure throughput and resource usage
./run_batch_processing.sh --mode test --chunk-size 10000 --users 100000

# Expected:
# - Complete in < 100 minutes
# - Throughput: > 1000 users/min
# - Memory: < 16 GB
# - CPU: < 80%
```

#### Phase 3: Accuracy Validation
```python
# Compare with current API results (sample of 100 users)
def validate_accuracy(test_users):
    """
    Call both API and server-side engine
    Compare results
    """
    matches = 0
    for user in test_users:
        api_results = call_cardgenius_api(user)
        db_results = fetch_from_db(user.user_id)
        
        if compare_recommendations(api_results, db_results):
            matches += 1
    
    accuracy = matches / len(test_users) * 100
    print(f"Accuracy: {accuracy:.1f}%")
    assert accuracy >= 95, "Accuracy below threshold"
```

### 10.2 Production Validation

**Post-Processing Checks:**
```sql
-- 1. Check all users processed
SELECT 
    (SELECT COUNT(*) FROM user_spending_data WHERE processing_status = 'completed') as completed,
    (SELECT COUNT(*) FROM user_spending_data WHERE processing_status = 'new') as pending,
    (SELECT COUNT(*) FROM user_spending_data WHERE processing_status = 'failed') as failed;

-- 2. Validate output completeness
SELECT 
    u.user_id,
    COUNT(r.id) as num_recommendations
FROM user_spending_data u
LEFT JOIN card_recommendations r ON u.user_id = r.user_id
WHERE u.processing_status = 'completed'
GROUP BY u.user_id
HAVING num_recommendations != 10;
-- Expected: 0 rows (all users should have exactly 10 recommendations)

-- 3. Check for data quality issues
SELECT 
    user_id,
    rank,
    card_name,
    net_savings
FROM card_recommendations
WHERE net_savings IS NULL
    OR total_savings_yearly IS NULL
    OR joining_fees IS NULL;
-- Expected: 0 rows (no NULL values in critical fields)

-- 4. Validate ranking order
SELECT 
    user_id,
    rank,
    net_savings,
    LEAD(net_savings) OVER (PARTITION BY user_id ORDER BY rank) as next_net_savings
FROM card_recommendations
WHERE rank < 10
HAVING net_savings < next_net_savings;
-- Expected: 0 rows (net_savings should be descending)
```

---

## 11. Deliverables & Timeline

### 11.1 Deliverables from CardGenius Tech Team

**Code & Services:**
- [ ] Batch processing service (parallel processing)
- [ ] Database integration module
- [ ] Error handling and retry logic
- [ ] Monitoring and logging
- [ ] Deployment scripts

**Documentation:**
- [ ] Technical implementation docs
- [ ] Database schema documentation
- [ ] Deployment guide
- [ ] Monitoring guide
- [ ] Troubleshooting guide

**Testing:**
- [ ] Unit tests (core logic)
- [ ] Integration tests (database)
- [ ] Performance tests (100K+ users)
- [ ] Validation tests (accuracy)

### 11.2 Deliverables from CashKaro Team

**Infrastructure:**
- [ ] Database access credentials
- [ ] Network connectivity (VPN/firewall rules)
- [ ] `user_spending_data` table created
- [ ] `card_recommendations` table created

**Data:**
- [ ] Initial 2M user data populated
- [ ] Weekly 50K user data feed process
- [ ] Data quality validation

**Support:**
- [ ] Points of contact (tech, product, data)
- [ ] Escalation process
- [ ] Change management process

### 11.3 Implementation Timeline

#### Week 1: Setup & Planning
- [ ] Database access provisioned
- [ ] Network connectivity established
- [ ] Test environment setup
- [ ] Technical kickoff meeting

#### Week 2-3: Development
- [ ] Batch processing service development
- [ ] Database integration
- [ ] Unit testing
- [ ] Code review

#### Week 4: Testing
- [ ] Integration testing (1K users)
- [ ] Performance testing (100K users)
- [ ] Accuracy validation
- [ ] Bug fixes

#### Week 5: Pre-Production
- [ ] Deploy to staging environment
- [ ] End-to-end testing
- [ ] Documentation finalization
- [ ] Training for support teams

#### Week 6: Production Deployment
- [ ] Deploy to production
- [ ] Process initial 2M users
- [ ] Validate results
- [ ] Monitor for 48 hours

#### Week 7: Stabilization
- [ ] Address any issues
- [ ] Optimize performance
- [ ] Setup weekly automation
- [ ] Project handoff

**Total Timeline: 7 weeks**

---

## 12. Success Criteria

### 12.1 Launch Criteria (Must Have)

- [ ] Process 2M users in < 24 hours
- [ ] 100% of users have recommendations
- [ ] All users have exactly 10 cards
- [ ] Net savings calculations accurate
- [ ] Zero critical bugs
- [ ] Monitoring dashboard live

### 12.2 Success Metrics (30 days post-launch)

- [ ] Weekly 50K batch completes in < 1 hour
- [ ] Error rate < 0.1%
- [ ] Zero manual interventions required
- [ ] 99.9% uptime
- [ ] Support tickets < 5/month

---

## 13. Support & Maintenance

### 13.1 Support Model

**CardGenius Responsibilities:**
- Processing engine maintenance
- Bug fixes
- Performance optimization
- Logic updates (new cards, rate changes)

**CashKaro Responsibilities:**
- Database maintenance
- Data quality
- User data population
- Consuming recommendation results

### 13.2 SLA

**Processing SLA:**
- Weekly batch: Complete within 2 hours of start
- Uptime: 99.9%
- Error rate: < 0.1%

**Support SLA:**
- Critical issues: Response in 1 hour, resolve in 4 hours
- High priority: Response in 4 hours, resolve in 24 hours
- Medium/Low: Response in 24 hours, resolve in 1 week

---

## 14. Appendix

### A. Database Connection Example

```python
# Python example using SQLAlchemy
from sqlalchemy import create_engine

# Connection string (credentials provided by CashKaro)
DB_URL = "mysql+pymysql://username:password@host:3306/cashkaro?charset=utf8mb4"

# Create engine with connection pool
engine = create_engine(
    DB_URL,
    pool_size=20,
    max_overflow=100,
    pool_timeout=30,
    pool_recycle=3600
)

# Usage
with engine.connect() as conn:
    users = conn.execute("SELECT * FROM user_spending_data WHERE processing_status = 'new' LIMIT 10000")
```

### B. Batch Processing Script Template

```bash
#!/bin/bash
# run_batch_processing.sh

MODE=${1:-weekly}  # initial, weekly, test
CHUNK_SIZE=${2:-10000}
WORKERS=${3:-100}

echo "Starting batch processing..."
echo "Mode: $MODE"
echo "Chunk size: $CHUNK_SIZE"
echo "Workers: $WORKERS"

python3 batch_processor.py \
    --mode $MODE \
    --chunk-size $CHUNK_SIZE \
    --workers $WORKERS \
    --log-level INFO \
    --log-file /var/log/cardgenius/batch_$(date +%Y%m%d_%H%M%S).log

if [ $? -eq 0 ]; then
    echo "Batch processing completed successfully"
    exit 0
else
    echo "Batch processing failed"
    exit 1
fi
```

### C. Monitoring Dashboard Query

```sql
-- Real-time processing dashboard
SELECT 
    'Total Users' as metric,
    COUNT(*) as value
FROM user_spending_data

UNION ALL

SELECT 
    'Completed' as metric,
    COUNT(*) as value
FROM user_spending_data
WHERE processing_status = 'completed'

UNION ALL

SELECT 
    'Pending' as metric,
    COUNT(*) as value
FROM user_spending_data
WHERE processing_status IN ('new', 'pending')

UNION ALL

SELECT 
    'Failed' as metric,
    COUNT(*) as value
FROM user_spending_data
WHERE processing_status = 'failed'

UNION ALL

SELECT 
    'Total Recommendations' as metric,
    COUNT(*) as value
FROM card_recommendations

UNION ALL

SELECT 
    'Avg Processing Time (min)' as metric,
    TIMESTAMPDIFF(MINUTE, MIN(processed_at), MAX(processed_at)) as value
FROM card_recommendations
WHERE DATE(processed_at) = CURDATE();
```

---

## 15. Open Questions & Decisions

### For CashKaro Team
1. **Database:** MySQL/PostgreSQL/Other? What version?
2. **Access:** Direct connection or API? VPN required?
3. **Schedule:** Confirm weekly schedule (day/time)
4. **Notifications:** Where to send alerts? (Email/Slack/PagerDuty)
5. **Data Retention:** How long to keep old recommendations?

### For CardGenius Team
6. **Infrastructure:** Where will processing service run?
7. **Deployment:** Docker/Kubernetes/VM?
8. **Monitoring:** Existing monitoring stack to integrate with?
9. **Timeline:** Confirm 7-week timeline is acceptable
10. **Resources:** How many engineers assigned to this project?

---

**Document Status:** Ready for Review  
**Next Steps:**
1. Review with CardGenius tech team
2. Review with CashKaro data team
3. Schedule kickoff meeting
4. Begin Week 1 tasks

**Contact:**
- **Product Owner:** [Your Name]
- **CashKaro Tech Lead:** [Name]
- **CardGenius Tech Lead:** [Name]
- **Data Team Lead:** [Name]



