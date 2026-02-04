# Google OAuth Setup Instructions

To enable Google Sign-In functionality in the Elevate application, follow these steps:

## 1. Create Google OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API (for profile information)
4. Go to "Credentials" in the left sidebar
5. Click "Create Credentials" > "OAuth 2.0 Client IDs"
6. Configure the OAuth consent screen if prompted
7. For application type, select "Web application"
8. Add the following authorized redirect URIs:
   - `http://localhost:5173` (for development)
   - `http://localhost:3000` (if using different port)
   - Your production domain (when deployed)

## 2. Update Environment Variables

### Backend (.env file)
Replace the placeholder values in `backend-node/.env`:
```
GOOGLE_CLIENT_ID=your_actual_google_client_id
GOOGLE_CLIENT_SECRET=your_actual_google_client_secret
```

### Frontend (.env file)
Replace the placeholder value in `frontend/.env`:
```
REACT_APP_GOOGLE_CLIENT_ID=your_actual_google_client_id
```

## 3. Configure Authorized Origins

In your Google Cloud Console, under OAuth 2.0 Client IDs, make sure to add:
- Authorized JavaScript origins:
  - `http://localhost:5173`
  - `http://localhost:3000`
  - Your production domain

## 4. Restart Servers

After updating the environment variables, restart both servers:
```bash
# In backend-node directory
npm start

# In frontend directory
npm run dev
```

## 5. Testing

Once configured, you should see the "Continue with Google" button on both the Login and Register pages. When clicked, it will:
- Authenticate the user with Google
- Create a new user account if one doesn't exist
- Log in existing users who signed up with Google
- Store the user's Google profile picture as their avatar