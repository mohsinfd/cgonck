# Product Requirements Document (PRD)
## CardGenius Batch Recommendations API - Performance Optimization

**Document Version:** 1.0  
**Date:** October 7, 2025  
**Owner:** Product Team  
**Stakeholders:** Tech Team, Data Team, Product Management

---

## 1. Executive Summary

### Problem Statement
The current CardGenius Batch Recommendations API processes 200 users in **5+ minutes** (timeout), which is **unacceptable for production use** by the data team. The bottleneck is sequential external API calls to the CardGenius recommendation engine.

### Current State
- ❌ **Throughput:** 22 users/min
- ❌ **Time for 200 users:** 300+ seconds (timeout)
- ❌ **Production ready:** No

### Target State
- ✅ **Throughput:** 100+ users/min (minimum)
- ✅ **Time for 200 users:** < 2 minutes
- ✅ **Production ready:** Yes

### Business Impact
- **Data Team blocked:** Cannot process daily batches of 200-500 users
- **Operational efficiency:** Manual workarounds required
- **Scalability:** System won't support growth beyond 50 users/batch

---

## 2. Background & Context

### System Architecture Overview

```
┌─────────────┐         ┌──────────────┐         ┌────────────────┐
│   Data Team │────────▶│  Our FastAPI │────────▶│   CardGenius   │
│  (Client)   │  Batch  │    Server    │ 1-by-1  │  External API  │
└─────────────┘         └──────────────┘         └────────────────┘
                              │
                              ├─ Background Job Queue
                              ├─ Excel Processing
                              └─ Result Aggregation
```

### Current Implementation
1. Data team uploads Excel file with 200+ users
2. Our API creates background job
3. **For each user sequentially:**
   - Read user spending data
   - Call CardGenius external API (~1.5s per call)
   - Parse and store results
4. Aggregate results and return

**Time Complexity:** O(n) where n = number of users  
**Bottleneck:** External API calls are sequential, not parallelized

### Business Use Case
- **Frequency:** Daily batches
- **Typical batch size:** 200-500 users
- **Use case:** Generate personalized credit card recommendations for CashKaro users
- **SLA expectation:** < 2 minutes for 200 users

---

## 3. Requirements

### 3.1 Functional Requirements

#### FR-1: Performance Optimization
**Priority:** P0 (Critical)

**Requirement:** The API must process 200 users in < 2 minutes (120 seconds)

**Acceptance Criteria:**
- [ ] 200 users processed in < 120 seconds (average)
- [ ] Throughput: minimum 100 users/min
- [ ] 95th percentile: < 150 seconds for 200 users
- [ ] No timeout errors for batches up to 500 users

#### FR-2: Maintain Existing Functionality
**Priority:** P0 (Critical)

**Requirement:** All existing API features must continue to work

**Acceptance Criteria:**
- [ ] Background job queue functioning
- [ ] Status monitoring endpoint working
- [ ] Results retrieval endpoint working
- [ ] Excel file processing working
- [ ] Authentication/API key validation working
- [ ] Error handling for failed users working

#### FR-3: Data Integrity
**Priority:** P0 (Critical)

**Requirement:** Optimization must not compromise data quality

**Acceptance Criteria:**
- [ ] All users processed successfully
- [ ] Recommendation quality unchanged
- [ ] Net savings calculations correct
- [ ] Card ranking order correct (by net_savings)
- [ ] No data loss or corruption

### 3.2 Non-Functional Requirements

#### NFR-1: Reliability
- **Error rate:** < 1% for individual user processing
- **Job completion rate:** > 99%
- **Retry logic:** Automatic retry for failed API calls (max 3 attempts)

#### NFR-2: Scalability
- **Concurrent jobs:** Support 3-5 simultaneous batch jobs
- **Max batch size:** 500 users per job
- **Resource limits:** Stay within Render free tier limits

#### NFR-3: Monitoring
- **Progress tracking:** Real-time progress updates (processed/total)
- **Logging:** Detailed logs for debugging
- **Metrics:** Track throughput, error rates, processing time

---

## 4. Technical Approaches

### 4.1 Approach A: Parallel External API Calls (RECOMMENDED)

#### Overview
Implement concurrent API calls to CardGenius using Python's ThreadPoolExecutor.

#### Technical Design

