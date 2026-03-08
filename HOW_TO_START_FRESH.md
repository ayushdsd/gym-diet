# How to Start Fresh - See Login/Location Selection

## The Issue

The app is loading cached authentication data and skipping directly to the dashboard. You need to clear this cached data to see the login flow.

## ✅ SOLUTION: Use the Logout Button

I've added a **Logout button** to the dashboard header (top right corner).

### Steps:

1. **Start the app** (if not already running):
   ```bash
   cd mobile
   npx expo start
   ```

2. **Open the app** in your browser/device
   - Press `w` for web
   - Press `a` for Android
   - Press `i` for iOS

3. **Click the "Logout" button** in the top right corner of the dashboard
   - It's a red button next to the Level badge and Streak flame

4. **You'll be redirected to the location selection screen** ✅

5. **Now you can test the complete flow**:
   - Select Location → Select Gym → Login/Register → Onboarding → Dashboard

## Alternative: Clear Browser Storage (Web Only)

If you're running on web and want to manually clear storage:

### Method 1: Browser Console
```javascript
// Open browser console (F12)
localStorage.clear();
sessionStorage.clear();
location.reload();
```

### Method 2: Browser DevTools
1. Open DevTools (F12)
2. Go to "Application" tab
3. Click "Clear storage"
4. Click "Clear site data"
5. Refresh the page

## Alternative: Clear App Data (Mobile)

### Android:
1. Long press the app icon
2. App info → Storage → Clear data
3. Reopen the app

### iOS:
1. Uninstall the app
2. Reinstall it

## Complete Auth Flow

Once you logout, you'll see this flow:

```
1. Select Location Screen
   ↓
2. Select Gym Screen
   ↓
3. Login/Register Screen
   ↓
4. Onboarding Flow (if first time)
   - Gender
   - Age
   - Height
   - Weight
   - Goal
   - Complete
   ↓
5. Dashboard (with gamification!)
```

## Testing the Gamification System

After logging in fresh:

1. **Log your first meal**:
   - Go to "Log Meal"
   - Enter: Protein: 30g, Carbs: 40g, Fats: 15g
   - Submit

2. **You should see**:
   - ✅ "+10 XP" animation
   - ✅ "First Steps" badge unlocked 🍽️
   - ✅ Streak: 1 day 🔥
   - ✅ Level 1 on dashboard

3. **View your profile**:
   - Click "View Profile" button
   - See your level, XP, streak, and badges

## Quick Test: Award Lots of XP

If you want to quickly test level-ups without logging many meals:

```python
# scripts/quick_xp_test.py
from app.db.session import SessionLocal
from app.models.models import User
from app.services.xp_manager import award_xp

db = SessionLocal()

# Get your user (replace 1 with your user ID)
user = db.query(User).filter(User.id == 1).first()

# Award 2500 XP (reaches level 5, earns streak freeze)
for i in range(250):
    award_xp(db, user, "meal_logged", {})
    db.commit()

print(f"Total XP: {user.total_xp}")
print(f"Level: {user.total_xp // 100}")
print(f"Streak Freezes: {user.streak_freeze_count}")

db.close()
```

Run it:
```bash
python scripts/quick_xp_test.py
```

Then refresh the dashboard to see your new level!

## Troubleshooting

### Issue: Logout button not visible
- Make sure you're on the dashboard
- Look in the top right corner next to the level badge
- It's a small red button that says "Logout"

### Issue: Still going to dashboard after logout
- Clear browser cache completely
- Try incognito/private browsing mode
- Check browser console for errors

### Issue: Backend not running
```bash
# Start the backend
uvicorn app.main:app --reload
```

### Issue: Database migrations not applied
```bash
# Apply migrations
alembic upgrade head
```

## Summary

**Easiest way**: Just click the **Logout button** in the top right corner of the dashboard! 🎯

This will clear all auth data and redirect you to the location selection screen where you can start fresh.
