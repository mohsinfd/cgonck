# Phase 3 Load - Quick Reference Card

**Configuration:** 20 parallel workers processing 200,000 users

---

## 📊 The Numbers (Every Second)

```
╔══════════════════════════════════════════╗
║  SUSTAINED LOAD (Typical Case)          ║
╠══════════════════════════════════════════╣
║  Requests per second:      13            ║
║  Concurrent connections:   20            ║
║  Response time:            1.5s avg      ║
║  Duration:                 4.2 hours     ║
╚══════════════════════════════════════════╝
```

---

## ⏱️ Timeline Breakdown

### Per Second
- **13 API calls complete**
- **13 new API calls start**
- **20 workers always busy**

### Per Minute
- **780 requests sent**
- **800 users processed**
- **28 MB data received**
- **0.4% progress**

### Per Hour
- **46,800 requests sent**
- **48,000 users processed**
- **1.68 GB data received**
- **24% progress**

### Total (4.2 hours)
- **200,000 requests sent**
- **200,000 users processed**
- **7 GB data received**
- **100% complete** ✓

---

## 🌐 Network Load

```
BANDWIDTH (Sustained):
├─ Outbound:  73 Kbps   (9 KB/s)
├─ Inbound:   3.7 Mbps  (455 KB/s)
└─ Total:     3.77 Mbps (468 KB/s)

PER REQUEST:
├─ Request size:   500 bytes
├─ Response size:  35 KB
└─ Round trip:     ~35.5 KB
```

---

## 🎯 Load Balancer View

**If CardGenius has 3 backend servers:**

```
Each Backend Server Receives:
├─ Connections: 6-7 (of our 20)
├─ Requests/sec: 4-5
├─ Load share: 33%
└─ Very manageable
```

---

## 📈 Load Pattern

```
Start:  0 → 13 req/s (ramp up in 5 seconds)
Hour 1: 13 req/s sustained ━━━━━━━━━━━━━
Hour 2: 13 req/s sustained ━━━━━━━━━━━━━
Hour 3: 13 req/s sustained ━━━━━━━━━━━━━
Hour 4: 13 req/s sustained ━━━━━━━━━━━━━
End:    13 → 0 req/s (wind down in 2 min)
```

---

## 🔢 Best/Typical/Worst Case

| Scenario | Req/Sec | Time for 200K |
|----------|---------|---------------|
| **Best** (1.0s response) | 20 | 2.8 hours |
| **Typical** (1.5s response) | 13 | 4.2 hours |
| **Worst** (3.0s response) | 7 | 8.3 hours |

---

## ✉️ Email CardGenius (Copy-Paste)

```
We'll be processing 200K users with:
- 13 requests/second sustained
- 20 concurrent connections
- Duration: ~4 hours
- Total: 200,000 API calls
- Bandwidth: 3.7 Mbps inbound

Questions:
1. Is this load acceptable?
2. Any rate limits we should know?
3. Preferred time window?
```

---

## 🚨 Monitor These

### Normal (Green)
```
✓ Requests/sec: 10-15
✓ Response time: < 3s
✓ Error rate: < 1%
✓ Progress: 800 users/min
```

### Warning (Yellow)
```
⚠ Requests/sec: 5-10
⚠ Response time: 3-5s
⚠ Error rate: 1-5%
⚠ Progress: 400-600 users/min
```

### Critical (Red)
```
✗ Requests/sec: < 5
✗ Response time: > 10s
✗ Error rate: > 5%
✗ No progress for 5+ min
```

---

## 💡 Key Points

1. **Very Predictable:** Steady 13 req/s, no spikes
2. **Very Manageable:** Production APIs handle this easily
3. **Long Duration:** 4+ hours continuous
4. **Coordinate:** Tell CardGenius 48 hours ahead
5. **Start Small:** Test with 5 workers first

---

**Bottom Line:**  
13 requests/second for 4 hours = Very reasonable load



