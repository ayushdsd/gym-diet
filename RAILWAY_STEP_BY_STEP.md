# Railway Database Fix - Step by Step

## The Issue
Your web service doesn't have access to the PostgreSQL DATABASE_URL.

## The Fix (5 Minutes)

### Step 1: Open Railway Dashboard
Go to: https://railway.app/dashboard

### Step 2: Open Your Project
Click on your gym-diet project

### Step 3: Identify Your Services
You should see 2 boxes/cards:
- One for your web app (might be called "gym-diet" or "web")
- One for PostgreSQL (might be called "Postgres" or "PostgreSQL")

If you only see ONE service, you need to add PostgreSQL first:
- Click "+ New"
- Select "Database"
- Select "Add PostgreSQL"
- Wait for it to provision (1-2 minutes)

### Step 4: Get DATABASE_URL from PostgreSQL
1. Click on the PostgreSQL service box
2. Click the "Variables" tab at the top
3. You'll see a list of variables including `DATABASE_URL`
4. Click the copy icon next to `DATABASE_URL` to copy it
5. The URL should start with `postgres://`

### Step 5: Add DATABASE_URL to Web Service
1. Click back to go to the project view
2. Click on your WEB service box (not PostgreSQL)
3. Click the "Variables" tab
4. Look for `DATABASE_URL` in the list

**If DATABASE_URL exists:**
- Click the three dots (...) next to it
- Click "Edit"
- Paste the URL you copied from PostgreSQL
- Click "Update"

**If DATABASE_URL doesn't exist:**
- Click "+ New Variable"
- Variable: `DATABASE_URL`
- Value: Paste the URL you copied
- Click "Add"

### Step 6: Wait for Redeploy
Railway will automatically redeploy your app (takes 2-3 minutes)

Watch the "Deployments" tab - you should see a new deployment starting.

### Step 7: Check Logs
1. Click on the latest deployment
2. Click "View Logs"
3. Look for the database connection check output
4. You should see: `✅ Using Railway PostgreSQL database`

## Alternative Method: Use Reference Variable

Instead of copying the URL, you can use a reference:

1. In your web service Variables tab
2. Add new variable:
   - Variable: `DATABASE_URL`
   - Value: `${{Postgres.DATABASE_URL}}`
3. Replace "Postgres" with your actual PostgreSQL service name

This is better because:
- Automatically updates if PostgreSQL URL changes
- No need to copy/paste
- Railway manages the connection

## Troubleshooting

### "I don't see a Variables tab"
Make sure you clicked on the service box itself, not just hovering over it.

### "The deployment still fails"
1. Check that you copied the ENTIRE DATABASE_URL (it's long)
2. Make sure you added it to the WEB service, not PostgreSQL
3. Try deleting and re-adding the variable

### "I see multiple DATABASE_URL variables"
Delete all of them, then add just one with the correct PostgreSQL URL.

## What Success Looks Like

In the deployment logs, you should see:
```
Running migrations...
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

No more "connection to localhost refused" errors!
