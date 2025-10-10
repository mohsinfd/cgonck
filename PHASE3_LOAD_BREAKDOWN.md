# Phase 3: Production Load - Minute-by-Minute Breakdown

**Configuration:** 20 parallel workers  
**Batch Size:** 200,000 users  
**Target API:** https://card-recommendation-api-v2.bankkaro.com/cg/api/pro

---

## Exact Load Per Second

### Best Case Scenario (API responds in 1.0s)

```
Every Second:
├─ Active requests: 20 (all workers busy)
├─ Requests completing: 20 requests/second
├─ New requests starting: 20 requests/second
└─ Throughput: 1,200 users/minute (20 × 60)

Network Traffic:
├─ Outbound: 20 requests × 500 bytes = 10 KB/s
├─ Inbound: 20 responses × 35 KB = 700 KB/s
└─ Total: 710 KB/s = 5.7 Mbps
```

**Timeline for 200K users:**
- 200,000 ÷ 1,200 = 167 minutes = **2.8 hours**

---

### Typical Case (API responds in 1.5s average)

```
Every Second:
├─ Active requests: 20 (all workers busy)
├─ Requests completing: 13-14 requests/second
├─ New requests starting: 13-14 requests/second
└─ Throughput: 800 users/minute (~13.3 × 60)

Network Traffic:
├─ Outbound: 13 requests × 500 bytes = 6.5 KB/s
├─ Inbound: 13 responses × 35 KB = 455 KB/s
└─ Total: 461.5 KB/s = 3.7 Mbps
```

**Timeline for 200K users:**
- 200,000 ÷ 800 = 250 minutes = **4.2 hours**

---

### Worst Case Scenario (API responds in 3.0s)

```
Every Second:
├─ Active requests: 20 (all workers busy)
├─ Requests completing: 6-7 requests/second
├─ New requests starting: 6-7 requests/second
└─ Throughput: 400 users/minute (~6.7 × 60)

Network Traffic:
├─ Outbound: 7 requests × 500 bytes = 3.5 KB/s
├─ Inbound: 7 responses × 35 KB = 245 KB/s
└─ Total: 248.5 KB/s = 2.0 Mbps
```

**Timeline for 200K users:**
- 200,000 ÷ 400 = 500 minutes = **8.3 hours**

---

## Minute-by-Minute Load Pattern

### First 10 Minutes (Ramp-Up)

```
Minute 0-1: Startup and initialization
- Requests: 0 → 20 (ramping up)
- Load: 0 → 13 req/s
- Users processed: ~40

Minute 1-2: Stabilization
- Requests: 20 concurrent (stable)
- Load: 13 req/s sustained
- Users processed: 800

Minute 2-10: Steady State
- Requests: 20 concurrent (stable)
- Load: 13 req/s sustained
- Users processed: 800/minute
- Total by minute 10: ~6,400 users
```

### Steady State (Bulk Processing)

```
Every Minute (Minute 10 - 250):
├─ Concurrent requests: 20 at all times
├─ Requests per second: 13 (average)
├─ Requests per minute: 13 × 60 = 780 requests
├─ Users processed: 800 users
└─ Progress: +0.4% completion per minute

Network Traffic Per Minute:
├─ Outbound: 6.5 KB/s × 60 = 390 KB/min
├─ Inbound: 455 KB/s × 60 = 27.3 MB/min
└─ Total: ~27.7 MB/minute
```

### Last 10 Minutes (Wind-Down)

```
Minute 240-245: Steady state continues
- Requests: 20 concurrent
- Load: 13 req/s sustained
- Remaining users: ~4,000

Minute 245-250: Final users
- Requests: 20 → 10 → 5 (declining)
- Load: 13 → 7 → 3 req/s
- Remaining users: 4,000 → 2,000 → 0

Minute 250: Completion
- All requests finished
- Final data processing and saving
- Users processed: 200,000 ✓
```

---

## Detailed Every-Second Breakdown (Sample 1 Minute)

Let's zoom into **Minute 100** (middle of processing):

```
Second 00: 13 requests complete, 13 new requests start
           20 workers busy | 13 req/s | 800/200,000 users complete
           
Second 01: 13 requests complete, 13 new requests start
           20 workers busy | 13 req/s | 813/200,000 users complete
           
Second 02: 14 requests complete, 14 new requests start
           20 workers busy | 14 req/s | 827/200,000 users complete
           
Second 03: 13 requests complete, 13 new requests start
           20 workers busy | 13 req/s | 840/200,000 users complete

... (pattern repeats)

Second 58: 13 requests complete, 13 new requests start
           20 workers busy | 13 req/s | 1,587/200,000 users complete
           
Second 59: 13 requests complete, 13 new requests start
           20 workers busy | 13 req/s | 1,600/200,000 users complete

End of Minute 100:
- Total requests this minute: 800
- Average requests per second: 13.3
- Total users processed so far: 80,000 (40% complete)
- Estimated time remaining: 150 minutes
```

