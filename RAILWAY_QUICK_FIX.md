# Railway Quick Fix - Database Not Connected

## The Real Problem

Railway's PostgreSQL database is **NOT connected** to your web service. That's why it's using `localhost` instead of Railway's database.

## Quick Fix (2 Minutes)

### Step 1: Go to Railway Dashboard
https://railway.app/dashboard → Your Project

### Step 2: Check Your Services

You should see TWO boxes:
- 📦 Your web service (Python app)
- 🗄️ PostgreSQL database

If you only see ONE, add PostgreSQL:
- Click "+ New"
- Select "Database" → "PostgreSQL"

### Step 3: Connect Them

**Method 1: Automatic (Easiest)**
1. Click on **PostgreSQL** service
2. Look for "Connected Services" or "Connect" tab
3. Your web service should be listed
4. If not, click "Connect" and select your web service

**Method 2: Manual (If Method 1 doesn't work)**
1. Click on **PostgreSQL** service
2. Go to "Variables" tab
3. **Copy** the `DATABASE_URL` value
4. Click on your **web service**
5. Go to "Variables" tab
6. Click "+ New Variable"
7. Name: `DATABASE_URL`
8. **Paste** the value you copied
9. Click "Add"

### Step 4: Verify

Click on your **web service** → "Variables" tab

You should now see:
```
DATABASE_URL = postgresql://postgres:xxxxx@containers-us-west-xxx.railway.app:5432/railway
```

NOT:
```
DATABASE_URL = postgresql://postgres:xxxxx@localhost:5432/gymdiet
```

### Step 5: Redeploy

Railway will automatically redeploy when you add the variable.

Or manually trigger:
- Go to "Deployments" tab
- Click "Deploy"

### Step 6: Watch Logs

In the deployment logs, you should now see:
```
✅ Running migrations: alembic upgrade head
INFO  [alembic.runtime.migration] Running upgrade
✅ Starting server
INFO:     Application startup complete.
```

## Test It

```bash
curl https://your-app.railway.app/docs
```

Should show the Swagger UI!

## Still Not Working?

Run the debug script:
```bash
railway run python scripts/check_database_url.py
```

Should show:
```
✅ Already using postgresql://
✅ Database connection successful!
```

## That's It!

Once the DATABASE_URL is set correctly, everything will work! 🎉

The code fixes we made earlier will handle the URL conversion automatically.
