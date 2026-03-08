# Fix: Redirect Loop on Expo Go

## Issue

The app was stuck in a redirect loop showing "This screen doesn't exist" and logging:
```
User not authenticated, redirecting to gym selection
User not authenticated, redirecting to gym selection
User not authenticated, redirecting to gym selection
...
```

## Root Causes

1. **Missing layout file** in `(auth)` folder - Routes weren't properly registered
2. **No navigation guard** in `index.tsx` - Kept re-navigating on every render

## Fixes Applied

### 1. Created Auth Layout (`mobile/app/(auth)/_layout.tsx`)

Added missing layout file to properly register auth routes:

```typescript
import { Stack } from "expo-router";

export default function AuthLayout() {
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="select-gym" />
      <Stack.Screen name="login" />
      <Stack.Screen name="register" />
    </Stack>
  );
}
```

### 2. Added Navigation Guard (`mobile/app/index.tsx`)

Prevented infinite redirect loop:

```typescript
const pathname = usePathname();
const [hasNavigated, setHasNavigated] = useState(false);

useEffect(() => {
  // Only navigate if we're on the index page and haven't navigated yet
  if (pathname !== "/" || hasNavigated) return;
  
  // ... navigation logic
}, [pathname, hasNavigated, ...]);
```

## How to Apply

### 1. Stop Expo

Press `Ctrl+C` in the terminal

### 2. Clear Cache and Restart

```bash
cd mobile
npx expo start -c
```

### 3. Test on Expo Go

1. **Close Expo Go app completely** (swipe away from recent apps)
2. **Reopen Expo Go**
3. **Scan QR code**
4. Should show "Loading..." briefly
5. Then show gym selection screen

## Expected Behavior

### Console Output (One Time Only)
```
API Base URL: http://192.168.x.x:8000
User not authenticated, redirecting to gym selection
```

Should only log ONCE, not repeatedly.

### Visual Flow
1. Shows "Loading..." screen (100ms)
2. Redirects to gym selection
3. Shows gym list or "No gyms available"

## Troubleshooting

### Issue: Still shows redirect loop

**Solution:**
1. Make sure you cleared cache: `npx expo start -c`
2. Close Expo Go completely (not just minimize)
3. Delete app data:
   - Android: Long press Expo Go → App Info → Storage → Clear Data
   - iOS: Delete and reinstall Expo Go
4. Restart and scan QR code again

### Issue: "This screen doesn't exist" persists

**Cause:** Old bundle cached

**Solution:**
```bash
# Stop Expo
# Delete cache folders
cd mobile
rm -rf .expo
rm -rf node_modules/.cache

# Restart
npx expo start -c
```

### Issue: Shows loading screen forever

**Cause:** Navigation not working

**Solution:**
1. Check console for errors
2. Verify `usePathname()` is working
3. Check if `hasNavigated` state is being set
4. Add more logging:
```typescript
console.log("Pathname:", pathname);
console.log("Has navigated:", hasNavigated);
```

## Why This Happened

### Missing Layout File

Expo Router requires a `_layout.tsx` file in each route group to:
- Register the routes
- Define navigation structure
- Set screen options

Without it, routes like `/(auth)/select-gym` weren't recognized, causing "Unmatched route" errors.

### Redirect Loop

The `useEffect` in `index.tsx` was running on every render because:
1. It navigated to gym selection
2. Navigation failed (no layout)
3. Stayed on index page
4. `useEffect` ran again
5. Repeat...

The guard prevents this by:
- Checking if we're on the index page (`pathname === "/"`)
- Only navigating once (`hasNavigated` flag)

## File Structure

After fixes, the structure should be:

```
mobile/app/
├── _layout.tsx              # Root layout
├── index.tsx                # Entry point with navigation
├── +not-found.tsx           # 404 handler
├── (auth)/
│   ├── _layout.tsx          # Auth layout (NEW!)
│   ├── select-gym.tsx
│   ├── login.tsx
│   └── register.tsx
└── (dashboard)/
    ├── _layout.tsx          # Dashboard layout
    ├── index.tsx
    ├── ai-chat.tsx
    └── log-meal.tsx
```

## Testing Checklist

- [ ] Expo restarted with cache clear
- [ ] Expo Go closed and reopened
- [ ] Shows "Loading..." briefly (not stuck)
- [ ] Redirects to gym selection (only once)
- [ ] Console shows redirect log only ONCE
- [ ] Can see gym list
- [ ] Can select a gym
- [ ] Can navigate to login/register
- [ ] No more "This screen doesn't exist"

## Summary

Added missing `_layout.tsx` file in the `(auth)` folder and added a navigation guard in `index.tsx` to prevent redirect loops. Restart Expo with cache clear and close/reopen Expo Go to apply the fix.
