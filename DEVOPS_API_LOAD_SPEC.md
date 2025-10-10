# DevOps Specification: CardGenius API Load Patterns

**Document Type:** Infrastructure Requirements  
**Audience:** DevOps Team  
**Date:** October 7, 2025  
**Priority:** High

---

## Executive Summary

We're implementing parallel processing for Card Genius recommendations, which will significantly increase the load on the CardGenius API endpoints. This document specifies the expected load patterns and infrastructure requirements.

**Key Numbers:**
- **Current:** 1 request every ~2.7 seconds (0.37 requests/second)
- **With Parallel (20 workers):** Up to **20 simultaneous requests** (burst capacity)
- **Sustained throughput:** ~400-800 requests/minute (~7-13 requests/second)

---

## 1. Current vs. Proposed Architecture

### Current (Sequential) Architecture
```
Our Server
    ↓
One API call at a time
    ↓
CardGenius Load Balancer
    ↓
CardGenius API Server(s)

Load Pattern:
- 1 request every 2.7 seconds
- Peak: 0.37 requests/second
- Very predictable, very low load
```

### Proposed (Parallel) Architecture
```
Our Server
    ↓
20 concurrent API calls simultaneously
    ↓
CardGenius Load Balancer
    ↓
CardGenius API Server(s)

Load Pattern:
- 20 concurrent connections
- Burst: 20 requests at once
- Sustained: 7-13 requests/second
- Duration: Hours (for large batches)
```

---

## 2. Load Specifications

### 2.1 Processing Scenarios

#### Scenario A: Initial 2M Users (One-Time)
```
Total Users: 2,000,000
Workers: 20 (parallel requests)
Time per Request: ~1.5 seconds average

Timeline:
- Chunk size: 10,000 users
- Total chunks: 200 chunks
- Time per chunk: 10,000 ÷ 400 users/min = 25 minutes
- Total time: 200 × 25 min = 5,000 minutes = 83 hours = 3.5 days

Load Pattern:
- Duration: 3-4 days continuous
- Concurrent connections: 20 at all times
- Requests per second: ~13 sustained
- Total API calls: 2,000,000 requests
```

#### Scenario B: Weekly 50K Users (Routine)
```
Total Users: 50,000
Workers: 20 (parallel requests)
Time per Request: ~1.5 seconds average

Timeline:
- Chunk size: 10,000 users (or process all at once)
- Total chunks: 5 chunks
- Time per chunk: 25 minutes
- Total time: 5 × 25 min = 125 minutes = 2 hours

Load Pattern:
- Duration: 2 hours weekly
- Concurrent connections: 20 at all times
- Requests per second: ~13 sustained
- Total API calls: 50,000 requests
- Schedule: Weekly (e.g., Monday 2 AM)
```

#### Scenario C: Test/Development (Daily)
```
Total Users: 100-1,000
Workers: 5-10 (reduced for testing)
Time per Request: ~1.5 seconds average

Load Pattern:
- Duration: Minutes
- Concurrent connections: 5-10
- Requests per second: 3-7
- Total API calls: 100-1,000 requests
```

---

## 3. Detailed API Call Pattern

### 3.1 Request Characteristics

**Endpoint:**
```
POST https://card-recommendation-api-v2.bankkaro.com/cg/api/pro
```

**Request Headers:**
```
Content-Type: application/json
User-Agent: CardGenius-Batch-Runner/1.0
```

**Request Body Size:**
```json
{
  "amazon_spends": 50000,
  "flipkart_spends": 30000,
  "grocery_spends_online": 15000,
  "other_online_spends": 25000,
  // ... 10+ additional fields
}

Typical size: ~500 bytes per request
```

**Response Size:**
```json
{
  "savings": [
    // 10-50 card recommendations
    // Each card: ~2KB of data
  ]
}

Typical size: 20-50 KB per response
```

**Timeout:**
- Connection timeout: 30 seconds
- Request timeout: 30 seconds
- Retry: Up to 3 attempts with exponential backoff

### 3.2 Connection Behavior

**Connection Pooling:**
- We use Python `requests.Session()` with connection pooling
- Reuses TCP connections across requests
- Max connections: 20 (one per worker)

**Keep-Alive:**
- HTTP Keep-Alive enabled by default
- Connections stay open for multiple requests
- Reduces TCP handshake overhead

