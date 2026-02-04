"""
Test script to verify the profile update endpoints work correctly
"""
import requests
import json
import time

def test_endpoints():
    base_url = "http://localhost:8000"
    
    print("Testing profile update endpoints...")
    
    # Test the health endpoint first
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json() if response.status_code == 200 else 'Failed'}")
    except Exception as e:
        print(f"Health check failed: {e}")
        print("Server may not be running. Please start the backend server on port 8000")
        return
    
    # Test the profile update endpoint
    test_data = {
        "user_id": "test_user_123",
        "username": "test_user",
        "age": 30,
        "weight": 70,
        "height": 175,
        "goal": "general_fitness",
        "experience": "intermediate",
        "equipment": ["dumbbells", "yoga_mat"],
        "body_issues": [],
        "dietary_preference": "balanced",
        "allergies": []
    }
    
    print("\nTesting /profile/update endpoint...")
    try:
        response = requests.put(f"{base_url}/profile/update", 
                              json=test_data, 
                              headers={"Content-Type": "application/json"})
        print(f"Profile update endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Profile update endpoint test failed: {e}")
    
    print("\nTesting /profile/update-with-regeneration endpoint...")
    try:
        response = requests.put(f"{base_url}/profile/update-with-regeneration", 
                              json=test_data, 
                              headers={"Content-Type": "application/json"})
        print(f"Profile update with regeneration endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Profile update with regeneration endpoint test failed: {e}")

if __name__ == "__main__":
    test_endpoints()