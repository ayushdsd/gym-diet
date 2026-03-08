#!/usr/bin/env python3
"""
Initialize Railway database with gym locations
"""
import requests
import sys

# Get Railway URL from command line
if len(sys.argv) < 2:
    print("Usage: python scripts/init_railway_gyms.py <RAILWAY_URL>")
    print("Example: python scripts/init_railway_gyms.py https://your-app.railway.app")
    sys.exit(1)

RAILWAY_URL = sys.argv[1].rstrip('/')

# Gym data
gyms = [
    {"name": "Gym Alpha", "location": "Downtown"},
    {"name": "Gym Beta", "location": "Uptown"},
    {"name": "Gym Gamma", "location": "Midtown"},
]

print(f"Initializing gyms on {RAILWAY_URL}...")
print("=" * 60)

for gym in gyms:
    try:
        response = requests.post(
            f"{RAILWAY_URL}/gyms",
            json=gym,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Created: {gym['name']} at {gym['location']} (ID: {data['id']})")
        elif response.status_code == 400:
            print(f"ℹ️  Already exists: {gym['name']}")
        else:
            print(f"❌ Failed: {gym['name']} - Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error creating {gym['name']}: {e}")

print("=" * 60)
print("Done! Gyms initialized.")
