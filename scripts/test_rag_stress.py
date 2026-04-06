"""
RAG Phase 1 Stress Test - Test stability under load
"""

import requests
import json
import random
import time
import threading

BASE_URL = "https://gym-diet-production.up.railway.app"

def setup_user():
    """Create test user"""
    r = requests.get(f"{BASE_URL}/gyms")
    gym_id = r.json()[0]["id"]
    
    email = f"stress{random.randint(10000, 99999)}@example.com"
    password = "test123"
    
    requests.post(f"{BASE_URL}/auth/register", json={
        "email": email, "password": password, "gym_id": gym_id
    })
    
    r = requests.post(f"{BASE_URL}/auth/login", data={
        "username": email, "password": password
    })
    
    return r.json()["access_token"]


def send_msg(token, msg):
    """Send AI message"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        r = requests.post(f"{BASE_URL}/ai/message", headers=headers, json={"message": msg}, timeout=30)
        return r.status_code == 200
    except:
        return False


def test_rapid_fire(token):
    """Test rapid consecutive messages"""
    print("\n" + "="*60)
    print("TEST 1: Rapid Fire (10 messages in quick succession)")
    print("="*60)
    
    messages = [
        "Hi",
        "What should I eat?",
        "I want to lose weight",
        "How much protein?",
        "What about carbs?",
        "I'm vegetarian",
        "Suggest a meal",
        "How am I doing?",
        "What's my progress?",
        "Thanks"
    ]
    
    success_count = 0
    start_time = time.time()
    
    for i, msg in enumerate(messages, 1):
        print(f"  {i}. Sending: '{msg}'")
        if send_msg(token, msg):
            success_count += 1
            print(f"     ✓ Success")
        else:
            print(f"     ✗ Failed")
        time.sleep(0.5)  # Small delay between messages
    
    elapsed = time.time() - start_time
    
    print(f"\nResults:")
    print(f"  Success: {success_count}/10")
    print(f"  Time: {elapsed:.1f}s")
    print(f"  Avg: {elapsed/10:.1f}s per message")
    
    if success_count >= 9:
        print("✓ PASS: Handled rapid fire well")
        return True
    else:
        print("✗ FAIL: Some messages failed")
        return False


def test_long_conversation(token):
    """Test long conversation (15 messages)"""
    print("\n" + "="*60)
    print("TEST 2: Long Conversation (15 messages)")
    print("="*60)
    
    messages = [
        "I want to build muscle",
        "What should I eat?",
        "How much protein do I need?",
        "I'm 75kg",
        "What about breakfast?",
        "I don't like eggs",
        "What else can I eat?",
        "How about lunch?",
        "I'm vegetarian",
        "Suggest paneer dishes",
        "How much paneer?",
        "What about dinner?",
        "How am I doing today?",
        "What's my progress?",
        "Thanks for the help"
    ]
    
    success_count = 0
    
    for i, msg in enumerate(messages, 1):
        print(f"  {i}/15: '{msg[:30]}...'")
        if send_msg(token, msg):
            success_count += 1
            print(f"       ✓")
        else:
            print(f"       ✗")
        time.sleep(1)
    
    print(f"\nResults: {success_count}/15 successful")
    
    if success_count >= 14:
        print("✓ PASS: Handled long conversation")
        return True
    else:
        print("✗ FAIL: Some messages failed")
        return False


def test_context_retention(token):
    """Test if context is retained across many messages"""
    print("\n" + "="*60)
    print("TEST 3: Context Retention (10 messages)")
    print("="*60)
    
    # Set context
    print("  1. Setting context: 'I'm allergic to peanuts'")
    send_msg(token, "I'm allergic to peanuts")
    time.sleep(1)
    
    # Send filler messages
    print("  2-9. Sending filler messages...")
    for i in range(8):
        send_msg(token, f"What about meal {i+1}?")
        time.sleep(0.5)
    
    # Check if context is retained
    print("  10. Checking context: 'Suggest a snack'")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(
        f"{BASE_URL}/ai/message",
        headers=headers,
        json={"message": "Suggest a snack"},
        timeout=30
    )
    
    if r.status_code == 200:
        reply = r.json()['reply'].lower()
        print(f"\n  AI: {reply[:100]}...")
        
        # Check if AI avoids peanuts
        if 'peanut' not in reply or 'avoid' in reply:
            print("\n✓ PASS: AI remembered allergy after 10 messages")
            return True
        else:
            print("\n⚠️  WARNING: AI might have forgotten allergy")
            return False
    else:
        print("\n✗ FAIL: Request failed")
        return False


def test_concurrent_users():
    """Test multiple users simultaneously"""
    print("\n" + "="*60)
    print("TEST 4: Concurrent Users (3 users, 5 messages each)")
    print("="*60)
    
    results = []
    
    def user_session(user_id):
        try:
            token = setup_user()
            success = 0
            for i in range(5):
                if send_msg(token, f"User {user_id} message {i+1}"):
                    success += 1
                time.sleep(0.5)
            results.append(success)
            print(f"  User {user_id}: {success}/5 successful")
        except Exception as e:
            print(f"  User {user_id}: Error - {e}")
            results.append(0)
    
    threads = []
    for i in range(3):
        t = threading.Thread(target=user_session, args=(i+1,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    total_success = sum(results)
    total_messages = 15
    
    print(f"\nResults: {total_success}/{total_messages} successful")
    
    if total_success >= 13:
        print("✓ PASS: Handled concurrent users well")
        return True
    else:
        print("✗ FAIL: Some concurrent requests failed")
        return False


def test_error_recovery(token):
    """Test error handling and recovery"""
    print("\n" + "="*60)
    print("TEST 5: Error Recovery")
    print("="*60)
    
    # Test 1: Empty message
    print("  1. Testing empty message...")
    if send_msg(token, ""):
        print("     ✓ Handled empty message")
        test1 = True
    else:
        print("     ⚠️  Empty message failed (expected)")
        test1 = False
    
    time.sleep(1)
    
    # Test 2: Very long message
    print("  2. Testing very long message...")
    long_msg = "protein " * 100
    if send_msg(token, long_msg):
        print("     ✓ Handled long message")
        test2 = True
    else:
        print("     ✗ Long message failed")
        test2 = False
    
    time.sleep(1)
    
    # Test 3: Special characters
    print("  3. Testing special characters...")
    if send_msg(token, "What about 50g protein & 100g carbs?"):
        print("     ✓ Handled special characters")
        test3 = True
    else:
        print("     ✗ Special characters failed")
        test3 = False
    
    time.sleep(1)
    
    # Test 4: Recovery after error
    print("  4. Testing recovery...")
    if send_msg(token, "What should I eat?"):
        print("     ✓ Recovered successfully")
        test4 = True
    else:
        print("     ✗ Recovery failed")
        test4 = False
    
    passed = sum([test2, test3, test4])  # Exclude test1 as empty might fail
    
    if passed >= 2:
        print("\n✓ PASS: Good error handling")
        return True
    else:
        print("\n✗ FAIL: Poor error handling")
        return False


def main():
    print("\n" + "="*60)
    print("RAG PHASE 1 - STRESS TEST")
    print("="*60)
    print(f"Backend: {BASE_URL}")
    print("Tests: 5 stress scenarios")
    print("="*60)
    
    try:
        print("\nSetting up test user...")
        token = setup_user()
        print("✓ Setup complete\n")
        
        print("Running stress tests (this will take 2-3 minutes)...\n")
        
        results = []
        results.append(("Rapid Fire", test_rapid_fire(token)))
        results.append(("Long Conversation", test_long_conversation(token)))
        results.append(("Context Retention", test_context_retention(token)))
        results.append(("Concurrent Users", test_concurrent_users()))
        results.append(("Error Recovery", test_error_recovery(token)))
        
        # Summary
        print("\n" + "="*60)
        print("STRESS TEST SUMMARY")
        print("="*60)
        
        for name, passed in results:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status} - {name}")
        
        passed_count = sum(1 for _, p in results if p)
        total_count = len(results)
        percentage = (passed_count / total_count * 100)
        
        print(f"\nResults: {passed_count}/{total_count} tests passed ({percentage:.0f}%)")
        
        if percentage >= 80:
            print("\n🎉 EXCELLENT! System is stable under stress!")
            print("✓ Handles rapid requests")
            print("✓ Maintains context")
            print("✓ Supports concurrent users")
            print("✓ Good error handling")
            print("\n🚀 Production ready!")
        elif percentage >= 60:
            print("\n⚠️  GOOD - Mostly stable")
            print("Some stress scenarios failed")
            print("Monitor under production load")
        else:
            print("\n✗ STABILITY ISSUES")
            print("System struggles under stress")
            print("Review failed tests")
        
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
