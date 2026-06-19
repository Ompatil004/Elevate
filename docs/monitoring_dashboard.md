# Monitoring Dashboard Specification

## Objective
Provide a single pane of glass for reliability, latency, and error diagnosis across frontend, Node backend, and Python backend.

## Core KPI Panels
1. API Success Rate
- Metric: successful responses / total responses
- Target: >= 99.5%

2. Workout Latency
- Metric: p50, p95, p99 for `/workout` and `/workout/async`
- Target: p95 <= 25s fresh, <= 8s cached

3. Frontend Load
- Metric: first meaningful load by cold/warm path
- Target: <= 4.0s cold, <= 2.5s cached

4. Pose Session Reliability
- Metric: model init failures per 100 sessions
- Target: downward trend and < 2%

5. Session Validity
- Metric: auth failures and token-expiry transitions
- Target: zero unexpected expiry mismatches

## Dependency Panels
1. Python model state
- Source: `GET /api/models/status`
- Fields: state, ready, last_error, load_time_ms

2. Mongo connectivity
- Source: Python `GET /health` dependencies.mongo and Node `/test-db`

3. Service worker/model cache warm hit ratio
- Source: frontend telemetry event counters

## Alert Rules
1. SEV-1
- API success rate < 97% for 5m
- `/workout` hard failures > 20% for 5m

2. SEV-2
- p95 workout latency > 30s for 10m
- model warmup error state persists > 10m

3. SEV-3
- elevated client warnings in pose-model preload path

## Required Log Fields
- timestamp
- level
- service
- endpoint
- status_code
- latency_ms
- request_id
- error_type
- error_message

## Ownership
- Frontend telemetry: Frontend owner
- Node service metrics: Node backend owner
- Python model metrics: Python backend owner
- Incident command: QA/Operations lead
