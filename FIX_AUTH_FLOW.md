# Fix: App Not Showing Login/Location Selection

## Problem

The app is skipping the login/location selection screens and going directly to the dashboard. This happens because there's cached authentication data in storage.

## Solution: Clear Cached Auth Data

### Option 1: Clear Storage via Browser Console (Web)

If running on web, open browser console and run:

```javascript
// Clear all auth data
localStorage.clear();
sessionStorage.clear();

// Or specifically clear auth keys
localStorage.removeItem('auth_token');
localStorage.removeItem('gym_id');
localStorage.removeItem('location');
localStorage.removeItem('user_id');
localStorage.removeItem('onboarding_completed');

// Reload the page
window.location.reload();
```

### Option 2: Add Logout Button (Recommended)

I'll add a logout button to the dashboard so you can easily clear auth and start fresh.

### Option 3: Clear AsyncStorage (Mobile)

If running on mobile device/emulator:

1. Uninstall the app
2. Reinstall it
3. Or use React Native Debugger to clear AsyncStorage

### Option 4: Use the Logout Endpoint

The app already has a logout function. Let me add a quick way to trigger it.

## Quick Fix Script

I'll create a simple logout button on the dashboard for you.
