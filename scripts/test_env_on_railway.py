#!/usr/bin/env python3
"""
Simple test to verify DATABASE_URL is being read on Railway
"""
import os
import sys

print("=" * 80)
print("SIMPLE ENVIRONMENT TEST")
print("=" * 80)

# Check if we're on Railway
railway_env = os.getenv("RAILWAY_ENVIRONMENT")
print(f"\n1. RAILWAY_ENVIRONMENT: {railway_env}")

# Check DATABASE_URL directly from os.getenv
db_url = os.getenv("DATABASE_URL")
print(f"\n2. DATABASE_URL from os.getenv():")
if db_url:
    # Mask password
    if "@" in db_url:
        parts = db_url.split("@")
        masked = parts[0].split(":")[0] + ":****@" + parts[1]
        print(f"   {masked}")
    else:
        print(f"   {db_url}")
    
    if "localhost" in db_url:
        print("   ❌ ERROR: Contains localhost!")
        print("   This means DATABASE_URL is NOT set in Railway")
        sys.exit(1)
    else:
        print("   ✅ Does not contain localhost")
else:
    print("   ❌ NOT SET")
    print("   This means DATABASE_URL environment variable is missing")
    sys.exit(1)

# Check if .env file exists
env_exists = os.path.exists(".env")
print(f"\n3. .env file exists: {env_exists}")
if env_exists:
    print("   ⚠️  WARNING: .env file should not be in Railway deployment!")

print("\n" + "=" * 80)
print("If you see this, DATABASE_URL is set correctly!")
print("=" * 80)
