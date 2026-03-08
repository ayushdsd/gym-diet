# Fix Railway Deployment - Quick Commands

## The Problem
Railway deployment failed with database connection error. The DATABASE_URL environment variable is not being read correctly, or needs conversion from `postgres://` to `postgresql://`.

## The Fix (Updated)
I've fixed the configuration to properly handle Railway's DATABASE_URL! Just commit and push:

```bash
# Add the fixed files
git add app/core/config.py app/db/session.py alembic/env.py scripts/check_database_url.py

# Commit the fix
git commit -m "Fix Railway DATABASE_URL configuration and PostgreSQL compatibility"

# Push to GitHub
git push origin main
```

## What Was Fixed

1. **app/core/config.py** - Made DATABASE_URL a property that automatically converts `postgres://` to `postgresql://`
2. **app/db/session.py** - Simplified to use the fixed config
3. **alembic/env.py** - Simplified to use the fixed config
4. **scripts/check_database_url.py** - Debug script to verify configuration

## What Happens Next

1. Railway detects the push
2. Automatically rebuilds and redeploys
3. Migrations run successfully
4. App starts successfully

## Watch the Deployment

Go to your Railway project and watch the logs:
- https://railway.app/dashboard
- Click your project
- Go to "Deployments"
- Watch the latest deployment

You should see:
```
✅ Running migrations: alembic upgrade head
✅ Starting server: uvicorn app.main:app
✅ Application startup complete
```

## Debug if Still Failing

If it still fails, run the debug script in Railway:

```bash
# Using Railway CLI
railway run python scripts/check_database_url.py
```

This will show you:
- If DATABASE_URL is set
- If the conversion is working
- If the database connection works

## Verify Environment Variables in Railway

Make sure these are set in Railway dashboard:

1. Go to your Railway project
2. Click on your web service
3. Go to "Variables" tab
4. Verify these exist:
   - `DATABASE_URL` (automatically set by PostgreSQL service)
   - `SECRET_KEY` (you need to set this)
   - `OPENAI_API_KEY` (you need to set this)
   - `ENVIRONMENT=production` (optional)

## Test Your API

Once deployed, test it:

```bash
# Replace with your Railway URL
curl https://your-app.railway.app/docs
curl https://your-app.railway.app/gyms
```

## Initialize Database

After successful deployment, add gyms:

```bash
python scripts/init_railway_db.py --url https://your-app.railway.app
```

## Still Having Issues?

If DATABASE_URL is not being set:

1. **Check PostgreSQL Service**: Make sure the PostgreSQL database is running in Railway
2. **Check Service Connection**: The web service should be connected to the PostgreSQL service
3. **Restart Services**: Try restarting both services in Railway
4. **Check Logs**: Look for specific error messages in deployment logs

## Done!

Your backend should now deploy successfully on Railway! 🎉

Next step: Update mobile app API URL and build APK.

See [BUILD_APK_GUIDE.md](BUILD_APK_GUIDE.md) for next steps.
