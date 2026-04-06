"""
Test RAG Phase 1 Implementation
Tests conversation context and user profile awareness
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
# Replace with your test user token
TOKEN = "YOUR_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def test_conversation_context():
    """Test that AI remembers previous messages"""
    print("\n=== TEST 1: Conversation Context ===")
    
    # First message
    print("\n1. User: 'I want to lose weight'")
    response1 = requests.post(
        f"{BASE_URL}/ai/message",
        headers=headers,
        json={"message": "I want to lose weight"}
    )
    print(f"   AI: {response1.json().get('reply', 'ERROR')}")
    
    # Second message (should remember first)
    print("\n2. User: 'What should I eat for breakfast?'")
    response2 = requests.post(
        f"{BASE_URL}/ai/message",
        headers=headers,
        json={"message": "What should I eat for breakfast?"}
    )
    print(f"   AI: {response2.json().get('reply', 'ERROR')}")
    
    # Check if AI references weight loss goal
    reply = response2.json().get('reply', '').lower()
    if 'weight' in reply or 'loss' in reply or 'fat' in reply:
        print("\n   ✅ PASS: AI remembered the weight loss goal!")
    else:
        print("\n   ⚠️  WARNING: AI might not have remembered the goal")


def test_user_profile_awareness():
    """Test that AI knows user's profile and progress"""
    print("\n\n=== TEST 2: User Profile Awareness ===")
    
    print("\nUser: 'How am I doing today?'")
    response = requests.post(
        f"{BASE_URL}/ai/message",
        headers=headers,
        json={"message": "How am I doing today?"}
    )
    print(f"AI: {response.json().get('reply', 'ERROR')}")
    
    # Check if AI mentions profile data
    reply = response.json().get('reply', '').lower()
    if any(word in reply for word in ['streak', 'level', 'target', 'goal', 'protein']):
        print("\n✅ PASS: AI is aware of user profile!")
    else:
        print("\n⚠️  WARNING: AI might not be using profile data")


def test_daily_progress_context():
    """Test that AI considers today's logged meals"""
    print("\n\n=== TEST 3: Daily Progress Context ===")
    
    # Log a meal first
    print("\n1. Logging a meal: 30g protein, 50g carbs, 10g fats")
    meal_response = requests.post(
        f"{BASE_URL}/meals",
        headers=headers,
        json={"protein": 30, "carbs": 50, "fats": 10}
    )
    print(f"   Meal logged: {meal_response.status_code == 200}")
    
    # Ask about progress
    print("\n2. User: 'What should I eat next?'")
    response = requests.post(
        f"{BASE_URL}/ai/message",
        headers=headers,
        json={"message": "What should I eat next?"}
    )
    print(f"   AI: {response.json().get('reply', 'ERROR')}")
    
    # Check if AI considers logged macros
    reply = response.json().get('reply', '').lower()
    if any(word in reply for word in ['remaining', 'left', 'more', 'already', 'logged']):
        print("\n   ✅ PASS: AI is considering today's progress!")
    else:
        print("\n   ⚠️  WARNING: AI might not be using daily progress")


def main():
    print("=" * 60)
    print("RAG PHASE 1 - TESTING")
    print("=" * 60)
    
    if TOKEN == "YOUR_TOKEN_HERE":
        print("\n❌ ERROR: Please set your TOKEN in the script")
        print("\nTo get a token:")
        print("1. Login via API or mobile app")
        print("2. Copy the access_token from the response")
        print("3. Update TOKEN variable in this script")
        sys.exit(1)
    
    try:
        # Run tests
        test_conversation_context()
        test_user_profile_awareness()
        test_daily_progress_context()
        
        print("\n" + "=" * 60)
        print("TESTING COMPLETE")
        print("=" * 60)
        print("\nIf all tests passed, RAG Phase 1 is working! 🎉")
        print("\nExpected improvements:")
        print("- AI remembers conversation context (last 5 messages)")
        print("- AI knows user's goals, targets, streak, and level")
        print("- AI considers today's logged meals")
        print("\nNext: Deploy to Railway and monitor metrics")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend")
        print("Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    main()