**TLS/SSL:**
- HTTPS connections (TLS 1.2+)
- Certificates validated
- All 20 workers establish SSL connections simultaneously

---

## 4. Load Balancer Considerations

### 4.1 Expected Behavior

**Connection Distribution:**
```
Our Server (20 workers)
    ↓
CardGenius Load Balancer
    ├──▶ API Server 1 (receives ~7 connections)
    ├──▶ API Server 2 (receives ~7 connections)
    └──▶ API Server 3 (receives ~6 connections)
```

**Assuming:**
- CardGenius has multiple backend servers
- Load balancer uses round-robin or least-connections
- Each backend can handle ~100 concurrent requests

### 4.2 Potential Issues

**Scenario 1: Single Backend Server**
```
If CardGenius only has 1 backend server:
- All 20 connections go to same server
- May cause resource contention
- Could hit rate limits

Mitigation:
- Reduce max_workers to 10
- Add client-side rate limiting
```

**Scenario 2: Sticky Sessions**
```
If load balancer uses sticky sessions (IP-based):
- All 20 connections might go to same backend
- Defeats purpose of load balancing
- One server gets hammered

Mitigation:
- Request load balancer to use round-robin
- Or distribute from multiple source IPs
```

**Scenario 3: Rate Limiting**
```
If load balancer has rate limits:
- May reject requests above threshold
- Could return 429 (Too Many Requests)
- Our retry logic will handle this

Mitigation:
- Coordinate with CardGenius team on limits
- Implement client-side rate limiting
- Add jitter to prevent thundering herd
```

---

## 5. Traffic Patterns

### 5.1 Bandwidth Estimation

#### Outbound (Our requests to CardGenius)
```
Request size: 500 bytes
Requests per second: 13
Bandwidth: 13 × 500 bytes = 6.5 KB/s = 52 Kbps

Peak (burst):
20 simultaneous requests = 20 × 500 bytes = 10 KB = 80 Kbps

Daily (for 2M processing):
2M requests × 500 bytes = 1 GB outbound per day
```

#### Inbound (CardGenius responses to us)
```
Response size: 35 KB average
Requests per second: 13
Bandwidth: 13 × 35 KB = 455 KB/s = 3.6 Mbps

Peak (burst):
20 simultaneous responses = 20 × 35 KB = 700 KB = 5.6 Mbps

Daily (for 2M processing):
2M requests × 35 KB = 70 GB inbound per day
```

**Total bandwidth (both directions):**
- Sustained: ~4 Mbps
- Peak: ~6 Mbps
- Daily: ~71 GB per day during 2M processing

### 5.2 Time-Based Load Distribution

```
Typical Daily Pattern (200K batch):

Hour 00-08: No load (idle)
Hour 08-09: Ramp up (testing, validation)
Hour 09-17: Full load (20 workers, 13 req/s sustained)
Hour 17-18: Ramp down (finishing last users)
Hour 18-24: No load (idle)

Graph:
Req/s
  13 |         ┌──────────────────┐
  10 |      ┌──┘                  └──┐
   7 |   ┌──┘                        └──┐
   4 |┌──┘                              └──┐
   1 |┘                                    └──
     └────────────────────────────────────────▶ Time
      00  04  08  12  16  20  24
```

---

## 6. Infrastructure Requirements

### 6.1 CardGenius API Servers

**Minimum Capacity Needed:**
```
Concurrent requests: 20
Request duration: 1.5 seconds average
Requests per second: 13

If each backend server can handle 100 concurrent requests:
Required: 20 ÷ 100 = 0.2 servers (1 server is sufficient)

If each backend server can handle 50 concurrent requests:
Required: 20 ÷ 50 = 0.4 servers (1 server is sufficient)

Conclusion: Current infrastructure likely sufficient
```

**Resource Usage per Request:**
- CPU: ~50ms of processing time
- Memory: ~10 MB per request
- I/O: Database lookups, card catalog access

**Total Resources (20 concurrent):**
- CPU: Minimal impact (requests are mostly I/O)
- Memory: 20 × 10 MB = 200 MB
- Connections: 20 TCP connections

### 6.2 Load Balancer Configuration

**Recommended Settings:**
```yaml
load_balancer:
  algorithm: round-robin  # Or least_connections
  health_check:
    interval: 30s
    timeout: 10s
    unhealthy_threshold: 3
  
  connection_limits:
    max_connections: 1000  # Total capacity
    per_client_max: 50     # Allow our 20 workers + buffer
  
  timeouts:
    connect: 10s
    request: 60s  # Allow for slower requests
    keepalive: 120s
  
  rate_limiting:
    enabled: true
    requests_per_second: 50  # Per client IP
    burst: 30  # Allow burst of 30 requests
```

