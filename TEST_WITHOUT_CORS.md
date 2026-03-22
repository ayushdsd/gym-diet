# Test Meal Logging Without CORS Issues

## The Problem

You're testing on **web (localhost:8081)** which has CORS restrictions. The backend is returning a 500 error, and when that happens, CORS headers aren't sent, causing the CORS error to appear.

The **real issue** is the 500 error, not CORS.

## Solution: Test on Mobile Instead of Web

### Option 1: Test on Physical Android Device (Best)

1. **Connect your Android phone via USB**
2. **Enable USB debugging** on your phone
3. **Run**:
   ```bash
   cd mobile
   npm start
   ```
4. **Press 'a'** to open on Android device
5. **Test meal logging** - No CORS issues!

### Option 2: Test on Android Emulator

1. **Start Android emulator** (Android Studio)
2. **Run**:
   ```bash
   cd mobile
   npm start
   ```
3. **Press 'a'** to open on emulator
4. **Test meal logging** - No CORS issues!

### Option 3: Build APK and Test

```bash
cd mobile
npx eas-cli build --platform android --profile production
```

Wait for build, download APK, install on device, test.

---

## Why This Happens

### Web Browser CORS Flow:
1. Browser sends OPTIONS preflight request
2. Server must respond with CORS headers
3. If server returns 500 error, no CORS headers sent
4. Browser blocks the request with CORS error

### Mobile App (No CORS):
1. App sends POST request directly
2. No preflight, no CORS checks
3. If server returns 500, you see the actual error
4. Much easier to debug!

---

## The Real Issue: 500 Error

The backend is crashing when you try to log a meal. Possible causes:

### 1. Database Connection Issue
- DATABASE_URL not set correctly
- Database not accessible
- Connection pool exhausted

### 2. Missing Data
- User not found
- Gym not found
- Invalid foreign keys

### 3. Gamification Error
- XP calculation failing
- Streak tracker error
- Badge system error

---

## Check Railway Logs

1. Go to https://railway.app
2. Open your project
3. Click on web service
4. Click "View Logs"
5. Look for errors when you try to log a meal
6. You'll see the actual Python error

Common errors to look for:
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) FATAL: ...
KeyError: ...
AttributeError: ...
IntegrityError: ...
```

---

## Quick Test: Use Postman or cURL

Test the endpoint directly without browser CORS:

### Get your token from browser console:
```javascript
console.log(localStorage.getItem('auth_token'))
```

### Test with PowerShell:
```powershell
$token = "YOUR_TOKEN_HERE"
$body = @{
    protein = 30
    carbs = 45
    fats = 15
    description = "Test meal"
} | ConvertTo-Json

Invoke-WebRequest `
    -Uri "https://gym-diet-production.up.railway.app/meals" `
    -Method POST `
    -Headers @{"Authorization"="Bearer $token"; "Content-Type"="application/json"} `
    -Body $body
```

This will show you the REAL error without CORS blocking it.

---

## Recommended Next Steps

1. **Check Railway logs** for the actual 500 error
2. **Test on Android device/emulator** (no CORS)
3. **Or use Postman/cURL** to see real error
4. **Fix the backend issue** causing 500
5. **Then test on web** will work

---

## Why Web Testing is Problematic

- ❌ CORS blocks errors
- ❌ Can't see real error messages
- ❌ Harder to debug
- ❌ Not representative of mobile app

## Why Mobile Testing is Better

- ✅ No CORS issues
- ✅ See real errors
- ✅ Easier to debug
- ✅ Tests actual app behavior

---

**Bottom Line**: The CORS error is hiding the real 500 error. Test on mobile or check Railway logs to see what's actually wrong.
