# Location Selection Feature - Testing Guide

## Status: Ready for Testing ✅

The location selection feature (Feature 1) has been implemented and the duplicate code bug has been fixed.

## What Was Fixed

1. **Removed duplicate code** in `mobile/app/(auth)/select-gym.tsx`
   - The file had duplicate return statements and component logic starting at line 204
   - All duplicate code has been removed
   - File now compiles without errors

## Implementation Summary

### Backend Changes ✅
- Added `location` field to Gym model
- Created migration: `alembic/versions/20260307_000005_add_location_to_gym.py`
- Added `/gyms/locations` endpoint to list unique locations
- Added location filtering to `/gyms` endpoint via query parameter
- Updated test gym creation script with locations

### Mobile Changes ✅
- Created `mobile/store/useLocation.ts` - Zustand store for location state with AsyncStorage persistence
- Created `mobile/app/(auth)/select-location.tsx` - Location selection screen with search
- Updated `mobile/app/(auth)/select-gym.tsx` - Gym list filtered by location with back button
- Updated `mobile/app/index.tsx` - Redirects to location selection for unauthenticated users
- Updated `mobile/app/(auth)/_layout.tsx` - Includes location screen in auth stack

## Testing Steps

### 1. Run Database Migration
```bash
alembic upgrade head
```

### 2. Create Test Gyms with Locations
```bash
python scripts/create_test_gyms.py
```

### 3. Start Backend
```bash
uvicorn app.main:app --reload
```

### 4. Test the Flow

#### Expected Flow:
1. **App Start** → Shows loading screen
2. **Location Selection** → User sees list of locations with search
3. **Select Location** → User taps a location and clicks "Continue to Gyms"
4. **Gym List** → Shows only gyms in selected location
5. **Back Button** → User can go back to change location
6. **Select Gym** → User selects gym and continues to login/register

#### What to Test:
- ✅ Location list loads from backend
- ✅ Search bar filters locations
- ✅ Selected location is highlighted
- ✅ "Continue to Gyms" button appears after selection
- ✅ Gym list shows only gyms in selected location
- ✅ Location badge shows selected location on gym screen
- ✅ Back button returns to location selection
- ✅ Empty state shows if no gyms in location
- ✅ Smooth animations throughout

## API Endpoints Used

```
GET /gyms/locations
Response: ["Mumbai", "Delhi", "Bangalore"]

GET /gyms?location=Mumbai
Response: [
  {
    "id": 1,
    "name": "PowerHouse Gym",
    "location": "Mumbai"
  }
]
```

## Troubleshooting

### "This screen doesn't exist" Error
- **Cause**: Navigation attempted before router was ready
- **Fix**: Already implemented - added delay and hasNavigated flag in index.tsx

### "No location selected" Loop
- **Cause**: Location not persisted or cleared
- **Fix**: Location is now persisted in AsyncStorage via Zustand

### Backend Connection Issues
- Check backend is running on `http://localhost:8000`
- Check CORS is configured (already done in app/main.py)
- For Expo Go, ensure you're using the correct network IP

## Next Features

After testing this feature, we'll implement in order:
1. ✅ Location selection flow (CURRENT - READY FOR TESTING)
2. ⏳ Persistent login (using Expo SecureStore)
3. ⏳ Meal history + delete functionality
4. ⏳ Real-time dashboard updates
5. ⏳ Onboarding macro calculator
6. ⏳ Monthly goal tracker
7. ⏳ AI chat history
8. ⏳ Day-wise meal history

## Files Modified

### Backend
- `app/models/models.py` - Added location field to Gym model
- `app/api/routes/gyms.py` - Added locations endpoint and filtering
- `app/schemas/gym.py` - Updated schemas with location
- `alembic/versions/20260307_000005_add_location_to_gym.py` - Migration file
- `scripts/create_test_gyms.py` - Updated with locations

### Mobile
- `mobile/store/useLocation.ts` - NEW: Location state management
- `mobile/app/(auth)/select-location.tsx` - NEW: Location selection screen
- `mobile/app/(auth)/select-gym.tsx` - UPDATED: Added location filtering and back button
- `mobile/app/index.tsx` - UPDATED: Redirects to location selection
- `mobile/app/(auth)/_layout.tsx` - UPDATED: Added location screen to stack
