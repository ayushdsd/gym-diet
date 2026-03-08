# Railway Deployment Fix - Database Connection Error

## Problem

When deploying to Railway, you get this error:

```
psycopg2.OperationalError: connection to server at "localhost" (::1), port 5432 failed: Connection refused
```

## Root Cause

Railway provides the PostgreSQL connection URL as `postgres://...` but SQLAlchemy 1.4+ requires `postgresql://...` (with "ql" at the end).

## Solution

I've already fixed this in your code! The changes were made to:

1. **alembic/env.py** - Fixed for migrations
2. **app/db/session.py** - Fixed for application database connection

Both files now automatically convert `postgres://` to `postgresql://`.

## Verify the Fix

### Step 1: Commit and Push Changes

```bash
git add alembic/env.py app/db/session.py
git commit -m "Fix Railway PostgreSQL URL for SQLAlchemy compatibility"
git push origin main
```

### Step 2: Railway Will Auto-Deploy

Railway will automatically detect the push and redeploy. Watch the logs:

1. Go to your Railway project
2. Click on your service
3. Go to "Deployments"
4. Watch the latest deployment logs

### Step 3: Verify Migrations Run Successfully

In the deployment logs, you should see:

```
✅ Running migrations: alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> 20260302_000001, init
INFO  [alembic.runtime.migration] Running upgrade 20260302_000001 -> 20260304_000002, user_role_check
...
✅ Starting server: uvicorn app.main:app --host 0.0.0.0 --port $PORT
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Alternative: Manual Environment Variable Fix

If you still have issues, you can also set the DATABASE_URL manually in Railway:

1. Go to your Railway project
2. Click on your service
3. Go to "Variables" tab
4. Find `DATABASE_URL`
5. If it starts with `postgres://`, change it to `postgresql://`
6. Save and redeploy

## Verify Database Connection

Once deployed, test the connection:

```bash
# Test the API docs endpoint
curl https://your-app.railway.app/docs

# Test the gyms endpoint
curl https://your-app.railway.app/gyms
```

If you see the Swagger UI or a JSON response, the database connection is working!

## Common Railway Deployment Issues

### Issue 1: Build Fails - Missing Dependencies

**Error**: `ModuleNotFoundError: No module named 'xyz'`

**Solution**: Add the missing package to `requirements.txt`

```bash
echo "package-name==version" >> requirements.txt
git add requirements.txt
git commit -m "Add missing dependency"
git push
```

### Issue 2: Migrations Fail - Table Already Exists

**Error**: `relation "table_name" already exists`

**Solution**: The database already has tables. Either:

Option A: Drop all tables and re-run migrations (CAUTION: Deletes all data)
```bash
# In Railway CLI
railway run python
>>> from app.db.session import engine
>>> from app.db.base import Base
>>> Base.metadata.drop_all(engine)
>>> exit()
railway run alembic upgrade head
```

Option B: Mark migrations as complete without running them
```bash
railway run alembic stamp head
```

### Issue 3: Environment Variables Not Set

**Error**: `KeyError: 'OPENAI_API_KEY'` or similar

**Solution**: Set all required environment variables in Railway:

1. Go to "Variables" tab
2. Add missing variables:
   - `SECRET_KEY`
   - `OPENAI_API_KEY`
   - `ENVIRONMENT=production`
3. Redeploy

### Issue 4: Port Binding Error

**Error**: `Address already in use`

**Solution**: Railway automatically sets the `PORT` environment variable. Make sure your `Procfile` uses `$PORT`:

```
web: alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Issue 5: CORS Errors from Mobile App

**Error**: Mobile app can't connect to API

**Solution**: Ensure CORS allows all origins in `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for mobile app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Debugging Railway Deployments

### View Logs

```bash
# Using Railway CLI
railway logs

# Or in Railway dashboard
# Go to Deployments → Click on deployment → View logs
```

### Check Environment Variables

```bash
# Using Railway CLI
railway variables

# Or in Railway dashboard
# Go to Variables tab
```

### Run Commands in Railway

```bash
# Using Railway CLI
railway run python --version
railway run alembic current
railway run alembic history
```

### Connect to PostgreSQL

```bash
# Using Railway CLI
railway run psql $DATABASE_URL

# Or get the connection string
railway variables | grep DATABASE_URL
```

## Success Checklist

After fixing and redeploying, verify:

- [ ] Deployment shows "Success" status
- [ ] Logs show migrations ran successfully
- [ ] Logs show "Application startup complete"
- [ ] `/docs` endpoint loads (Swagger UI)
- [ ] `/gyms` endpoint returns data
- [ ] Mobile app can connect to API

## Next Steps

Once your backend is deployed successfully:

1. ✅ Initialize database with gyms:
   ```bash
   python scripts/init_railway_db.py --url https://your-app.railway.app
   ```

2. ✅ Update mobile app API URL in `mobile/config/api.ts`

3. ✅ Build Android APK:
   ```bash
   cd mobile
   eas build --platform android --profile preview
   ```

4. ✅ Test the complete flow!

## Still Having Issues?

If you're still experiencing problems:

1. **Check Railway Status**: https://status.railway.app
2. **Railway Discord**: https://discord.gg/railway
3. **Check Logs**: Look for specific error messages
4. **Verify PostgreSQL**: Ensure the database service is running
5. **Test Locally**: Make sure it works locally first

## Summary

The database connection error has been fixed by updating the code to handle Railway's PostgreSQL URL format. Just commit and push the changes, and Railway will automatically redeploy with the fix!

```bash
git add alembic/env.py app/db/session.py
git commit -m "Fix Railway PostgreSQL URL compatibility"
git push origin main
```

Your deployment should now succeed! 🚀