### 6.3 Database Load

**CardGenius needs to handle:**
```
Query pattern per API request:
1. Fetch card catalog (~100 cards)
2. Calculate points for each card
3. Sort and return top 10

Database operations:
- Read-heavy (no writes from our requests)
- Card catalog queries (mostly cached)
- Calculation engine (CPU-bound, minimal DB)

Load increase:
- Current: 0.37 queries/second
- New: 13 queries/second (35x increase)

If card catalog is properly cached:
- Minimal database impact
- Mostly CPU for calculations
```

---

## 7. Monitoring Requirements

### 7.1 Metrics to Track

**API Server Metrics:**
```
- Requests per second (should show ~13 sustained)
- Response times (p50, p95, p99)
- Error rates (should be < 1%)
- Concurrent connections (should show ~20)
- CPU usage (monitor for spikes)
- Memory usage (monitor for leaks)
```

**Load Balancer Metrics:**
```
- Connection distribution across backends
- Health check status
- Rate limit triggers
- Timeout errors
- SSL handshake time
```

**Our Client Metrics:**
```
- Throughput (users processed per minute)
- API call success rate
- Retry count
- Average response time
- Queue depth (workers waiting)
```

### 7.2 Alerting Thresholds

**Critical Alerts:**
- Error rate > 5% (triggers immediate investigation)
- API response time > 10 seconds (p95)
- Zero successful requests for 5 minutes
- Connection pool exhausted

**Warning Alerts:**
- Error rate > 1%
- API response time > 5 seconds (p95)
- CPU usage > 80% sustained
- Memory usage > 90%

---

## 8. Rollout Plan

### Phase 1: Testing (Week 1)
```
Configuration:
- max_workers: 5
- Batch size: 100 users
- Duration: 1-2 minutes

Purpose: Validate parallel processing works
Expected load: 5 concurrent, 3 req/s
Risk: Low
```

### Phase 2: Small Production (Week 2)
```
Configuration:
- max_workers: 10
- Batch size: 5,000 users
- Duration: ~12 minutes

Purpose: Test with real load
Expected load: 10 concurrent, 7 req/s
Risk: Low-Medium
```

### Phase 3: Full Scale (Week 3+)
```
Configuration:
- max_workers: 20
- Batch size: 10,000-200,000 users
- Duration: Hours

Purpose: Production use
Expected load: 20 concurrent, 13 req/s
Risk: Medium (coordinate with CardGenius)
```

---

## 9. Failure Scenarios & Mitigation

### 9.1 API Rate Limiting

**Symptom:**
```
HTTP 429 Too Many Requests
X-RateLimit-Remaining: 0
```

**Impact:**
- Some requests fail
- Automatic retry with exponential backoff
- Slower processing overall

**Mitigation:**
1. Reduce `max_workers` from 20 → 10
2. Implement client-side rate limiting
3. Coordinate with CardGenius to increase limits

### 9.2 Server Overload

**Symptom:**
```
HTTP 503 Service Unavailable
Timeouts (30+ seconds)
High error rate (>10%)
```

**Impact:**
- Many requests fail
- Processing stops or very slow

**Mitigation:**
1. Reduce `max_workers` from 20 → 5
2. Add delays between requests
3. Process in smaller batches
4. Coordinate with CardGenius to scale up

### 9.3 Connection Pool Exhaustion

**Symptom:**
```
Connection pool full
Can't acquire connection
Requests queued
```

**Impact:**
- Requests wait longer
- Lower throughput

**Mitigation:**
1. Increase connection pool size
2. Reduce `max_workers`
3. Add connection timeout monitoring

### 9.4 Network Issues

**Symptom:**
```
Connection reset by peer
DNS resolution failures
SSL handshake errors
```

**Impact:**
- Random request failures
- Retry logic kicks in

**Mitigation:**
1. Retry with exponential backoff (already implemented)
2. Check network connectivity
3. Verify DNS resolution
4. Check SSL certificates

---

## 10. Configuration Options

### 10.1 Adjusting Parallelism

**File:** `real_config.json`

