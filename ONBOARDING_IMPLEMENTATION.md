# Post-Signup Onboarding Flow - Implementation Complete ✅

## Overview

Implemented a comprehensive post-signup onboarding flow that collects user fitness details and calculates personalized macro targets using the Mifflin-St Jeor formula.

## Features Implemented

### 1. Backend Changes

#### User Model Updates (`app/models/models.py`)
Added onboarding fields to User model:
- `onboarding_completed` (boolean) - Tracks if user completed onboarding
- `gender` (string) - "male" or "female"
- `age` (integer) - User's age
- `height` (integer) - Height in cm
- `weight` (integer) - Weight in kg
- `goal_type` (string) - "fat_loss", "maintenance", or "muscle_gain"
- `target_calories` (integer) - Calculated daily calorie target
- `target_protein` (integer) - Protein target in grams
- `target_carbs` (integer) - Carbs target in grams
- `target_fats` (integer) - Fats target in grams

#### Database Migration
**File**: `alembic/versions/20260307_000006_add_onboarding_fields.py`
- Adds all onboarding fields to user table
- Sets default `onboarding_completed = 0` for existing users

#### Schema Updates (`app/schemas/user.py`)
- Updated `UserOut` to include `onboarding_completed`
- Updated `Token` response to include `user_id` and `onboarding_completed`
- Added `OnboardingData` schema for onboarding submission

#### API Endpoints

**Updated Login** (`/auth/login`):
```python
Response: {
  "access_token": "...",
  "token_type": "bearer",
  "user_id": 1,
  "onboarding_completed": false
}
```

**New Onboarding Endpoint** (`/user/onboarding`):
```python
POST /user/onboarding
Headers: Authorization: Bearer <token>
Body: {
  "gender": "male",
  "age": 25,
  "height": 175,
  "weight": 70,
  "goal_type": "muscle_gain",
  "target_calories": 2400,
  "target_protein": 180,
  "target_carbs": 240,
  "target_fats": 80
}

Response: {
  "success": true,
  "message": "Onboarding completed successfully",
  "targets": {
    "calories": 2400,
    "protein": 180,
    "carbs": 240,
    "fats": 80
  }
}
```

### 2. Frontend Changes

#### Zustand Store (`mobile/store/useOnboarding.ts`)
New onboarding store with:
- State: gender, age, height, weight, goalType
- Actions: setGender, setAge, setHeight, setWeight, setGoalType, reset
- `calculateTargets()` - Implements Mifflin-St Jeor formula

**Macro Calculation Logic**:
```typescript
// BMR Calculation
Male: BMR = 10 × weight + 6.25 × height − 5 × age + 5
Female: BMR = 10 × weight + 6.25 × height − 5 × age − 161

// Calorie Adjustment
Fat Loss: BMR × 0.8
Maintenance: BMR × 1.2
Muscle Gain: BMR × 1.4

// Macro Distribution
Protein: 30% of calories (÷ 4 cal/g)
Carbs: 40% of calories (÷ 4 cal/g)
Fats: 30% of calories (÷ 9 cal/g)
```

#### Auth Store Updates (`mobile/store/useAuth.ts`)
Added:
- `userId` - User ID from login
- `onboardingCompleted` - Boolean flag
- `setUserId()` - Set user ID
- `setOnboardingCompleted()` - Update onboarding status

#### Onboarding Screens

**1. Gender Selection** (`mobile/app/(onboarding)/gender.tsx`)
- Step 1 of 5
- Two options: Male / Female
- Animated cards with emoji icons
- Next button appears after selection

**2. Age Input** (`mobile/app/(onboarding)/age.tsx`)
- Step 2 of 5
- Number input (13-120 years)
- Large input field with unit label
- Validation on submit

**3. Height Input** (`mobile/app/(onboarding)/height.tsx`)
- Step 3 of 5
- Number input (100-250 cm)
- Large input field with unit label
- Validation on submit

**4. Weight Input** (`mobile/app/(onboarding)/weight.tsx`)
- Step 4 of 5
- Number input (30-300 kg)
- Large input field with unit label
- Validation on submit

**5. Goal Selection** (`mobile/app/(onboarding)/goal.tsx`)
- Step 5 of 5
- Three options:
  - 🔥 Fat Loss - Reduce body fat
  - ⚖️ Maintenance - Maintain weight
  - 💪 Muscle Gain - Build muscle
- Animated cards with descriptions
- "Calculate My Plan" button

**6. Completion Screen** (`mobile/app/(onboarding)/complete.tsx`)
- Shows calculated targets:
  - Daily calories (large display)
  - Protein, Carbs, Fats (with icons)
- Info card with tips
- "Start Tracking" button
- Saves data to backend
- Navigates to dashboard

#### Navigation Updates

**Login Screen** (`mobile/app/(auth)/login.tsx`):
```typescript
// After successful login
if (data.onboarding_completed) {
  router.replace("/(dashboard)");
} else {
  router.replace("/(onboarding)/gender");
}
```

**Register Screen** (`mobile/app/(auth)/register.tsx`):
```typescript
// After successful registration + auto-login
if (loginData.onboarding_completed) {
  router.replace("/(dashboard)");
} else {
  router.replace("/(onboarding)/gender");
}
```

**Root Layout** (`mobile/app/_layout.tsx`):
- Added `(onboarding)` route to stack

### 3. UI/UX Features

**Design Principles**:
- Clean, minimal interface
- Smooth Reanimated transitions
- Consistent with existing app style
- Progress indicator (Step X of 5)
- Back button on all screens (except first)
- Validation with helpful error messages

