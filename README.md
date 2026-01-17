# Elevate AI - Fitness & Nutrition Platform

Elevate AI is a comprehensive fitness and nutrition platform that leverages artificial intelligence to provide personalized workout plans, meal recommendations, and exercise tracking.

## System Architecture

The application follows a modern, scalable architecture with four major layers:

### 1. Frontend Layer (React.js)
- Built with React.js and Bootstrap CSS
- Provides user interfaces for:
  - Signup/Login
  - Meal Planner
  - Workout Tracker
  - Dashboard with analytics
  - AI Chatbot
  - Pose Detection module
- Communicates with backend via REST APIs using JSON responses

### 2. Backend Layer (Node.js + Express)
- Central controller of the application
- Responsibilities include:
  - Handling API requests
  - Authentication using JWT
  - CRUD operations
  - Leaderboard and streak management
  - Sending notifications
  - Communicating with the AI/ML service

### 3. Database Layer (MongoDB Atlas)
- Stores data using MongoDB Atlas with Mongoose ORM
- Contains collections for:
  - User profiles
  - Meal plans
  - Workout logs
  - Progress logs
  - Rep-count logs
  - Achievements
  - Chatbot history

### 4. AI & ML Layer (Python – FastAPI)
- Runs separately using FastAPI
- Handles:
  - Meal planning (XGBoost model)
  - Workout suggestions (Decision Tree/Logic-based model)
  - AI chatbot (GPT/LLaMA with RAG)

## Features

- **User Authentication**: Secure signup and login with JWT
- **Personalized Workouts**: AI-generated workout plans based on experience level
- **Smart Nutrition**: Meal recommendations tailored to fitness goals
- **Exercise Tracking**: Real-time pose detection and rep counting
- **Progress Monitoring**: Track weight, measurements, and fitness milestones
- **AI Assistant**: Chatbot for fitness and nutrition guidance
- **Analytics Dashboard**: Visualize progress and achievements

## Tech Stack

### Frontend
- React.js
- Bootstrap CSS
- React Router DOM
- Axios for API calls

### Backend
- Node.js
- Express.js
- MongoDB/Mongoose
- JWT for authentication
- BCrypt for password hashing

### AI/ML Services
- Python
- FastAPI
- OpenCV
- MediaPipe
- Scikit-learn
- XGBoost

## Setup Instructions

### Prerequisites
- Node.js (v14 or higher)
- MongoDB (local or Atlas)
- Python (for AI/ML services)

### Frontend Setup
1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

### Backend Setup
1. Navigate to the backend directory:
```bash
cd backend-node
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file with the required environment variables:
```env
MONGODB_URI=your_mongodb_connection_string
JWT_SECRET=your_jwt_secret
ML_SERVICE_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

### AI/ML Service Setup
1. Navigate to the Python backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login a user

### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile

### Workouts
- `POST /api/workouts` - Create a new workout
- `GET /api/workouts` - Get all workouts for a user
- `GET /api/workouts/public` - Get all public workouts
- `GET /api/workouts/:id` - Get a specific workout
- `PUT /api/workouts/:id` - Update a workout
- `DELETE /api/workouts/:id` - Delete a workout

### Meals
- `POST /api/meals` - Create a new meal
- `GET /api/meals` - Get all meals for a user
- `GET /api/meals/public` - Get all public meals
- `GET /api/meals/:id` - Get a specific meal
- `PUT /api/meals/:id` - Update a meal
- `DELETE /api/meals/:id` - Delete a meal

### Progress
- `POST /api/progress` - Log progress
- `GET /api/progress` - Get all progress logs for a user
- `GET /api/progress/:date` - Get progress for a specific date
- `PUT /api/progress/:id` - Update a progress log
- `DELETE /api/progress/:id` - Delete a progress log

### ML Service
- `POST /api/ml/predict_meal` - Get meal prediction from ML service
- `POST /api/ml/suggest_workout` - Get workout suggestion from ML service
- `POST /api/ml/chat` - Chat with AI assistant

### Chat
- `POST /api/chat/message` - Send a message to the chatbot

## Project Structure

```
Elevate/
├── backend-node/           # Node.js/Express backend
│   ├── controllers/        # Request/response logic
│   ├── models/             # Mongoose schemas
│   ├── routes/             # API endpoints
│   ├── middleware/         # Authentication/validation
│   ├── utils/              # Utility functions
│   ├── config/             # Configuration files
│   ├── server.js           # Main server file
│   └── package.json
├── frontend/              # React frontend
│   ├── public/            # Static assets
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── utils/         # Utility functions
│   │   ├── App.jsx        # Main app component
│   │   └── index.jsx      # Entry point
│   └── package.json
├── backend/               # Python/FastAPI ML service
│   ├── app/
│   │   ├── main.py        # Main API file
│   │   ├── ml_utils.py    # ML utilities
│   │   └── pose_tracker.py # Pose tracking
│   ├── data/              # Training data
│   ├── models/            # ML models
│   ├── requirements.txt
│   └── README.md
└── README.md
```

## External Integrations

- **Spoonacular/Edamam**: For recipes and nutritional data
- **Cloudinary/AWS S3**: For profile image storage
- **FCM/Twilio**: For push notifications, email, and WhatsApp alerts

## Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.