```python
# Current: Sequential (SLOW)
def process_batch(users):
    results = []
    for user in users:  # Sequential loop
        result = call_cardgenius_api(user)  # ~1.5s each
        results.append(result)
    return results
# Time: 200 × 1.5s = 300 seconds ❌

# Proposed: Parallel (FAST)
from concurrent.futures import ThreadPoolExecutor

def process_batch(users):
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(call_cardgenius_api, users))
    return results
# Time: (200 / 20) × 1.5s = 15 seconds ✅
```

#### Implementation Details

**File:** `cardgenius_batch_runner.py`

**Changes Required:**
1. Import `ThreadPoolExecutor` from `concurrent.futures`
2. Modify `process_all_users()` method to use parallel processing
3. Add configuration for `max_workers` (default: 20)
4. Implement rate limiting to respect CardGenius API limits
5. Add retry logic with exponential backoff for failed requests

**Configuration Parameters:**
```python
{
    "parallel_processing": {
        "enabled": true,
        "max_workers": 20,  # Concurrent API calls
        "rate_limit": {
            "max_requests_per_second": 10,
            "burst_size": 20
        },
        "retry": {
            "max_attempts": 3,
            "backoff_multiplier": 2,
            "initial_delay": 1
        }
    }
}
```

#### Pros
- ✅ **Massive speed improvement:** 15-20x faster
- ✅ **Simple to implement:** ~100 lines of code
- ✅ **No external dependencies:** Uses standard library
- ✅ **Maintains existing architecture:** No breaking changes
- ✅ **Quick turnaround:** 2-4 hours implementation

#### Cons
- ⚠️ **Depends on CardGenius API rate limits:** Need to verify limits
- ⚠️ **Increased load on external API:** May hit rate limits
- ⚠️ **Resource usage:** Higher memory/CPU during processing

#### Risk Mitigation
- **Rate limiting:** Implement token bucket algorithm
- **Monitoring:** Track CardGenius API response times and errors
- **Graceful degradation:** Fall back to sequential if errors spike
- **Testing:** Load test with CardGenius team coordination

---

### 4.2 Approach B: Server-Side Recommendation Logic (ALTERNATIVE)

#### Overview
**This is what your tech team is suggesting:** Implement card recommendation logic directly in our server, eliminating the need for external CardGenius API calls.

#### Technical Design

```python
# Current: External API Call
def get_recommendations(user_data):
    response = requests.post(
        "https://card-recommendation-api-v2.bankkaro.com/cg/api/pro",
        json=user_data
    )
    return response.json()  # ~1.5s per call

# Proposed: Server-Side Logic
def get_recommendations(user_data):
    # Step 1: Get all available cards from database/config
    all_cards = load_card_catalog()  # 50-100 cards
    
    # Step 2: Calculate savings for each card
    recommendations = []
    for card in all_cards:
        savings = calculate_card_savings(user_data, card)
        recommendations.append({
            'card_name': card.name,
            'net_savings': savings.net,
            'total_savings_yearly': savings.yearly,
            'joining_fees': card.joining_fees,
            # ... other fields
        })
    
    # Step 3: Sort by net_savings and return top 10
    recommendations.sort(key=lambda x: x['net_savings'], reverse=True)
    return recommendations[:10]
# Time: < 0.1s per user (no network calls) ✅
```

#### Implementation Details

**New Components Required:**

1. **Card Catalog Database**
   - All credit cards with their properties
   - Reward rates, fees, benefits, caps
   - Update frequency: Weekly/monthly

2. **Calculation Engine**
   - Points calculation per category (Amazon, Flipkart, etc.)
   - Redemption value calculation (vouchers, cashback)
   - Net savings formula: `total_savings - joining_fees + extra_benefits`
   - ROI calculation

3. **Business Rules Engine**
   - Card eligibility rules
   - Spending category mappings
   - Special offers and milestones
   - Seasonal promotions

**File Structure:**
```
card_recommendation_engine/
├── card_catalog.py          # Card data management
├── calculation_engine.py    # Core calculation logic
├── business_rules.py        # Card-specific rules
├── redemption_calculator.py # Points-to-value conversion
├── config/
│   ├── cards.json          # All card definitions
│   ├── reward_rates.json   # Category-wise reward rates
│   └── rules.json          # Business rules
└── tests/
    └── test_calculations.py
```