**Conservative (Safe):**
```json
{
  "processing": {
    "max_workers": 5
  }
}

Load: 5 concurrent, 3 req/s
Time for 200K: ~1,111 minutes = 18.5 hours
```

**Moderate (Recommended):**
```json
{
  "processing": {
    "max_workers": 10
  }
}

Load: 10 concurrent, 7 req/s
Time for 200K: ~555 minutes = 9.25 hours
```

**Aggressive (Maximum):**
```json
{
  "processing": {
    "max_workers": 20
  }
}

Load: 20 concurrent, 13 req/s
Time for 200K: ~277 minutes = 4.6 hours
```

**Ultra-Aggressive (Not Recommended):**
```json
{
  "processing": {
    "max_workers": 50
  }
}

Load: 50 concurrent, 33 req/s
Time for 200K: ~111 minutes = 1.85 hours
Risk: Very likely to hit rate limits or overload
```

### 10.2 Rate Limiting

**Currently:** No client-side rate limiting (relies on CardGenius)

**If needed, add:**
```json
{
  "api": {
    "rate_limit": {
      "enabled": true,
      "requests_per_second": 10,
      "burst": 20
    }
  }
}
```

This would cap our requests to 10/second even with 20 workers.

---

## 11. Communication Plan

### 11.1 Notification to CardGenius Team

**When:** 48 hours before first large batch (2M users)

**Message Template:**
```
Subject: High-Volume API Usage Notification - CardGenius Recommendations

Hi CardGenius Team,

We're implementing parallel processing for card recommendations and will be 
making significantly more API calls to your endpoints.

Expected Load:
- Endpoint: https://card-recommendation-api-v2.bankkaro.com/cg/api/pro
- Concurrent connections: 20
- Requests per second: ~13 sustained
- Duration: 3-4 days continuous (for 2M user backfill)
- Total requests: 2,000,000

Timeline:
- Testing: [Date] - 100 users (5 workers, low load)
- Small batch: [Date] - 5K users (10 workers, medium load)
- Full batch: [Date] - 2M users (20 workers, full load)

Questions:
1. Are there any rate limits we should be aware of?
2. Should we use a specific User-Agent header?
3. Do you need us to come from specific IP addresses?
4. Is your load balancer configured for this load?
5. Should we schedule this during off-peak hours?

Please let us know if you have any concerns or need us to adjust our approach.

Best regards,
CashKaro Team
```

### 11.2 Internal Stakeholders

**Notify:**
- DevOps team (this document)
- Product team (timeline impact)
- Data team (when results will be ready)

---

## 12. Checklist for DevOps

### Pre-Launch
- [ ] Review this document with team
- [ ] Coordinate with CardGenius team
- [ ] Verify network connectivity
- [ ] Test with 100 users (5 workers)
- [ ] Monitor for 30 minutes
- [ ] Check for errors or warnings

### Launch Day
- [ ] Start with 5K users (10 workers)
- [ ] Monitor load balancer metrics
- [ ] Monitor API response times
- [ ] Check error rates (should be < 1%)
- [ ] If all good, proceed to full scale

### During Processing
- [ ] Monitor every hour
- [ ] Check progress logs
- [ ] Watch for error spikes
- [ ] Monitor CardGenius API health
- [ ] Be ready to reduce workers if needed

### Post-Processing
- [ ] Verify all users processed
- [ ] Check error rate summary
- [ ] Review performance metrics
- [ ] Document any issues
- [ ] Optimize for next run

---

## 13. Questions & Answers

**Q: Will this break the CardGenius API?**  
A: Very unlikely. 20 concurrent requests is modest for a production API with load balancer. However, we'll coordinate with their team first.

**Q: What if we hit rate limits?**  
A: Our retry logic handles this automatically. We can also reduce `max_workers` if needed.

**Q: Can we make it even faster?**  
A: Yes, we could increase `max_workers` to 50-100, but this requires CardGenius approval and may hit limits.

**Q: What if CardGenius API goes down?**  
A: Processing stops, our retry logic kicks in. We can resume from where we left off using checkpoints (not yet implemented, but easy to add).

**Q: How do we test this safely?**  
A: Start with 5 workers and 100 users. Monitor closely. Gradually increase.

---

**Document Prepared By:** Product Team  
**Technical Review:** DevOps Team  
**Approval Required:** CardGenius Team (for large batches)

**Status:** Ready for Review  
**Last Updated:** October 7, 2025



