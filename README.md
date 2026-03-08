# Gym Diet Tracker

A full-stack mobile application for tracking nutrition, meals, and fitness goals with AI-powered features and gamification.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![React Native](https://img.shields.io/badge/react--native-0.74-blue.svg)
![Tests](https://img.shields.io/badge/tests-162%20passing-brightgreen.svg)

## 🌟 Features

### Backend (FastAPI + PostgreSQL)
- 🔐 **JWT Authentication** - Secure user authentication
- 🏋️ **Multi-gym Support** - Multiple gym locations
- 🍽️ **Meal Logging** - Manual and AI-powered meal tracking
- 🤖 **AI Chat Assistant** - OpenAI-powered nutrition advice
- 🎮 **Gamification System** - XP, levels, badges, and streaks
- 📊 **Progress Tracking** - Daily and monthly nutrition tracking
- 🎯 **Personalized Targets** - Custom macro and calorie goals
- ✅ **162 Passing Tests** - Comprehensive test coverage

### Mobile App (React Native + Expo)
- 📱 **Modern UI** - Smooth animations and intuitive design
- 🎨 **Tab Navigation** - Easy access to all features
- 📝 **Onboarding Flow** - Personalized setup experience
- 📊 **Dashboard** - Visual macro tracking with animated rings
- 🤖 **AI Meal Logging** - Chat with AI to log meals
- 💬 **Chat History** - Persistent conversation history
- 🏆 **Gamification** - Earn XP, level up, unlock badges
- 👤 **Profile Management** - View stats and manage account

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (or use Railway for deployment)
- OpenAI API key

### Backend Setup

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/gym-diet-tracker.git
cd gym-diet-tracker

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

Backend available at: http://localhost:8000
API Docs: http://localhost:8000/docs

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

## 📦 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **OpenAI API** - AI chat functionality
- **JWT** - Authentication
- **Pytest** - Testing

### Mobile
- **React Native** - Cross-platform mobile framework
- **Expo** - Development platform
- **TypeScript** - Type safety
- **Zustand** - State management
- **React Native Reanimated** - Animations
- **NativeWind** - Tailwind CSS for React Native
- **Expo Router** - File-based routing

## 🎯 Key Features Explained

### Gamification System
- **XP System**: Earn XP for logging meals and hitting goals
- **Levels**: Progress through levels with increasing XP requirements
- **Streaks**: Maintain daily activity streaks with freeze protection
- **Badges**: Unlock achievements for milestones
- **Animations**: Smooth level-up and badge unlock animations

### AI-Powered Meal Logging
- Natural language meal input
- Automatic macro calculation
- Conversation history
- Nutrition advice and tips

### Progress Tracking
- Daily macro totals with visual rings
- Monthly goal completion calendar
- Weekly averages
- Personalized nutrition targets

## 📱 Screenshots

(Add screenshots of your app here)

## 🚀 Deployment

### Deploy Backend to Railway

```bash
# See detailed guide
cat DEPLOY_TO_RAILWAY.md
```

Quick steps:
1. Push code to GitHub
2. Connect Railway to your repository
3. Add PostgreSQL database
4. Set environment variables
5. Deploy automatically

### Build Android APK

```bash
# See detailed guide
cat BUILD_APK_GUIDE.md
```

Quick steps:
1. Install EAS CLI: `npm install -g eas-cli`
2. Login: `eas login`
3. Build: `eas build --platform android --profile preview`
4. Download and install APK

### Complete Deployment Guide

See [DEPLOYMENT_QUICK_START.md](DEPLOYMENT_QUICK_START.md) for a 30-minute deployment guide.

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

### Mobile Tests

```bash
cd mobile
npm test
```

## 📚 Documentation

- [Complete Deployment Guide](COMPLETE_DEPLOYMENT_GUIDE.md)
- [Railway Deployment](DEPLOY_TO_RAILWAY.md)
- [APK Build Guide](BUILD_APK_GUIDE.md)
- [Quick Start](DEPLOYMENT_QUICK_START.md)
- [GitHub Upload Guide](GITHUB_UPLOAD_GUIDE.md)

## 🔧 Configuration

### Environment Variables

Create `.env` file in root directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/gym_diet

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Environment
ENVIRONMENT=development
```

### Mobile Configuration

Edit `mobile/config/api.ts` to set your backend URL:

```typescript
const PRODUCTION_API_URL = 'https://your-app.railway.app';
```

## 💰 Cost Breakdown

### Development (Free)
- Local development: $0
- Expo Go testing: $0
- GitHub: $0

### Production
- **Railway Hobby**: $5/month (backend + database)
- **EAS Build Free**: 30 builds/month
- **OpenAI API**: Pay-as-you-go (~$0.002/message)

**Total**: ~$5-10/month

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)

## 🙏 Acknowledgments

- OpenAI for AI chat functionality
- Expo team for amazing mobile development tools
- FastAPI for the excellent backend framework
- Railway for easy deployment

## 📞 Support

For support, email your-email@example.com or open an issue on GitHub.

## 🗺️ Roadmap

- [ ] iOS app build
- [ ] Push notifications
- [ ] Social features (friends, challenges)
- [ ] Barcode scanning for food items
- [ ] Recipe suggestions
- [ ] Workout tracking integration
- [ ] Premium features

---

Made with ❤️ by Your Name
