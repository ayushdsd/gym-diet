# Gym Diet Tracker - Complete Project Overview

## Project Description
A full-stack mobile application for tracking nutrition, meals, and fitness goals with AI-powered meal logging, gamification features, and multi-gym support.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Authentication**: JWT tokens with OAuth2
- **AI Integration**: OpenAI GPT for meal analysis
- **Deployment**: Railway (https://gym-diet-production.up.railway.app)
- **Testing**: Pytest (162 tests, all passing)

### Frontend (Mobile)
- **Framework**: React Native with Expo SDK 54
- **Router**: Expo Router (file-based routing)
- **Styling**: NativeWind (TailwindCSS for React Native)
- **Animations**: React Native Reanimated 4.1.6
- **State Management**: Zustand
- **Build System**: EAS Build
- **Package Manager**: npm

## Project Structure

```
GYM DIET/
├── app/                          # Backend FastAPI application
│   ├── api/
│   │   ├── routes/              # API endpoints
│   │   │   ├── auth.py          # Authentication (login, register)
│   │   │   ├── gyms.py          # Gym management
│   │   │   ├── meals.py         # Meal logging and tracking
│   │   │   ├── ai.py            # AI chat for meal logging
│   │   │   └── gamification.py  # XP, levels, badges, streaks
│   │   └── deps.py              # Dependencies (auth, DB)
│   ├── core/
│   │   ├── config.py            # Environment configuration
│   │   └── security.py          # Password hashing, JWT
│   ├── db/
│   │   ├── base.py              # Database models import
│   │   └── session.py           # Database session management
│   ├── models/
│   │   └── models.py            # SQLAlchemy models (User, Gym, Meal, etc.)
│   ├── schemas/                 # Pydantic schemas for validation
│   ├── services/                # Business logic
│   │   ├── ai.py                # OpenAI integration
│   │   ├── nutrition.py         # Nutrition calculations
│   │   ├── gamification.py      # Gamification orchestration
│   │   ├── xp_manager.py        # XP calculation and leveling
│   │   ├── achievement_system.py # Badge unlocking logic
│   │   ├── streak_tracker.py    # Daily streak tracking
│   │   ├── level_system.py      # Level progression
│   │   └── timezone_utils.py    # Timezone handling
│   ├── middleware/
│   │   └── tenant.py            # Multi-gym tenant isolation
│   └── main.py                  # FastAPI app initialization
├── alembic/                     # Database migrations
│   └── versions/                # Migration files (12 migrations)
├── tests/                       # Backend tests (162 tests)
├── mobile/                      # React Native mobile app
│   ├── app/                     # Expo Router pages
│   │   ├── (auth)/             # Authentication flow
│   │   │   ├── select-gym.tsx   # Gym selection
│   │   │   ├── select-location.tsx # Location selection
│   │   │   ├── login.tsx        # Login screen
│   │   │   └── register.tsx     # Registration screen
│   │   ├── (onboarding)/       # User onboarding flow
│   │   │   ├── gender.tsx       # Gender selection
│   │   │   ├── age.tsx          # Age input
│   │   │   ├── height.tsx       # Height input
│   │   │   ├── weight.tsx       # Weight input
│   │   │   ├── goal.tsx         # Goal selection
│   │   │   └── complete.tsx     # Nutrition plan display
│   │   ├── (tabs)/             # Main app tabs
│   │   │   ├── index.tsx        # Dashboard (home)
│   │   │   ├── log-meal.tsx     # Manual meal logging
│   │   │   ├── ai-chat.tsx      # AI-powered meal logging
│   │   │   ├── monthly-progress.tsx # Monthly tracking
│   │   │   ├── gamification-profile.tsx # XP, badges, streaks
│   │   │   └── profile.tsx      # User profile & settings
│   │   ├── _layout.tsx          # Root layout with GestureHandlerRootView
│   │   └── index.tsx            # Entry point
│   ├── components/              # Reusable UI components
│   │   ├── BadgeGrid.tsx        # Badge display grid
│   │   ├── XPProgressBar.tsx    # XP progress visualization
│   │   ├── LevelUpModal.tsx     # Level up celebration
│   │   ├── StreakFlame.tsx      # Streak indicator
│   │   ├── MonthlyGoalTracker.tsx # Calendar view
│   │   └── ConfettiAnimation.tsx # Celebration animation
│   ├── store/                   # Zustand state management
│   │   ├── useAuth.ts           # Authentication state
│   │   ├── useMeals.ts          # Meals data
│   │   ├── useGamification.ts   # XP, badges, streaks
│   │   ├── useChat.ts           # AI chat messages
│   │   └── useOnboarding.ts     # Onboarding flow state
│   ├── services/
│   │   └── api.ts               # API client with fetch wrapper
│   ├── config/
│   │   └── api.ts               # API URL configuration
│   ├── utils/
│   │   └── haptics.ts           # Haptic feedback
│   ├── app.json                 # Expo configuration
│   ├── eas.json                 # EAS Build configuration
│   ├── package.json             # Dependencies
│   └── metro.config.js          # Metro bundler config
└── scripts/                     # Utility scripts
    ├── create_test_user.py      # Create test users
    ├── init_railway_gyms.py     # Initialize gyms on Railway
    └── populate_monthly_data.py # Generate test data
```

## Key Features

### 1. Multi-Gym Authentication System
- Users select gym and location before login/register
- Tenant isolation ensures data separation between gyms
- JWT-based authentication with secure token storage
- Persistent authentication (stays logged in)

### 2. User Onboarding
- 5-step onboarding flow: gender, age, height, weight, goal
- Automatic nutrition target calculation based on:
  - BMR (Basal Metabolic Rate)
  - Activity level
  - Goal type (fat loss, maintenance, muscle gain)
- Personalized daily targets: calories, protein, carbs, fats

### 3. Meal Tracking
- **Manual Logging**: Form-based meal entry
- **AI-Powered Logging**: Natural language meal description
  - OpenAI GPT analyzes meal descriptions
  - Extracts macros automatically
  - Conversational interface
- Real-time macro tracking with animated progress rings
- Daily totals calculation
- Meal deletion functionality

### 4. Gamification System
- **XP (Experience Points)**:
  - Earn XP for logging meals
  - Bonus XP for hitting macro targets
  - XP history tracking
- **Levels**: Progressive leveling system (1-100)
- **Badges**: 12 achievement badges
  - First Meal, Week Warrior, Macro Master, etc.
  - Unlock conditions tracked automatically
- **Streaks**: Daily login streak tracking
  - Streak freeze system (3 freezes)
  - Automatic streak maintenance
- **Animations**: Confetti, level-up modals, badge unlocks

### 5. Monthly Progress Tracking
- Calendar view of daily meal logging
- Color-coded status indicators
- Monthly goal completion percentage
- Historical data visualization

### 6. Dashboard
- Modern UI inspired by Apple Fitness/Whoop
- Personalized greeting with user name
- Animated macro rings (protein, carbs, fats, calories)
- Today's meals display
- Gamification stats (level, XP, streaks)
- Monthly progress preview

## Database Schema

### Core Tables
- **users**: User accounts with authentication
- **gyms**: Gym locations
- **meals**: Meal logs with macros
- **chat_messages**: AI chat history
- **xp_logs**: XP transaction history
- **badges**: Badge definitions
- **user_badges**: User badge unlocks
- **streak_history**: Daily streak records

### Key Relationships
- User → Gym (many-to-one)
- User → Meals (one-to-many)
- User → ChatMessages (one-to-many)
- User → XPLogs (one-to-many)
- User → UserBadges (many-to-many through user_badges)

## API Endpoints

### Authentication
- `POST /auth/register` - Create new user account
- `POST /auth/token` - Login and get JWT token

### Gyms
- `GET /gyms` - List all gyms
- `POST /gyms` - Create new gym (admin)

### Meals
- `GET /meals` - Get user's meals
- `POST /meals` - Log a meal
- `DELETE /meals/{meal_id}` - Delete a meal
- `GET /meals/totals/daily` - Get daily macro totals
- `GET /meals/monthly-goals` - Get monthly progress

### AI Chat
- `POST /ai/message` - Send message to AI
- `GET /ai/history` - Get chat history

### Gamification
- `GET /gamification/profile` - Get XP, level, streaks
- `GET /gamification/badges` - Get all badges and user unlocks
- `GET /gamification/xp-history` - Get XP transaction history

### User
- `POST /user/onboarding` - Save onboarding data
- `GET /user/profile` - Get user profile
- `GET /user/targets` - Get nutrition targets

## Environment Configuration

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
JWT_SECRET=your-secret-key
OPENAI_API_KEY=sk-...
```

### Mobile (app.json)
```json
{
  "extra": {
    "apiUrl": "https://gym-diet-production.up.railway.app"
  }
}
```

### Local Testing Override
In `mobile/config/api.ts`, set `FORCE_PRODUCTION_URL = true` to test with Railway backend locally without building APK.

## Deployment

### Backend (Railway)
1. **Services**:
   - PostgreSQL database service
   - Web service (FastAPI app)
2. **Environment Variables** (set in web service):
   - `DATABASE_URL` (from PostgreSQL service)
   - `JWT_SECRET`
   - `OPENAI_API_KEY`
3. **Deployment**: Automatic from git push
4. **URL**: https://gym-diet-production.up.railway.app
5. **Database Initialization**:
   ```bash
   alembic upgrade head
   python scripts/init_railway_gyms.py https://gym-diet-production.up.railway.app
   ```

### Mobile (EAS Build)
1. **Prerequisites**:
   - EAS CLI: `npm install -g eas-cli`
   - Expo account (logged in as `ayushdsd`)
   - EAS Project ID: `05ecd0a0-03fe-4ac5-a933-9b11725730d1`
2. **Build Command**:
   ```bash
   cd mobile
   npx eas-cli build --platform android --profile production
   ```
3. **Build Configuration** (eas.json):
   - Node version: 22.11.0
   - Build type: APK
   - Cache disabled for clean builds
4. **Download**: APK available from EAS build artifacts

## Critical Implementation Details

### 1. API URL Configuration
- **Production**: Set in `app.json` extra.apiUrl (highest priority)
- **Development**: Auto-detects based on platform
  - Web: localhost:8000
  - Android Emulator: 10.0.2.2:8000
  - Physical Device: Uses dev server IP
- **Testing Override**: `FORCE_PRODUCTION_URL` flag in config/api.ts

### 2. Gesture Handler Setup
- **CRITICAL**: App must be wrapped in `GestureHandlerRootView` in `_layout.tsx`
- Required for all gesture-based interactions
- Without it, buttons and gestures won't work in APK

### 3. NativeWind/Metro Config
- Metro config has try-catch fallback for NativeWind
- Handles lightningcss native binary issues on EAS Build
- Gracefully degrades if NativeWind fails to load

### 4. Button Components
- Use `TouchableOpacity` instead of custom `PressableScale`
- More reliable in production builds
- Prevents crashes from gesture handler issues

### 5. ScrollView Usage
- All pages with content that might overflow must use `ScrollView`
- Critical pages: complete onboarding, dashboard, profile, monthly progress
- Simple forms (login, register, onboarding steps) don't need scrolling

### 6. State Management
- Zustand stores cleared on logout
- Prevents data leakage between users
- Auth state persisted in SecureStore

### 7. Timezone Handling
- All dates stored in UTC
- Converted to user timezone for display
- Streak tracking uses user's local day boundaries

## Testing

### Backend Tests
```bash
pytest                    # Run all 162 tests
pytest tests/test_*.py   # Run specific test file
```

### Test Coverage
- Authentication & authorization
- Meal CRUD operations
- AI meal analysis
- Gamification logic (XP, badges, streaks, levels)
- Nutrition calculations
- Timezone utilities
- Multi-gym tenant isolation

## Common Issues & Solutions

### Issue: Buttons not working in APK
**Solution**: Ensure `GestureHandlerRootView` wraps app in `_layout.tsx`

### Issue: App uses localhost instead of Railway URL
**Solution**: Check `app.json` has `extra.apiUrl` set correctly

### Issue: NativeWind styles not applying in APK
**Solution**: Metro config has fallback - styles may not work but app won't crash

### Issue: Page content not scrollable
**Solution**: Wrap content in `ScrollView` with proper styling

### Issue: Railway DATABASE_URL not working
**Solution**: Manually add DATABASE_URL variable to web service (not just PostgreSQL service)

### Issue: EAS Build fails on dependencies
**Solution**: 
- Remove package-lock.json and regenerate
- Ensure all versions match Expo SDK 54
- Check for peer dependency conflicts

## Development Workflow

### Backend Development
1. Start PostgreSQL
2. Run migrations: `alembic upgrade head`
3. Start server: `uvicorn app.main:app --reload`
4. Run tests: `pytest`

### Mobile Development
1. Install dependencies: `npm install`
2. Start dev server: `npm start`
3. Open in browser or Expo Go
4. For Railway testing: Set `FORCE_PRODUCTION_URL = true`

### Building APK
1. Commit all changes to git
2. Run: `npx eas-cli build --platform android --profile production`
3. Wait for build (10-15 minutes)
4. Download APK from provided URL

## Future Agent Instructions

### When Adding New Features
1. **Backend**: Add route → service → test
2. **Mobile**: Add screen → API call → state management
3. **Always**: Update this document with new features

### When Fixing Bugs
1. Check if issue is in APK or development
2. For APK issues: Check gesture handler, ScrollView, API URL config
3. For API issues: Check Railway environment variables
4. Always run tests before committing

### When Modifying UI
1. Ensure ScrollView for pages with dynamic content
2. Use TouchableOpacity for buttons (not PressableScale)
3. Test on actual device, not just browser
4. Check animations work in production build

### Code Style Guidelines
1. Use TypeScript for type safety
2. Follow existing patterns in codebase
3. Add comments for complex logic
4. Keep components small and focused
5. Use Zustand for global state
6. Use React hooks for local state

## Important Files to Never Modify Without Understanding

1. `mobile/app/_layout.tsx` - Root layout with gesture handler
2. `mobile/config/api.ts` - API URL configuration logic
3. `mobile/metro.config.js` - Metro bundler with NativeWind fallback
4. `app/middleware/tenant.py` - Multi-gym isolation
5. `app/core/security.py` - Authentication logic
6. `alembic/versions/*` - Database migrations (never edit, only add new)

## Quick Reference Commands

```bash
# Backend
alembic upgrade head              # Run migrations
uvicorn app.main:app --reload    # Start dev server
pytest                           # Run tests
python scripts/create_test_user.py # Create test user

# Mobile
npm start                        # Start dev server
npm install                      # Install dependencies
npx eas-cli build --platform android --profile production # Build APK
npx tsc --noEmit                # Check TypeScript errors

# Railway
# Set DATABASE_URL in web service variables
# Deploy: automatic on git push
```

## Contact & Resources
- Backend URL: https://gym-diet-production.up.railway.app
- EAS Project: ayushdsd/mobile
- Package: com.ayushdsd.mobile

---

**Last Updated**: March 9, 2026
**Project Status**: Production-ready, APK deployed
**Test Coverage**: 162 tests passing
