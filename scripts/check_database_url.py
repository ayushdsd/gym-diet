"""
Debug script to check DATABASE_URL configuration.
Run this in Railway to verify the database URL is being read correctly.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

print("=" * 60)
print("DATABASE URL CONFIGURATION CHECK")
print("=" * 60)

# Check ALL environment variables
print(f"\n0. All Environment Variables:")
all_vars = os.environ
db_related = {k: v for k, v in all_vars.items() if 'DATA' in k.upper() or 'DB' in k.upper() or 'POSTGRES' in k.upper()}
if db_related:
    for key, value in db_related.items():
        # Mask passwords
        if "@" in value and "://" in value:
            parts = value.split("@")
            user_pass = parts[0].split("://")[1]
            if ":" in user_pass:
                user = user_pass.split(":")[0]
                masked = value.replace(user_pass, f"{user}:****")
                print(f"   {key} = {masked}")
            else:
                print(f"   {key} = {value}")
        else:
            print(f"   {key} = {value}")
else:
    print("   ❌ No database-related environment variables found!")

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
    
    # Check if it contains localhost
    if "localhost" in raw_db_url:
        print("   ⚠️  WARNING: Contains 'localhost' - this is wrong for Railway!")
    elif "railway.app" in raw_db_url or "railway" in raw_db_url:
        print("   ✅ Contains Railway hostname - looks correct!")
else:
    print("   ❌ NOT SET")

# Try importing settings
print(f"\n2. Importing settings...")
try:
    from app.core.config import settings
    print("   ✅ Settings imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import settings: {e}")
    sys.exit(1)

# Check settings DATABASE_URL
print(f"\n3. Settings DATABASE_URL (after conversion):")
try:
    db_url = settings.DATABASE_URL
    if db_url:
        # Mask password
        if "@" in db_url:
            parts = db_url.split("@")
            user_pass = parts[0].split("://")[1]
            if ":" in user_pass:
                user = user_pass.split(":")[0]
                masked = db_url.replace(user_pass, f"{user}:****")
                print(f"   {masked}")
            else:
                print(f"   {db_url}")
        else:
            print(f"   {db_url}")
        
        # Check if it contains localhost
        if "localhost" in db_url:
            print("   ❌ ERROR: Still contains 'localhost'!")
            print("   This means the DATABASE_URL variable is not being read from Railway")
        elif "railway.app" in db_url or "railway" in db_url:
            print("   ✅ Contains Railway hostname - correct!")
    else:
        print("   ❌ NOT SET")
except Exception as e:
    print(f"   ❌ Error accessing DATABASE_URL: {e}")

# Check if conversion happened
print(f"\n4. URL Conversion Check:")
if raw_db_url and raw_db_url.startswith("postgres://"):
    if settings.DATABASE_URL.startswith("postgresql://"):
        print("   ✅ Successfully converted postgres:// to postgresql://")
    else:
        print("   ❌ Conversion failed!")
elif raw_db_url and raw_db_url.startswith("postgresql://"):
    print("   ✅ Already using postgresql://")
else:
    print("   ⚠️  Using default/local database URL")
    print("   This means DATABASE_URL is NOT set in Railway environment variables")

# Check other important settings
print(f"\n5. Other Settings:")
print(f"   JWT_SECRET: {'✅ SET' if settings.JWT_SECRET != 'change-this-secret' else '⚠️  Using default'}")
print(f"   OPENAI_API_KEY: {'✅ SET' if settings.OPENAI_API_KEY else '❌ NOT SET'}")

# Try to connect
print(f"\n6. Testing Database Connection:")
try:
    from sqlalchemy import create_engine, text
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("   ✅ Database connection successful!")
except Exception as e:
    print(f"   ❌ Database connection failed:")
    print(f"      {str(e)}")

print("\n" + "=" * 60)
print("DIAGNOSIS")
print("=" * 60)

if raw_db_url and "localhost" not in raw_db_url:
    print("✅ DATABASE_URL is set correctly in Railway")
    print("✅ Your deployment should work!")
elif raw_db_url and "localhost" in raw_db_url:
    print("❌ DATABASE_URL is set but contains 'localhost'")
    print("   Action: Check the value in Railway dashboard")
    print("   It should contain 'railway.app' not 'localhost'")
else:
    print("❌ DATABASE_URL is NOT set in Railway")
    print("   Action: Add DATABASE_URL variable in Railway dashboard")
    print("   1. Go to your PostgreSQL service")
    print("   2. Copy the DATABASE_URL value")
    print("   3. Add it to your web service variables")

print("=" * 60)
print("END OF CHECK")
print("=" * 60)
