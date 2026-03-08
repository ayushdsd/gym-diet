"""
Debug script to check DATABASE_URL configuration.
Run this in Railway to verify the database URL is being read correctly.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings

print("=" * 60)
print("DATABASE URL CONFIGURATION CHECK")
print("=" * 60)

# Check raw environment variable
raw_db_url = os.getenv("DATABASE_URL")
print(f"\n1. Raw DATABASE_URL from environment:")
if raw_db_url:
    # Mask password for security
    if "@" in raw_db_url:
        parts = raw_db_url.split("@")
        user_pass = parts[0].split("://")[1]
        if ":" in user_pass:
            user = user_pass.split(":")[0]
            masked = raw_db_url.replace(user_pass, f"{user}:****")
            print(f"   {masked}")
        else:
            print(f"   {raw_db_url}")
    else:
        print(f"   {raw_db_url}")
else:
    print("   ❌ NOT SET")

# Check settings DATABASE_URL
print(f"\n2. Settings DATABASE_URL (after conversion):")
if settings.DATABASE_URL:
    # Mask password
    if "@" in settings.DATABASE_URL:
        parts = settings.DATABASE_URL.split("@")
        user_pass = parts[0].split("://")[1]
        if ":" in user_pass:
            user = user_pass.split(":")[0]
            masked = settings.DATABASE_URL.replace(user_pass, f"{user}:****")
            print(f"   {masked}")
        else:
            print(f"   {settings.DATABASE_URL}")
    else:
        print(f"   {settings.DATABASE_URL}")
else:
    print("   ❌ NOT SET")

# Check if conversion happened
print(f"\n3. URL Conversion Check:")
if raw_db_url and raw_db_url.startswith("postgres://"):
    if settings.DATABASE_URL.startswith("postgresql://"):
        print("   ✅ Successfully converted postgres:// to postgresql://")
    else:
        print("   ❌ Conversion failed!")
elif raw_db_url and raw_db_url.startswith("postgresql://"):
    print("   ✅ Already using postgresql://")
else:
    print("   ⚠️  Using default/local database URL")

# Check other important settings
print(f"\n4. Other Settings:")
print(f"   JWT_SECRET: {'✅ SET' if settings.JWT_SECRET != 'change-this-secret' else '⚠️  Using default'}")
print(f"   OPENAI_API_KEY: {'✅ SET' if settings.OPENAI_API_KEY else '❌ NOT SET'}")

# Try to connect
print(f"\n5. Testing Database Connection:")
try:
    from sqlalchemy import create_engine
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("   ✅ Database connection successful!")
except Exception as e:
    print(f"   ❌ Database connection failed:")
    print(f"      {str(e)}")

print("\n" + "=" * 60)
print("END OF CHECK")
print("=" * 60)