---

## Load Balancer View

### What CardGenius Load Balancer Sees

**Every Second:**
```
Incoming Connections:
├─ Source IP: [Your server IP]
├─ Active connections: 20 concurrent
├─ New connections: 0 (connections reused via Keep-Alive)
├─ Requests on existing connections: ~13/second
└─ Distribution across backends: ~7 req/s per backend (if 3 backends)

Connection Pattern:
00:00 → 20 connections established (HTTP Keep-Alive)
00:01 → 13 POST requests arrive
00:02 → 13 POST requests arrive
00:03 → 14 POST requests arrive
...
04:00 → Connections still alive, 13 requests arrive
04:01 → Connections still alive, 13 requests arrive
...
(Pattern continues for 4+ hours)
```

**Every Minute:**
```
Load Balancer Metrics:
├─ Connections from client: 20 (stable)
├─ Requests routed: ~780/minute
├─ Data received: 390 KB
├─ Data sent: 27.3 MB
├─ Backend distribution:
│   ├─ Server 1: ~260 requests (33%)
│   ├─ Server 2: ~260 requests (33%)
│   └─ Server 3: ~260 requests (34%)
└─ Health: All backends healthy
```

---

## Detailed Request Flow (Every Second)

### Timeline of Events in 1 Second

```
Time 0.000s: Start of second
├─ Worker 1: Request completes, starts new request
├─ Worker 2: Request in progress (0.5s remaining)
├─ Worker 3: Request completes, starts new request
├─ Worker 4: Request in progress (0.8s remaining)
├─ ...
└─ Worker 20: Request completes, starts new request

Time 0.100s:
├─ 2 more requests complete
├─ 2 new requests start
├─ Current active: 20 workers busy

Time 0.500s:
├─ 3 more requests complete
├─ 3 new requests start
├─ Current active: 20 workers busy

Time 1.000s: End of second
├─ Total completed this second: 13 requests
├─ Total started this second: 13 requests
├─ Current active: 20 workers busy
└─ Ready for next second
```

---

## Network Packet Analysis

### Every Second - Packet-Level View

**Outbound (Your server → CardGenius):**
```
13 HTTP POST requests per second
├─ Each request:
│   ├─ TCP SYN (if new): 0 bytes (reusing connections)
│   ├─ HTTP headers: ~200 bytes
│   ├─ JSON payload: ~500 bytes
│   └─ Total: ~700 bytes
└─ Per second: 13 × 700 bytes = 9.1 KB/s
```

**Inbound (CardGenius → Your server):**
```
13 HTTP responses per second
├─ Each response:
│   ├─ HTTP headers: ~300 bytes
│   ├─ JSON payload: ~35,000 bytes
│   └─ Total: ~35,300 bytes
└─ Per second: 13 × 35.3 KB = 459 KB/s
```

**Total Bandwidth Every Second:**
```
Outbound: 9.1 KB/s = 73 Kbps
Inbound: 459 KB/s = 3.7 Mbps
Total: 468 KB/s = 3.77 Mbps
```

---

## Connection Distribution

### How 20 Workers Map to Backend Servers

**Assuming CardGenius has 3 backend servers:**

```
Load Balancer (Round-Robin)
├─ Backend Server 1:
│   ├─ Connections: 7 (from our 20 workers)
│   ├─ Requests/second: ~4.3
│   └─ Load: 33% of total
│
├─ Backend Server 2:
│   ├─ Connections: 7 (from our 20 workers)
│   ├─ Requests/second: ~4.3
│   └─ Load: 33% of total
│
└─ Backend Server 3:
    ├─ Connections: 6 (from our 20 workers)
    ├─ Requests/second: ~4.4
    └─ Load: 34% of total
```

**Per Backend Server Every Second:**
```
Concurrent requests: ~6-7
Requests completing: ~4-5 per second
CPU usage: ~20-30% (estimation)
Memory: ~70-100 MB
Response time: 1.5s average
```

---

## Hourly Breakdown

### Hour-by-Hour for Full 200K Batch

**Hour 1:**
```
Time: 00:00 - 01:00
├─ Users processed: 48,000 (24%)
├─ Requests sent: 46,800
├─ Data transfer: 1.63 GB inbound, 23 MB outbound
├─ Current load: 13 req/s sustained
└─ Status: Steady state, no issues
```

**Hour 2:**
```
Time: 01:00 - 02:00
├─ Users processed: 96,000 total (48%)
├─ Requests sent: 93,600 total
├─ Data transfer: 3.26 GB inbound, 46 MB outbound
├─ Current load: 13 req/s sustained
└─ Status: Steady state, no issues
```

