import requests
import json

# Base URL for the FastAPI server
BASE_URL = "http://localhost:8000"

def test_meal_endpoint():
    """Test the enhanced meal endpoint with additional attributes."""
    print("Testing /ml/recommend-meal endpoint...")
    
    # Test data with additional attributes
    meal_data = {
        "goal": "Weight Loss", 
        "calorie_target": 300,
        "meal_type": "Dinner",
        "dietary_restrictions": ["Vegetarian"],
        "allergies": ["Nuts"],
        "protein_target": 20.0,
        "carb_target": 30.0,
        "fat_target": 10.0,
        "spice_level": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ml/recommend-meal", json=meal_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error testing meal endpoint: {e}")
    
    print("-" * 50)

def test_workout_endpoint():
    """Test the enhanced workout endpoint with additional attributes."""
    print("Testing /ml/recommend-workout endpoint...")
    
    # Test data with additional attributes
    workout_data = {
        "goal": "Strength",
        "experience": "Intermediate",
        "equipment_available": ["Dumbbells", "Barbell"],
        "target_muscle_group": "chest",
        "injury_history": ["Knee"],
        "preferred_exercise_type": "Free Weights",
        "intensity_level": "Moderate"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ml/recommend-workout", json=workout_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error testing workout endpoint: {e}")
    
    print("-" * 50)

def test_chat_endpoint():
    """Test the enhanced chat endpoint with additional attributes."""
    print("Testing /ml/chat endpoint...")
    
    # Test data with additional attributes
    chat_data = {
        "prompt": "What's a good post-workout meal?",
        "user_profile": {
            "age": 30,
            "gender": "Male",
            "height": 180,
            "weight": 75,
            "fitness_level": "Intermediate",
            "medical_conditions": ["None"]
        },
        "context": "Nutrition",
        "response_length": "Detailed"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ml/chat", json=chat_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error testing chat endpoint: {e}")
    
    print("-" * 50)

if __name__ == "__main__":
    print("Testing enhanced API endpoints...")
    print("Make sure to start the FastAPI server with 'uvicorn main:app --reload' before running this test.")
    print("=" * 50)
    
    test_meal_endpoint()
    test_workout_endpoint()
    test_chat_endpoint()
    
    print("Testing completed!")