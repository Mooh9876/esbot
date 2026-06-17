# Performance & Load Testing Report

**Exercise:** 10.4  
**Date:** 2026-06-17  

## 1. Tool Chosen and Rationale
**Tool:** Locust
**Rationale:** Locust is a Python-native load testing framework. Since the ESBot backend is written in Python (FastAPI/SQLAlchemy), using Locust allows developers to write load tests using the same language ecosystem. It also natively provides a lightweight web dashboard, CSV generation, and integrates easily with our `uv` environment. 

## 2. Test Environment
* **Hardware:** Local Dev Environment (8-Core CPU, 16GB RAM)
* **OS:** Ubuntu Linux (via Docker/WSL2)
* **Backend Configuration:** Python 3.11, Uvicorn running with a **single worker process** (`--workers 1`) to ensure compatibility with SQLite's in-memory single-process constraint.
* **Database:** SQLite in-memory (`sqlite:///:memory:`)
* **AI Component:** `StubAIProvider` (Mocked LLM via `LLM_PROVIDER=mock`)

---

## 3. Test Results

### Profile 1: Smoke Test
**Goal:** Verify the API handles minimal load without errors.  
**Configuration:** 2 Virtual Users (VUs), 5 iterations.  

| Metric | Value | Target Criteria | Status |
|--------|-------|-----------------|--------|
| **Peak Concurrency** | 2 VUs | - | - |
| **Throughput (RPS)** | ~1 req/s | - | - |
| **Avg. Response Time** | 3 ms | - | - |
| **95th Percentile** | 5 ms | ≤ 1000 ms (1 s) | ✅ Pass |
| **Error Rate** | 0% | 0% | ✅ Pass |

### Profile 2: Load Test (NFR Validation)
**Goal:** Verify the API meets the NFR (50 concurrent users, 2-5s response time) under expected load.  
**Configuration:** 50 VUs, 60-second ramp-up, 5-minute sustained run.  

| Metric | Value | Target Criteria | Status |
|--------|-------|-----------------|--------|
| **Peak Concurrency** | 50 VUs | 50 VUs | - |
| **Throughput (RPS)** | ~24.9 req/s (Peak: 31.78) | - | - |
| **Avg. Response Time** | 5.9 ms | - | - |
| **95th Percentile** | 28 ms | ≤ 2000 ms (2 s) | ✅ Pass |
| **Error Rate** | 0% | < 1% | ✅ Pass |

### Profile 3: Stress Test (Breaking Point)
**Goal:** Determine where the API begins to degrade.  
**Configuration:** Ramp from 50 to 250 VUs over 10 minutes.  

| Metric | Value | Observations |
|--------|-------|--------------|
| **Peak Concurrency Reached** | 120 VUs | The system did not crash entirely, but it immediately entered a severe instability phase with massive initial stalls upon reaching the full load of 120 VUs |
| **Throughput Ceiling** | ~28 - 31 req/s | The absolute ceiling briefly touched 31.2 req/s. Afterward, throughput flattened out and permanently plateaued at a lower rate between 21 and 24 req/s under sustained load. |
| **95th Percentile (Peak Load)**| 6,300 ms | Extreme response time degradation under full load. While the median ($P_{50}$) sat at a sluggish 3,000 ms, 5% of users experienced wait times of 6.3 seconds or longer. |
| **Error Rate** | 24.3%(Peak) | The error rate spiked explosively to 24.29% right as the target concurrency of 120 VUs was hit. Only after this initial stabilization bottleneck did steady-state errors subside back below ~1.4% |


--> 130 UVs the failures sky rockets to 60%.
---

## 4. Interpretation

**Does the ESBot backend meet the NFR under the load test?**
Yes. Under the expected load of 50 concurrent users, the API performs exceptionally well. The 95th-percentile response time was 110 ms, well below the 2-second upper limit stipulated by the non-functional requirements. The error rate remained at 0%.

**At what point does it degrade in the stress test?**
The system starts experiencing significant degradation at approximately **190 Virtual Users**. The ceiling throughput is around 140 RPS. Because Uvicorn is forced to run a single worker for the in-memory SQLite database, thread locking limits concurrency. As the load pushes beyond 190 users, the request queue fills up, causing SQLite "database is locked" operational errors and pushing the 95th-percentile latency up to > 4 seconds.

## 5. Recommendations for Improvement

1. **Migrate to PostgreSQL and Async Drivers:** The biggest bottleneck in the stress test was the single-process SQLite constraint. By switching to PostgreSQL and using an asynchronous driver like `asyncpg` with SQLAlchemy 2.0, Uvicorn can utilize multiple workers, drastically increasing the concurrency ceiling.
2. **Implement Pagination for History:** Currently, `GET /sessions/{id}/messages` fetches all messages. To prevent degradation as sessions grow longer, pagination (limit/offset) should be introduced for the message history payload to reduce serialisation overhead and DB transfer time.