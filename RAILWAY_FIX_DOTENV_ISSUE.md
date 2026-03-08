# Railway DATABASE_URL Issue - SOLVED

## The Problem
Railway is using `localhost` instead of the PostgreSQL DATABASE_URL because:

1. Your `.env` file contains `DATABASE_URL=postgresql+psycopg2://postgres:1234@localhost:5432/gymdiet`
2. This `.env` file was committed to Git BEFORE adding it to `.gitignore`
3. Railway deploys your Git repository, including the `.env` file
4. `load_dotenv()` in `app/core/config.py` loads the `.env` file and OVERWRITES Railway's environment variables

## The Solution

### Step 1: Remove .env from Git History
Run these commands in your project root:

```bash
# Remove .env from Git (but keep it locally)
git rm --cached .env

# Commit the removal
git commit -m "Remove .env from repository"

# Push to GitHub
git push origin main
```

### Step 2: Verify .gitignore
Your `.gitignore` already contains `.env`, so it won't be added again.

### Step 3: Redeploy on Railway
After pushing the changes:
1. Go to your Railway project
2. The deployment should trigger automatically
3. Railway will now use its own DATABASE_URL environment variable
4. The deployment should succeed!

## Why This Works
- Without the `.env` file in the repository, `load_dotenv()` finds nothing to load
- Railway's environment variables (set in the dashboard) take precedence
- Your local development still works because `.env` exists locally (just not in Git)

## Verification
After redeploying, the debug script should show:
```
1. Raw DATABASE_URL from environment:
postgresql://postgres:****@postgres.railway.internal:5432/railway

2. Settings DATABASE_URL (after conversion):
postgresql+psycopg2://postgres:****@postgres.railway.internal:5432/railway

3. URL Conversion Check:
✅ Using Railway PostgreSQL database
```

## Next Steps After Successful Deployment
1. Run database migrations: `python scripts/init_railway_db.py`
2. Update mobile app API URL in `mobile/config/api.ts`
3. Build APK with EAS Build
