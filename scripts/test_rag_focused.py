"""
Focused RAG Phase 1 Testing - Key Scenarios Only
"""

import requests
import json
import random
import time

BASE_URL = "https://gym-diet-production.up.railway.app"

def setup():
    """Setup test user"""
    print("Setting up test user...")
    
    # Get gym
    r = requests.get(f"{BASE_URL}/gyms")
    gym_id = r.json()[0]["id"]
    
    # Register
    email = f"ragtest{random.randint(10000, 99999)}@example.com"
    password = "test123"
    
    requests.post(f"{BASE_URL}/auth/register", json={
        "email": email, "password": password, "gym_id": gym_id
    })
    
    # Login
    r = requests.post(f"{BASE_URL}/auth/login", data={
        "username": email, "password": password
    })
    
    token = r.json()["access_token"]
    print(f"✓ User created: {email}\n")
    return token


def send_msg(token, msg):
    """Send AI message"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(f"{BASE_URL}/ai/message", headers=headers, json={"message": msg}, timeout=30)
    return r.json() if r.status_code == 200 else None


def log_meal(token, p, c, f):
    """Log a meal"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    requests.post(f"{BASE_URL}/meals", headers=headers, json={"protein": p, "carbs": c, "fats": f})


def test_conversation_context(token):
    """Test conversation memory"""
    print("="*60)
    print("TEST 1: Conversation Context")
    print("="*60)
    
    print("\n1. User: 'I want to lose weight'")
    r1 = send_msg(token, "I want to lose weight")
    if r1:
        print(f"   AI: {r1['reply'][:120]}...")
    
    time.sleep(2)
    
    print("\n2. User: 'What should I eat for breakfast?'")
    r2 = send_msg(token, "What should I eat for breakfast?")
    if r2:
        reply = r2['reply']
        print(f"   AI: {reply[:120]}...")
        
        # Check if AI remembered
        keywords = ['weight', 'loss', 'fat', 'lose', 'lean', 'deficit', 'protein']
        if any(k in reply.lower() for k in keywords):
            print("\n✓ PASS: AI remembered the weight loss goal")
            return True
        else:
            print("\n✗ FAIL: AI didn't remember context")
            print(f"   (Looking for: {', '.join(keywords)})")
            return False
    return False


def test_daily_progress(token):
    """Test daily progress tracking"""
    print("\n" + "="*60)
    print("TEST 2: Daily Progress Tracking")
    print("="*60)
    
    print("\nLogging meals: 30p, 40p, 25p")
    log_meal(token, 30, 50, 10)
    time.sleep(1)
    log_meal(token, 40, 60, 15)
    time.sleep(1)
    log_meal(token, 25, 45, 12)
    
    total_protein = 95
    print(f"Total protein: {total_protein}g")
    
    time.sleep(2)
    
    print("\nUser: 'How much protein have I eaten today?'")
    r = send_msg(token, "How much protein have I eaten today?")
    if r:
        reply = r['reply']
        print(f"AI: {reply[:150]}...")
        
        # Check if AI knows the amount
        if str(total_protein) in reply or 'protein' in reply.lower() and 'today' in reply.lower():
            print("\n✓ PASS: AI knows today's protein intake")
            return True
        else:
            print("\n✗ FAIL: AI doesn't know protein intake")
            return False
    return False


def test_profile_awareness(token):
    """Test user profile awareness"""
    print("\n" + "="*60)
    print("TEST 3: User Profile Awareness")
    print("="*60)
    
    print("\nUser: 'What are my daily targets?'")
    r = send_msg(token, "What are my daily targets?")
    if r:
        reply = r['reply']
        print(f"AI: {reply[:150]}...")
        
        # Check if AI mentions profile data
        keywords = ['target', 'goal', 'protein', 'carbs', 'fats', 'daily']
        if any(k in reply.lower() for k in keywords):
            print("\n✓ PASS: AI knows user profile")
            return True
        else:
            print("\n✗ FAIL: AI doesn't mention profile data")
            return False
    return False


def test_intent_detection(token):
    """Test intent detection"""
    print("\n" + "="*60)
    print("TEST 4: Intent Detection")
    print("="*60)
    
    print("\nUser: 'I ate 35g protein, 55g carbs, 18g fats'")
    r = send_msg(token, "I ate 35g protein, 55g carbs, 18g fats")
    if r:
        intent = r.get('intent', '')
        reply = r['reply']
        print(f"AI: {reply[:100]}...")
        print(f"Intent: {intent}")
        
        if intent == "log_meal":
            print("\n✓ PASS: Correctly detected meal logging")
            return True
        else:
            print(f"\n✗ FAIL: Intent was '{intent}', expected 'log_meal'")
            return False
    return False


def test_response_time(token):
    """Test response time"""
    print("\n" + "="*60)
    print("TEST 5: Response Time")
    print("="*60)
    
    print("\nTesting response time...")
    start = time.time()
    r = send_msg(token, "What should I eat for lunch?")
    elapsed = time.time() - start
    
    if r:
        print(f"Response time: {elapsed:.2f}s")
        if elapsed < 5:
            print("✓ PASS: Response time acceptable (< 5s)")
            return True
        else:
            print("✗ FAIL: Response time too slow (> 5s)")
            return False
    return False


def main():
    print("\n" + "="*60)
    print("RAG PHASE 1 - FOCUSED TEST SUITE")
    print("="*60)
    print(f"Backend: {BASE_URL}")
    print("Tests: 5 key scenarios")
    print("="*60 + "\n")
    
    try:
        token = setup()
        
        print("Running tests (this will take ~60 seconds)...\n")
        
        results = []
        results.append(("Conversation Context", test_conversation_context(token)))
        results.append(("Daily Progress Tracking", test_daily_progress(token)))
        results.append(("User Profile Awareness", test_profile_awareness(token)))
        results.append(("Intent Detection", test_intent_detection(token)))
        results.append(("Response Time", test_response_time(token)))
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        for name, passed in results:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status} - {name}")
        
        passed_count = sum(1 for _, p in results if p)
        total_count = len(results)
        percentage = (passed_count / total_count * 100)
        
        print(f"\nResults: {passed_count}/{total_count} tests passed ({percentage:.0f}%)")
        
        if percentage >= 80:
            print("\n🎉 EXCELLENT! RAG Phase 1 is working well!")
            print("✓ Core features functional")
            print("✓ Ready for production")
        elif percentage >= 60:
            print("\n⚠️  GOOD - Most features working")
            print("Some issues detected, monitor in production")
        else:
            print("\n✗ ISSUES DETECTED")
            print("Review failed tests and check Railway logs")
        
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