**Hour 3:**
```
Time: 02:00 - 03:00
├─ Users processed: 144,000 total (72%)
├─ Requests sent: 140,400 total
├─ Data transfer: 4.89 GB inbound, 69 MB outbound
├─ Current load: 13 req/s sustained
└─ Status: Steady state, no issues
```

**Hour 4:**
```
Time: 03:00 - 04:00
├─ Users processed: 192,000 total (96%)
├─ Requests sent: 187,200 total
├─ Data transfer: 6.52 GB inbound, 92 MB outbound
├─ Current load: 13 req/s sustained
└─ Status: Steady state, no issues
```

**Hour 5 (Partial):**
```
Time: 04:00 - 04:10
├─ Users processed: 200,000 total (100%) ✓
├─ Requests sent: 200,000 total
├─ Data transfer: 6.93 GB inbound, 97 MB outbound
├─ Current load: 13 → 0 req/s (wind down)
└─ Status: COMPLETE
```

---

## Peak vs Sustained Load

### Burst Load (Initial 5 seconds)

```
Second 1: Ramp up
├─ Workers starting: 5
├─ Concurrent requests: 5
└─ Load: 5 req/s

Second 2: More ramp up
├─ Workers starting: 10
├─ Concurrent requests: 10
└─ Load: 10 req/s

Second 3: Near full
├─ Workers starting: 15
├─ Concurrent requests: 15
└─ Load: 15 req/s

Second 4: Full load reached
├─ Workers running: 20
├─ Concurrent requests: 20
└─ Load: 20 req/s (burst)

Second 5+: Sustained
├─ Workers running: 20
├─ Concurrent requests: 20
└─ Load: 13 req/s (sustained)
```

### Why Sustained < Burst?

```
Burst Capacity: 20 workers × 1 req/worker = 20 req/s theoretical
Sustained Reality: 20 workers ÷ 1.5s per request = 13.3 req/s actual

The difference:
- Workers don't complete at exactly the same instant
- Some requests take longer than average
- Network latency varies
- Processing time varies per user
- Result: "Bursty" pattern averaging to 13 req/s
```

---

## Load Pattern Visualization

### Requests Per Second Over Time

```
Req/s
  20 |     ┌─┐
  15 |   ┌─┘ └─────────────────────────────────────────┐
  13 | ──┴──────────────────────────────────────────────┴──
  10 | 
   5 | ┌─┘                                              └─┐
   0 |─┘                                                  └─
     └───────────────────────────────────────────────────▶
     0s  5s  10s            ...            4h 10m    4h 15m
         
     Startup  Steady State (13 req/s sustained)  Shutdown
```

### Bandwidth Usage Over Time

```
Mbps
  6 |
  4 |   ┌──────────────────────────────────────────┐
  3.7|───┴──────────────────────────────────────────┴───
  2 |
  0 |───┘                                            └───
    └───────────────────────────────────────────────────▶
    0m  5m  10m            ...            4h 10m    4h 15m
```

---

## What DevOps Should Monitor

### Every Minute Checklist

```
✓ Active connections: Should stay at 20
✓ Requests per second: Should average ~13
✓ Response time: Should stay < 3 seconds (p95)
✓ Error rate: Should stay < 1%
✓ Throughput: Should be ~800 users/minute
✓ Data transfer: Should be ~28 MB/minute inbound
```

### Alert Thresholds

**Warning (Check but not urgent):**
```
- Requests per second drops below 10
- Response time (p95) exceeds 5 seconds
- Error rate exceeds 1%
- Throughput drops below 600 users/min
```

**Critical (Investigate immediately):**
```
- Requests per second drops below 5
- Response time (p95) exceeds 10 seconds
- Error rate exceeds 5%
- All workers stuck/no progress for 5 minutes
- Connection errors
```

---

## Summary Table

| Time Unit | Requests | Users Processed | Data Transfer | Notes |
|-----------|----------|----------------|---------------|-------|
| **Per Second** | 13 | 13 | 468 KB | Sustained load |
| **Per Minute** | 780 | 800 | 28 MB | 0.4% progress |
| **Per Hour** | 46,800 | 48,000 | 1.68 GB | 24% progress |
| **Total (4.2 hours)** | 200,000 | 200,000 | 7 GB | 100% complete |

---

## Key Takeaways for DevOps

1. **Sustained Load:** 13 requests/second for 4+ hours straight
2. **Concurrent Connections:** 20 at all times (via Keep-Alive)
3. **Bandwidth:** 3.7 Mbps inbound sustained
4. **Per Backend (if 3 backends):** ~4-5 req/s each
5. **Very Predictable:** No spikes, very steady pattern
6. **Duration:** 4-10 hours depending on API response time

**This is a very manageable load** for a production API with load balancer.

---

**For your DevOps email to CardGenius, you can say:**

> "We'll be sending 13 requests per second sustained, with 20 concurrent connections, for approximately 4 hours. This translates to ~800 requests per minute and ~48,000 requests per hour, for a total of 200,000 requests."