#### Algorithm Flow

```
For each user:
    1. Parse spending data (Amazon, Flipkart, Myntra, etc.)
    2. For each card in catalog:
        a. Check eligibility rules
        b. Calculate category-wise points:
           - Amazon points = amazon_spend × card.amazon_rate
           - Flipkart points = flipkart_spend × card.flipkart_rate
           - (repeat for all categories)
        c. Calculate redemption value:
           - Find best redemption method (vouchers/cashback)
           - Convert points to rupees
        d. Calculate net savings:
           - total_savings - joining_fees + extra_benefits
        e. Store result
    3. Sort all cards by net_savings (descending)
    4. Return top 10 cards

Time complexity: O(U × C) where U=users, C=cards
With U=200, C=100: ~20,000 iterations
Processing time: < 5 seconds for 200 users ✅
```

#### Example: Card Calculation Logic

```python
class Card:
    def __init__(self, name, joining_fees, reward_rates, caps, benefits):
        self.name = name
        self.joining_fees = joining_fees
        self.reward_rates = reward_rates  # Dict: category -> rate
        self.caps = caps  # Dict: category -> max_points
        self.benefits = benefits  # Annual benefits value
        
    def calculate_savings(self, user_spending):
        total_points = 0
        
        # Calculate category-wise points
        for category, spend in user_spending.items():
            rate = self.reward_rates.get(category, 0)
            points = spend * rate
            
            # Apply caps if exists
            if category in self.caps:
                points = min(points, self.caps[category])
            
            total_points += points
        
        # Convert points to rupees (best redemption method)
        redemption_value = self.get_best_redemption_value(total_points)
        
        # Calculate net savings
        net_savings = (
            redemption_value 
            - self.joining_fees 
            + self.benefits
        )
        
        return {
            'card_name': self.name,
            'total_points': total_points,
            'total_savings_yearly': redemption_value,
            'joining_fees': self.joining_fees,
            'total_extra_benefits': self.benefits,
            'net_savings': net_savings
        }

# Example usage
user_spending = {
    'amazon': 50000,
    'flipkart': 30000,
    'myntra': 10000,
    'grocery': 15000
}

card = Card(
    name='ICICI Amazon Pay',
    joining_fees=500,
    reward_rates={
        'amazon': 0.05,      # 5% on Amazon
        'other_online': 0.01 # 1% on others
    },
    caps={'amazon': 5000},   # Max 5000 points on Amazon
    benefits=1000            # Annual benefits
)

result = card.calculate_savings(user_spending)
# Output: {
#   'card_name': 'ICICI Amazon Pay',
#   'net_savings': 3500,  # Based on calculations
#   ...
# }
```

#### Data Requirements

**Card Catalog Structure:**
```json
{
  "cards": [
    {
      "card_id": "icici_amazon_pay",
      "card_name": "ICICI Amazon Pay Credit Card",
      "issuer": "ICICI Bank",
      "joining_fees": 500,
      "annual_fees": 500,
      "reward_rates": {
        "amazon": {
          "base_rate": 0.05,
          "multiplier": 1,
          "point_value": 1,
          "cap_monthly": 5000,
          "cap_yearly": 60000
        },
        "flipkart": {
          "base_rate": 0.01,
          "multiplier": 1,
          "point_value": 1
        },
        "other_online": {
          "base_rate": 0.01,
          "multiplier": 1,
          "point_value": 1
        }
      },
      "redemption_options": [
        {
          "method": "Vouchers",
          "conversion_rate": 1.0,
          "min_points": 100,
          "opt_type": "Vouchers"
        },
        {
          "method": "Cashback",
          "conversion_rate": 0.9,
          "min_points": 500,
          "opt_type": "Cashback"
        }
      ],
      "extra_benefits": {
        "annual_value": 1000,
        "description": "Amazon Prime membership"
      },
      "eligibility": {
        "min_monthly_income": 25000,
        "min_credit_score": 750
      }
    }
  ]
}
```

#### Pros
- ✅ **Ultra-fast:** < 5 seconds for 200 users (60x faster)
- ✅ **No external dependencies:** Complete control
- ✅ **No rate limits:** Process unlimited users
- ✅ **Offline capability:** Works without internet
- ✅ **Cost savings:** No external API costs
- ✅ **Customization:** Full control over recommendation logic

