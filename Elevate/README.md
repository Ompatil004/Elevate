# Elevate Fitness Platform

## Project Overview

Elevate is a comprehensive fitness platform with AI-powered recommendations, pose detection, and personalized workout/meal planning.

## Project Structure

```
Elevate/
├── backend/                 # Node.js/Express API server
│   ├── models/              # MongoDB schemas (User, Exercise)
│   ├── routes/              # API endpoints (users, exercises, ml, test)
│   ├── middleware/          # Authentication middleware
│   ├── config/              # Database configuration
│   ├── services/            # Backend services
│   ├── .env                 # Environment variables
│   └── server.js            # Main server file
├── Backend-ml/              # Python ML backend
│   ├── main.py              # FastAPI server
│   ├── train.py             # Model training script
│   ├── exercise_cv.py       # Pose detection module
│   ├── requirements.txt     # Python dependencies
│   ├── data/                # Training data
│   └── models/              # Trained ML models
└── frontend/                # React/Vite frontend
    ├── src/
    │   ├── components/      # React UI components
    │   ├── context/         # React Context providers (Auth, UserData)
    │   ├── services/        # API service layer (axios)
    │   ├── utils/           # Utility functions
    │   ├── App.tsx          # Main application component
    │   └── main.tsx         # Application entry point
    ├── public/
    ├── package.json
    └── vite.config.ts
```

## Module Integration

### 1. Authentication Module
- **Frontend**: `AuthContext.tsx` using React Context
- **Backend**: JWT-based authentication in `routes/users.js`
- **Flow**: Register/Login → JWT token → Protected routes

### 2. User Data Module
- **Frontend**: `UserDataContext.tsx` manages user profile
- **Backend**: `User` model with fitness data fields
- **Database**: MongoDB with User schema

### 3. Meal Planner
- **Frontend**: `MealPlan.tsx` fetches recommendations via ML API
- **Backend**: `/api/ml/recommend-meal` endpoint
- **ML Service**: Gemini-powered nutrition recommendations

### 4. Exercise Planner
- **Frontend**: `Workout.tsx` fetches recommendations via ML API
- **Backend**: `/api/ml/recommend-workout` endpoint
- **ML Service**: XGBoost model for workout suggestions

### 5. Pose Detection
- **Frontend**: `PoseDetection.tsx` with camera integration
- **Backend**: Python MediaPipe + OpenCV in `exercise_cv.py`
- **ML Service**: Real-time rep counting

### 6. AI Chatbot
- **Frontend**: `Chatbot.tsx` with conversation interface
- **Backend**: `/api/ml/chat` endpoint
- **ML Service**: Google Gemini integration

## Environment Setup

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
# Update VITE_API_BASE_URL in .env
npm run dev
```

### Backend
```bash
cd backend
npm install
cp .env.example .env
# Update MongoDB URI and JWT_SECRET in .env
npm run dev
```

### ML Backend
```bash
cd Backend-ml
pip install -r requirements.txt
python train.py  # To train models
uvicorn main:app --reload  # To start server
```

## API Endpoints

### Authentication
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - Login user
- `GET /api/users/profile` - Get user profile (requires auth)
- `PUT /api/users/profile` - Update user profile (requires auth)

### ML Services
- `POST /api/ml/recommend-workout` - Get workout recommendations
- `POST /api/ml/recommend-meal` - Get meal recommendations
- `POST /api/ml/chat` - AI health assistant
- `POST /api/ml/start-exercise-tracking` - Start pose detection
- `GET /api/ml/get-supported-exercises` - Get exercises for CV

### Exercises
- `GET /api/exercises` - Get all exercises
- `POST /api/exercises` - Create exercise (requires auth)

## Running the Full Application

1. Start the ML backend: `cd Backend-ml && uvicorn main:app --reload`
2. Start the Node.js backend: `cd backend && npm run dev`
3. Start the frontend: `cd frontend && npm run dev`

## Key Features Implemented

1. ✅ **Complete Authentication Flow** - JWT-based auth with React Context
2. ✅ **User Profile Management** - MongoDB integration with profile fields
3. ✅ **ML-Powered Meal Planning** - Gemini API for nutrition recommendations
4. ✅ **ML-Powered Workout Planning** - Exercise recommendation engine
5. ✅ **Pose Detection** - Real-time exercise form tracking
6. ✅ **AI Health Assistant** - Chatbot for fitness guidance
7. ✅ **Responsive UI** - Mobile-friendly interface
8. ✅ **State Management** - React Context for global state
9. ✅ **API Integration** - Full backend-frontend connectivity
10. ✅ **Database Layer** - MongoDB with Mongoose ODM

## Troubleshooting

### Common Issues
- ML backend not responding: Ensure `uvicorn main:app --reload` is running on port 8000
- Authentication failing: Check JWT_SECRET is properly set in backend .env
- Camera access blocked: Ensure HTTPS or localhost for camera access
- ML recommendations not working: Verify Google API key in Backend-ml/.env

### Port Configuration
- Frontend: 3000
- Backend: 5000 (or set PORT environment variable)
- ML Backend: 8000

## Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **Backend**: Node.js, Express.js
- **Database**: MongoDB Atlas with Mongoose
- **ML/AI**: Python, FastAPI, Google Gemini, OpenCV, MediaPipe
- **Authentication**: JWT, bcrypt
- **Styling**: Tailwind CSS, Radix UI
- **State Management**: React Context API
- **API Communication**: Axios