# Elevate Backend API Documentation

## Base URL
All API endpoints are prefixed with `/api/`:
- Development: `http://localhost:5000/api/`
- Production: `https://your-deployed-backend-url/api/`

## Authentication
Most endpoints require authentication using JWT tokens. Include the token in the request headers:

```
x-auth-token: YOUR_JWT_TOKEN
```

## Endpoints

### Authentication

#### Register a new user
- **POST** `/users/register`
- **Description**: Creates a new user account
- **Request Body**:
  ```json
  {
    "name": "string",
    "email": "string",
    "password": "string"
  }
  ```
- **Response**:
  ```json
  {
    "token": "string",
    "user": {
      "id": "string",
      "name": "string",
      "email": "string"
    }
  }
  ```

#### Login user
- **POST** `/users/login`
- **Description**: Authenticates a user and returns a JWT token
- **Request Body**:
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```
- **Response**:
  ```json
  {
    "token": "string",
    "user": {
      "id": "string",
      "name": "string",
      "email": "string"
    }
  }
  ```

#### Get user profile
- **GET** `/users/profile`
- **Description**: Gets the authenticated user's profile
- **Headers**: `x-auth-token: YOUR_JWT_TOKEN`
- **Response**:
  ```json
  {
    "id": "string",
    "name": "string",
    "email": "string",
    "date": "string"
  }
  ```

### Exercises

#### Get all exercises
- **GET** `/exercises`
- **Description**: Gets all exercises in the system
- **Response**:
  ```json
  [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "category": "string",
      "difficulty": "string",
      "duration": "number",
      "createdBy": "string",
      "equipment": ["string"],
      "steps": [
        {
          "step": "number",
          "description": "string"
        }
      ],
      "createdAt": "string"
    }
  ]
  ```

#### Get exercise by ID
- **GET** `/exercises/:id`
- **Description**: Gets a specific exercise by its ID
- **Response**: Single exercise object as shown above

#### Create new exercise
- **POST** `/exercises`
- **Description**: Creates a new exercise
- **Headers**: `x-auth-token: YOUR_JWT_TOKEN`
- **Request Body**:
  ```json
  {
    "name": "string",
    "description": "string",
    "category": "string",
    "difficulty": "string",
    "duration": "number",
    "equipment": ["string"],
    "steps": [
      {
        "step": "number",
        "description": "string"
      }
    ]
  }
  ```
- **Response**: Created exercise object

#### Update an exercise
- **PUT** `/exercises/:id`
- **Description**: Updates an existing exercise
- **Headers**: `x-auth-token: YOUR_JWT_TOKEN`
- **Request Body**: Same as create but with updated fields
- **Response**: Updated exercise object

#### Delete an exercise
- **DELETE** `/exercises/:id`
- **Description**: Deletes an exercise
- **Headers**: `x-auth-token: YOUR_JWT_TOKEN`
- **Response**:
  ```json
  {
    "msg": "Exercise removed"
  }
  ```

### ML Services

#### Recommend workout
- **POST** `/ml/recommend-workout`
- **Description**: Gets personalized workout recommendations
- **Headers**: `x-auth-token: YOUR_JWT_TOKEN`
- **Request Body**:
  ```json
  {
    "goal": "string",
    "experience": "string",
    "equipment_available": ["string"],
    "time_available": "number",
    "target_muscle_group": "string",
    "injury_history": ["string"],
    "preferred_exercise_type": "string",
    "intensity_level": "string",
    "frequency_per_week": "number",
    "focus_area": "string",
    "gym_or_home": "string",
    "specific_body_part": "string",
    "cardio_minutes": "number",
    "rest_days": ["string"],
    "progression_type": "string"
  }
  ```
- **Response**: Workout recommendations

#### Recommend meal
- **POST** `/ml/recommend-meal`
- **Description**: Gets personalized meal recommendations
- **Headers**: `x-auth-token: YOUR_JWT_TOKEN`
- **Request Body**:
  ```json
  {
    "goal": "string",
    "calorie_target": "number",
    "meal_type": "string",
    "dietary_restrictions": ["string"],
    "allergies": ["string"],
    "meal_time": "string",
    "budget": "number",
    "protein_target": "number",
    "carb_target": "number",
    "fat_target": "number",
    "preferred_cuisine": "string",
    "cooking_skill": "string",
    "ingredients": ["string"],
    "avoid_ingredients": ["string"],
    "spice_level": "number",
    "prep_time": "number"
  }
  ```
- **Response**: Meal recommendations

#### Chat with AI health assistant
- **POST** `/ml/chat`
- **Description**: Chat with the AI health assistant
- **Headers**: `x-auth-token: YOUR_JWT_TOKEN`
- **Request Body**:
  ```json
  {
    "prompt": "string",
    "user_profile": {
      "age": "number",
      "gender": "string",
      "height": "number",
      "weight": "number",
      "fitness_level": "string",
      "medical_conditions": ["string"]
    },
    "context": "string",
    "response_length": "string"
  }
  ```
- **Response**: AI-generated response

#### Generate creative meal plan
- **POST** `/ml/generate-meal-plan-creative`
- **Description**: Generate a creative meal plan
- **Headers**: `x-auth-token: YOUR_JWT_TOKEN`
- **Request Body**:
  ```json
  {
    "goal": "string",
    "meals": [
      {
        "name": "string",
        "calories": "number",
        "protein": "number",
        "fat": "number",
        "carbohydrates": "number"
      }
    ]
  }
  ```
- **Response**: Creative meal plan

#### Start exercise tracking
- **POST** `/ml/start-exercise-tracking`
- **Description**: Start computer vision-based exercise tracking
- **Headers**: `x-auth-token: YOUR_JWT_TOKEN`
- **Request Body**:
  ```json
  {
    "exercise_name": "string",
    "camera_index": "number"
  }
  ```
- **Response**: Exercise tracking status

#### Get supported exercises
- **GET** `/ml/get-supported-exercises`
- **Description**: Get list of exercises supported by computer vision
- **Headers**: `x-auth-token: YOUR_JWT_TOKEN`
- **Response**:
  ```json
  {
    "supported_exercises": ["string"],
    "message": "string"
  }
  ```

#### Check ML health
- **GET** `/ml/health`
- **Description**: Check the status of the ML backend
- **Response**: ML backend status

### Test Endpoints

#### Test all endpoints
- **GET** `/test`
- **Description**: Test endpoint that verifies all test endpoints are working

#### Test database
- **GET** `/test/db`
- **Description**: Test endpoint that verifies database connectivity

#### Test authentication
- **GET** `/test/auth`
- **Description**: Test endpoint that verifies authentication middleware is working

#### Test ML integration
- **GET** `/test/ml`
- **Description**: Test endpoint that verifies ML integration is ready

### Documentation

#### API Documentation
- **GET** `/docs`
- **Description**: Get this API documentation in JSON format

## Error Handling

All error responses follow this format:
```json
{
  "msg": "Error message"
}
```

For authentication errors:
```json
{
  "msg": "No token, authorization denied"
}
```

## Environment Variables

- `MONGODB_URI`: MongoDB Atlas connection string
- `JWT_SECRET`: Secret for JWT token generation
- `ML_BACKEND_URL`: URL for the ML backend service
- `PORT`: Port for the backend server (default: 5000)
- `FRONTEND_URL`: URL for the frontend application
- `NODE_ENV`: Environment mode (development/production)