#### Cons
- ❌ **High implementation effort:** 2-3 weeks development
- ❌ **Maintenance burden:** Need to maintain card catalog
- ❌ **Data accuracy:** Must sync with CardGenius regularly
- ❌ **Business logic complexity:** Need to replicate all CardGenius rules
- ❌ **Testing overhead:** Extensive testing required
- ❌ **Feature parity risk:** May miss CardGenius features

#### Risk Mitigation
- **Data sync:** Automated weekly sync with CardGenius
- **Validation:** Compare results with CardGenius for sample users
- **Monitoring:** Alert on significant deviations from CardGenius
- **Rollback plan:** Keep external API fallback option
- **Documentation:** Comprehensive business rules documentation

---

## 5. Comparison: Approach A vs Approach B

| Criteria | Approach A (Parallel API) | Approach B (Server-Side Logic) |
|----------|---------------------------|--------------------------------|
| **Speed** | 15-30s for 200 users | < 5s for 200 users |
| **Implementation Time** | 2-4 hours | 2-3 weeks |
| **Complexity** | Low | High |
| **Maintenance** | Low | High |
| **Risk** | Low | Medium-High |
| **Data Accuracy** | 100% (uses CardGenius) | 95-99% (needs validation) |
| **Cost** | Low (existing API) | Medium (dev time + maintenance) |
| **Scalability** | Limited by API rate limits | Unlimited |
| **Flexibility** | Depends on CardGenius | Full control |
| **Feature Updates** | Automatic (CardGenius) | Manual (need to sync) |

---

## 6. Recommended Approach

### Phase 1 (Immediate): Approach A - Parallel Processing
**Timeline:** 1 week  
**Rationale:**
- Solves immediate production blocker
- Low risk, quick implementation
- Maintains data accuracy and feature parity
- Buys time to evaluate Approach B properly

**Deliverables:**
- [ ] Parallel processing implementation
- [ ] Rate limiting and retry logic
- [ ] Performance testing with 200+ users
- [ ] Production deployment
- [ ] Monitoring and alerting

### Phase 2 (Future): Evaluate Approach B
**Timeline:** 1-2 months  
**Rationale:**
- Need more data on CardGenius API reliability
- Requires buy-in from CardGenius team
- Needs thorough cost-benefit analysis
- Can run in parallel as POC

**Deliverables:**
- [ ] Card catalog data collection
- [ ] POC implementation (20% of cards)
- [ ] Accuracy validation study
- [ ] Cost-benefit analysis
- [ ] Go/no-go decision

---

## 7. Implementation Plan (Phase 1)

### Week 1: Parallel Processing Implementation

#### Day 1-2: Development
- [ ] Implement ThreadPoolExecutor in `cardgenius_batch_runner.py`
- [ ] Add configuration for max_workers
- [ ] Implement basic rate limiting
- [ ] Add retry logic with exponential backoff
- [ ] Update logging for parallel execution

#### Day 3-4: Testing
- [ ] Unit tests for parallel processing logic
- [ ] Integration tests with CardGenius API
- [ ] Load testing with 10, 50, 100, 200, 500 users
- [ ] Verify data integrity across all test cases
- [ ] Performance benchmarking and profiling

#### Day 5: Deployment & Monitoring
- [ ] Deploy to staging environment
- [ ] Run production-like tests
- [ ] Deploy to production (Render)
- [ ] Monitor performance metrics
- [ ] Document configuration and usage

### Success Metrics
- **Primary:** 200 users processed in < 120 seconds
- **Secondary:** Error rate < 1%, throughput > 100 users/min
- **Monitoring:** Real-time dashboards for job status

---

## 8. Technical Specifications

### 8.1 API Endpoints (No Changes)

All existing endpoints remain unchanged:

- **POST /api/v1/recommendations** - Submit batch job
- **GET /api/v1/status/{job_id}** - Check job status
- **GET /api/v1/results/{job_id}** - Get results
- **GET /api/v1/jobs** - List all jobs
- **DELETE /api/v1/jobs/{job_id}** - Cancel job

### 8.2 Configuration

**New configuration in `real_config.json`:**

