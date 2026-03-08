# Railway Deployment Checklist

## Pre-Deployment ✓

- [x] Code pushed to GitHub
- [x] `.env` is in `.gitignore` (not deployed)
- [x] Railway project created
- [x] PostgreSQL service added to Railway
- [x] All environment variables set in Railway dashboard

## The Missing Step ❌ → ✅

- [ ] **DATABASE_URL added to web service** ← YOU ARE HERE

This is what you need to do right now!

## How to Add DATABASE_URL

### Quick Method (2 minutes)
1. Open Railway dashboard
2. Click on PostgreSQL service
3. Go to Variables tab
4. Copy the DATABASE_URL value
5. Go back to project view
6. Click on Web service
7. Go to Variables tab
8. Click "+ New Variable"
9. Name: `DATABASE_URL`
10. Value: Paste what you copied
11. Click "Add"
12. Wait for automatic redeploy

### Alternative: Use Reference
Instead of copying, use: `${{Postgres.DATABASE_URL}}`
(Replace "Postgres" with your PostgreSQL service name)

## Post-Deployment Checklist

After DATABASE_URL is added and deployment succeeds:

- [ ] Check deployment logs for success message
- [ ] Verify no "localhost" errors
- [ ] Run `python scripts/init_railway_db.py` to add gyms
- [ ] Test API endpoints (health check, login, etc.)
- [ ] Update mobile app API URL
- [ ] Test mobile app with Railway backend
- [ ] Build APK with `eas build`

## Troubleshooting

### Deployment still fails?
- [ ] Verify DATABASE_URL is in WEB service, not PostgreSQL service
- [ ] Check you copied the entire URL (very long string)
- [ ] Try deleting and re-adding the variable
- [ ] Verify PostgreSQL service is running (green status)

### Can't find Variables tab?
- [ ] Make sure you clicked ON the service box
- [ ] Look at the top navigation: Settings, Variables, Metrics, etc.

### Multiple DATABASE_URL variables?
- [ ] Delete all of them
- [ ] Add just one with the correct PostgreSQL URL

## Success Indicators

You'll know it's working when you see in the logs:

```
✅ Running migrations...
✅ INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
✅ INFO:     Application startup complete.
✅ INFO:     Uvicorn running on http://0.0.0.0:PORT
```

No errors about "localhost" or "connection refused"!

## Time Estimate

- Adding DATABASE_URL: 2 minutes
- Automatic redeploy: 2-3 minutes
- Verification: 1 minute
- Total: ~5-6 minutes

## Need Help?

Read these guides in order:
1. **RAILWAY_FIX_SUMMARY.md** - Start here (simplest)
2. **RAILWAY_STEP_BY_STEP.md** - Detailed walkthrough
3. **RAILWAY_ARCHITECTURE.md** - Understand why this is needed
4. **ACTION_PLAN.md** - Complete deployment plan

## The Bottom Line

Railway's PostgreSQL DATABASE_URL is NOT automatically shared with your web service. You must manually add it as a variable in your web service. That's it. That's the whole issue.
