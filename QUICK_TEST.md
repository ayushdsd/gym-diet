# Quick Test Guide - Multi-Gym Authentication

## 1. Start Everything

```bash
# Terminal 1: Backend
uvicorn app.main:app --reload

# Terminal 2: Create gyms
python scripts/create_test_gyms.py

# Terminal 3: Mobile
cd mobile
npx expo start -c
```

## 2. Test Registration Flow

1. Open app in browser (press `w`)
2. Should see gym selection screen
3. Click on "PowerFit Gym" card
4. Click "Create New Account"
5. Fill form:
   - Email: `test@powerfit.com`
   - Password: `password123`
   - Confirm: `password123`
6. Click "Create Account"
7. Should auto-login and show dashboard

## 3. Test Login Flow

1. Clear storage or logout
2. Open app → Gym selection
3. Click on "PowerFit Gym"
4. Click "Continue to Login"
5. Fill form:
   - Email: `test@powerfit.com`
   - Password: `password123`
6. Click "Sign In"
7. Should show dashboard

## 4. Test Features

1. Log a meal manually
2. Use AI chat: "I ate chicken breast with rice"
3. Pull down to refresh dashboard
4. Check XP and level progress
5. Check macro rings update

## Expected Console Output

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
Token preview: eyJhbGciOiJIUzI1NiIs...
Token saved to store
```

### AI Chat
```
=== AI CHAT MOUNTED ===
Token on mount: Token exists
=== SEND MESSAGE DEBUG ===
Token exists: true
✅ Sending message: I ate chicken breast with rice
Response status: 200
```

## Quick Checks

- [ ] Backend running on localhost:8000
- [ ] Test gyms created (5 gyms)
- [ ] Mobile app starts without errors
- [ ] Gym selection shows gyms
- [ ] Can select a gym (purple border + checkmark)
- [ ] Can create new account
- [ ] Auto-login works after registration
- [ ] Dashboard loads with data
- [ ] Can login with existing account
- [ ] Token persists after refresh
- [ ] AI chat works
- [ ] Meal logging works
- [ ] Dashboard updates on refresh

## Troubleshooting

### No gyms showing
```bash
python scripts/create_test_gyms.py
```

### Backend not running
```bash
uvicorn app.main:app --reload
```

### Token not persisting
```bash
cd mobile
npx expo start -c
```

### Registration fails
- Check backend console for errors
- Verify gym exists in database
- Try different email

## Documentation

- `AUTH_SETUP_GUIDE.md` - Complete setup guide
- `MULTI_GYM_AUTH_SUMMARY.md` - Implementation summary
- `mobile/AUTH_FLOW_GUIDE.md` - Detailed flow docs
