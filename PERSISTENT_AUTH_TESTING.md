# Persistent Authentication Testing Guide

## Quick Test Checklist

### ✅ Test 1: Fresh Install (New User)
1. Clear app data or use fresh install
2. Open app
3. **Expected**: Location selection screen appears
4. Complete full flow: Location → Gym → Register → Onboarding → Dashboard
5. **Expected**: Reaches dashboard successfully

### ✅ Test 2: App Restart (Persistent Login)
1. Login to app and reach dashboard
2. **Close app completely** (swipe away from recent apps)
3. Reopen app
4. **Expected**: 
   - Brief loading screen
   - Automatically navigates to dashboard
   - No login screen shown
   - User data intact

### ✅ Test 3: Logout Functionality
1. From dashboard, locate logout button (top right, red button)
2. Click "Logout"
3. **Expected**: Navigates to location selection
4. Close and reopen app
5. **Expected**: Still on location selection (not auto-logged in)

### ✅ Test 4: Incomplete Onboarding
1. Register new account
2. Start onboarding (e.g., complete gender selection)
3. Close app before completing all steps
4. Reopen app
5. **Expected**: 
   - Resumes at onboarding screen
   - Not sent to dashboard
   - Progress preserved

### ✅ Test 5: Multiple Sessions
1. Login on device A
2. Logout
3. Login with different account
4. Close and reopen app
5. **Expected**: Second account remains logged in

## Detailed Testing Scenarios

### Scenario 1: First Time User Journey
```
Step 1: Open app
  → See: Loading screen (brief)
  → Navigate to: Location selection

Step 2: Select location (e.g., "Mumbai")
  → Click: Continue button
  → Navigate to: Gym selection (filtered by Mumbai)

Step 3: Select gym (e.g., "PowerFit Mumbai Central")
  → Click: Continue button
  → Navigate to: Login screen

Step 4: Click "Create New Account"
  → Navigate to: Register screen

Step 5: Fill registration form
  - Email: test@example.com
  - Password: password123
  - Confirm: password123
  → Click: Create Account
  → Backend: Creates user
  → Auto-login: Triggered
  → SecureStore: Saves auth data
  → Navigate to: Onboarding (gender selection)

Step 6: Complete onboarding
  - Gender → Age → Height → Weight → Goal
  → Backend: Calculates macros
  → SecureStore: Updates onboarding status
  → Navigate to: Dashboard

Step 7: Close app completely

Step 8: Reopen app
  → See: Loading screen (brief)
  → SecureStore: Loads saved session
  → Navigate to: Dashboard (automatic)
  ✅ SUCCESS: No login required
```

### Scenario 2: Returning User
```
Step 1: Open app
  → Loading screen appears
  → loadSession() runs
  → SecureStore checked for token
  → Token found: ✅
  → Auth state restored
  → Navigate to: Dashboard

Step 2: Verify data
  → Macros displayed correctly
  → XP and level shown
  → Streak count accurate
  ✅ SUCCESS: Session fully restored
```

### Scenario 3: Logout and Re-login
```
Step 1: From dashboard, click "Logout"
  → logout() function called
  → SecureStore: All keys deleted
  → Zustand state: Reset
  → Navigate to: Location selection

Step 2: Close and reopen app
  → loadSession() runs
  → SecureStore: No token found
  → Navigate to: Location selection
  ✅ SUCCESS: Logout persisted

Step 3: Login again
  → Select location → gym → login
  → Enter credentials
  → Backend validates
  → saveAuthData() called
  → SecureStore: New session saved
  → Navigate to: Dashboard

Step 4: Close and reopen app
  → Navigate to: Dashboard (automatic)
  ✅ SUCCESS: New session persisted
```

## Console Log Verification

### Expected Logs on App Start (Authenticated):
```
=== LOADING SESSION ===
Token found: true
Gym ID found: 1
User ID found: 123
Onboarding completed: true
✅ Session restored successfully
=== NAVIGATION DECISION ===
Is authenticated: true
Has token: true
Has gym ID: true
Onboarding completed: true
✅ Redirecting to dashboard
```

### Expected Logs on App Start (Not Authenticated):
```
=== LOADING SESSION ===
Token found: false
Gym ID found: null
User ID found: null
Onboarding completed: false
❌ No valid session found
=== NAVIGATION DECISION ===
Is authenticated: false
Has token: false
Has gym ID: false
Onboarding completed: false
❌ Not authenticated, redirecting to location selection
```

