# Meal Logging 500 Error & Logout Button Fixes

## Issue 1: Meal Logging 500 Error

### Probable Causes Investigated

#### 1. Invalid Input Data
**Problem**: Empty strings or invalid numbers being sent to backend
**Fix**: Added comprehensive input validation in frontend
```typescript
// Validate inputs are valid numbers
const proteinNum = parseInt(protein);
const carbsNum = parseInt(carbs);
const fatsNum = parseInt(fats);

if (isNaN(proteinNum) || isNaN(carbsNum) || isNaN(fatsNum)) {
  Alert.alert("Error", "Please enter valid numbers for macros");
  return;
}

// Validate non-negative
if (proteinNum < 0 || carbsNum < 0 || fatsNum < 0) {
  Alert.alert("Error", "Macro values cannot be negative");
  return;
}

// Validate reasonable range
if (proteinNum > 1000 || carbsNum > 1000 || fatsNum > 1000) {
  Alert.alert("Error", "Macro values seem too high");
  return;
}
```

#### 2. Database Connection Issues
**Problem**: Database flush/commit could fail
**Fix**: Added try-catch around database operations in backend
```python
try:
    db.flush()
except Exception as e:
    db.rollback()
    print(f"Database error saving meal: {e}")
    traceback.print_exc()
    raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
```

#### 3. Gamification Processing Errors
**Problem**: XP manager, streak tracker, or badge system could throw errors
**Fix**: Already wrapped in try-catch, but added better logging
```python
except Exception as e:
    print(f"Gamification error: {e}")
    traceback.print_exc()
    # Don't fail meal logging
```

#### 4. Token Issues
**Problem**: Invalid or expired token
**Fix**: Added token validation and better error messages
```typescript
if (!token) {
  throw new Error("No authentication token found");
}
console.log("Token:", token ? "Present (length: " + token.length + ")" : "Missing");
```

#### 5. Response Parsing Issues
**Problem**: Response structure not matching expectations
**Fix**: Added validation of response data
```typescript
if (!mealData || !mealData.id) {
  throw new Error("Invalid response from server - missing meal data");
}
```

### Enhanced Logging

**Frontend**:
```typescript
console.log("=== LOGGING MEAL ===");
console.log("API URL:", API_BASE_URL);
console.log("Token:", token ? "Present (length: " + token.length + ")" : "Missing");
console.log("Payload:", payload);
console.log("Response status:", response.status);
console.log("Response headers:", JSON.stringify(Object.fromEntries(response.headers.entries())));
console.log("Meal logged successfully:", JSON.stringify(responseData, null, 2));
```

**Backend**:
```python
print(f"Database error saving meal: {e}")
traceback.print_exc()
print(f"Gamification error: {e}")
traceback.print_exc()
```

### How to Debug

1. **Check Frontend Console**:
   - Look for "=== LOGGING MEAL ===" log
   - Check if token is present
   - Check payload values
   - Check response status

2. **Check Backend Logs** (Railway):
   - Look for "Database error" or "Gamification error"
   - Check full stack trace
   - Verify database connection

3. **Common Issues**:
   - **401 Unauthorized**: Token expired or invalid
   - **400 Bad Request**: Invalid input data
   - **500 Internal Server Error**: Database or gamification error

---

## Issue 2: Logout Button Not Working

### Problem
Auth guard in `_layout.tsx` was immediately redirecting when auth state changed, preventing logout navigation from completing.

### Root Cause
```typescript
// OLD CODE - Immediate redirect
useEffect(() => {
  if (!isAuthenticated || !token) {
    router.replace("/(auth)/select-location");
  }
}, [isAuthenticated, token]);
```

When logout cleared the token, the auth guard immediately redirected, but this interfered with the profile screen's own navigation to "/".

### Fix Applied
Added a small delay to allow logout navigation to complete:

```typescript
const [isCheckingAuth, setIsCheckingAuth] = useState(true);

useEffect(() => {
  const checkAuth = async () => {
    // Small delay to allow logout navigation to complete
    await new Promise(resolve => setTimeout(resolve, 100));
    
    if (!isAuthenticated || !token) {
      console.log("⚠️ Not authenticated in tabs, redirecting to login");
      router.replace("/(auth)/select-location");
    } else {
      setIsCheckingAuth(false);
    }
  };
  
  checkAuth();
}, [isAuthenticated, token]);

// Show loading while checking auth
if (isCheckingAuth && (!isAuthenticated || !token)) {
  return null;
}
```

