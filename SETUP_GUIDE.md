# Complete Setup Guide

## The Issue
The app was using a fake "dev-token" instead of real authentication. Now it's fixed to use proper backend login.

## Quick Setup (5 minutes)

### Step 1: Create Test User

```bash
# In project root
python scripts/create_test_user.py
```

You should see:
```
✅ Created gym: Gym A (ID: 1)
✅ Created test user:
   Email: test@example.com
   Password: password
   Gym ID: 1

🎉 Setup complete! You can now login with:
   Email: test@example.com
   Password: password
```

### Step 2: Start Backend

```bash
# In project root
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify it's running:
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

### Step 3: Start Frontend

```bash
cd mobile
npx expo start --clear
```

### Step 4: Login

1. Open app in Expo Go
2. Select "Gym A"
3. Login with:
   - **Email**: `test@example.com`
   - **Password**: `password`
4. You should see the dashboard!

## Verify Everything Works

### Test 1: Check Token
After login, open browser console and look for:
```
Login successful, token: eyJ...
```

### Test 2: Dashboard Loads
You should see:
- Level badge (Level 0)
- Streak flame (0 days)
- Four macro rings (all at 0%)
- Two action buttons (Log Meal, AI Chat)

### Test 3: Log a Meal Manually
1. Click "Log Meal" button
2. Enter:
   - Protein: 50
   - Carbs: 100
   - Fats: 20
3. Click "Log Meal & Earn XP"
4. Should see success alert
5. Return to dashboard
6. **Pull down to refresh**
7. Should see:
   - Macro rings updated
   - XP increased to 10
   - Level still 0 (need 100 XP for level 1)

### Test 4: AI Chat
1. Click "AI Chat" button
2. Type: "I ate chicken breast with rice"
3. Press send (↑ button)
4. Should see:
   - Your message appears (purple bubble)
   - Typing indicator (3 dots)
   - AI response (gray bubble)
   - Success card "Meal Logged! +10 XP"
5. Return to dashboard
6. **Pull down to refresh**
7. Should see updated data

## Environment Setup

### Backend `.env` File

Create `.env` in project root:

```env
# Database
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/gymdiet

# JWT
JWT_SECRET=your-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# OpenAI (Required for AI Chat)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Macro Targets (Optional)
DEFAULT_TARGET_CALORIES=2000
DEFAULT_TARGET_PROTEIN=150
DEFAULT_TARGET_CARBS=250
DEFAULT_TARGET_FATS=60
```

### Database Setup

```bash
# Create database
createdb gymdiet

# Run migrations
alembic upgrade head

# Create test user
python scripts/create_test_user.py
```

## Troubleshooting

### Issue: "Cannot send: empty input or no token"

**Cause**: Not logged in or token not saved

**Fix**:
1. Make sure you logged in successfully
2. Check console for "Login successful, token: ..."
3. If no token, backend might not be running
4. Try logging in again

### Issue: Login fails with "Invalid credentials"

**Cause**: User doesn't exist or wrong password

**Fix**:
1. Run: `python scripts/create_test_user.py`
2. Use exact credentials:
   - Email: `test@example.com`
   - Password: `password`
3. Check backend is running

### Issue: AI Chat says "having trouble connecting"

**Cause**: Backend not running or OpenAI key missing

**Fix**:
1. Check backend is running: `curl http://localhost:8000/health`
2. Check `.env` has `OPENAI_API_KEY`
3. Restart backend after adding key

### Issue: Dashboard shows all zeros

**Cause**: No meals logged yet

**Fix**:
1. Log a meal (manual or AI)
2. Pull down to refresh dashboard
3. Data should appear

### Issue: Data doesn't update after logging meal

**Cause**: Need to refresh dashboard

**Fix**:
1. Go to dashboard
2. **Pull down to refresh** (swipe down)
3. Data will update

## Testing Checklist

- [ ] Backend running on port 8000
- [ ] Database created and migrated
- [ ] Test user created
- [ ] Frontend running in Expo
- [ ] Can select gym
- [ ] Can login successfully
- [ ] Dashboard loads with data
- [ ] Can log meal manually
- [ ] Dashboard updates after refresh
- [ ] AI chat responds to messages
- [ ] AI chat logs meals automatically
- [ ] XP increases after logging meals

## API Endpoints Reference

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password"
```

### Get Progress
```bash
curl http://localhost:8000/user/progress \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Log Meal
```bash
curl -X POST http://localhost:8000/meals \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"protein":50,"carbs":100,"fats":20}'
```

### AI Chat
```bash
curl -X POST http://localhost:8000/ai/message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message":"I ate chicken"}'
```

## Success!

When everything is working:

✅ Login works and saves token
✅ Dashboard loads with your data
✅ Macro rings show progress
✅ Can log meals manually
✅ AI chat responds and logs meals
✅ XP increases with each meal
✅ Dashboard updates on refresh
✅ Streak increases daily

Enjoy your nutrition tracking app! 🎉
