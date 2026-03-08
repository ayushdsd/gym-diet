# Feature 2: Monthly Goal Tracker - Testing Guide

## Pre-Testing Setup

### 1. Ensure Backend is Running
```bash
# Should already be running with auto-reload
# Check terminal for: "Application startup complete"
```

### 2. Populate Test Data (Recommended)
```bash
python scripts/populate_monthly_data.py
```

Expected output:
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

### 3. Restart Mobile App
```bash
cd mobile
npx expo start -c
```

## Test Scenarios

### ✅ Test 1: View Monthly Tracker

**Steps:**
1. Open app and login
2. Navigate to dashboard
3. Scroll down past "Today's Macros" section
4. Locate "📅 Monthly Goal Tracker" card

**Expected Results:**
- Calendar grid displays current month name (e.g., "March 2026")
- Days are arranged in 7-column grid (S M T W T F S)
- Each day shows a colored circle with day number
- Statistics show "X / Y Days Completed" and "Z% Completion Rate"
- Legend shows color meanings (green, red, gray)
- Info box explains ±10% goal criteria

**Pass Criteria:**
- ✓ All UI elements visible
- ✓ Current month displayed correctly
- ✓ Days animate in smoothly
- ✓ Colors match status (green/red/gray)

---

### ✅ Test 2: Verify Day Colors

**Steps:**
1. Look at the calendar grid
2. Identify days with different colors
3. Check if colors match expected status

**Expected Results:**
- **Green days**: Should have checkmark (✓)
- **Red days**: Should have X mark (✗)
- **Gray days**: No meals logged
- Today's date should be visible

**Pass Criteria:**
- ✓ Green = goals met (macros within ±10%)
- ✓ Red = goals missed (has data but not within range)
- ✓ Gray = no data logged
- ✓ Status indicators (✓/✗) visible on colored days

---

### ✅ Test 3: Check Statistics Accuracy

**Steps:**
1. Count green days manually
2. Compare with "Days Completed" stat
3. Verify completion rate calculation

**Expected Results:**
- Completed count matches green days
- Total days = days from start of month to today
- Completion rate = (completed / days_with_data) × 100

**Example:**
- If 3 green days out of 5 logged days
- Should show: "3 / 7 Days Completed" (7 = days in month so far)
- Completion rate: "60.0%" (3/5 = 60%)

**Pass Criteria:**
- ✓ Numbers are accurate
- ✓ Percentage calculated correctly
- ✓ Stats update on refresh

---

### ✅ Test 4: Log Meal and Refresh

**Steps:**
1. Note current completion stats
2. Tap "Log Meal" button
3. Enter macros that meet goals:
   - Protein: 150g
   - Carbs: 250g
   - Fats: 60g
4. Submit meal
5. Return to dashboard
6. Pull down to refresh

**Expected Results:**
- Today's cell turns green with ✓
- Completed count increases by 1
- Completion rate updates
- Smooth animation on update

**Pass Criteria:**
- ✓ Today's status changes to green
- ✓ Stats increment correctly
- ✓ No errors in console
- ✓ Refresh animation smooth

---

### ✅ Test 5: Log Incomplete Meal

**Steps:**
1. Clear today's data (or test on new day)
2. Tap "Log Meal"
3. Enter macros that DON'T meet goals:
   - Protein: 50g (too low)
   - Carbs: 100g (too low)
   - Fats: 20g (too low)
4. Submit meal
5. Return to dashboard
6. Pull down to refresh

**Expected Results:**
- Today's cell turns red with ✗
- Completed count stays same
- Day still counts as "logged"
- Completion rate may decrease

**Pass Criteria:**
- ✓ Today's status changes to red
- ✓ Completed count unchanged
- ✓ Total days with data increases
- ✓ Completion rate recalculates

---

### ✅ Test 6: Animation Performance

**Steps:**
1. Force close app
2. Reopen and login
3. Navigate to dashboard
4. Watch monthly tracker load

**Expected Results:**
- Container fades in (300ms)
- Stats fade in with delay (100ms)
- Calendar fades in with delay (200ms)
- Days animate in sequence (20ms per day)
- Smooth 60fps animations

**Pass Criteria:**
- ✓ No janky animations
- ✓ Staggered entrance looks smooth
- ✓ No layout shifts during animation
- ✓ Animations complete in ~1 second

---

### ✅ Test 7: Edge Cases

#### 7a. First Day of Month
**Steps:**
1. (If testing on March 1st)
2. Check if only 1 day shows

