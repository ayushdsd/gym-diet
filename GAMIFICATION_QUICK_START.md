# Gamification System - Quick Start Guide

## Prerequisites

Make sure you have:
- Python backend running
- PostgreSQL database running
- Mobile app dependencies installed

## Step 1: Apply Database Migrations

The gamification system requires 5 new database migrations. Apply them:

```bash
# Navigate to project root
cd C:\Users\Ayush\Desktop\GYM DIET

# Apply all pending migrations
alembic upgrade head
```

You should see output confirming these migrations were applied:
- `20260307_000008_add_gamification_fields`
- `20260307_000009_add_xplog_action_type`
- `20260307_000010_create_badge_table`
- `20260307_000011_create_user_badge_table`
- `20260307_000012_create_streak_history_table`

## Step 2: Start the Backend Server

```bash
# Start FastAPI server
uvicorn app.main:app --reload
```

The server should start on `http://localhost:8000`

Verify the new endpoints are available:
- `http://localhost:8000/docs` - Check for `/gamification/*` endpoints

## Step 3: Start the Mobile App

Open a new terminal:

```bash
# Navigate to mobile directory
cd mobile

# Start Expo
npx expo start
```

Choose your platform:
- Press `w` for web
- Press `a` for Android
- Press `i` for iOS

## Step 4: Test the Gamification System

### Test 1: Log Your First Meal (Earn First Badge!)

1. Login to the app
2. Navigate to "Log Meal"
3. Enter meal data:
   - Protein: 30g
   - Carbs: 40g
   - Fats: 15g
4. Submit

**Expected Results**:
- ✅ +10 XP awarded
- ✅ "First Steps" badge unlocked 🍽️
- ✅ Streak starts at 1 day
- ✅ Level 1 displayed on dashboard
- ✅ XP progress bar shows 10/100 XP

### Test 2: View Gamification Profile

1. On dashboard, tap "View Profile" button
2. See your gamification stats:
   - Current Level: 1
   - Total XP: 10
   - Current Streak: 1 🔥
   - Badges: 1/9 unlocked
   - XP History chart

### Test 3: Earn More XP and Level Up

Log multiple meals to earn XP:

```
Meal 1: +10 XP → Total: 10 XP (Level 1)
Meal 2: +10 XP → Total: 20 XP (Level 1)
Meal 3: +10 XP → Total: 30 XP (Level 1)
...continue until...
Meal 40: +10 XP → Total: 400 XP (Level 2!) 🎉
```

**At 400 XP, you'll level up to Level 2!**
- Level-up modal appears
- Confetti animation plays
- "Level 2 Reached!" message

### Test 4: Build a Streak

Log meals on consecutive days:

**Day 1**: Log meal → Streak: 1 day
**Day 2**: Log meal → Streak: 2 days
**Day 3**: Log meal → Streak: 3 days
...
**Day 7**: Log meal → Streak: 7 days 🔥 (gold flame!)
- Unlock "Week Warrior" badge
- Unlock "Consistent Logger" badge
- 1.5x XP multiplier activated!

### Test 5: Reach Level 5 (Earn Streak Freeze)

Keep logging meals until you reach 2,500 XP (Level 5):

**At Level 5**:
- Level-up modal shows "Streak Freeze Earned!" ❄️
- Freeze count: 1
- Can now miss 1 day without losing streak

## Quick Testing Script

Want to test quickly? Use this Python script to award XP directly:

```python
# scripts/test_gamification.py
from app.db.session import SessionLocal
from app.models.models import User
from app.services.xp_manager import award_xp
from app.services.level_system import calculate_level

db = SessionLocal()

# Get your user (replace with your user ID)
user = db.query(User).filter(User.id == 1).first()

# Award 2500 XP to reach level 5
for i in range(250):
    award_xp(db, user, "meal_logged", {})
    db.commit()

print(f"Total XP: {user.total_xp}")
print(f"Level: {calculate_level(user.total_xp)}")
print(f"Streak Freezes: {user.streak_freeze_count}")

db.close()
```

Run it:
```bash
python scripts/test_gamification.py
```

## Verify Everything Works

### Backend Verification

```bash
# Run all tests
python -m pytest tests/ -v

# Should see: 139 passed
```

### API Verification

Test the endpoints manually:

