#!/usr/bin/env python3
"""
Create test gyms for development
"""
import requests
import sys

API_BASE = "http://localhost:8000"

def create_gym(name: str, location: str):
    """Create a gym"""
    try:
        response = requests.post(
            f"{API_BASE}/gyms",
            json={"name": name, "location": location}
        )
        
        if response.status_code == 201:
            gym = response.json()
            print(f"✅ Created gym: {gym['name']} in {gym['location']} (ID: {gym['id']})")
            return gym
        elif response.status_code == 400:
            print(f"⚠️  Gym '{name}' already exists")
            return None
        else:
            print(f"❌ Failed to create gym '{name}': {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to backend at {API_BASE}")
        print("   Make sure the backend is running: uvicorn app.main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error creating gym '{name}': {e}")
        return None

def main():
    print("Creating test gyms with locations...\n")
    
    # Create test gyms with different locations
    gyms = [
        ("PowerFit Gym", "New York"),
        ("Elite Fitness", "New York"),
        ("Iron Paradise", "Los Angeles"),
        ("Muscle Factory", "Los Angeles"),
        ("FitZone", "Chicago"),
        ("Strength Hub", "Chicago"),
        ("Peak Performance", "Miami"),
        ("Apex Gym", "Miami"),
    ]
    
    created_gyms = []
    for gym_name, location in gyms:
        gym = create_gym(gym_name, location)
        if gym:
            created_gyms.append(gym)
    
    print(f"\n{'='*50}")
    print(f"Summary: {len(created_gyms)} gyms created/verified")
    print(f"{'='*50}\n")
    
    if created_gyms:
        # Group by location
        locations = {}
        for gym in created_gyms:
            loc = gym['location']
            if loc not in locations:
                locations[loc] = []
            locations[loc].append(gym['name'])
        
        print("Gyms by location:")
        for location, gym_names in sorted(locations.items()):
            print(f"\n  📍 {location}:")
            for name in gym_names:
                print(f"     - {name}")
    
    print("\n💡 You can now:")
    print("   1. Start the mobile app: cd mobile && npx expo start")
    print("   2. Select a location")
    print("   3. Select a gym from that location")
    print("   4. Create a new account or login")

if __name__ == "__main__":
    main()
