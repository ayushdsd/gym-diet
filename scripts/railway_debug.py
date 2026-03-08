#!/usr/bin/env python3
"""
Comprehensive Railway debug script.
This should be run ON Railway to diagnose database connection issues.
"""
import os
import sys

print("=" * 80)
print("RAILWAY COMPREHENSIVE DEBUG")
print("=" * 80)

# 1. Check if we're on Railway
print("\n1. ENVIRONMENT DETECTION")
print("-" * 80)
railway_env = os.getenv("RAILWAY_ENVIRONMENT")
railway_project = os.getenv("RAILWAY_PROJECT_NAME")
railway_service = os.getenv("RAILWAY_SERVICE_NAME")

if railway_env:
    print(f"✅ Running on Railway")
    print(f"   Environment: {railway_env}")
    print(f"   Project: {railway_project}")
    print(f"   Service: {railway_service}")
else:
    print("⚠️  Not running on Railway (or Railway env vars not set)")

# 2. Check ALL environment variables
print("\n2. ALL ENVIRONMENT VARIABLES")
print("-" * 80)
all_vars = dict(os.environ)
print(f"Total environment variables: {len(all_vars)}")

# Show Railway-specific vars
railway_vars = {k: v for k, v in all_vars.items() if k.startswith("RAILWAY")}
if railway_vars:
    print("\nRailway variables:")
    for key, value in sorted(railway_vars.items()):
        print(f"   {key} = {value}")

# 3. Check DATABASE_URL specifically
print("\n3. DATABASE_URL ANALYSIS")
print("-" * 80)
db_url = os.getenv("DATABASE_URL")
if db_url:
    print(f"✅ DATABASE_URL is SET")
    print(f"   Length: {len(db_url)} characters")
    
    # Parse and mask
    if "://" in db_url and "@" in db_url:
        protocol = db_url.split("://")[0]
        rest = db_url.split("://")[1]
        
        if "@" in rest:
            creds, host_db = rest.split("@", 1)
            if ":" in creds:
                user, password = creds.split(":", 1)
                masked_url = f"{protocol}://{user}:{'*' * len(password)}@{host_db}"
            else:
                masked_url = f"{protocol}://{creds}@{host_db}"
        else:
            masked_url = db_url
    else:
        masked_url = db_url
    
    print(f"   Value: {masked_url}")
    
    # Analyze the URL
    if "localhost" in db_url or "127.0.0.1" in db_url:
        print("   ❌ ERROR: Contains localhost!")
        print("   This is wrong for Railway deployment")
    elif "railway.internal" in db_url or "railway.app" in db_url:
        print("   ✅ Contains Railway hostname - correct!")
    else:
        print("   ⚠️  Unknown hostname")
    
    if db_url.startswith("postgres://"):
        print("   ℹ️  Format: postgres:// (will be converted to postgresql://)")
    elif db_url.startswith("postgresql://"):
        print("   ℹ️  Format: postgresql:// (correct for SQLAlchemy)")
    else:
        print("   ⚠️  Unknown protocol")
else:
    print("❌ DATABASE_URL is NOT SET")
    print("   This is the problem!")

# 4. Check for .env file
print("\n4. .ENV FILE CHECK")
print("-" * 80)
env_file_exists = os.path.exists(".env")
print(f".env file exists: {env_file_exists}")
if env_file_exists:
    print("⚠️  WARNING: .env file exists in deployment!")
    print("   This file might override Railway's environment variables")
    print("   .env should NOT be in your Git repository")
    try:
        with open(".env", "r") as f:
            lines = f.readlines()
        print(f"   .env has {len(lines)} lines")
        # Check if DATABASE_URL is in .env
        for line in lines:
            if line.strip().startswith("DATABASE_URL"):
                print(f"   ⚠️  Found DATABASE_URL in .env: {line.strip()[:50]}...")
                print("   This is overriding Railway's DATABASE_URL!")
    except Exception as e:
        print(f"   Error reading .env: {e}")
else:
    print("✅ No .env file (correct for Railway)")

