# Railway Database Not Connected - Fix Guide

## Problem Identified

The debug script shows:
```
⚠️  Using default/local database URL
postgresql+psycopg2://postgres:****@localhost:5432/gymdiet
```

This means **Railway is NOT setting the `DATABASE_URL` environment variable**. The PostgreSQL service is not connected to your web service.

## Solution: Connect PostgreSQL to Web Service

### Step 1: Check PostgreSQL Service Exists

1. Go to your Railway project: https://railway.app/dashboard
2. You should see TWO services:
   - Your web service (Python app)
   - PostgreSQL database service

If you DON'T see the PostgreSQL service, you need to add it:
- Click "+ New"
- Select "Database"
- Choose "PostgreSQL"
- Railway will create it

### Step 2: Connect Services (IMPORTANT!)

Railway needs to know that your web service should use the PostgreSQL database:

**Option A: Automatic Connection (Recommended)**

1. Click on your **PostgreSQL service**
2. Go to "Connect" tab
3. You should see your web service listed
4. If not listed, the services aren't connected

**Option B: Manual Connection via Variables**

1. Click on your **PostgreSQL service**
2. Go to "Variables" tab
3. Copy the `DATABASE_URL` value (it will look like: `postgresql://postgres:password@host:port/database`)
4. Click on your **web service**
5. Go to "Variables" tab
6. Click "+ New Variable"
7. Name: `DATABASE_URL`
8. Value: Paste the URL you copied
9. Click "Add"

### Step 3: Verify Connection

After connecting, check the variables:

1. Click on your **web service**
2. Go to "Variables" tab
3. You should now see `DATABASE_URL` with a value like:
   ```
   postgresql://postgres:xxxxx@containers-us-west-xxx.railway.app:5432/railway
   ```

### Step 4: Redeploy

1. Go to "Deployments" tab
2. Click "Deploy" or push a new commit to trigger deployment
3. Watch the logs

You should now see migrations run successfully!

## Alternative: Use Railway's Reference Variables

Railway can automatically reference the PostgreSQL service:

1. Click on your **web service**
2. Go to "Variables" tab
3. Click "+ New Variable"
4. Click "Add Reference"
5. Select your PostgreSQL service
6. Select `DATABASE_URL`
7. This creates a reference that automatically updates

## Verify It's Working

After connecting and redeploying, run the debug script again:

```bash
railway run python scripts/check_database_url.py
```

You should now see:
```
1. Raw DATABASE_URL from environment:
   postgresql://postgres:****@containers-us-west-xxx.railway.app:5432/railway

2. Settings DATABASE_URL (after conversion):
   postgresql://postgres:****@containers-us-west-xxx.railway.app:5432/railway

3. URL Conversion Check:
   ✅ Already using postgresql://

5. Testing Database Connection:
   ✅ Database connection successful!
```

## Common Issues

### Issue: PostgreSQL Service Not Created

**Solution**: Create it manually
1. Click "+ New" in your project
2. Select "Database" → "PostgreSQL"
3. Wait for it to provision

### Issue: Services in Different Projects

**Solution**: Both services must be in the SAME Railway project
- If they're in different projects, create a new PostgreSQL in the correct project

### Issue: DATABASE_URL Still Not Set

**Solution**: Manually copy and paste the URL
1. Get URL from PostgreSQL service variables
2. Add it to web service variables
3. Redeploy

### Issue: Wrong DATABASE_URL Format

**Solution**: Ensure it starts with `postgresql://` (not `postgres://`)
- Railway should provide `postgresql://` by default
- If it's `postgres://`, our code will convert it

## Test Your Deployment

Once DATABASE_URL is set correctly:

```bash
# Test the API
curl https://your-app.railway.app/docs

# Should show Swagger UI, not an error
```

## Summary

The issue is that Railway's PostgreSQL service is not connected to your web service. Follow these steps:

1. ✅ Verify PostgreSQL service exists
2. ✅ Connect PostgreSQL to web service (via Connect tab or manual variable)
3. ✅ Verify `DATABASE_URL` appears in web service variables
4. ✅ Redeploy
5. ✅ Test with debug script
6. ✅ Test API endpoints

Once connected, your deployment will succeed! 🚀
