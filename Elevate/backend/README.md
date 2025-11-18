# Elevate Backend

The backend for the Elevate fitness platform built with Express.js, Node.js and connected to MongoDB Atlas.

## Features

- User authentication and management
- Exercise management with CRUD operations
- Integration with ML backend for workout and meal recommendations
- Computer vision integration for exercise tracking
- AI health assistant powered by Google Gemini

## Prerequisites

- Node.js (v14 or higher)
- MongoDB Atlas account
- Python environment for ML backend (backend/ml)

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create a `.env` file in the backend root and configure the following variables:
   ```env
   # Database
   MONGODB_URI=your_mongodb_atlas_connection_string_here

   # JWT
   JWT_SECRET=your_jwt_secret_key_here

   # ML Backend
   ML_BACKEND_URL=http://localhost:8000

   # Server
   PORT=5000

   # Frontend
   FRONTEND_URL=http://localhost:3000

   # Security
   NODE_ENV=development
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

## ML Backend Integration

1. First, ensure the ML backend is running:
   ```bash
   cd ml
   pip install -r requirements.txt
   python train.py
   uvicorn main:app --reload --port 8000
   ```

2. The backend will automatically connect to the ML services at the URL specified in `ML_BACKEND_URL`.

## API Endpoints

### Authentication
- `POST /api/users/register` - Register a new user
- `POST /api/users/login` - Login a user
- `GET /api/users/profile` - Get user profile (requires auth token)

### Exercises
- `GET /api/exercises` - Get all exercises
- `GET /api/exercises/:id` - Get exercise by ID
- `POST /api/exercises` - Create a new exercise (requires auth)
- `PUT /api/exercises/:id` - Update an exercise (requires auth)
- `DELETE /api/exercises/:id` - Delete an exercise (requires auth)

### ML Services
- `POST /api/ml/recommend-workout` - Get workout recommendations
- `POST /api/ml/recommend-meal` - Get meal recommendations
- `POST /api/ml/chat` - Chat with AI health assistant
- `POST /api/ml/generate-meal-plan-creative` - Generate creative meal plan
- `POST /api/ml/start-exercise-tracking` - Start exercise tracking
- `GET /api/ml/get-supported-exercises` - Get supported exercises for CV
- `GET /api/ml/health` - Check ML backend health

## Frontend Integration

The backend is configured to work with the frontend application. The frontend should make API calls to `http://localhost:5000/api/` during development.

## Security

- CORS is configured to allow requests from the frontend origin
- JWT tokens are required for protected routes
- Security headers are implemented

## Deployment

1. Set `NODE_ENV=production` in your environment variables
2. Ensure your MongoDB Atlas connection string is properly secured
3. Deploy to your preferred platform (Heroku, AWS, etc.)

## Environment Variables

- `MONGODB_URI`: MongoDB Atlas connection string
- `JWT_SECRET`: Secret for JWT token generation
- `ML_BACKEND_URL`: URL for the ML backend service
- `PORT`: Port for the backend server (default: 5000)
- `FRONTEND_URL`: URL for the frontend application
- `NODE_ENV`: Environment mode (development/production)