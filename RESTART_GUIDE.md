# Complete Restart Guide

## Issues Fixed

1. ✅ **Entry file error** - Changed `package.json` main field from `index.ts` to `index.js`
2. ✅ **Navigation error** - Changed `app/index.tsx` to use `<Redirect>` instead of `router.replace()`

## How to Restart

### Step 1: Stop Current Server
Press `Ctrl+C` in the terminal running Expo

### Step 2: Clear Cache and Restart
```bash
cd mobile
npx expo start -c
```

### Step 3: Open in Browser
Press `w` in the terminal to open in browser

## What You Should See

### First Launch (No Authentication)
1. App loads with loading spinner
2. Automatically redirects to **Gym Selection Screen**
3. Shows list of available gyms

### If No Gyms Appear
Run this in another terminal:
```bash
python scripts/create_test_gyms.py
```

This creates 5 test gyms:
- PowerFit Gym
- Elite Fitness
- Iron Paradise
- Muscle Factory
- FitZone

## Complete Test Flow

### Terminal Setup
```bash
# Terminal 1: Backend
cd "C:\Users\Ayush\Desktop\GYM DIET"
uvicorn app.main:app --reload

# Terminal 2: Create test gyms (first time only)
python scripts/create_test_gyms.py

# Terminal 3: Mobile app
cd mobile
npx expo start -c
```

### Test Registration
1. Open app in browser (press `w`)
2. Select "PowerFit Gym"
3. Click "Create New Account"
4. Fill form:
   - Email: `test@powerfit.com`
   - Password: `password123`
   - Confirm: `password123`
5. Click "Create Account"
6. Should auto-login and show dashboard

### Test Login
1. Clear storage (browser console): `localStorage.clear()`
2. Refresh page
3. Select "PowerFit Gym"
4. Click "Continue to Login"
5. Enter credentials from registration
6. Should show dashboard

### Test Features
1. Log a meal manually
2. Use AI chat: "I ate chicken breast with rice"
3. Pull down to refresh dashboard
4. Check XP and macro rings update

## Expected Console Output

### App Launch
```
User not authenticated, redirecting to gym selection
```

### Gym Selection
```
Loaded gyms: [{ id: 1, name: "PowerFit Gym" }, ...]
Selected gym: 1
Setting gymId in store: 1
```

### Registration
```
Attempting registration for: test@powerfit.com at gym: 1
=== REGISTRATION SUCCESS ===
User created: test@powerfit.com
Auto-login successful
Token saved to store
```

### Login
```
Attempting login for: test@powerfit.com
=== LOGIN SUCCESS ===
Access token received: Yes
Token saved to store
```

## Troubleshooting

### Issue: Still getting navigation error
**Solution:**
```bash
cd mobile
rm -rf .expo
rm -rf node_modules/.cache
npx expo start -c
```

### Issue: "Cannot resolve entry file"
**Solution:** Verify `package.json` has `"main": "index.js"` (not `index.ts`)

### Issue: No gyms showing
**Solution:**
```bash
python scripts/create_test_gyms.py
```

### Issue: Backend not responding
**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/docs

# If not, start it
uvicorn app.main:app --reload
```

### Issue: Token not persisting
**Solution:**
```bash
# Verify AsyncStorage is installed
npm list @react-native-async-storage/async-storage

# If not installed
npm install @react-native-async-storage/async-storage --legacy-peer-deps

# Restart with cache clear
npx expo start -c
```

## Quick Checklist

- [ ] Backend running on localhost:8000
- [ ] Test gyms created (5 gyms)
- [ ] Mobile app starts without errors
- [ ] Gym selection screen shows
- [ ] Can select a gym
- [ ] Can create new account
- [ ] Auto-login works
- [ ] Dashboard loads
- [ ] Can login with existing account
- [ ] Token persists after refresh
- [ ] AI chat works
- [ ] Meal logging works

## Documentation

- `mobile/FIX_ENTRY_ERROR.md` - Entry file error fix
- `mobile/FIX_NAVIGATION_ERROR.md` - Navigation error fix
- `AUTH_SETUP_GUIDE.md` - Complete authentication setup
- `MULTI_GYM_AUTH_SUMMARY.md` - Implementation summary
- `QUICK_TEST.md` - Quick testing guide

## Summary

All navigation and entry file errors have been fixed. The app should now:
1. Load without errors
2. Show gym selection screen
3. Allow registration and login
4. Persist authentication
5. Protect routes based on auth state

Restart the app with cache clear and it should work perfectly!
