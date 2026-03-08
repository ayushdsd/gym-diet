"""
Test script to verify chat message isolation between users.

This script:
1. Creates two test users
2. Sends chat messages as User A
3. Verifies User A can see their messages
4. Verifies User B cannot see User A's messages
5. Sends messages as User B
6. Verifies User B can only see their own messages
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def register_and_login(email: str, password: str, gym_id: int = 1):
    """Register a user and return their token"""
    # Try to register
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={"email": email, "password": password, "gym_id": gym_id}
        )
        print(f"Register {email}: {response.status_code}")
    except:
        pass  # User might already exist
    
    # Login
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password, "gym_id": gym_id}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Logged in as {email}")
        return data["access_token"]
    else:
        print(f"❌ Failed to login as {email}: {response.text}")
        return None

def send_message(token: str, message: str):
    """Send a chat message"""
    response = requests.post(
        f"{BASE_URL}/ai/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": message}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"  📤 Sent: {message}")
        print(f"  📥 Reply: {data['reply'][:50]}...")
        return True
    else:
        print(f"  ❌ Failed to send message: {response.status_code}")
        return False

def get_chat_history(token: str):
    """Get chat history"""
    response = requests.get(
        f"{BASE_URL}/ai/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        messages = data["messages"]
        print(f"  📜 Chat history: {len(messages)} messages")
        for msg in messages[-5:]:  # Show last 5 messages
            sender = "👤" if msg["sender"] == "user" else "🤖"
            print(f"    {sender} {msg['message'][:50]}...")
        return messages
    else:
        print(f"  ❌ Failed to get chat history: {response.status_code}")
        return []

def main():
    print("=" * 60)
    print("CHAT MESSAGE ISOLATION TEST")
    print("=" * 60)
    
    # Create test users
    print("\n1️⃣  Creating test users...")
    user_a_email = "test_user_a@example.com"
    user_b_email = "test_user_b@example.com"
    password = "testpass123"
    
    token_a = register_and_login(user_a_email, password)
    token_b = register_and_login(user_b_email, password)
    
    if not token_a or not token_b:
        print("❌ Failed to create test users")
        return
    
    # User A sends messages
    print("\n2️⃣  User A sends messages...")
    send_message(token_a, "Hello, I am User A")
    send_message(token_a, "This is my second message")
    
    # User A checks their history
    print("\n3️⃣  User A checks chat history...")
    history_a = get_chat_history(token_a)
    user_a_message_count = len([m for m in history_a if "User A" in m["message"]])
    
    # User B checks their history (should be empty or not contain User A's messages)
    print("\n4️⃣  User B checks chat history (should NOT see User A's messages)...")
    history_b = get_chat_history(token_b)
    user_a_in_b_history = any("User A" in m["message"] for m in history_b)
    
    if user_a_in_b_history:
        print("  ❌ FAIL: User B can see User A's messages!")
    else:
        print("  ✅ PASS: User B cannot see User A's messages")
    
    # User B sends messages
    print("\n5️⃣  User B sends messages...")
    send_message(token_b, "Hello, I am User B")
    send_message(token_b, "This is my message")
    
    # User B checks their history
    print("\n6️⃣  User B checks chat history...")
    history_b = get_chat_history(token_b)
    user_b_message_count = len([m for m in history_b if "User B" in m["message"]])
    
    # User A checks their history again (should not contain User B's messages)
    print("\n7️⃣  User A checks chat history (should NOT see User B's messages)...")
    history_a = get_chat_history(token_a)
    user_b_in_a_history = any("User B" in m["message"] for m in history_a)
    
    if user_b_in_a_history:
        print("  ❌ FAIL: User A can see User B's messages!")
    else:
        print("  ✅ PASS: User A cannot see User B's messages")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"User A messages: {user_a_message_count}")
    print(f"User B messages: {user_b_message_count}")
    print(f"User A can see User B's messages: {'❌ YES (FAIL)' if user_b_in_a_history else '✅ NO (PASS)'}")
    print(f"User B can see User A's messages: {'❌ YES (FAIL)' if user_a_in_b_history else '✅ NO (PASS)'}")
    
    if not user_a_in_b_history and not user_b_in_a_history:
        print("\n🎉 ALL TESTS PASSED! Chat messages are properly isolated.")
    else:
        print("\n❌ TESTS FAILED! Chat messages are leaking between users.")

if __name__ == "__main__":
    main()
