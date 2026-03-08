"""
Initialize Railway database with gyms and test data.

Usage:
    python scripts/init_railway_db.py --url https://your-app.railway.app
"""

import requests
import argparse
import sys

def create_gyms(base_url: str):
    """Create initial gyms"""
    gyms = [
        {"name": "Downtown Fitness", "location": "New York"},
        {"name": "Westside Gym", "location": "Los Angeles"},
        {"name": "Central Training", "location": "Chicago"},
        {"name": "Northside Athletics", "location": "Houston"},
        {"name": "Southside Strength", "location": "Phoenix"},
    ]
    
    print("Creating gyms...")
    created_count = 0
    
    for gym in gyms:
        try:
            response = requests.post(f"{base_url}/gyms", json=gym)
            if response.status_code in [200, 201]:
                print(f"  ✅ Created: {gym['name']} ({gym['location']})")
                created_count += 1
            elif response.status_code == 400:
                print(f"  ⚠️  Already exists: {gym['name']}")
            else:
                print(f"  ❌ Failed: {gym['name']} - Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error creating {gym['name']}: {e}")
    
    print(f"\nCreated {created_count} new gyms")
    return created_count

def test_api(base_url: str):
    """Test API endpoints"""
    print("\nTesting API endpoints...")
    
    # Test docs
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("  ✅ /docs - OK")
        else:
            print(f"  ❌ /docs - Status {response.status_code}")
    except Exception as e:
        print(f"  ❌ /docs - Error: {e}")
    
    # Test gyms list
    try:
        response = requests.get(f"{base_url}/gyms")
        if response.status_code == 200:
            gyms = response.json()
            print(f"  ✅ /gyms - OK ({len(gyms)} gyms)")
        else:
            print(f"  ❌ /gyms - Status {response.status_code}")
    except Exception as e:
        print(f"  ❌ /gyms - Error: {e}")

def create_test_user(base_url: str):
    """Create a test user"""
    print("\nCreating test user...")
    
    user_data = {
        "email": "test@example.com",
        "password": "testpass123",
        "gym_id": 1
    }
    
    try:
        response = requests.post(f"{base_url}/auth/register", json=user_data)
        if response.status_code in [200, 201]:
            print("  ✅ Test user created")
            print(f"     Email: {user_data['email']}")
            print(f"     Password: {user_data['password']}")
            return True
        elif response.status_code == 400:
            print("  ⚠️  Test user already exists")
            return True
        else:
            print(f"  ❌ Failed to create test user - Status {response.status_code}")
            print(f"     Response: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Error creating test user: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Initialize Railway database')
    parser.add_argument('--url', required=True, help='Railway app URL (e.g., https://your-app.railway.app)')
    parser.add_argument('--skip-test-user', action='store_true', help='Skip creating test user')
    
    args = parser.parse_args()
    base_url = args.url.rstrip('/')
    
    print("=" * 60)
    print("RAILWAY DATABASE INITIALIZATION")
    print("=" * 60)
    print(f"Backend URL: {base_url}")
    print()
    
    # Test API
    test_api(base_url)
    
    # Create gyms
    print()
    created = create_gyms(base_url)
    
    # Create test user
    if not args.skip_test_user:
        create_test_user(base_url)
    
    print()
    print("=" * 60)
    print("INITIALIZATION COMPLETE")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Visit your API docs:", f"{base_url}/docs")
    print("2. Test the mobile app with the Railway URL")
    print("3. Create more users via the app")
    print()
    
    if created > 0:
        print("✅ Database initialized successfully!")
    else:
        print("⚠️  No new data created (may already exist)")

if __name__ == "__main__":
    main()
