# Google OAuth 2.0 Setup Guide

> **BUG-D2 fix:** This file was referenced in README.md but did not exist.

This guide walks you through setting up Google Sign-In for the Elevate app's **Login** and **Register** pages.

---

## Prerequisites

- A Google account
- Access to [Google Cloud Console](https://console.cloud.google.com/)

---

## Step 1 — Create or Select a Google Cloud Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com/)
2. Click the **project selector** at the top left
3. Click **New Project**, give it a name (e.g. `Elevate Fitness`), and click **Create**

---

## Step 2 — Enable the Google Identity API

1. In the left sidebar select **APIs & Services › Library**
2. Search for `Google Identity` and select **Google Identity Services**
3. Click **Enable**

---

## Step 3 — Configure the OAuth Consent Screen

1. Go to **APIs & Services › OAuth consent screen**
2. Select **External** (unless you have a Google Workspace org) → **Create**
3. Fill in:
   - **App name**: `Elevate Fitness`
   - **User support email**: your email
   - **Developer contact email**: your email
4. Click **Save and Continue** through the remaining steps
5. Back on the Consent Screen summary, click **Publish App** (makes it available to all Google users)

---

## Step 4 — Create OAuth 2.0 Credentials

1. Go to **APIs & Services › Credentials**
2. Click **Create Credentials › OAuth client ID**
3. Choose **Application type: Web application**
4. Set a name (e.g. `Elevate Web Client`)
5. Under **Authorised JavaScript origins**, add:
   ```
   http://localhost:5173
   http://localhost:3000
   https://your-production-domain.com
   ```
6. Under **Authorised redirect URIs**, add:
   ```
   http://localhost:5173
   https://your-production-domain.com
   ```
7. Click **Create**
8. Copy the **Client ID** (looks like `1234567890-abc...xyz.apps.googleusercontent.com`)

---

## Step 5 — Add the Client ID to Your Environment Files

### Frontend (`frontend/.env`)

```env
VITE_GOOGLE_CLIENT_ID=1234567890-abc...xyz.apps.googleusercontent.com
```

### Backend Node.js (`backend-node/.env`)

```env
GOOGLE_CLIENT_ID=1234567890-abc...xyz.apps.googleusercontent.com
```

> ⚠️ Both values must be **identical** — the frontend sends a token signed against the Client ID, and the backend verifies it using the same ID.

---

## Step 6 — Verify It Works

1. Start all services with `start_all.sh` (Linux/Mac) or `start_all.bat` (Windows)
2. Open `http://localhost:5173/login`
3. You should see a **Continue with Google** button
4. Click it and complete the Google sign-in flow
5. You should be redirected to `/dashboard` (existing user) or `/profile-setup` (new user)

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `Google Client ID not configured` | Check `VITE_GOOGLE_CLIENT_ID` in `frontend/.env` |
| `Invalid token` from backend | Check `GOOGLE_CLIENT_ID` in `backend-node/.env` matches exactly |
| `redirect_uri_mismatch` | Add your exact origin URL to the Authorised JavaScript origins list |
| Button does not appear | Check browser console for CSP / script-load errors |
| Works in dev, fails in prod | Add the production domain to both Origins and Redirect URIs lists |