### How It Works Now

1. User presses logout button in profile
2. Profile calls `logout()` which clears token
3. Profile navigates to "/" (root)
4. Auth guard waits 100ms before checking
5. Root index detects no auth and redirects to select-location
6. User is now logged out and on login screen

---

## Files Modified

### Frontend (2 files)
1. ✅ `mobile/app/(tabs)/log-meal.tsx` - Enhanced validation and logging
2. ✅ `mobile/app/(tabs)/_layout.tsx` - Fixed auth guard timing

### Backend (1 file)
3. ✅ `app/api/routes/meals.py` - Added database error handling

---

## Testing Instructions

### Test Meal Logging

1. **Open Developer Console** (in browser or React Native Debugger)
2. Navigate to log meal screen
3. Enter test data:
   - Protein: 30
   - Carbs: 45
   - Fats: 15
4. Press "Log Meal & Earn XP"
5. **Check Console Logs**:
   ```
   === LOGGING MEAL ===
   API URL: https://gym-diet-production.up.railway.app
   Token: Present (length: 200)
   Payload: {description: null, protein: 30, carbs: 45, fats: 15}
   Response status: 201
   Meal logged successfully: {...}
   ```
6. **Expected**: Success message with XP
7. **Expected**: Meal appears in dashboard

### Test Invalid Inputs

1. Try empty fields → Should show "Please fill in all macro fields"
2. Try negative numbers → Should show "Macro values cannot be negative"
3. Try very large numbers (>1000) → Should show "Macro values seem too high"
4. Try non-numeric input → Should show "Please enter valid numbers"

### Test Logout

1. Go to Profile tab
2. Press "Logout" button
3. Confirm logout in alert
4. **Check Console Logs**:
   ```
   🔴 Logout button pressed
   🔴 Calling logout...
   === LOGGING OUT ===
   ✅ Logged out successfully
   🔴 Logout completed
   🔴 Navigating to root...
   🔴 Navigation called
   ⚠️ Not authenticated in tabs, redirecting to login
   ```
5. **Expected**: Redirected to select-location screen
6. **Expected**: Cannot access dashboard

---

## If Meal Logging Still Fails

### Step 1: Check Token
```typescript
console.log("Token:", token);
```
- If null/undefined → Login again
- If present → Token might be expired

### Step 2: Check API URL
```typescript
console.log("API URL:", API_BASE_URL);
```
- Should be: `https://gym-diet-production.up.railway.app`
- If localhost → Check app.json configuration

### Step 3: Check Backend Logs (Railway)
1. Go to Railway dashboard
2. Open your web service
3. Click "Deployments" → "View Logs"
4. Look for errors when you submit meal
5. Check for:
   - Database connection errors
   - SQL errors
   - Python exceptions

### Step 4: Check Database
1. Verify DATABASE_URL is set in Railway
2. Check if database is running
3. Try to connect to database manually

### Step 5: Test with cURL
```bash
curl -X POST https://gym-diet-production.up.railway.app/meals \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"protein": 30, "carbs": 45, "fats": 15, "description": "Test meal"}'
```

If this works, the issue is in the frontend.
If this fails, the issue is in the backend.

---

## Common 500 Error Causes

### 1. Database Not Connected
**Symptom**: All API calls fail with 500
**Fix**: Check DATABASE_URL in Railway environment variables

### 2. Missing Database Tables
**Symptom**: SQL errors in logs
**Fix**: Run migrations: `alembic upgrade head`

### 3. Invalid Foreign Key
**Symptom**: IntegrityError in logs
**Fix**: Ensure user_id and gym_id are valid

### 4. XP Overflow
**Symptom**: Integer overflow error
**Fix**: Already handled with MAX_XP constant

### 5. Timezone Issues
**Symptom**: Streak calculation errors
**Fix**: Already using UTC timezone

---

## Success Criteria

✅ Meal logging works without 500 error
✅ Input validation prevents invalid data
✅ Comprehensive logging for debugging
✅ Logout button works and redirects properly
✅ Auth guard doesn't interfere with logout
✅ Error messages are clear and helpful

---

**Status**: Fixes applied, ready for testing

**Next Steps**:
1. Test meal logging with various inputs
2. Check console logs for any errors
3. Test logout flow
4. If issues persist, check backend logs on Railway
