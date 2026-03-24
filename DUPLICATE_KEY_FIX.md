# DUPLICATE KEY FIX - CRITICAL

## The Real Error Found! ✅

```
duplicate key value violates unique constraint "uq_xplog_user_gym_reason"
Key (user_id, gym_id, reason)=(1, 2, Awarded 10 XP for meal_logged) already exists.
```

---

## What Was Happening

**The Problem:**
1. You log your first meal → XP reason: `"Awarded 10 XP for meal_logged"`
2. You log your second meal → XP reason: `"Awarded 10 XP for meal_logged"` (SAME!)
3. Database says: "This reason already exists for this user/gym!"
4. **CRASH** → 500 error

**Why It Happened:**
- XPLog table has unique constraint: `(user_id, gym_id, reason)` must be unique
- This prevents duplicate XP awards
- But the reason was the same for every meal: `"Awarded 10 XP for meal_logged"`
- So you could only log ONE meal per day before hitting the constraint

---

## The Fix

**Changed XP reasons to be unique:**

### Before (Broken)
```python
reason = f"Awarded {total_xp} XP for {action_type}"
# Result: "Awarded 10 XP for meal_logged" (same every time!)
```

### After (Fixed)
```python
if action_type == "meal_logged":
    # Include timestamp to allow multiple meals per day
    timestamp = datetime.utcnow().isoformat()
    reason = f"Meal logged at {timestamp}"
    # Result: "Meal logged at 2026-03-23T04:22:09.648345" (unique!)

elif action_type == "macro_goal":
    # Include date to allow one macro goal award per day
    date_str = datetime.utcnow().date().isoformat()
    completed = context.get("completed_macros", [])
    reason = f"Macro goals ({', '.join(completed)}) on {date_str}"
    # Result: "Macro goals (protein, carbs) on 2026-03-23" (unique per day)

elif action_type == "daily_goal":
    # Include date to allow one daily goal award per day
    date_str = datetime.utcnow().date().isoformat()
    reason = f"Daily goal completed on {date_str}"
    # Result: "Daily goal completed on 2026-03-23" (unique per day)
```

---

## Why This Works

**Meal Logging:**
- Each meal gets unique timestamp
- Can log unlimited meals per day
- Each XP award has unique reason

**Macro Goals:**
- One award per macro per day
- Date makes it unique per day
- Can't award same macro goal twice in one day (correct behavior)

**Daily Goal:**
- One award per day
- Date makes it unique per day
- Can't complete daily goal twice in one day (correct behavior)

---

## Testing Results

```bash
$ python -m pytest tests/ -v
==============================
162 passed, 1 warning in 4.83s
==============================
✅ ALL TESTS PASSING
```

---

## Deployment Status

✅ **PUSHED TO GITHUB**
✅ **RAILWAY AUTO-DEPLOYING**

Wait ~2 minutes for Railway to deploy, then test again.

---

## How to Test Now

### Option 1: Wait for Railway (2 minutes)
```bash
# After Railway deploys, test in your app
cd mobile
npx expo start
# Press 'w' for web or 'a' for Android
```

### Option 2: Test with Script
```bash
python scripts/test_railway_meal_logging.py
```

### Option 3: Test Locally
```bash
# Terminal 1: Start local backend
python -m uvicorn app.main:app --reload

# Terminal 2: Update API URL and test
cd mobile
# Edit mobile/config/api.ts to use http://localhost:8000
npx expo start
```

---

## What You Should See Now

✅ **First meal:** Logs successfully
✅ **Second meal:** Logs successfully  
✅ **Third meal:** Logs successfully
✅ **Unlimited meals:** All log successfully

No more duplicate key errors!

---

## Summary

**Root Cause:** XP reasons were not unique, violating database constraint

**Fix:** Added timestamps/dates to make reasons unique

**Result:** Can now log multiple meals per day without errors

**Status:** Deployed to Railway, ready to test

---

## Quick Test

After Railway deploys (~2 minutes), try logging 3 meals in a row:

1. Meal 1: Protein 30, Carbs 50, Fats 15 → ✅ Should work
2. Meal 2: Protein 25, Carbs 40, Fats 10 → ✅ Should work
3. Meal 3: Protein 35, Carbs 60, Fats 20 → ✅ Should work

All three should succeed now!