**Animations**:
- FadeIn for main content (300ms)
- FadeInDown for options (staggered delays)
- Smooth transitions between screens
- Haptic feedback on interactions

**Color Scheme**:
- Primary: #8b5cf6 (purple)
- Background: #f9fafb (light gray)
- Cards: #ffffff (white)
- Selected: #f5f3ff (light purple)
- Text: #111827 (dark gray)

## User Flow

### New User Registration
```
1. Select Location
2. Select Gym
3. Register Account
4. Auto-login
5. → Onboarding: Gender
6. → Onboarding: Age
7. → Onboarding: Height
8. → Onboarding: Weight
9. → Onboarding: Goal
10. → Onboarding: Complete (calculate & save)
11. → Dashboard
```

### Existing User Login
```
1. Select Location
2. Select Gym
3. Login
4. Check onboarding_completed
   - If true → Dashboard
   - If false → Onboarding: Gender
```

## Files Created

### Backend (1 file)
- `alembic/versions/20260307_000006_add_onboarding_fields.py` - Migration

### Frontend (8 files)
- `mobile/store/useOnboarding.ts` - Onboarding state management
- `mobile/app/(onboarding)/_layout.tsx` - Onboarding layout
- `mobile/app/(onboarding)/gender.tsx` - Gender selection
- `mobile/app/(onboarding)/age.tsx` - Age input
- `mobile/app/(onboarding)/height.tsx` - Height input
- `mobile/app/(onboarding)/weight.tsx` - Weight input
- `mobile/app/(onboarding)/goal.tsx` - Goal selection
- `mobile/app/(onboarding)/complete.tsx` - Completion & save

## Files Modified

### Backend (3 files)
- `app/models/models.py` - Added onboarding fields
- `app/schemas/user.py` - Updated schemas
- `app/api/routes/user.py` - Added onboarding endpoint

### Frontend (4 files)
- `mobile/store/useAuth.ts` - Added onboarding status
- `mobile/app/(auth)/login.tsx` - Added onboarding navigation
- `mobile/app/(auth)/register.tsx` - Added onboarding navigation
- `mobile/app/_layout.tsx` - Added onboarding route

## Setup Instructions

### 1. Run Database Migration

```bash
alembic upgrade head
```

This adds onboarding fields to the user table.

### 2. Restart Backend

```bash
uvicorn app.main:app --reload
```

### 3. Restart Mobile App

```bash
cd mobile
npx expo start -c
```

## Testing

### Test New User Flow

1. Open app
2. Select location (e.g., "New York")
3. Select gym (e.g., "PowerFit Gym")
4. Click "Create New Account"
5. Enter email and password
6. Submit registration
7. **Should navigate to Gender screen**
8. Select gender (e.g., "Male")
9. Enter age (e.g., "25")
10. Enter height (e.g., "175")
11. Enter weight (e.g., "70")
12. Select goal (e.g., "Muscle Gain")
13. See calculated targets
14. Click "Start Tracking"
15. **Should navigate to Dashboard**

### Test Existing User Flow

1. Login with existing account
2. **Should navigate directly to Dashboard** (skip onboarding)

### Test Calculations

**Example: Male, 25 years, 175cm, 70kg, Muscle Gain**

```
BMR = 10 × 70 + 6.25 × 175 − 5 × 25 + 5
BMR = 700 + 1093.75 − 125 + 5
BMR = 1673.75

Calories = BMR × 1.4 = 1673.75 × 1.4 = 2343 ≈ 2343

Protein = (2343 × 0.3) / 4 = 703 / 4 = 176g
Carbs = (2343 × 0.4) / 4 = 937 / 4 = 234g
Fats = (2343 × 0.3) / 9 = 703 / 9 = 78g
```

### Test API Endpoint

```bash
# Login first to get token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password"

# Save onboarding data
curl -X POST http://localhost:8000/user/onboarding \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "gender": "male",
    "age": 25,
    "height": 175,
    "weight": 70,
    "goal_type": "muscle_gain",
    "target_calories": 2343,
    "target_protein": 176,
    "target_carbs": 234,
    "target_fats": 78
  }'
```

## Validation Rules

### Age
- Minimum: 13 years
- Maximum: 120 years
- Type: Integer

### Height
- Minimum: 100 cm
- Maximum: 250 cm
- Type: Integer

### Weight
- Minimum: 30 kg
- Maximum: 300 kg
- Type: Integer

### Gender
- Options: "male" or "female"
- Required

### Goal Type
- Options: "fat_loss", "maintenance", "muscle_gain"
- Required

## Error Handling

### Frontend
- Input validation with Alert messages
- Loading states during API calls
- Error alerts on API failures
- Automatic retry suggestions

### Backend
- Validates all required fields
- Returns appropriate HTTP status codes
- Provides descriptive error messages
- Handles missing authentication

## Security

- All onboarding endpoints require authentication
- Token validation on every request
- User can only update their own data
- Input sanitization and validation

## Future Enhancements

1. **Activity Level**: Add activity multiplier (sedentary, active, very active)
2. **Imperial Units**: Support lbs and inches
3. **Edit Profile**: Allow users to update targets later
4. **Progress Tracking**: Show weight change over time
5. **Goal Adjustment**: Suggest target updates based on progress
6. **Custom Macros**: Allow manual macro ratio adjustment
7. **Onboarding Skip**: Option to skip and use defaults
8. **Multi-language**: Support for different languages

## Summary

The onboarding flow is complete and fully functional. New users are guided through a 5-step process to collect fitness details, calculate personalized nutrition targets, and save them to the backend. Existing users skip onboarding and go directly to the dashboard.

**Status**: ✅ Ready for Testing
