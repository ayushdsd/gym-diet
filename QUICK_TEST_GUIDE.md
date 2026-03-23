# Quick Test Guide - Verify Fixes

## 🎯 What We Fixed

1. ✅ Meal logging 500 error
2. ✅ Logout button not working

---

## 🧪 Test #1: Meal Logging

### Method A: Android Device (Best - No CORS)

```bash
cd mobile
npx expo start
```
Press `a` for Android

**Steps:**
1. Login to app
2. Click the + button (center FAB)
3. Choose "Manual Logging"
4. Enter: Protein: 30, Carbs: 50, Fats: 15
5. Click "Log Meal"
6. ✅ Should succeed and show success message

---

### Method B: Test Script (Bypasses CORS)

```bash
python scripts/test_railway_meal_logging.py
```

**Expected Output:**
```
============================================================
RAILWAY MEAL LOGGING DEBUG SCRIPT
============================================================

=== Testing Health Endpoint ===
Status: 200
Response: {'status': 'healthy'}

✅ Backend is healthy!

=== Testing Login ===
Status: 200
Login successful! Token: eyJhbGciOiJIUzI1NiIs...

✅ Login successful!

=== Testing Meal Logging ===
Payload: {
  "description": "Test meal from script",
  "protein": 30,
  "carbs": 50,
  "fats": 15
}
Status: 201
Success! Response: {
  "meal": {...},
  "gamification": {...}
}

✅ Meal logging works!
```

---

### Method C: Web Browser (May Show CORS if Error)

```bash
cd mobile
npx expo start
```
Press `w` for web

**If you see CORS error:**
- It means backend is still returning 500
- Check Railway logs for actual Python error
- Use Method A or B instead

---

## 🧪 Test #2: Logout Button

**Steps:**
1. Open app and login
2. Navigate to "Profile" tab (bottom right)
3. Scroll down to "Logout" button (red button at bottom)
4. Click "Logout"
5. Confirm in alert dialog
6. ✅ Should redirect to location selection screen smoothly

**What to Look For:**
- ✅ No hanging or freezing
- ✅ Smooth transition
- ✅ Redirects to location selection
- ✅ Can login again successfully

---

## 📊 Check Railway Logs

If meal logging still fails:

1. Go to https://railway.app
2. Login and select your project
3. Click on backend service
4. Click "Deployments" tab
5. Click latest deployment
6. Click "View Logs"

**Look for:**
- ❌ Red markers = Critical errors
- ⚠️ Yellow markers = Warnings
- ✅ Green markers = Success

**Common errors to check:**
- Database connection issues
- Missing environment variables
- Python exceptions

---

## ✅ Success Criteria

### Meal Logging Success
- [ ] Meal is saved to database
- [ ] Success message appears
- [ ] Meal appears in "Today's Meals" on dashboard
- [ ] XP is awarded (check profile)
- [ ] No errors in console

### Logout Success
- [ ] Logout button responds to click
- [ ] Alert dialog appears
- [ ] After confirming, redirects to location selection
- [ ] Can login again
- [ ] No errors in console

---

## 🐛 If Issues Persist

### Meal Logging Still Fails

**Check Railway Logs:**
```
Look for Python traceback with actual error
```

**Test Locally:**
```bash
# Start local backend
python -m uvicorn app.main:app --reload

# Update mobile/config/api.ts to use localhost
export const API_BASE_URL = "http://localhost:8000";

# Test again
```

**Common Fixes:**
- Check DATABASE_URL is set in Railway
- Check all environment variables are set
- Restart Railway service

---

### Logout Still Not Working

**Check Browser Console:**
```javascript
// Look for errors like:
// - Navigation errors
// - State update errors
// - Token errors
```

**Try:**
```bash
# Clear app cache
cd mobile
rm -rf .expo
rm -rf node_modules/.cache

# Restart
npx expo start --clear
```

---

## 📝 Report Issues

If tests fail, provide:

1. **Which test failed?** (Meal logging or logout)
2. **Error message** (exact text)
3. **Railway logs** (if meal logging)
4. **Browser console** (if logout)
5. **Platform** (Android, iOS, or web)

---

## 🎉 Expected Results

After testing, you should see:

✅ Meal logging works on all platforms
✅ Logout button works smoothly
✅ No CORS errors
✅ No 500 errors
✅ Clean user experience

---

## ⏱️ Deployment Status

**Backend:** Deployed to Railway (auto-deploy from GitHub)
**Frontend:** Ready to test (no deployment needed)

**Check deployment:**
```bash
# Should return 200 OK
curl https://gym-diet-production.up.railway.app/health
```

---

## 🚀 Quick Start

**Fastest way to test everything:**

```bash
# Terminal 1: Test backend
python scripts/test_railway_meal_logging.py

# Terminal 2: Test frontend
cd mobile
npx expo start
# Press 'a' for Android

# Then test:
# 1. Login
# 2. Log a meal (+ button)
# 3. Logout (Profile tab)
```

Done! 🎉
