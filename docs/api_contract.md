# API Contract

## Version
- Contract Version: 2026-04-10
- Stability: Backward-compatible for current frontend clients

## Standard Response Envelopes

### Success
All Python API endpoints follow this envelope:

```json
{
  "success": true,
  "message": "Human readable status",
  "data": {},
  "timestamp": "2026-04-10T10:00:00.000000"
}
```

### Error
Errors are returned as HTTP errors with FastAPI detail fields:

```json
{
  "detail": "Error text or structured object"
}
```

Node API endpoints return JSON status and message fields and use HTTP status codes for failures.

## Authentication
- Header for authenticated routes: `x-auth-token: <jwt>`
- Admin routes use `x-admin-token: <jwt>`

## Node Backend (http://localhost:5000/api)

### Auth
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/google`
- `POST /auth/logout`
- `POST /auth/reset-password/request`
- `POST /auth/reset-password/confirm`

### Profile
- `GET /profile`
- `POST /profile/update`
- `POST /profile/trends`
- `GET /profile/trends?period=week|month|year`
- `GET /profile/workout-history`
- `POST /profile/workout-history`
- `GET /profile/meal-history`
- `POST /profile/meal-history`

### Users
- `POST /users/workout/save`
- `POST /users/meals/save`

### Admin
- `POST /admin/login`
- `POST /admin/logout`
- `GET /admin/verify`
- `GET /admin/users`
- `GET /admin/users/stats/overview`
- `GET /admin/users/:id`
- `POST /admin/users/:id/suspend`
- `POST /admin/users/:id/activate`
- `POST /admin/users/:id/reset-password`
- `DELETE /admin/users/:id`
- `GET /admin/system/health`
- `GET /admin/system/stats`
- `GET /admin/system/maintenance`
- `POST /admin/system/maintenance`
- `GET /admin/system/audit-logs`
- `POST /admin/system/announcement`
- `DELETE /admin/system/announcement/:announcementId`
- `GET /admin/system/announcements`
- `GET /admin/content/exercises`
- `POST /admin/content/exercises`
- `PUT /admin/content/exercises/:id`
- `DELETE /admin/content/exercises/:id`
- `GET /admin/content/workout-rules`
- `POST /admin/content/workout-rules`

## Python Backend (http://localhost:8000)

### Health / Models
- `GET /`
- `GET /health`
- `GET /api/models/status`
- `POST /api/models/warmup?background=true|false`

### Workout
- `POST /workout`
- `POST /workout/async`
- `GET /workout/status/{job_id}`
- `POST /workout/cache/invalidate`
- `GET /api/weekly-plan`
- `GET /api/swap-options?day_index=0..6`
- `POST /api/swap-rest-to-workout`
- `POST /api/swap-workout-to-rest`
- `POST /api/swap-rest-day` (backward alias)

### Nutrition / Chat
- `POST /nutrition`
- `POST /nutrition/daily`
- `POST /nutrition/swap`
- `POST /api/chat`

### Profile Plan Regeneration
- `PUT /profile/update`

## Backward Compatibility Rules
1. Existing fields are never silently removed from success payloads.
2. New fields can be added in `data` while preserving old top-level fields where currently used.
3. Legacy aliases remain available for one release cycle before removal.
4. Frontend endpoint wrappers in `frontend/src/api.js` are the source of truth for client usage.

## Contract QA Gates
- Node QA script: `backend-node/python_api_contract_qa.js`
- Python contract tests: `backend-python/tests/test_python_api_contract.py`
- CI workflow: `.github/workflows/quality-gates.yml`
