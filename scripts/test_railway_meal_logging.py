"""
Test script to debug Railway meal logging 500 error.
This bypasses CORS by making direct API calls.
"""
import requests
import json

# Railway backend URL
BASE_URL = "https://gym-diet-production.up.railway.app"

def test_health():
    """Test if backend is responding"""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_login():
    """Test login and get token"""
    print("\n=== Testing Login ===")
    try:
        # Try to login with test credentials
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Login successful! Token: {data.get('access_token', '')[:20]}...")
            return data.get('access_token')
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def test_meal_logging(token):
    """Test meal logging with token"""
    print("\n=== Testing Meal Logging ===")
    try:
        payload = {
            "description": "Test meal from script",
            "protein": 30,
            "carbs": 50,
            "fats": 15
        }
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/meals",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            print(f"Success! Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"Failed! Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("RAILWAY MEAL LOGGING DEBUG SCRIPT")
    print("=" * 60)
    
    # Step 1: Test health
    if not test_health():
        print("\n❌ Backend is not responding!")
        exit(1)
    
    print("\n✅ Backend is healthy!")
    
    # Step 2: Login
    token = test_login()
    if not token:
        print("\n❌ Login failed! Create a test user first.")
        print("Run: python scripts/create_test_user.py")
        exit(1)
    
    print("\n✅ Login successful!")
    
    # Step 3: Test meal logging
    if test_meal_logging(token):
        print("\n✅ Meal logging works!")
    else:
        print("\n❌ Meal logging failed!")
        print("\nThis is the actual error causing the 500 response.")
        print("Check Railway logs for Python traceback.")
