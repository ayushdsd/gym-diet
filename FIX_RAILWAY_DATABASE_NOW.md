# Fix Railway Database Connection - 3 Commands

## The Problem
Your `.env` file is in Git and overriding Railway's DATABASE_URL.

## The Fix (Run These 3 Commands)

```bash
# 1. Remove .env from Git (keeps it locally for development)
git rm --cached .env

# 2. Commit the change
git commit -m "Remove .env from repository"

# 3. Push to GitHub (Railway will auto-redeploy)
git push origin main
```

## What Happens Next
1. Railway detects the push and starts a new deployment
2. Without `.env` in the repo, Railway uses its own DATABASE_URL
3. Your app connects to Railway's PostgreSQL database
4. Deployment succeeds! ✅

## Verify Before Pushing (Optional)
```bash
python scripts/verify_env_not_in_git.py
```

## After Successful Deployment
1. Initialize database with gyms:
   ```bash
   python scripts/init_railway_db.py
   ```

2. Update mobile app API URL in `mobile/config/api.ts`:
   ```typescript
   export const API_URL = 'https://your-app.railway.app';
   ```

3. Build APK:
   ```bash
   cd mobile
   eas build --platform android --profile production
   ```

## Why This Works
- `.env` files are for LOCAL development only
- Railway sets environment variables through its dashboard
- When `.env` exists in the deployed code, it overrides Railway's variables
- Removing `.env` from Git lets Railway's variables work correctly
- Your local development still works because `.env` exists on your machine

## Your Local .env is Safe
The `git rm --cached .env` command only removes it from Git tracking.
Your local `.env` file stays on your computer for development.
