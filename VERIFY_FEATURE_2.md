# Verify Feature 2 Installation

Quick verification steps to ensure Feature 2 is working correctly.

## 1. Check Backend Endpoint

```bash
# Test the API endpoint (replace with your auth token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/meals/monthly-goals
```

**Expected Response:**
```json
{
  "month": "March 2026",
  "days": [...],
  "completed_count": 0,
  "total_days": 7,
  "completion_rate": 0.0
}
```

✅ If you get JSON response → Backend is working!

## 2. Populate Test Data

```bash
python scripts/populate_monthly_data.py
```

**Expected Output:**
```
✅ Found user: test@example.com (ID: 1)
🗑️  Cleared existing meals for March 2026
✅ Created meal data for March 2026
📊 Stats:
   - Total days in month so far: 7
   - Days with meals logged: 5
   - Days meeting goals: 3
   - Completion rate: 60.0%
🎯 You can now test the Monthly Goal Tracker!
```

✅ If you see stats → Test data created!

## 3. Check Frontend Files

```bash
# Verify component exists
ls mobile/components/MonthlyGoalTracker.tsx

# Verify integration
grep -n "MonthlyGoalTracker" mobile/app/\(dashboard\)/index.tsx
```

**Expected:**
```
mobile/components/MonthlyGoalTracker.tsx
Line 10: import { MonthlyGoalTracker } from "../../components/MonthlyGoalTracker";
Line 150: <MonthlyGoalTracker data={monthlyGoals} loading={loadingMonthly} />
```

✅ If files exist and imports found → Frontend is integrated!

## 4. Start Mobile App

```bash
cd mobile
npx expo start -c
```

**Expected:**
- Metro bundler starts
- QR code appears
- No compilation errors

✅ If app starts → Ready to test!

## 5. Visual Verification

Open the app and check:

1. **Dashboard loads** ✓
2. **Scroll down past macro rings** ✓
3. **See "📅 Monthly Goal Tracker"** ✓
4. **Calendar grid visible** ✓
5. **Days are colored (green/red/gray)** ✓
6. **Stats show "X / Y Days Completed"** ✓
7. **Completion rate percentage shown** ✓
8. **Legend explains colors** ✓

✅ All visible → Feature 2 is working!

## 6. Test Interaction

1. **Tap "Log Meal"**
2. **Enter**: 150p, 250c, 60f
3. **Submit meal**
4. **Return to dashboard**
5. **Pull down to refresh**
6. **Check today's cell turns green** ✓

✅ If today turns green → Full integration working!

## Quick Diagnostic

If something doesn't work:

### Backend Issues
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check logs for errors
# Look in terminal where uvicorn is running
```

### Frontend Issues
```bash
# Check for TypeScript errors
cd mobile
npx tsc --noEmit

# Clear cache and restart
npx expo start -c
```

### Data Issues
```bash
# Re-run populate script
python scripts/populate_monthly_data.py

# Or manually log meals via app
```

## Success Checklist

- [ ] Backend endpoint responds
- [ ] Test data script runs
- [ ] Frontend files exist
- [ ] App compiles without errors
- [ ] Monthly tracker visible on dashboard
- [ ] Calendar shows colored days
- [ ] Stats display correctly
- [ ] Refresh updates data
- [ ] Logging meal changes today's color

**All checked?** Feature 2 is fully working! 🎉

## Need Help?

Check these files:
- `FEATURE_2_IMPLEMENTATION.md` - Technical details
- `FEATURE_2_TESTING.md` - Full test scenarios
- `FEATURE_2_READY.md` - Quick reference

## Console Commands Summary

```bash
# Backend
uvicorn app.main:app --reload

# Test data
python scripts/populate_monthly_data.py

# Frontend
cd mobile
npx expo start -c

# Verify endpoint
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/meals/monthly-goals
```

That's it! Feature 2 should now be fully functional. 🚀
