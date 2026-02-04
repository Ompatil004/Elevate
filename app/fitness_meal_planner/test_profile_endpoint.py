"""
Test script to verify the profile update endpoint works
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

def test_routes():
    app = create_app()
    
    print("Available routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {', '.join(rule.methods)}")
    
    print("\nProfile-related routes:")
    for rule in app.url_map.iter_rules():
        if 'profile' in str(rule).lower():
            print(f"  {rule.rule} -> {', '.join(rule.methods)}")
    
    # Test the endpoint directly
    with app.test_client() as client:
        print("\nTesting profile update endpoint...")
        
        # First, try to create a user to test with
        user_response = client.post('/api/user', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'age': 30,
            'gender': 'male',
            'weight': 70,
            'height': 175,
            'fitness_level': 'beginner',
            'goal': 'general_fitness',
            'experience_level': 'beginner',
            'equipment_available': ['none'],
            'injuries': [],
            'health_conditions': [],
            'dietary_preferences': 'balanced',
            'allergies': [],
            'preferred_categories': [],
            'disliked_exercises': [],
            'preferred_cuisines': [],
            'disliked_ingredients': [],
            'eating_frequency': 'regular'
        })
        
        print(f"User creation response: {user_response.status_code}")
        if user_response.status_code in [200, 201]:
            user_data = user_response.get_json()
            print(f"User created: {user_data}")

            # Extract user_id from response
            user_id = None
            if user_data and 'user_id' in user_data:
                user_id = user_data['user_id']
            elif user_data and 'id' in user_data:
                user_id = user_data['id']
            else:
                # If no user_id in response, try with default
                user_id = 1
                print(f"Using default user_id: {user_id}")

            # Now test profile update with the created user
            profile_update_data = {
                'user_id': user_id,
                'name': 'Updated Test User',
                'fitness_level': 'intermediate',
                'goal': 'strength',
                'equipment_available': ['dumbbells', 'yoga_mat']
            }

            profile_response = client.put('/api/profile/update', json=profile_update_data)
            print(f"Profile update response: {profile_response.status_code}")
            print(f"Profile update data: {profile_response.get_json()}")
        else:
            print("Creating user failed, trying profile update with default user ID...")
            # Try profile update with default user ID
            profile_update_data = {
                'user_id': 1,
                'name': 'Test User',
                'fitness_level': 'intermediate',
                'goal': 'strength'
            }

            profile_response = client.put('/api/profile/update', json=profile_update_data)
            print(f"Profile update response: {profile_response.status_code}")
            print(f"Profile update data: {profile_response.get_json()}")

if __name__ == "__main__":
    test_routes()