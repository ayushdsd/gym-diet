# AI Diet Tracker 🤖🍽️

An intelligent diet tracking mobile app powered by AI that makes nutrition logging effortless. Simply chat with your AI assistant to log meals, get personalized nutrition advice, and track your progress with gamification features.

## 🎯 What is AI Diet Tracker?

AI Diet Tracker is a conversational nutrition app that uses artificial intelligence to make diet tracking as simple as having a conversation. Instead of manually entering calories and macros, just tell the AI what you ate - "I had chicken breast with rice and broccoli" - and it automatically calculates and logs your nutrition.

The app combines AI-powered meal logging with gamification (XP, levels, badges, streaks) to make healthy eating engaging and sustainable.

## ✨ Key Features

### 🤖 AI-Powered Meal Logging
- **Natural Language Input** - Just describe what you ate in plain English
- **Automatic Macro Calculation** - AI estimates protein, carbs, fats, and calories
- **Conversation History** - All your chats are saved and synced
- **Nutrition Advice** - Ask questions and get personalized diet tips
- **Smart Recognition** - Understands portion sizes, cooking methods, and ingredients

### 📊 Visual Progress Tracking
- **Interactive Dashboard** - See your daily macro progress at a glance
- **Animated Macro Rings** - Beautiful circular progress indicators
- **Hero Card** - Dynamic calorie tracker that changes color based on progress
- **Monthly Calendar** - Track goal completion over time
- **XP History Chart** - Visualize your consistency with graphs

### 🎮 Gamification System
- **XP & Levels** - Earn experience points for logging meals and hitting goals
- **Streak Tracking** - Build daily streaks with freeze protection
- **Badge Achievements** - Unlock badges for milestones (First Meal, 7-Day Streak, etc.)
- **Level-Up Animations** - Celebrate progress with confetti and animations
- **Leaderboard Ready** - Compete with friends (coming soon)

### 🏋️ Gym Integration
- **Multi-Gym Support** - Connect with your gym location
- **Branded Experience** - Gym logos and custom colors throughout the app
- **Location-Based** - Find gyms in your city (Mumbai, Delhi, Thane, etc.)
- **Gym Banners** - Promotional carousels for gym events and offers

## 📱 App Pages & Features

### 1. 🏠 Dashboard (Home)
The main hub showing your daily nutrition progress:
- **Hero Card** - Large calorie tracker with dynamic gradient (blue → green when goal reached)
- **Macro Rings** - Circular progress indicators for Protein, Carbs, Fats, and Calories
- **Today's Meals** - List of all meals logged today with delete option
- **Gamification Stats** - Current streak, level, and XP progress
- **Monthly Preview** - Quick view of this month's goal completion
- **Pull to Refresh** - Update all data with a swipe down

### 2. 🤖 AI Chat
Conversational meal logging and nutrition assistant:
- **Chat Interface** - Natural conversation with AI assistant
- **Quick Actions** - Pre-filled prompts for common tasks
- **Meal Logging** - Say "I ate chicken and rice" to log meals automatically
- **Nutrition Advice** - Ask questions like "Should I eat more protein?"
- **Progress Queries** - Check your weekly/monthly progress via chat
- **Chat History** - All conversations are saved and synced
- **Typing Indicator** - See when AI is thinking
- **Success Animations** - Confetti when meals are logged

### 3. 📝 Log Meal (Manual)
Traditional meal logging with AI assistance:
- **AI-Powered Input** - Describe meal in natural language
- **Macro Breakdown** - See estimated protein, carbs, fats, calories
- **Confirmation Card** - Review before saving
- **Edit Macros** - Adjust AI estimates if needed
- **Quick Log** - Save meals in seconds
- **XP Rewards** - Earn XP for each meal logged

### 4. 🏆 Gamification Profile
Comprehensive view of your achievements:
- **Level Badge** - Large animated badge showing current level
- **XP Progress Bar** - Visual progress to next level
- **Streak Stats** - Current streak and highest streak
- **Streak Freezes** - Available freeze count for missed days
- **Badge Grid** - All unlocked and locked achievements
- **XP History Chart** - 30-day graph of XP earned
- **Pull to Refresh** - Update all gamification data

