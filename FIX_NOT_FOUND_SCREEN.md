# Fix: "This screen doesn't exist" on Expo Go

## Issue

Expo Go was showing "This screen doesn't exist" instead of the gym selection screen.

## Cause

The `<Redirect>` component in `app/index.tsx` doesn't work reliably on native (Expo Go). It works on web but causes routing issues on physical devices.

## Fix Applied

### 1. Simplified Root Layout (`app/_layout.tsx`)

Removed navigation logic from the root layout and explicitly defined all routes:

```typescript
<Stack>
  <Stack.Screen name="index" options={{ headerShown: false }} />
  <Stack.Screen name="(auth)" options={{ headerShown: false }} />
  <Stack.Screen name="(dashboard)" options={{ headerShown: false }} />
  <Stack.Screen name="+not-found" options={{ headerShown: false }} />
</Stack>
```

### 2. Updated Index Screen (`app/index.tsx`)

Changed from `<Redirect>` to `router.replace()` with proper timing:

```typescript
useEffect(() => {
  const timeout = setTimeout(() => {
    if (token && gymId) {
      router.replace("/(dashboard)");
    } else {
      router.replace("/(auth)/select-gym");
    }
  }, 100);
  
  return () => clearTimeout(timeout);
}, [token, gymId, router]);
```

## How to Apply

### 1. Stop Expo

Press `Ctrl+C` in the terminal running Expo

### 2. Clear Cache and Restart

```bash
cd mobile
npx expo start -c
```

### 3. Test on Expo Go

1. Open Expo Go app on your phone
2. Scan the QR code
3. Should show "Loading..." briefly
4. Then redirect to gym selection screen

## Expected Behavior

### First Launch (No Auth)
1. Shows loading spinner with "Loading..." text
2. After 100ms, redirects to gym selection screen
3. Shows list of gyms

### With Auth (Returning User)
1. Shows loading spinner with "Loading..." text
2. After 100ms, redirects to dashboard
3. Shows dashboard with macros and XP

## Console Output

You should see:
```
API Base URL: http://192.168.x.x:8000
User not authenticated, redirecting to gym selection
```

Or if authenticated:
```
API Base URL: http://192.168.x.x:8000
User authenticated, redirecting to dashboard
```

## Troubleshooting

### Issue: Still shows "This screen doesn't exist"

**Solution:**
1. Make sure you cleared cache: `npx expo start -c`
2. Close Expo Go app completely (swipe away from recent apps)
3. Reopen Expo Go
4. Scan QR code again

### Issue: Stuck on "Loading..." screen

**Cause:** Navigation not working

**Solution:**
1. Check console for errors
2. Make sure `useAuth` store is working
3. Try clearing AsyncStorage:
   ```javascript
   // In Expo Go, shake device → Debug Remote JS
   // In console:
   AsyncStorage.clear()
   ```

### Issue: Redirects to wrong screen

**Cause:** Token/gymId state issue

**Solution:**
1. Clear storage and restart
2. Check console logs for token/gymId values
3. Make sure login is saving token correctly

## Testing Checklist

- [ ] Expo restarted with cache clear
- [ ] Expo Go app closed and reopened
- [ ] Shows "Loading..." briefly
- [ ] Redirects to gym selection (first time)
- [ ] Can see gyms or "No gyms available"
- [ ] Can select a gym
- [ ] Can register/login
- [ ] After login, redirects to dashboard
- [ ] Dashboard shows correctly

## Why This Works

### Web vs Native Routing

**Web (Browser):**
- `<Redirect>` works immediately
- Router is synchronous
- No timing issues

**Native (Expo Go):**
- `<Redirect>` can cause race conditions
- Router needs time to initialize
- `router.replace()` with timeout is more reliable

### The 100ms Delay

The small delay ensures:
1. Router is fully initialized
2. Auth state is loaded from AsyncStorage
3. Navigation happens after component mount
4. Prevents "Unmatched route" errors

## Summary

Changed from `<Redirect>` component to `router.replace()` with a small delay to ensure reliable navigation on both web and Expo Go. Restart Expo with cache clear to apply the fix.
