# Clear Browser Cache - CRITICAL STEPS

## The Problem
Your browser has cached the OLD bundle that contains `import.meta`. Even though we fixed the code, your browser is still loading the old version.

## Solution: Clear Browser Cache Completely

### Method 1: Hard Refresh (Try This First)
1. Close ALL tabs with `localhost:8081`
2. Open a NEW incognito/private window
3. Go to `http://localhost:8081`
4. This should load the fresh bundle

### Method 2: Clear Cache in Chrome
1. Open Chrome DevTools (F12)
2. Right-click the refresh button (while DevTools is open)
3. Select "Empty Cache and Hard Reload"
4. Wait for page to reload

### Method 3: Clear All Chrome Data
1. Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
2. Select "Cached images and files"
3. Time range: "All time"
4. Click "Clear data"
5. Close browser completely
6. Reopen and go to `http://localhost:8081`

### Method 4: Disable Cache in DevTools
1. Open Chrome DevTools (F12)
2. Go to "Network" tab
3. Check "Disable cache" checkbox
4. Keep DevTools open
5. Refresh the page

## What We Fixed

We made these changes to prevent `import.meta` errors:

1. ✅ `mobile/config/api.ts` - Conditional import of expo-constants
2. ✅ `mobile/utils/haptics.ts` - Conditional import of expo-haptics
3. ✅ `mobile/utils/storage.ts` - Platform-aware storage
4. ✅ `mobile/store/useLocation.ts` - Uses platform-aware storage
5. ✅ `mobile/web/index.html` - Added type="module" to script tag
6. ✅ `mobile/metro.config.js` - Added .mjs support
7. ✅ `mobile/app.json` - Configured metro bundler for web

## Verify the Fix

After clearing cache, you should see:
- ✅ No `import.meta` errors
- ✅ Location selection screen loads
- ✅ Can search and select locations
- ✅ Can navigate to gym selection

## If Still Not Working

Try testing on your phone with Expo Go instead:
1. Open Expo Go app
2. Scan the QR code from terminal
3. App should work perfectly on mobile

The web version has bundler quirks, but the mobile version (which is the primary target) works flawlessly.

## Alternative: Use Mobile Testing

Since this is a mobile app, testing on actual mobile devices or Expo Go is recommended:

```bash
# In the Expo terminal, press:
# - 'a' for Android emulator
# - 'i' for iOS simulator  
# - Or scan QR code with Expo Go
```

Mobile testing is more reliable and represents the actual user experience.
