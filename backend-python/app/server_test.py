"""
Simple test server to verify endpoints work
"""
from main import app
import uvicorn
import threading
import time
import requests

def start_server():
    """Start the server in a separate thread"""
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

def test_server():
    """Test the server endpoints"""
    # Wait a bit for server to start
    time.sleep(3)
    
    print("Testing endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get("http://127.0.0.1:8000/health")
        print(f"Health endpoint: {response.status_code}")
    except:
        print("Health endpoint not accessible - server may not be running")
        return
    
    # Test profile endpoints
    test_data = {
        "user_id": "test_user_123",
        "username": "test_user",
        "age": 30,
        "weight": 70,
        "height": 175,
        "goal": "general_fitness",
        "experience": "intermediate"
    }
    
    try:
        response = requests.put("http://127.0.0.1:8000/profile/update", json=test_data)
        print(f"Profile update endpoint: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Profile update endpoint error: {e}")
    
    try:
        response = requests.put("http://127.0.0.1:8000/profile/update-with-regeneration", json=test_data)
        print(f"Profile update with regeneration endpoint: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Profile update with regeneration endpoint error: {e}")

if __name__ == "__main__":
    import sys
    import subprocess
    
    print("Starting server and testing endpoints...")
    
    # Start server in background
    server_process = subprocess.Popen([sys.executable, "-c", 
        "from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8000, log_level='warning')"])
    
    # Wait for server to start
    time.sleep(5)
    
    # Test endpoints
    test_server()
    
    # Kill server process
    server_process.terminate()
    server_process.wait()
    print("Server test completed.")