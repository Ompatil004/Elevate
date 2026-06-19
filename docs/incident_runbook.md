# Incident Runbook

## Scope
Operational runbook for high-impact failures in auth, workout generation, media loading, and persistence flows.

## Severity Model
- SEV-1: Full outage or major user-facing failure.
- SEV-2: Partial outage or degraded core function.
- SEV-3: Non-blocking regression.

## Global Triage Checklist
1. Confirm affected service and endpoint.
2. Check `/health` on Python backend and Node `/health`.
3. Capture request ID from response header `x-request-id`.
4. Check latest deploy/change window.
5. Scope blast radius: all users, region, role-specific, or endpoint-specific.
6. Decide rollback/hotfix path.

## Playbook: Auth/Session Errors
### Symptoms
- 401 spikes
- forced logouts
- invalid token errors after refresh

### Checks
1. Node env contains `JWT_SECRET`, `ADMIN_JWT_SECRET`.
2. Token age and expiration claims.
3. Frontend sends `x-auth-token` or `x-admin-token` correctly.

### Immediate Actions
1. Restore correct secrets from secure config.
2. Invalidate broken sessions if secret mismatch occurred.
3. Redeploy and monitor auth success rate for 30 minutes.

## Playbook: Workout Timeout / Failure
### Symptoms
- `POST /workout` slow or failing
- users cannot generate plan

### Checks
1. Python `/health` for model warmup and dependency state.
2. `GET /api/models/status` for workout engine state and last error.
3. rate-limit responses (429) frequency.

### Immediate Actions
1. Trigger warmup: `POST /api/models/warmup`.
2. Use async path fallback: `/workout/async` and poll endpoint.
3. If cold start failure persists, restart Python service and recheck status endpoint.

## Playbook: Media/Pose Model Load Failures
### Symptoms
- camera starts but pose model does not load
- pose session stuck in warming state

### Checks
1. Browser network requests to MediaPipe CDN and Google storage.
2. Service worker cache entries for model assets.
3. GPU delegate fallback behavior in `PoseDetector`.

### Immediate Actions
1. Force model warm preload on workout route entry.
2. Validate fallback candidate model list loads with CPU delegate.
3. If CDN blocked, communicate temporary no-camera mode guidance.

## Playbook: DB Persistence Failures
### Symptoms
- plan generated but not saved
- swap history missing
- user updates not reflected

### Checks
1. Python `/health` dependency `mongo.ok`.
2. Node database connectivity endpoint `/test-db`.
3. write-operation errors in service logs using request ID.

### Immediate Actions
1. Verify Mongo availability and credentials.
2. Retry write path with idempotent endpoint where possible.
3. Escalate to database owner if replica/cluster instability detected.

## Recovery Verification
1. Repeat failed user flow with test account.
2. Confirm metrics recovery to baseline (error rate, latency).
3. Close incident only after 30-minute stable window.

## Postmortem Template
- Incident summary
- Timeline with UTC timestamps
- Root cause
- Containment and permanent fix
- Regression test added
- Owner and target date