```json
{
  "processing": {
    "parallel": {
      "enabled": true,
      "max_workers": 20,
      "chunk_size": 50
    },
    "rate_limiting": {
      "enabled": true,
      "requests_per_second": 10,
      "burst_size": 20
    },
    "retry": {
      "enabled": true,
      "max_attempts": 3,
      "backoff_multiplier": 2,
      "initial_delay_seconds": 1
    }
  }
}
```

### 8.3 Monitoring & Logging

**New metrics to track:**
- `batch_processing_time_seconds` - Total time per batch
- `user_processing_time_seconds` - Time per user (avg, p95, p99)
- `api_call_success_rate` - Success rate for CardGenius API
- `api_call_retry_count` - Number of retries triggered
- `concurrent_workers_active` - Active parallel workers

**Enhanced logging:**
```
2025-10-07 10:30:15 - INFO - Starting parallel batch processing: 200 users, 20 workers
2025-10-07 10:30:16 - INFO - Worker pool initialized: 20 workers
2025-10-07 10:30:17 - INFO - Progress: 20/200 users (10%) - 5s elapsed
2025-10-07 10:30:22 - INFO - Progress: 100/200 users (50%) - 10s elapsed
2025-10-07 10:30:27 - INFO - Progress: 200/200 users (100%) - 15s elapsed
2025-10-07 10:30:28 - INFO - Batch completed: 200 users in 15.2s (789 users/min)
```

---

## 9. Open Questions & Decisions Required

### Q1: CardGenius API Rate Limits
**Question:** What are the rate limits for CardGenius API?  
**Impact:** Determines max_workers configuration  
**Owner:** Tech Team  
**Deadline:** Before implementation starts

**Action:** Contact CardGenius team to confirm:
- Requests per second limit
- Concurrent connections limit
- Throttling behavior
- Recommended best practices

### Q2: Error Handling Strategy
**Question:** How should we handle partial batch failures?  
**Options:**
- A) Return partial results (successful users only)
- B) Fail entire batch if any user fails
- C) Retry failed users and return combined results

**Recommendation:** Option C (most robust)  
**Owner:** Product Team  
**Deadline:** Before development starts

### Q3: Cost Analysis
**Question:** Will parallel processing increase CardGenius API costs?  
**Impact:** Budget approval may be required  
**Owner:** Finance/Product Team  
**Deadline:** Before production deployment

---

## 10. Success Criteria

### Launch Criteria (Must Have)
- [ ] 200 users processed in < 120 seconds (95th percentile)
- [ ] Error rate < 1% for individual users
- [ ] 100% feature parity with current implementation
- [ ] Zero data quality regressions
- [ ] Monitoring and alerting in place
- [ ] Documentation complete

### Success Metrics (30 days post-launch)
- [ ] Data team using API for daily batches
- [ ] Average batch size: 200-500 users
- [ ] Average processing time: < 60 seconds for 200 users
- [ ] 99%+ job completion rate
- [ ] Zero production incidents
- [ ] < 5 support tickets related to performance

---

## 11. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| CardGenius rate limiting | High | Medium | Implement rate limiting, contact CardGenius |
| Increased error rates | Medium | Low | Robust retry logic, monitoring |
| Memory/CPU exhaustion | Medium | Low | Resource monitoring, worker limits |
| Data quality issues | High | Very Low | Extensive testing, validation |
| Production downtime | High | Very Low | Staged rollout, rollback plan |

---

## 12. Appendix

### A. Test Results Summary

**Current Performance (Sequential):**
- 10 users: 26.81 seconds (22.4 users/min)
- 200 users: 300+ seconds timeout

**Expected Performance (Parallel, 20 workers):**
- 10 users: ~2-3 seconds (200+ users/min)
- 200 users: ~15-30 seconds (400-800 users/min)

### B. References
- CardGenius API Documentation
- Real-World Test Report (`REAL_WORLD_TEST_REPORT.md`)
- Performance Test Results
- Current Implementation (`cardgenius_batch_runner.py`)

### C. Contact Information
- **Product Owner:** [Your Name]
- **Tech Lead:** [Tech Team Lead]
- **Data Team Lead:** [Data Team Lead]
- **CardGenius POC:** [External Contact]

---

**Document Status:** Draft for Review  
**Next Review Date:** [Insert Date]  
**Approval Required From:** Tech Lead, Product Manager



