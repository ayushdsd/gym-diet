# Onboarding Flow - Quick Start Guide

## What Was Built

A 5-step post-signup onboarding flow that collects user fitness details and calculates personalized macro targets.

## Quick Setup

```bash
# 1. Run migration
alembic upgrade head

# 2. Restart backend
uvicorn app.main:app --reload

# 3. Restart mobile
cd mobile
npx expo start -c
```

## User Flow

### New Users
```
Register → Gender → Age → Height → Weight → Goal → Complete → Dashboard
```

### Existing Users
```
Login → Dashboard (skip onboarding)
```

## Onboarding Steps

1. **Gender**: Male or Female
2. **Age**: 13-120 years
3. **Height**: 100-250 cm
4. **Weight**: 30-300 kg
5. **Goal**: Fat Loss / Maintenance / Muscle Gain

## Macro Calculation

**Formula**: Mifflin-St Jeor

**BMR**:
- Male: `10 × weight + 6.25 × height − 5 × age + 5`
- Female: `10 × weight + 6.25 × height − 5 × age − 161`

**Calories**:
- Fat Loss: `BMR × 0.8`
- Maintenance: `BMR × 1.2`
- Muscle Gain: `BMR × 1.4`

**Macros**:
- Protein: 30% of calories (÷ 4 cal/g)
- Carbs: 40% of calories (÷ 4 cal/g)
- Fats: 30% of calories (÷ 9 cal/g)

## API Endpoints

### Login (Updated)
```
POST /auth/login
Response: {
  "access_token": "...",
  "user_id": 1,
  "onboarding_completed": false
}
```

### Save Onboarding (New)
```
POST /user/onboarding
Headers: Authorization: Bearer <token>
Body: {
  "gender": "male",
  "age": 25,
  "height": 175,
  "weight": 70,
  "goal_type": "muscle_gain",
  "target_calories": 2343,
  "target_protein": 176,
  "target_carbs": 234,
  "target_fats": 78
}
```

## Files Created

**Backend**:
- Migration: `alembic/versions/20260307_000006_add_onboarding_fields.py`

**Frontend**:
- Store: `mobile/store/useOnboarding.ts`
- Screens: `mobile/app/(onboarding)/*.tsx` (6 files)

## Files Modified

**Backend**:
- `app/models/models.py` - Added fields
- `app/schemas/user.py` - Updated schemas
- `app/api/routes/user.py` - Added endpoint

**Frontend**:
- `mobile/store/useAuth.ts` - Added onboarding status
- `mobile/app/(auth)/login.tsx` - Navigation logic
- `mobile/app/(auth)/register.tsx` - Navigation logic
- `mobile/app/_layout.tsx` - Added route

## Quick Test

1. Create new account
2. Complete onboarding (5 steps)
3. See calculated targets
4. Click "Start Tracking"
5. Arrive at dashboard

## Example Calculation

**Input**: Male, 25 years, 175cm, 70kg, Muscle Gain

**Output**:
- Calories: 2343
- Protein: 176g
- Carbs: 234g
- Fats: 78g

## Status

✅ Complete and ready for testing!

See `ONBOARDING_IMPLEMENTATION.md` for full details.
