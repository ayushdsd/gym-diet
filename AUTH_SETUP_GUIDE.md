# Multi-Gym Authentication Setup Guide

## What's New

The app now supports multi-gym authentication where:
- Each gym has its own isolated members and data
- Users select a gym before logging in or registering
- Beautiful, modern UI with smooth animations
- Complete registration flow with validation

## Quick Start

### 1. Start Backend

```bash
cd "C:\Users\Ayush\Desktop\GYM DIET"
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 2. Create Test Gyms

```bash
python scripts/create_test_gyms.py
```

This creates 5 test gyms:
- PowerFit Gym
- Elite Fitness
- Iron Paradise
- Muscle Factory
- FitZone

### 3. Start Mobile App

```bash
cd mobile
npx expo start -c
```

Press `w` to open in browser.

### 4. Test the Flow

1. **App opens** → Shows gym selection screen
2. **Select a gym** → Click on any gym card
3. **Click "Create New Account"**
4. **Fill registration form:**
   - Email: `test@powerfit.com`
   - Password: `password123`
   - Confirm Password: `password123`
5. **Submit** → Auto-logs in and goes to dashboard
6. **Test features:**
   - Log a meal manually
   - Use AI chat to log meals
   - Pull to refresh dashboard
   - Check XP and level progress

## Authentication Flow

```
App Launch
    ↓
Check Auth (token + gymId)
    ↓
    ├─ Authenticated → Dashboard
    └─ Not Authenticated → Gym Selection
                              ↓
                        Select Gym
                              ↓
                    ├─ Login ────────→ Dashboard
                    └─ Register ─────→ Dashboard
```

## API Endpoints

### Backend Changes

Added public endpoint to list gyms:

```python
# app/api/routes/gyms.py
@router.get("", response_model=list[GymOut])
def list_gyms(db: Session = Depends(get_db)):
    """Public endpoint to list all gyms"""
    gyms = db.query(Gym).all()
    return gyms
```

### Available Endpoints

1. **List Gyms** (Public)
   ```
   GET /gyms
   Response: [{ id: 1, name: "PowerFit Gym" }, ...]
   ```

2. **Register**
   ```
   POST /auth/register
   Body: {
     email: "user@example.com",
     password: "password",
     gym_id: 1,
     role: "member"
   }
   ```

3. **Login**
   ```
   POST /auth/login
   Body: username=email&password=password
   Response: { access_token: "...", token_type: "bearer" }
   ```

## New Files

### Mobile App

1. **`mobile/app/index.tsx`**
   - Entry point with auth check
   - Redirects to gym selection or dashboard

2. **`mobile/app/(auth)/select-gym.tsx`**
   - Lists all available gyms
   - Beautiful card layout with animations
   - Stores selected gym in Zustand

3. **`mobile/app/(auth)/login.tsx`**
   - Shows selected gym name
   - Email/password login
   - Links to registration

4. **`mobile/app/(auth)/register.tsx`**
   - Shows selected gym name
   - Email/password/confirm registration
   - Form validation
   - Auto-login after registration

### Backend

1. **`app/api/routes/gyms.py`** (Modified)
   - Added `GET /gyms` endpoint to list all gyms

### Scripts

1. **`scripts/create_test_gyms.py`**
   - Creates 5 test gyms for development

### Documentation

1. **`mobile/AUTH_FLOW_GUIDE.md`**
   - Detailed authentication flow documentation

2. **`AUTH_SETUP_GUIDE.md`** (This file)
   - Quick setup guide

## Features

### Gym Selection Screen
- ✅ Fetches all gyms from backend
- ✅ Beautiful card layout with gym icons
- ✅ Visual selection feedback (purple border + checkmark)
- ✅ Smooth fade-in animations
- ✅ Empty state handling
- ✅ Error handling with alerts
- ✅ Haptic feedback

### Login Screen
- ✅ Shows selected gym badge
- ✅ Email and password fields
- ✅ Form validation
- ✅ Loading state with spinner
- ✅ Back button to gym selection
- ✅ Link to registration
- ✅ Haptic feedback
- ✅ Error handling

### Registration Screen
- ✅ Shows selected gym badge
- ✅ Email, password, confirm password fields
- ✅ Comprehensive validation:
  - All fields required
  - Valid email format
  - Password min 6 characters
  - Passwords must match
- ✅ Loading state with spinner
- ✅ Back button to gym selection
- ✅ Link to login
- ✅ Auto-login after success
- ✅ Scrollable form
- ✅ Haptic feedback
- ✅ Error handling

## Testing Scenarios

### Scenario 1: New User Registration

1. Open app → Gym selection
2. Select "PowerFit Gym"
3. Click "Create New Account"
4. Enter:
   - Email: `john@powerfit.com`
   - Password: `password123`
   - Confirm: `password123`
5. Submit → Should auto-login and show dashboard
6. Check console for:
   ```
   === REGISTRATION SUCCESS ===
   User created: john@powerfit.com
   Auto-login successful
   Token saved to store
   ```

### Scenario 2: Existing User Login

1. Open app → Gym selection
2. Select "PowerFit Gym"
3. Click "Continue to Login"
4. Enter:
   - Email: `john@powerfit.com`
   - Password: `password123`
5. Submit → Should show dashboard
6. Check console for:
   ```
   === LOGIN SUCCESS ===
   Access token received: Yes
   Token saved to store
   ```

### Scenario 3: Multi-Gym Isolation

1. Register user at "PowerFit Gym": `user1@powerfit.com`
2. Log some meals
3. Logout (or clear storage)
4. Register user at "Elite Fitness": `user2@elite.com`
5. Check dashboard → Should be empty (different gym)
6. This proves gym isolation works

### Scenario 4: Form Validation

Test registration validation:
- Empty fields → "Please fill in all fields"
- Invalid email → "Please enter a valid email address"
- Short password → "Password must be at least 6 characters"
- Mismatched passwords → "Passwords do not match"
- Existing email → "An account with this email already exists"

## Console Debugging

### Expected Console Output

**Gym Selection:**
```
Loaded gyms: [{ id: 1, name: "PowerFit Gym" }, ...]
Selected gym: 1
Setting gymId in store: 1
```

**Registration:**
```
Attempting registration for: john@powerfit.com at gym: 1
=== REGISTRATION SUCCESS ===
User created: john@powerfit.com
Auto-login successful
Token saved to store
Setting token in store: Token exists
```

**Login:**
```
Attempting login for: john@powerfit.com
=== LOGIN SUCCESS ===
Access token received: Yes
Token preview: eyJhbGciOiJIUzI1NiIs...
Token saved to store
Setting token in store: Token exists
```

## Troubleshooting

### Issue: "Failed to load gyms"

**Cause:** Backend not running or wrong URL

**Solution:**
1. Check backend is running: `http://localhost:8000/docs`
2. Check console for connection errors
3. Restart backend: `uvicorn app.main:app --reload`

