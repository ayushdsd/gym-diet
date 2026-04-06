"""
Test RAG Phase 1 on Production Railway Backend
"""

import requests
import json
import sys

# Production Railway URL
BASE_URL = "https://gym-diet-production.up.railway.app"

def get_test_token():
    """Login and get a test token"""
    print("\n=== Getting Test Token ===")
    
    # Try to login with test credentials (OAuth2 form data)
    login_data = {
        "username": "test@example.com",  # OAuth2 uses 'username' field
        "password": "test123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=login_data  # Use form data, not JSON
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ Login successful!")
            return token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None


def test_conversation_context(token):
    """Test that AI remembers previous messages"""
    print("\n" + "="*60)
    print("TEST 1: Conversation Context")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # First message
    print("\n1️⃣ User: 'I want to lose weight'")
    try:
        response1 = requests.post(
            f"{BASE_URL}/ai/message",
            headers=headers,
            json={"message": "I want to lose weight"}
        )
        
        if response1.status_code == 200:
            reply1 = response1.json().get('reply', 'No reply')
            print(f"   AI: {reply1}")
        else:
            print(f"   ❌ Error: {response1.status_code} - {response1.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Second message (should remember first)
    print("\n2️⃣ User: 'What should I eat for breakfast?'")
    try:
        response2 = requests.post(
            f"{BASE_URL}/ai/message",
            headers=headers,
            json={"message": "What should I eat for breakfast?"}
        )
        
        if response2.status_code == 200:
            reply2 = response2.json().get('reply', 'No reply')
            print(f"   AI: {reply2}")
            
            # Check if AI references weight loss goal
            reply_lower = reply2.lower()
            if any(word in reply_lower for word in ['weight', 'loss', 'fat', 'lose', 'deficit']):
                print("\n   ✅ PASS: AI remembered the weight loss goal!")
                return True
            else:
                print("\n   ⚠️  WARNING: AI might not have remembered the goal")
                print(f"   (Looking for keywords: weight, loss, fat, lose, deficit)")
                return False
        else:
            print(f"   ❌ Error: {response2.status_code} - {response2.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_user_profile_awareness(token):
    """Test that AI knows user's profile and progress"""
    print("\n" + "="*60)
    print("TEST 2: User Profile Awareness")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n💬 User: 'How am I doing today?'")
    try:
        response = requests.post(
            f"{BASE_URL}/ai/message",
            headers=headers,
            json={"message": "How am I doing today?"}
        )
        
        if response.status_code == 200:
            reply = response.json().get('reply', 'No reply')
            print(f"   AI: {reply}")
            
            # Check if AI mentions profile data
            reply_lower = reply.lower()
            profile_keywords = ['streak', 'level', 'target', 'goal', 'protein', 'carbs', 'fats', 'progress']
            found_keywords = [word for word in profile_keywords if word in reply_lower]
            
            if found_keywords:
                print(f"\n   ✅ PASS: AI is aware of user profile!")
                print(f"   Found keywords: {', '.join(found_keywords)}")
                return True
            else:
                print(f"\n   ⚠️  WARNING: AI might not be using profile data")
                print(f"   (Looking for: {', '.join(profile_keywords)})")
                return False
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_daily_progress_context(token):
    """Test that AI considers today's logged meals"""
    print("\n" + "="*60)
    print("TEST 3: Daily Progress Context")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Log a meal first
    print("\n1️⃣ Logging a meal: 30g protein, 50g carbs, 10g fats")
    try:
        meal_response = requests.post(
            f"{BASE_URL}/meals",
            headers=headers,
            json={"protein": 30, "carbs": 50, "fats": 10}
        )
        
        if meal_response.status_code == 200:
            print(f"   ✅ Meal logged successfully")
        else:
            print(f"   ⚠️  Meal logging status: {meal_response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Error logging meal: {e}")
    
    # Ask about progress
    print("\n2️⃣ User: 'What should I eat next?'")
    try:
        response = requests.post(
            f"{BASE_URL}/ai/message",
            headers=headers,
            json={"message": "What should I eat next?"}
        )
        
        if response.status_code == 200:
            reply = response.json().get('reply', 'No reply')
            print(f"   AI: {reply}")
            
            # Check if AI considers logged macros
            reply_lower = reply.lower()
            progress_keywords = ['remaining', 'left', 'more', 'already', 'logged', 'today', 'so far', 'progress']
            found_keywords = [word for word in progress_keywords if word in reply_lower]
            
            if found_keywords:
                print(f"\n   ✅ PASS: AI is considering today's progress!")
                print(f"   Found keywords: {', '.join(found_keywords)}")
                return True
            else:
                print(f"\n   ⚠️  WARNING: AI might not be using daily progress")
                print(f"   (Looking for: {', '.join(progress_keywords)})")
                return False
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    print("="*60)
    print("RAG PHASE 1 - PRODUCTION TESTING")
    print("Testing on: " + BASE_URL)
    print("="*60)
    
    # Get test token
    token = get_test_token()
    
    if not token:
        print("\n❌ Cannot proceed without authentication token")
        print("\nPlease ensure:")
        print("1. Railway backend is deployed and running")
        print("2. Test user exists (email: test@example.com, password: test123)")
        print("3. Or manually set TOKEN in the script")
        sys.exit(1)
    
    # Run tests
    results = []
    
    try:
        results.append(("Conversation Context", test_conversation_context(token)))
        results.append(("User Profile Awareness", test_user_profile_awareness(token)))
        results.append(("Daily Progress Context", test_daily_progress_context(token)))
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        sys.exit(1)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! RAG Phase 1 is working on production!")
        print("\nExpected improvements:")
        print("- AI remembers conversation context (last 5 messages)")
        print("- AI knows user's goals, targets, streak, and level")
        print("- AI considers today's logged meals")
        print("\nNext: Monitor user feedback and metrics")
    else:
        print("\n⚠️  Some tests failed. Check the logs above for details.")
        print("\nPossible issues:")
        print("- Railway deployment might still be in progress")
        print("- OpenAI API key might not be set")
        print("- Database connection issues")
        print("\nCheck Railway logs for more details")


if __name__ == "__main__":
    main()
