# Elevate AI Backend

This is the Node.js/Express backend for the Elevate AI fitness application. It handles user authentication, data management, and communication with the ML service.

## Features

- User authentication with JWT
- CRUD operations for workouts, meals, and progress tracking
- Integration with ML service for workout and meal recommendations
- Progress tracking and analytics
- Leaderboard and streak management
- Notification system

## Architecture

The backend follows a layered architecture:
- **Controllers**: Handle request/response logic
- **Models**: Define data structures using Mongoose schemas
- **Routes**: Define API endpoints
- **Middleware**: Handle authentication and validation
- **Utils**: Contain utility functions

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file in the root directory with the following variables:
```env
MONGODB_URI=mongodb://localhost:27017/elevate
JWT_SECRET=your_jwt_secret_key_here
ML_SERVICE_URL=http://localhost:8000
SPOONACULAR_API_KEY=your_spoonacular_api_key
EDAMAM_APP_ID=your_edamam_app_id
EDAMAM_APP_KEY=your_edamam_app_key
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
FCM_SERVER_KEY=your_firebase_server_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

3. Start the development server:
```bash
npm run dev
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

## Database Schema

The application uses MongoDB with the following collections:

- **Users**: Store user profiles and preferences
- **Workouts**: Store workout plans and exercises
- **Meals**: Store meal plans and recipes
- **Progress**: Store daily progress logs
- **Achievements**: Store user achievements

## External Integrations

- **Spoonacular/Edamam**: For recipes and nutritional data
- **Cloudinary/AWS S3**: For profile image storage
- **FCM/Twilio**: For push notifications, email, and WhatsApp alerts