# 🧪 Testing Instructions - Feature 1: Location Filter

## Current Status

✅ **Backend Running**: `http://localhost:8000`
✅ **Mobile App Running**: Expo Dev Server on `http://localhost:8081`
✅ **Database Migrated**: Location field added to gyms
✅ **Test Data Created**: Gyms in New York, Chicago, and Miami
✅ **Web Fixed**: Platform-aware storage for web compatibility

## Quick Start Testing

### On Your Phone (Recommended)
1. Open **Expo Go** app
2. Scan the QR code from the terminal
3. App will load automatically

### On Web Browser
1. In the Expo terminal, press `w`
2. Browser opens at `http://localhost:8081`
3. Test the flow in browser

### On Android Emulator
1. In the Expo terminal, press `a`
2. Emulator launches automatically
3. App installs and opens

## What You Should See

### 1️⃣ Location Selection Screen
```
📍
Select Your Location
Choose your city to find nearby gyms

[Search bar]

📍 New York
   Tap to select

📍 Chicago
   Tap to select

📍 Miami
   Tap to select
```

**Test Actions:**
- Type in search bar → Locations filter
- Tap a location → Gets purple border + checkmark
- "Continue to Gyms" button appears

### 2️⃣ Gym Selection Screen
```
← Back

📍 New York

🏋️
Select Your Gym
Choose your gym in New York

[List of gyms in New York only]
```

**Test Actions:**
- Verify only gyms from selected location show
- Tap "← Back" → Returns to location selection
- Select different location → Different gyms appear
- Select a gym → Login/Register buttons appear

### 3️⃣ Login/Register
- Continue to existing login/register flow
- This part was already working

## Test Scenarios

### Scenario 1: Happy Path
1. ✅ Open app
2. ✅ See location selection
3. ✅ Select "Chicago"
4. ✅ See 2 gyms: FitZone, Strength Hub
5. ✅ Select a gym
6. ✅ Continue to login

### Scenario 2: Search
1. ✅ Open app
2. ✅ Type "new" in search
3. ✅ See only "New York"
4. ✅ Clear search
5. ✅ See all locations again

### Scenario 3: Change Location
1. ✅ Select "New York"
2. ✅ See New York gyms
3. ✅ Tap "← Back"
4. ✅ Select "Miami"
5. ✅ See Miami gyms (Peak Performance, Apex Gym)

### Scenario 4: Persistence
1. ✅ Select a location
2. ✅ Close app completely
3. ✅ Reopen app
4. ✅ Should remember location (skip to gym selection)

## Expected Console Output

### When app loads:
```
API Base URL: http://192.168.1.4:8000
Loaded locations: ["New York", "Chicago", "Miami"]
```

### When selecting location:
```
Selected location: Chicago
Setting location: Chicago
```

### When loading gyms:
```
Fetching gyms from: http://192.168.1.4:8000/gyms?location=Chicago
Loaded gyms: [{"id":5,"name":"FitZone","location":"Chicago"}, ...]
```

## Common Issues & Solutions

### ❌ "Failed to load locations"
**Cause:** Backend not running
**Fix:** Check terminal, backend should show "Uvicorn running on http://127.0.0.1:8000"

### ❌ "No gyms available"
**Cause:** No gyms in that location
**Fix:** Run `python scripts/create_test_gyms.py` to create test gyms

### ❌ Can't connect from phone
**Cause:** Phone and computer on different networks
**Fix:** 
- Ensure both on same WiFi
- Check firewall settings
- Try web version first

### ❌ Location doesn't persist
**Cause:** AsyncStorage not working
**Fix:**
- Clear app data
- Restart app
- Check for errors in console

## Verification Checklist

Before moving to Feature 2, verify:

- [ ] Location selection screen appears first
- [ ] Can search and filter locations
- [ ] Can select a location
- [ ] Location badge shows on gym screen
- [ ] Gyms are filtered by location
- [ ] Can go back and change location
- [ ] Location persists after app restart
- [ ] Animations are smooth
- [ ] Haptic feedback works (on mobile)
- [ ] No errors in console
- [ ] Can continue to login/register

## API Testing (Optional)

Test backend directly:

```bash
# List locations
curl http://localhost:8000/gyms/locations

# List gyms in Chicago
curl "http://localhost:8000/gyms?location=Chicago"

# List gyms in Miami
curl "http://localhost:8000/gyms?location=Miami"
```

## Stopping the Servers

When done testing:

1. **Stop Mobile App**: Press `Ctrl+C` in Expo terminal
2. **Stop Backend**: Press `Ctrl+C` in backend terminal

Or keep them running for continued testing.

## Next Feature

After confirming Feature 1 works:
→ **Feature 2: Persistent Login** (already partially implemented)

## Need Help?

Check these files:
- `FEATURE_1_READY.md` - Detailed implementation info
- `LOCATION_FEATURE_TESTING.md` - Complete testing guide
- `mobile/app/(auth)/select-location.tsx` - Location screen code
- `mobile/app/(auth)/select-gym.tsx` - Gym screen code

---

**Ready to test!** Open Expo Go and scan the QR code. 📱