**Expected:**
- Only current day visible
- Stats show "0 / 1" or "1 / 1"

#### 7b. No Data Yet
**Steps:**
1. Create new user
2. View dashboard before logging meals

**Expected:**
- All days gray
- Stats show "0 / X Days Completed"
- Completion rate: "0.0%"

#### 7c. Perfect Month
**Steps:**
1. Use populate script with 100% completion
2. View tracker

**Expected:**
- All days green with ✓
- Completion rate: "100.0%"

**Pass Criteria:**
- ✓ Edge cases handled gracefully
- ✓ No crashes or errors
- ✓ UI remains readable

---

### ✅ Test 8: Pull-to-Refresh

**Steps:**
1. View dashboard with monthly tracker
2. Pull down from top
3. Release to refresh
4. Wait for data to reload

**Expected Results:**
- Refresh spinner shows
- All dashboard data reloads
- Monthly tracker updates
- Animations replay

**Pass Criteria:**
- ✓ Refresh works smoothly
- ✓ Monthly data updates
- ✓ No duplicate API calls
- ✓ Loading states handled

---

### ✅ Test 9: API Response Validation

**Steps:**
1. Open browser dev tools or Postman
2. Make request: `GET http://localhost:8000/meals/monthly-goals`
3. Include auth token in header

**Expected Response:**
```json
{
  "month": "March 2026",
  "days": [
    {
      "date": "2026-03-01",
      "status": "completed",
      "totals": {
        "protein": 155,
        "carbs": 245,
        "fats": 58,
        "calories": 2010
      }
    }
  ],
  "completed_count": 18,
  "total_days": 30,
  "completion_rate": 60.0
}
```

**Pass Criteria:**
- ✓ Status 200 OK
- ✓ JSON structure correct
- ✓ All required fields present
- ✓ Dates in ISO format
- ✓ Numbers are accurate

---

### ✅ Test 10: Console Logs

**Steps:**
1. Open React Native debugger or browser console
2. Navigate to dashboard
3. Check for relevant logs

**Expected Logs:**
```
Loaded monthly goals: { month: "March 2026", ... }
```

**Pass Criteria:**
- ✓ No error messages
- ✓ API calls successful
- ✓ Data loaded correctly
- ✓ No warnings about missing data

---

## Common Issues & Solutions

### Issue: Tracker Not Showing
**Solution:**
- Check if backend is running
- Verify API endpoint exists
- Check auth token is valid
- Look for errors in console

### Issue: All Days Gray
**Solution:**
- Run populate script: `python scripts/populate_monthly_data.py`
- Or manually log meals for current month
- Refresh dashboard

### Issue: Wrong Colors
**Solution:**
- Verify macro targets match (150p, 250c, 60f)
- Check ±10% calculation
- Ensure meals are in current month
- Check timezone settings

### Issue: Stats Don't Update
**Solution:**
- Pull down to refresh
- Check API response in network tab
- Verify state updates in component
- Restart app if needed

### Issue: Animations Laggy
**Solution:**
- Close other apps
- Test on physical device (not simulator)
- Check React Native Reanimated is installed
- Reduce animation delays if needed

---

## Success Criteria

Feature 2 is considered fully working when:

✅ Monthly tracker displays on dashboard  
✅ Calendar grid shows current month  
✅ Days are color-coded correctly  
✅ Statistics are accurate  
✅ Animations are smooth  
✅ Pull-to-refresh updates data  
✅ API endpoint returns correct data  
✅ No console errors  
✅ Works on both web and Expo Go  
✅ Test data script works  

---

## Performance Benchmarks

- **API Response Time**: < 200ms
- **Component Render**: < 100ms
- **Animation Duration**: ~1 second total
- **Refresh Time**: < 500ms
- **Memory Usage**: < 50MB increase

---

## Next Steps After Testing

1. ✅ Verify all test scenarios pass
2. ✅ Check performance benchmarks
3. ✅ Test on multiple devices
4. ✅ Review console for warnings
5. ✅ Document any issues found
6. 🚀 Feature ready for production!

---

## Quick Test Checklist

- [ ] Backend running
- [ ] Test data populated
- [ ] Mobile app started
- [ ] Can view tracker
- [ ] Colors correct
- [ ] Stats accurate
- [ ] Log meal works
- [ ] Refresh works
- [ ] Animations smooth
- [ ] No errors

**All checked?** Feature 2 is ready! 🎉
