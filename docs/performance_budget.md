# Performance Budget

## Frontend
- Initial JS payload budget: <= 300 KB gzip
- Route-level lazy chunks: <= 220 KB gzip per heavy route
- First meaningful paint:
  - cold <= 4.0s
  - warm <= 2.5s

## Backend Python
- `/workout` p95 <= 25s fresh
- `/workout` p95 <= 8s cached
- `/nutrition` p95 <= 10s
- `/api/models/status` p95 <= 300ms

## Backend Node
- `/api/auth/login` p95 <= 600ms
- `/api/profile` p95 <= 800ms
- admin routes p95 <= 1200ms

## Pose Model Load
- model preload trigger at Workout page entry
- warm cached camera start target <= 2s

## Verification Commands
- `cd frontend && npm test`
- `cd backend-node && npm test`
- `python -m unittest discover -s backend-python/tests -p "test_*.py"`

## Fallback Policy
- If model not ready, use deterministic error and prompt retry.
- If async workout exceeds max wait, return job id and keep polling path available.