### 5. 📅 Monthly Progress
Calendar view of your nutrition journey:
- **Goal Calendar** - Visual grid showing daily goal completion
- **Color Coding** - Green (goal met), yellow (partial), gray (missed)
- **Monthly Stats** - Total days, completion rate, current streak
- **Weekly Averages** - See which days you perform best
- **Month Navigation** - Swipe between months
- **Detailed View** - Tap any day to see full breakdown

### 6. 🏋️ Gym
Gym information and promotions:
- **Gym Banner Carousel** - Swipeable promotional banners
- **Gym Details** - Name, location, description
- **Branded Colors** - UI adapts to gym's primary color
- **Contact Info** - Quick access to gym details
- **Location Map** - Find your gym (coming soon)

### 7. 👤 Profile
Account management and settings:
- **User Info** - Email, name, gym membership
- **Macro Targets** - View and edit daily goals
- **Onboarding Data** - Age, gender, height, weight, fitness goal
- **Account Actions** - Logout, delete account
- **App Version** - Current version info
- **Support Links** - Help and feedback

### 8. 🎯 Onboarding Flow
Personalized setup for new users:
- **Welcome Screen** - Introduction to the app
- **Gender Selection** - Male, Female, Other
- **Age Input** - Enter your age
- **Height Input** - Metric or imperial units
- **Weight Input** - Current weight
- **Goal Selection** - Lose weight, maintain, gain muscle
- **Completion** - Automatic macro target calculation

### 9. 🔐 Authentication
Secure login and registration:
- **Login** - Email and password
- **Register** - Create new account
- **Location Selection** - Choose your city
- **Gym Selection** - Pick your gym from the list
- **JWT Tokens** - Secure authentication
- **Auto-Login** - Stay logged in

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (or use Railway for deployment)
- OpenAI API key

### Backend Setup

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/ai-diet-tracker.git
cd ai-diet-tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your values

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Mobile Setup

```bash
# Navigate to mobile directory
cd mobile

# Install dependencies
npm install

# Start Expo
npx expo start

# Scan QR code with Expo Go app
```


## 🎯 How It Works

### AI Meal Logging Flow
1. User types: "I ate 200g chicken breast with 150g rice and broccoli"
2. Message sent to OpenAI GPT-4 with nutrition context
3. AI extracts meal components and estimates macros
4. Backend saves meal to database
5. User earns XP for logging
6. Dashboard updates with new totals
7. Confetti animation if goal reached

### Gamification System
- **XP Calculation**: Base XP (10) + Bonus for hitting goals
- **Level Formula**: XP required = 100 × level
- **Streak Rules**: Log at least 1 meal per day to maintain streak
- **Freeze System**: Use freezes to protect streak on missed days
- **Badge Triggers**: Automatic unlock when conditions are met

### Data Flow
```
Mobile App → API Request → FastAPI Backend → PostgreSQL Database
                ↓
         OpenAI API (for AI features)
                ↓
         Response → Update UI → Animations
```

## 🎨 Design Philosophy

- **Conversation First** - Make nutrition tracking feel like chatting with a friend
- **Visual Feedback** - Animations and colors provide instant feedback
- **Gamification** - Make healthy habits fun and rewarding
- **Minimal Friction** - Log meals in seconds, not minutes
- **Beautiful UI** - Modern design with smooth animations
- **Data Transparency** - Always show what the AI calculated

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_gamification_routes.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

All 162 tests should pass ✅

Test coverage includes:
- Authentication & JWT tokens
- Meal logging and CRUD operations
- AI chat integration
- Gamification (XP, levels, streaks, badges)
- Multi-gym support
- Progress tracking
- Timezone handling

### Mobile Tests

```bash
cd mobile
npm test
```




## 🎯 Use Cases

### For Gym Members
- Track nutrition alongside workouts
- Get AI-powered meal suggestions
- Compete with gym friends (coming soon)
- See gym promotions and events

### For Fitness Enthusiasts
- Effortless meal logging via chat
- Visual progress tracking
- Gamified habit building
- Personalized macro targets

### For Gyms
- Branded member experience
- Nutrition tracking for clients
- Engagement through gamification
- Promotional banner space


## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.



If you find this project useful, please consider giving it a star ⭐