### Expected Logs on Login:
```
=== LOGIN SUCCESS ===
Access token received: Yes
Token preview: eyJhbGciOiJIUzI1NiIs...
User ID: 123
Onboarding completed: true
=== SAVING AUTH DATA ===
Token: Yes
Gym ID: 1
User ID: 123
Onboarding completed: true
✅ Auth data saved successfully
Auth data saved to SecureStore
```

### Expected Logs on Logout:
```
=== LOGGING OUT ===
✅ Logged out successfully
```

## Common Issues and Solutions

### Issue 1: App doesn't auto-login after restart
**Symptoms**: Always shows location selection
**Possible Causes**:
- SecureStore not saving properly
- Token not being loaded
- Navigation logic issue

**Debug Steps**:
1. Check console for "Session restored successfully"
2. Verify SecureStore has data:
   ```typescript
   const token = await SecureStore.getItemAsync('auth_token');
   console.log('Token:', token);
   ```
3. Check if `isAuthenticated` is true in Zustand

**Solution**: Ensure `saveAuthData()` is called after login

### Issue 2: Logout doesn't work
**Symptoms**: User still logged in after logout
**Possible Causes**:
- SecureStore not clearing
- State not resetting

**Debug Steps**:
1. Check console for "Logged out successfully"
2. Verify SecureStore is empty after logout
3. Check Zustand state is reset

**Solution**: Ensure `logout()` function completes all steps

### Issue 3: Onboarding status not persisting
**Symptoms**: Always redirected to onboarding
**Possible Causes**:
- Onboarding status not saved to SecureStore
- Backend not returning correct status

**Debug Steps**:
1. Check backend response includes `onboarding_completed`
2. Verify SecureStore has `onboarding_completed` key
3. Check console logs during login

**Solution**: Ensure backend returns onboarding status

### Issue 4: Loading screen flickers
**Symptoms**: Brief flash of location screen before dashboard
**Possible Causes**:
- Navigation timing issue
- Session loading too slow

**Debug Steps**:
1. Check `isLoading` state in index.tsx
2. Verify navigation only happens after loading complete

**Solution**: Ensure navigation waits for `isLoading === false`

## Performance Checks

### Loading Time:
- Session restore should take < 100ms
- Total app start to dashboard: < 500ms
- No visible flicker between screens

### Memory Usage:
- SecureStore data is minimal (< 1KB)
- No memory leaks from auth state
- Zustand state properly managed

### Network Calls:
- No unnecessary API calls on app start
- Token validated only when needed
- Efficient data loading

## Security Verification

### Check 1: Token Storage
```typescript
// Should NOT find token in AsyncStorage
const asyncToken = await AsyncStorage.getItem('auth_token');
console.log('AsyncStorage token:', asyncToken); // Should be null

// Should find token in SecureStore
const secureToken = await SecureStore.getItemAsync('auth_token');
console.log('SecureStore token:', secureToken ? 'Exists' : 'None');
```

### Check 2: Token Exposure
- Token should NOT appear in console logs (except debug mode)
- Token should NOT be in plain text storage
- Token should be cleared on logout

### Check 3: Session Validation
- Expired tokens should trigger re-login
- Invalid tokens should be rejected
- Backend should validate all requests

## Platform-Specific Testing

### iOS:
- Test on physical device (SecureStore uses Keychain)
- Verify Face ID/Touch ID doesn't interfere
- Check app backgrounding behavior

### Android:
- Test on physical device (SecureStore uses EncryptedSharedPreferences)
- Verify fingerprint doesn't interfere
- Check app killing behavior

### Web:
- SecureStore falls back to localStorage
- Less secure but functional
- Test in browser

## Automated Testing (Future)

### Unit Tests:
```typescript
describe('Auth Store', () => {
  it('should save auth data to SecureStore', async () => {
    await saveAuthData('token', 1, 123, true);
    const token = await SecureStore.getItemAsync('auth_token');
    expect(token).toBe('token');
  });

  it('should load session from SecureStore', async () => {
    await loadSession();
    expect(isAuthenticated).toBe(true);
  });

  it('should clear auth data on logout', async () => {
    await logout();
    const token = await SecureStore.getItemAsync('auth_token');
    expect(token).toBeNull();
  });
});
```

## Success Criteria

✅ User remains logged in after app restart
✅ Logout clears session completely
✅ New users see location selection
✅ Returning users see dashboard immediately
✅ Onboarding status persists correctly
✅ No security vulnerabilities
✅ No performance issues
✅ Works on iOS, Android, and Web

## Conclusion

Follow this testing guide to ensure persistent authentication works correctly. All tests should pass before considering the feature production-ready.
