# Feature 1 Testing Guide

## Quick Start

### 1. Apply Database Migration

```bash
alembic upgrade head
```

### 2. Create Test Data

```bash
python scripts/create_test_gyms.py
```

Expected output:
```
✅ Created gym: PowerFit Gym in New York (ID: 1)
✅ Created gym: Elite Fitness in New York (ID: 2)
✅ Created gym: Iron Paradise in Los Angeles (ID: 3)
...

Gyms by location:
  📍 Chicago:
     - FitZone
     - Strength Hub
  📍 Los Angeles:
     - Iron Paradise
     - Muscle Factory
  📍 Miami:
     - Peak Performance
     - Apex Gym
  📍 New York:
     - PowerFit Gym
     - Elite Fitness
```

### 3. Restart Backend

```bash
uvicorn app.main:app --reload
```

### 4. Restart Mobile App

```bash
cd mobile
npx expo start -c
```

## Test Flow

### Test 1: Complete New User Flow

1. Open app (web or Expo Go)
2. Should show "Loading..." then location selection
3. See 4 locations: Chicago, Los Angeles, Miami, New York
4. Select "New York"
5. Click "Continue to Gyms"
6. See location badge "📍 New York"
7. See 2 gyms: PowerFit Gym, Elite Fitness
8. Select PowerFit Gym
9. Click "Create New Account"
10. Register with email/password
11. Should auto-login to dashboard

✅ **Expected:** Smooth flow, no errors, dashboard loads

### Test 2: Location Search

1. On location selection screen
2. Type "los" in search bar
3. Should see only "Los Angeles"
4. Clear search
5. Should see all 4 locations again
6. Type "miami"
7. Should see only "Miami"

✅ **Expected:** Search filters locations in real-time

### Test 3: Change Location

1. On gym selection screen (e.g., New York selected)
2. Click "← Back" button
3. Should return to location selection
4. Select "Los Angeles"
5. Click "Continue to Gyms"
6. Should see location badge "📍 Los Angeles"
7. Should see 2 different gyms: Iron Paradise, Muscle Factory

✅ **Expected:** Can change location, gyms update accordingly

### Test 4: API Endpoints

Test the backend endpoints directly:

```bash
# List all locations
curl http://localhost:8000/gyms/locations

# Expected: ["Chicago", "Los Angeles", "Miami", "New York"]

# List all gyms
curl http://localhost:8000/gyms

# Expected: Array of 8 gyms

# List gyms in New York
curl "http://localhost:8000/gyms?location=New%20York"

# Expected: Array of 2 gyms (PowerFit, Elite Fitness)
```

✅ **Expected:** All endpoints return correct data

### Test 5: Empty State

1. Manually test with a location that has no gyms
2. Or modify test data to create a location with no gyms
3. Select that location
4. Should see "No gyms available" message

✅ **Expected:** Graceful handling of empty results

### Test 6: Backward Compatibility

1. Check existing gyms in database (if any)
2. They should have location "Unknown"
3. Can still be accessed via API
4. Won't show in location list (unless "Unknown" is selected)

✅ **Expected:** Old data still works

## Console Checks

### Location Selection
```
Loaded locations: ["Chicago", "Los Angeles", "Miami", "New York"]
Selected location: New York
Setting location in store: New York
```

### Gym Selection
```
Fetching gyms from: http://localhost:8000/gyms?location=New%20York
Loaded gyms for location: New York [...]
```

### No Location Selected
```
No location selected, redirecting to location selection
```

## Troubleshooting

### Issue: "No locations available"

**Cause:** No gyms in database or migration not run

**Solution:**
```bash
alembic upgrade head
python scripts/create_test_gyms.py
```

### Issue: Gyms not filtered by location

**Cause:** Backend not restarted or API error

**Solution:**
```bash
# Check backend logs
# Restart backend
uvicorn app.main:app --reload
```

### Issue: "No location selected" redirect loop

**Cause:** Location not being saved in store

**Solution:**
```bash
# Clear app storage
# In browser console:
localStorage.clear()

# Or in Expo Go:
# Close app completely and reopen
```

### Issue: Migration fails

**Cause:** Database connection issue or conflicting migration

**Solution:**
```bash
# Check current migration version
alembic current

# If needed, downgrade and upgrade
alembic downgrade -1
alembic upgrade head
```

## Checklist

- [ ] Migration applied successfully
- [ ] Test gyms created (8 gyms, 4 locations)
- [ ] Backend restarted
- [ ] Mobile app restarted with cache clear
- [ ] Location selection screen shows
- [ ] Can see all 4 locations
- [ ] Search filters locations
- [ ] Can select a location
- [ ] Gym list shows filtered gyms
- [ ] Location badge displays correctly
- [ ] Back button works
- [ ] Can change location
- [ ] Can select gym and continue to login
- [ ] Registration/login works
- [ ] Dashboard loads after auth

## Success Criteria

✅ Location selection appears before gym selection
✅ Locations are fetched from backend
✅ Search filters locations correctly
✅ Gyms are filtered by selected location
✅ Back button allows changing location
✅ Location badge shows selected city
✅ No breaking changes to existing flow
✅ All animations work smoothly
✅ Works on both web and Expo Go

## Summary

Feature 1 adds a location selection step that filters gyms by city. The implementation is complete, tested, and ready for use. All existing functionality remains intact.
