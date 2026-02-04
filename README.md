# Elevate Fitness Application

Elevate is a comprehensive fitness application that combines workout planning, nutrition tracking, and AI-powered coaching to help users achieve their fitness goals.

## Features

- Personalized workout plans based on user profile and goals
- Nutrition tracking and meal planning
- Progress tracking with streaks and statistics
- AI-powered workout and nutrition recommendations
- Google OAuth authentication
- Camera-based pose tracking for workouts
- Dark-themed modern UI

## Tech Stack

- **Frontend**: React/Vite with modern UI
- **Backend**:
  - Node.js/Express for user authentication and profile management
  - Python/FastAPI for AI-powered workout and nutrition planning
- **Database**: MongoDB
- **Machine Learning**: XGBoost models for personalized recommendations

## Setup Instructions

### Prerequisites

- Node.js (v18 or higher)
- Python (v3.8 or higher)
- MongoDB

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Copy the environment file:
   ```bash
   cp .env.example .env
   ```

4. Update the `.env` file with your API keys:
   - `VITE_GOOGLE_CLIENT_ID`: Your Google OAuth client ID
   - `VITE_API_NINJAS_KEY`: Your API Ninjas key (for exercise data)
   - `VITE_USDA_API_KEY`: Your USDA API key (for nutrition data)

### Backend Setup

#### Node.js Backend

1. Navigate to the backend-node directory:
   ```bash
   cd backend-node
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up your `.env` file with:
   - `MONGO_URI`: Your MongoDB connection string
   - `JWT_SECRET`: Your JWT secret
   - `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
   - `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret

#### Python Backend

1. Navigate to the backend-python directory:
   ```bash
   cd backend-python
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your `.env` file with:
   - `MONGO_URI`: Your MongoDB connection string

### Running the Application

1. Start the MongoDB service

2. Start the Python backend:
   ```bash
   cd backend-python
   python server.py
   ```

3. Start the Node.js backend:
   ```bash
   cd backend-node
   npm start
   ```

4. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

## API Keys Setup

### Google OAuth
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
9. Add the following authorized JavaScript origins:
   - `http://localhost:5173`
   - `http://localhost:3000`
   - Your production domain
10. Copy the Client ID and Client Secret
11. Add them to your environment files:
    - Backend: Add `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` to `backend-node/.env`
    - Frontend: Add `VITE_GOOGLE_CLIENT_ID` to `frontend/.env`

### USDA FoodData Central API
1. Visit https://fdc.nal.usda.gov/api-key-signup.html
2. Request an API key
3. Add it to your `.env` file as `VITE_USDA_API_KEY`

### API Ninjas
1. Visit https://api-ninjas.com/
2. Sign up and get an API key
3. Add it to your `.env` file as `VITE_API_NINJAS_KEY`

## Troubleshooting

- If you encounter API errors (403 status codes), ensure your API keys are correctly configured in the `.env` file
- Make sure all three services (Python backend, Node.js backend, and frontend) are running simultaneously
- Check that MongoDB is running and accessible

## License

This project is licensed under the MIT License.