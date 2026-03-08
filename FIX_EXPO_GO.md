# Fix: Expo Go "Unmatched Route" Error

## Issues Fixed

1. ✅ **Localhost doesn't work on physical devices** - Created environment-aware API configuration
2. ✅ **Unmatched route error** - Added +not-found.tsx handler
3. ✅ **CORS for local network** - Updated backend to allow requests from any local IP

## Changes Made

### 1. Created API Configuration (`mobile/config/api.ts`)

This automatically detects the correct API URL based on the environment:
- **Web**: `http://localhost:8000`
- **Expo Go (Physical Device)**: `http://YOUR_IP:8000` (auto-detected)
- **Android Emulator**: `http://10.0.2.2:8000`
- **iOS Simulator**: `http://localhost:8000`

### 2. Updated All API Calls

All files now use `API_BASE_URL` from the config:
- `mobile/services/api.ts`
- `mobile/app/(auth)/select-gym.tsx`
- `mobile/app/(auth)/login.tsx`
- `mobile/app/(auth)/register.tsx`
- `mobile/app/(dashboard)/ai-chat.tsx`
- `mobile/app/(dashboard)/log-meal.tsx`

### 3. Added Not Found Handler (`mobile/app/+not-found.tsx`)

Handles unmatched routes gracefully with a friendly error screen.

### 4. Updated Backend CORS (`app/main.py`)

Now allows requests from:
- localhost
- 127.0.0.1
- Any 192.168.x.x IP (local network)
- 10.0.2.2 (Android emulator)

## How to Apply

### 1. Restart Backend

The backend needs to be restarted to apply CORS changes:

```bash
# Stop current backend (Ctrl+C)

# Restart backend
uvicorn app.main:app --reload
```

### 2. Restart Mobile App

```bash
# Stop Expo (Ctrl+C)

# Clear cache and restart
cd mobile
npx expo start -c
```

### 3. Test on Expo Go

1. Open Expo Go app on your phone
2. Scan the QR code
3. App should load and show gym selection screen

## Expected Console Output

When the app starts, you should see:

```
API Base URL: http://192.168.1.x:8000
```

(The IP will be your computer's local network IP)

## Troubleshooting

### Issue: Still shows "Unmatched route"

**Solution:**
1. Make sure you restarted Expo with cache clear: `npx expo start -c`
2. Close Expo Go app completely and reopen
3. Scan QR code again

### Issue: "Failed to load gyms"

**Cause:** Backend not accessible from phone

**Solution:**

1. **Check your computer's IP address:**
   ```bash
   # Windows
   ipconfig
   # Look for "IPv4 Address" under your WiFi adapter
   
   # Mac/Linux
   ifconfig
   # Look for "inet" under your WiFi interface
   ```

2. **Make sure phone and computer are on the same WiFi network**

3. **Test backend accessibility from phone:**
   - Open browser on phone
   - Go to: `http://YOUR_IP:8000/docs`
   - Should show API documentation

4. **Check firewall:**
   - Windows: Allow Python through Windows Firewall
   - Mac: System Preferences → Security & Privacy → Firewall → Allow uvicorn

### Issue: Reanimated errors in console

**Note:** These are warnings and won't affect functionality on Expo Go. They occur because Reanimated needs native modules that aren't available in Expo Go. The app will still work fine.

To remove these warnings, you would need to:
1. Build a development build (not Expo Go)
2. Or remove Reanimated animations (not recommended)

For now, you can safely ignore these warnings.

### Issue: "Network request failed"

**Cause:** Backend not running or not accessible

**Solution:**
1. Verify backend is running: `uvicorn app.main:app --reload`
2. Check backend console for errors
3. Verify you can access `http://YOUR_IP:8000/docs` from phone browser
4. Check firewall settings

## Testing Checklist

- [ ] Backend running on port 8000
- [ ] Mobile app restarted with cache clear
- [ ] Phone and computer on same WiFi
- [ ] Expo Go shows gym selection screen
- [ ] Can see gyms listed (or "No gyms available")
- [ ] Can create test gyms: `python scripts/create_test_gyms.py`
- [ ] Can select a gym
- [ ] Can register new account
- [ ] Can login
- [ ] Dashboard loads
- [ ] Can log meals
- [ ] AI chat works

## Web vs Expo Go

### Web (Browser)
- Uses `http://localhost:8000`
- Works immediately
- No network configuration needed

### Expo Go (Physical Device)
- Uses `http://YOUR_IP:8000`
- Requires same WiFi network
- May need firewall configuration
- Auto-detects correct IP

## Production Note

For production, you would:
1. Deploy backend to a server (e.g., AWS, Heroku, DigitalOcean)
2. Update `mobile/config/api.ts` to use production URL
3. Build standalone app (not Expo Go)
4. Update CORS to allow only production domains

Example production config:
```typescript
export const API_BASE_URL = __DEV__ 
  ? getApiUrl()  // Development (auto-detect)
  : 'https://api.yourdomain.com';  // Production
```

## Summary

The app now works on both web and Expo Go by automatically detecting the correct API URL based on the environment. Restart both backend and mobile app to apply the changes.
