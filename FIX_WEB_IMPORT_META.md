# Fix: Web "import.meta" Error

## Problem
When opening the app in web browser, got error:
```
Uncaught SyntaxError: Cannot use 'import.meta' outside a module
```

## Root Cause
Two issues were causing this error:
1. `@react-native-async-storage/async-storage` doesn't work on web
2. `expo-constants` uses `import.meta` internally which isn't supported in web bundles

## Solution

### 1. Platform-Aware Storage
Created a storage adapter that uses `localStorage` on web and `AsyncStorage` on native.

### 2. Conditional Import of expo-constants
Changed `expo-constants` to only load on native platforms using dynamic `require()`.

## Files Changed

### 1. Created `mobile/utils/storage.ts`
Platform-aware storage adapter that automatically switches between AsyncStorage and localStorage.

### 2. Updated `mobile/store/useLocation.ts`
Changed from:
```typescript
import AsyncStorage from "@react-native-async-storage/async-storage";
storage: createJSONStorage(() => AsyncStorage),
```

To:
```typescript
import storage from "../utils/storage";
storage: createJSONStorage(() => storage),
```

### 3. Updated `mobile/config/api.ts`
Changed from:
```typescript
import Constants from 'expo-constants';
```

To:
```typescript
// Only import Constants on native platforms
let Constants: any = null;
if (Platform.OS !== 'web') {
  Constants = require('expo-constants').default;
}
```

This prevents `expo-constants` from loading on web, avoiding the `import.meta` error.

## Result
✅ App now works on web browser
✅ Storage works on all platforms
✅ API URL detection works on native
✅ No import.meta errors

## Testing
1. Open web browser: Press `w` in Expo terminal or visit `http://localhost:8081`
2. App should load without errors
3. Select a location
4. Refresh page → Location persists (stored in localStorage)
5. Test on Expo Go → Should still work with device IP detection

## Note
When using packages that might have web compatibility issues:
- Use dynamic `require()` with platform checks
- Only load native-specific packages on native platforms
- Provide web alternatives when needed
