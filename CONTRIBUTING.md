# Contributing to Elevate

Thank you for your interest in contributing to the Elevate Fitness Platform. This guide covers development setup, coding standards, commit conventions, and pull-request workflow.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Branch Naming](#branch-naming)
4. [Commit Message Convention](#commit-message-convention)
5. [Code Quality Gates](#code-quality-gates)
6. [Pull Request Workflow](#pull-request-workflow)
7. [Environment Variables](#environment-variables)
8. [Testing](#testing)

---

## Prerequisites

| Tool | Minimum version |
|------|----------------|
| Node.js | 18 LTS |
| Python | 3.10 |
| MongoDB | 6.0 |

---

## Local Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/elevate.git
cd elevate

# 2. Node backend
cd backend-node
cp .env.example .env          # fill in MONGO_URI, JWT_SECRET, …
npm install
npm run dev                   # starts on :5000

# 3. Python backend
cd ../backend-python
cp .env.example .env          # fill in GEMINI_API_KEY, MONGO_URI, …
pip install -r requirements.txt
uvicorn server:app --reload   # starts on :8000

# 4. Frontend
cd ../frontend
cp .env.example .env          # set VITE_API_URL=http://localhost:5000
npm install
npm run dev                   # starts on :5173
```

---

## Branch Naming

```
<type>/<short-description>
```

| Type | Use for |
|------|---------|
| `feat/` | New feature |
| `fix/` | Bug fix |
| `chore/` | Dependency updates, tooling |
| `docs/` | Documentation only |
| `refactor/` | Code restructure without behaviour change |
| `test/` | Adding or updating tests |

Examples: `feat/rate-limiting`, `fix/meal-normalization-bug`

---

## Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

[optional body]

[optional footer: BREAKING CHANGE or issue refs]
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

**Scope** (optional): `auth`, `workout`, `nutrition`, `profile`, `frontend`, `ci`

**Examples:**
```
feat(auth): add HttpOnly cookie support for JWT storage
fix(nutrition): remove duplicate buildMealData helper (BUG-N2)
docs: add CONTRIBUTING guide
```

**Rules:**
- Subject in imperative mood, no trailing period
- Subject ≤ 72 characters
- Reference audit items where applicable (e.g., `SEC-8`, `BUG-N2`)

---

## Code Quality Gates

Run these before every commit:

```bash
# Node backend
cd backend-node
npm run lint            # ESLint

# Python backend
cd backend-python
ruff check .            # linting
# or: flake8 .

# Frontend
cd frontend
npm run lint
npm run build           # verify production build succeeds
```

---

## Pull Request Workflow

1. Fork the repo → create your branch from `main`
2. Make changes following the standards above
3. Ensure all lint / type-check / test gates pass
4. Open a PR against `main` with:
   - A clear **title** following the commit convention
   - A description explaining *why* (not just *what*)
   - A link to the related issue / audit item
5. Request review from at least one peer
6. Squash-merge once approved

---

## Environment Variables

Never commit `.env` files. Use `.env.example` as the template. See `docs/deployment.md` for production variables.

| Variable | Backend | Purpose |
|----------|---------|---------|
| `MONGO_URI` | Node + Python | MongoDB connection string |
| `JWT_SECRET` | Node | Signing secret for auth tokens |
| `GEMINI_API_KEY` | Python | Google Gemini LLM access |
| `NODE_ENV` | Node | `development` / `production` |
| `ALLOWED_ORIGINS` | Node | CORS comma-separated origins |

---

## Testing

```bash
# Node backend unit tests (when added)
cd backend-node && npm test

# Python backend unit tests (when added)
cd backend-python && pytest

# Frontend E2E (when added)
cd frontend && npm run test:e2e
```

> **Note:** CI test infrastructure is tracked in **BUG-C2**. Until it is set up, manually run the commands above before merging.
