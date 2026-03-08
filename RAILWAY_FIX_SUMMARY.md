# Railway Database Fix - Simple Summary

## The Problem
Your Railway deployment shows `localhost` in the DATABASE_URL, which means Railway's PostgreSQL DATABASE_URL is NOT being passed to your web service.

## The Root Cause
Railway services are isolated. Even though you created a PostgreSQL database, you must manually connect it to your web service by adding the DATABASE_URL variable.

## The Solution (3 Steps)

### 1. Get DATABASE_URL from PostgreSQL Service
```
Railway Dashboard → Click PostgreSQL service → Variables tab → Copy DATABASE_URL
```

The URL should look like:
```
postgres://postgres:xxxxx@postgres.railway.internal:5432/railway
```

### 2. Add DATABASE_URL to Web Service
```
Railway Dashboard → Click Web service → Variables tab → + New Variable
```

Add:
- Name: `DATABASE_URL`
- Value: (paste the URL you copied)

OR use a reference (better):
- Name: `DATABASE_URL`  
- Value: `${{Postgres.DATABASE_URL}}`

(Replace "Postgres" with your actual PostgreSQL service name)

### 3. Wait for Redeploy
Railway will automatically redeploy (2-3 minutes).

## How to Verify Success

Check the deployment logs. You should see:
```
✅ Database connection successful!
Running migrations...
INFO:     Application startup complete.
```

No more "connection to localhost refused" errors!

## Why This Happens

Railway doesn't automatically share environment variables between services. You must explicitly connect them.

Think of it like this:
- PostgreSQL service has DATABASE_URL
- Web service needs DATABASE_URL
- You must manually give web service access to PostgreSQL's DATABASE_URL

## Quick Reference

| What | Where | Action |
|------|-------|--------|
| Get URL | PostgreSQL service → Variables | Copy DATABASE_URL |
| Set URL | Web service → Variables | Add DATABASE_URL |
| Verify | Web service → Deployments → Logs | Check for success |

## Still Not Working?

1. Make sure you're adding DATABASE_URL to the WEB service, not PostgreSQL
2. Make sure you copied the ENTIRE URL (it's very long)
3. Try deleting and re-adding the variable
4. Check that your PostgreSQL service is running (green status)

## Next Steps After Success

1. Database migrations run automatically
2. Initialize gyms: Run `scripts/init_railway_db.py`
3. Update mobile app API URL in `mobile/config/api.ts`
4. Build APK with `eas build`