# 5. Try importing settings
print("\n5. SETTINGS MODULE")
print("-" * 80)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from app.core.config import settings
    print("✅ Settings imported successfully")
    
    # Check settings.DATABASE_URL
    settings_db_url = settings.DATABASE_URL
    print(f"\nSettings.DATABASE_URL:")
    
    # Mask password
    if "://" in settings_db_url and "@" in settings_db_url:
        protocol = settings_db_url.split("://")[0]
        rest = settings_db_url.split("://")[1]
        if "@" in rest:
            creds, host_db = rest.split("@", 1)
            if ":" in creds:
                user, password = creds.split(":", 1)
                masked = f"{protocol}://{user}:{'*' * len(password)}@{host_db}"
            else:
                masked = f"{protocol}://{creds}@{host_db}"
        else:
            masked = settings_db_url
    else:
        masked = settings_db_url
    
    print(f"   {masked}")
    
    # Compare with env var
    if db_url and settings_db_url != db_url and not settings_db_url.startswith("postgresql://"):
        print("   ⚠️  Settings DATABASE_URL differs from environment variable!")
    
    # Check if conversion happened
    if db_url and db_url.startswith("postgres://"):
        if settings_db_url.startswith("postgresql://"):
            print("   ✅ Successfully converted postgres:// to postgresql://")
        else:
            print("   ❌ Conversion failed!")
    
    # Check other settings
    print(f"\nOther settings:")
    print(f"   JWT_SECRET: {'SET' if settings.JWT_SECRET and settings.JWT_SECRET != 'change-this-secret' else 'NOT SET'}")
    print(f"   OPENAI_API_KEY: {'SET' if settings.OPENAI_API_KEY else 'NOT SET'}")
    
except Exception as e:
    print(f"❌ Failed to import settings: {e}")
    import traceback
    traceback.print_exc()

# 6. Test database connection
print("\n6. DATABASE CONNECTION TEST")
print("-" * 80)
try:
    from sqlalchemy import create_engine, text
    from app.core.config import settings
    
    print("Creating engine...")
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    
    print("Attempting connection...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ Database connection successful!")
        print(f"   PostgreSQL version: {version[:50]}...")
        
        # Try to get current database name
        result = conn.execute(text("SELECT current_database()"))
        db_name = result.fetchone()[0]
        print(f"   Connected to database: {db_name}")
        
except Exception as e:
    print(f"❌ Database connection failed!")
    print(f"   Error: {str(e)}")
    
    if "localhost" in str(e) or "127.0.0.1" in str(e):
        print("\n   DIAGNOSIS: Trying to connect to localhost")
        print("   This means DATABASE_URL is not set correctly")
    elif "password authentication failed" in str(e):
        print("\n   DIAGNOSIS: Authentication failed")
        print("   Check that DATABASE_URL has correct credentials")
    elif "could not translate host name" in str(e):
        print("\n   DIAGNOSIS: Cannot resolve hostname")
        print("   Check that DATABASE_URL has correct hostname")
    
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

# 7. Check Python environment
print("\n7. PYTHON ENVIRONMENT")
print("-" * 80)
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

# Check installed packages
try:
    import sqlalchemy
    print(f"SQLAlchemy version: {sqlalchemy.__version__}")
except:
    print("SQLAlchemy: NOT INSTALLED")

try:
    import psycopg2
    print(f"psycopg2 version: {psycopg2.__version__}")
except:
    print("psycopg2: NOT INSTALLED")

# 8. Final diagnosis
print("\n" + "=" * 80)
print("DIAGNOSIS")
print("=" * 80)

if not db_url:
    print("❌ PROBLEM: DATABASE_URL environment variable is NOT SET")
    print("\n📋 SOLUTION:")
    print("   1. Go to Railway dashboard")
    print("   2. Click on PostgreSQL service → Variables")
    print("   3. Copy the DATABASE_URL value")
    print("   4. Click on Web service → Variables")
    print("   5. Add DATABASE_URL variable with the copied value")
    print("   OR use reference: ${{Postgres.DATABASE_URL}}")
    
elif env_file_exists and "DATABASE_URL" in open(".env").read():
    print("❌ PROBLEM: .env file is overriding Railway's DATABASE_URL")
    print("\n📋 SOLUTION:")
    print("   1. Remove .env from Git: git rm --cached .env")
    print("   2. Commit: git commit -m 'Remove .env'")
    print("   3. Push: git push origin main")
    print("   4. Railway will redeploy without .env file")
    
elif "localhost" in db_url:
    print("❌ PROBLEM: DATABASE_URL contains localhost")
    print("\n📋 SOLUTION:")
    print("   The DATABASE_URL in Railway is set to localhost")
    print("   1. Go to Railway dashboard → Web service → Variables")
    print("   2. Edit DATABASE_URL")
    print("   3. Set it to: ${{Postgres.DATABASE_URL}}")
    print("   This will use the PostgreSQL service's URL")
    
else:
    print("✅ Configuration looks correct!")
    print("\nIf deployment still fails, check:")
    print("   1. PostgreSQL service is running (green status)")
    print("   2. Web service has DATABASE_URL variable")
    print("   3. No .env file in repository")
    print("   4. Deployment logs for specific errors")

print("=" * 80)
print("END OF DEBUG")
print("=" * 80)