```bash
# Get gamification profile
curl -X GET "http://localhost:8000/gamification/profile" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get badges
curl -X GET "http://localhost:8000/gamification/badges" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get XP history
curl -X GET "http://localhost:8000/gamification/xp-history?days=30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Frontend Verification

Check these components are visible:
- ✅ Dashboard shows level badge
- ✅ Dashboard shows streak flame 🔥
- ✅ Dashboard shows XP progress bar
- ✅ "View Profile" button with notification badge (if new badges)
- ✅ Gamification profile page loads
- ✅ Badge grid shows all 9 badges
- ✅ XP history chart displays

## Troubleshooting

### Issue: Migrations fail

```bash
# Check current migration version
alembic current

# If stuck, try:
alembic downgrade -1
alembic upgrade head
```

### Issue: Backend errors

```bash
# Check logs for errors
# Look for import errors or database connection issues

# Verify all services are importable:
python -c "from app.services.level_system import calculate_level; print('OK')"
python -c "from app.services.xp_manager import award_xp; print('OK')"
python -c "from app.services.streak_tracker import mark_day_active; print('OK')"
```

### Issue: Frontend not showing gamification

```bash
# Clear cache and restart
cd mobile
rm -rf .expo
npx expo start --clear
```

### Issue: Animations not playing

Check browser console for errors. Animations use React Native Reanimated, which requires:
- Reanimated plugin in babel.config.js
- Proper imports in components

## What to Expect

### Dashboard View
```
┌─────────────────────────────┐
│  Level 1  ⭐                │
│  10 / 100 XP                │
│  [████░░░░░░] 10%           │
│                             │
│  🔥 1 day streak            │
│  ❄️ x0 freezes              │
│                             │
│  [View Profile]             │
└─────────────────────────────┘
```

### After Logging Meal
```
1. XP animation: "+10 XP" floats up
2. If level up: Modal with confetti
3. If badge: Badge popup appears
4. Dashboard updates automatically
```

### Gamification Profile
```
┌─────────────────────────────┐
│  Level 1  ⭐                │
│  10 / 100 XP (10%)          │
│                             │
│  Current Streak: 1 🔥       │
│  Highest Streak: 1          │
│  Streak Freezes: 0 ❄️       │
│                             │
│  Badges (1/9)               │
│  ┌─────┬─────┬─────┐       │
│  │ 🍽️  │ 📝  │ 🎯  │       │
│  │ ✓   │ ✗   │ ✗   │       │
│  └─────┴─────┴─────┘       │
│                             │
│  XP History (30 days)       │
│  [Chart showing daily XP]   │
└─────────────────────────────┘
```

## Next Steps

1. **Test all badge unlocks**: Try to unlock all 9 badges
2. **Test streak mechanics**: Build a 7-day streak, then 30-day
3. **Test streak freeze**: Miss a day after earning a freeze
4. **Test level progression**: Reach levels 5, 10, 20
5. **Test timezone handling**: Change gym location, verify streaks

## Badge Unlock Guide

| Badge | Requirement | XP Needed |
|-------|-------------|-----------|
| 🍽️ First Steps | Log 1 meal | 0 |
| 📝 Consistent Logger | 7-day streak | ~70 |
| 🎯 Macro Master | Hit daily goal 10x | ~500 |
| 🔥 Week Warrior | 7-day streak | ~70 |
| 🏆 Month Champion | 30-day streak | ~300 |
| 💯 Century Club | 100-day streak | ~1000 |
| ⭐ Level 10 | Reach level 10 | 10,000 |
| 🌟 Level 20 | Reach level 20 | 40,000 |
| 👑 Level 50 | Reach level 50 | 250,000 |

## Support

If you encounter issues:
1. Check `TASK_12_FINAL_TESTING_GUIDE.md` for detailed testing
2. Check `GAMIFICATION_SYSTEM_COMPLETE.md` for architecture
3. Run backend tests: `python -m pytest tests/ -v`
4. Check browser console for frontend errors

## Success Checklist

- ✅ Migrations applied
- ✅ Backend server running
- ✅ Mobile app running
- ✅ Can log meals
- ✅ XP is awarded
- ✅ Badges unlock
- ✅ Streaks increment
- ✅ Dashboard shows gamification
- ✅ Profile page loads
- ✅ Animations play

**You're all set! Start logging meals and watch your XP grow! 🚀**