### Issue: "No gyms available"

**Cause:** No gyms in database

**Solution:**
```bash
python scripts/create_test_gyms.py
```

### Issue: "An account with this email already exists"

**Cause:** Email already registered at this gym

**Solution:**
1. Use a different email
2. Or go to login instead

### Issue: "Selected gym not found"

**Cause:** Gym was deleted from database

**Solution:**
1. Go back to gym selection
2. Select a different gym
3. Or recreate gyms: `python scripts/create_test_gyms.py`

### Issue: Token not persisting

**Cause:** AsyncStorage not installed or not working

**Solution:**
1. Check AsyncStorage is installed:
   ```bash
   npm list @react-native-async-storage/async-storage
   ```
2. If not installed:
   ```bash
   npm install @react-native-async-storage/async-storage --legacy-peer-deps
   ```
3. Clear cache and restart:
   ```bash
   npx expo start -c
   ```

## Manual Testing Checklist

- [ ] Backend starts successfully
- [ ] Test gyms created
- [ ] Mobile app starts
- [ ] Gym selection screen loads gyms
- [ ] Can select a gym (visual feedback works)
- [ ] Can navigate to registration
- [ ] Registration form validation works
- [ ] Can create new account
- [ ] Auto-login after registration works
- [ ] Dashboard loads after registration
- [ ] Can logout (if implemented)
- [ ] Can navigate to login
- [ ] Can login with created account
- [ ] Dashboard loads after login
- [ ] Token persists after app refresh
- [ ] Can log meals
- [ ] Can use AI chat
- [ ] Dashboard updates after pull-to-refresh

## Next Steps

Once authentication is working:

1. **Add Logout**
   - Add logout button in dashboard
   - Clear token and gymId
   - Redirect to gym selection

2. **Add Profile Screen**
   - Show user info
   - Show gym name
   - Edit profile option

3. **Add Forgot Password**
   - Email verification
   - Password reset flow

4. **Add Social Login**
   - Google Sign-In
   - Apple Sign-In

5. **Add Gym Switching**
   - If user is member of multiple gyms
   - Switch between gyms

## Summary

The multi-gym authentication system is now complete with:
- ✅ Gym selection screen
- ✅ Login screen
- ✅ Registration screen
- ✅ Token persistence
- ✅ Form validation
- ✅ Error handling
- ✅ Beautiful UI with animations
- ✅ Haptic feedback
- ✅ Backend integration
- ✅ Multi-gym isolation

All API endpoints are properly integrated and the flow is smooth and intuitive.
