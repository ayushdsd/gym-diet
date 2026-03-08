# Railway Database Connection - Final Fix

## Root Cause
Railway's PostgreSQL DATABASE_URL is NOT being set in your web service environment.

Your debug output shows:
```
Raw DATABASE_URL from environment:
postgresql+psycopg2://postgres:****@localhost:5432/gymdiet
```

This is the DEFAULT value from `config.py`, NOT Railway's PostgreSQL URL.
Railway's PostgreSQL URL should look like: `postgres://postgres:****@postgres.railway.internal:5432/railway`

## The Real Problem
Railway's PostgreSQL service is not properly connected to your web service.

## Solution: Connect PostgreSQL to Web Service

### Step 1: Check PostgreSQL Service
1. Go to your Railway project dashboard
2. You should see TWO services:
   - Your web service (the main app)
   - PostgreSQL service

### Step 2: Get the DATABASE_URL from PostgreSQL
1. Click on the PostgreSQL service
2. Go to the "Variables" tab
3. You should see a variable called `DATABASE_URL`
4. Copy this value (it starts with `postgres://`)

### Step 3: Add DATABASE_URL to Web Service
1. Click on your web service (not PostgreSQL)
2. Go to the "Variables" tab
3. Click "New Variable"
4. Add:
   - Variable name: `DATABASE_URL`
   - Value: Paste the URL you copied from PostgreSQL service
5. Click "Add"

### Step 4: Alternative - Use Reference Variable (Recommended)
Instead of copying the URL, use Railway's reference feature:
1. In your web service Variables tab
2. Click "New Variable"
3. Variable name: `DATABASE_URL`
4. Value: `${{Postgres.DATABASE_URL}}` (replace "Postgres" with your PostgreSQL service name)
5. This automatically uses the PostgreSQL URL and updates if it changes

### Step 5: Redeploy
After adding the variable, Railway should automatically redeploy.
If not, click "Deploy" → "Redeploy"

## Verification
After redeployment, check the logs. The debug script should show:
```
1. Raw DATABASE_URL from environment:
postgres://postgres:****@postgres.railway.internal:5432/railway

2. Settings DATABASE_URL (after conversion):
postgresql+psycopg2://postgres:****@postgres.railway.internal:5432/railway

3. URL Conversion Check:
✅ Using Railway PostgreSQL database
```

## Common Issues

### Issue 1: PostgreSQL Service Not Created
If you don't see a PostgreSQL service:
1. Click "New" → "Database" → "Add PostgreSQL"
2. Wait for it to provision
3. Then follow steps above to connect it

### Issue 2: Wrong Service Name in Reference
If using `${{Postgres.DATABASE_URL}}` doesn't work:
1. Check the exact name of your PostgreSQL service
2. Use that name: `${{YourServiceName.DATABASE_URL}}`

### Issue 3: Variables Not Updating
1. Delete the DATABASE_URL variable from web service
2. Wait 10 seconds
3. Add it again
4. Redeploy

## Why This Happens
Railway services are isolated by default. Even though you created a PostgreSQL service, it doesn't automatically set DATABASE_URL in your web service. You must explicitly connect them by:
- Copying the DATABASE_URL, OR
- Using a reference variable like `${{Postgres.DATABASE_URL}}`

## Next Steps After Success
1. Database migrations will run automatically (in startCommand)
2. Initialize gyms: `python scripts/init_railway_db.py`
3. Update mobile API URL
4. Build APK
