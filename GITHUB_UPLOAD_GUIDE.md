# Upload Project to GitHub - Step by Step Guide

## Prerequisites
- Git installed on your computer
- GitHub account (create one at https://github.com if you don't have one)

---

## Step 1: Create .gitignore File

First, let's make sure we don't upload sensitive or unnecessary files.

Create `.gitignore` in your root directory (if it doesn't exist):

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Database
*.db
*.sqlite
*.sqlite3
gym_diet.db

# Environment variables
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Node modules (mobile app)
mobile/node_modules/
mobile/.expo/
mobile/.expo-shared/
mobile/dist/
mobile/web-build/

# Mobile build artifacts
mobile/android/
mobile/ios/
mobile/.expo/

# Benchmarks
.benchmarks/
```

---

## Step 2: Initialize Git Repository

Open your terminal in the project root directory:

```bash
# Initialize git repository
git init

# Check git status
git status
```

---

## Step 3: Create GitHub Repository

1. Go to https://github.com
2. Click the "+" icon in the top right
3. Select "New repository"
4. Fill in the details:
   - **Repository name**: `gym-diet-tracker` (or your preferred name)
   - **Description**: "Full-stack gym diet tracking app with AI-powered meal logging and gamification"
   - **Visibility**: Choose "Public" or "Private"
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click "Create repository"

---

## Step 4: Add Files to Git

```bash
# Add all files to staging
git add .

# Check what will be committed
git status

# Commit the files
git commit -m "Initial commit: Full-stack gym diet tracker with gamification"
```

---

## Step 5: Connect to GitHub

Copy the commands from your GitHub repository page (they look like this):

```bash
# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/gym-diet-tracker.git

# Verify remote was added
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

---

## Step 6: Verify Upload

1. Go to your GitHub repository page
2. Refresh the page
3. You should see all your files uploaded

---

## Step 7: Create README.md (Optional but Recommended)

Create a nice README for your repository:

```bash
# Create README.md in root directory
```

```markdown
# Gym Diet Tracker

A full-stack mobile application for tracking nutrition, meals, and fitness goals with AI-powered features and gamification.

## Features

### Backend (FastAPI + PostgreSQL)
- 🔐 JWT Authentication
- 🏋️ Multi-gym support
- 🍽️ Meal logging (manual + AI-powered)
- 🤖 AI chat assistant with OpenAI
- 🎮 Gamification system (XP, levels, badges, streaks)
- 📊 Monthly progress tracking
- 🎯 Personalized nutrition targets
- ✅ 162 passing tests

### Mobile App (React Native + Expo)
- 📱 Modern UI with smooth animations
- 🎨 Bottom tab navigation
- 📝 Onboarding flow
- 📊 Dashboard with macro rings
- 🤖 AI-powered meal logging
- 💬 Chat history
- 🏆 Gamification features
- 👤 Profile management

## Tech Stack

### Backend
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- OpenAI API
- JWT Authentication

### Mobile
- React Native
- Expo Router
- TypeScript
- Zustand (State Management)
- React Native Reanimated
- NativeWind (Styling)

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (or use Railway)
- OpenAI API key

### Backend Setup

1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/gym-diet-tracker.git
cd gym-diet-tracker
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your values
```

5. Run migrations
```bash
alembic upgrade head
```

6. Start the server
```bash
uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

### Mobile Setup

1. Navigate to mobile directory
```bash
cd mobile
```

2. Install dependencies
```bash
npm install
```

3. Start Expo
```bash
npx expo start
```

4. Scan QR code with Expo Go app (iOS/Android)

## Deployment

### Deploy Backend to Railway
See [DEPLOY_TO_RAILWAY.md](DEPLOY_TO_RAILWAY.md)

### Build Android APK
See [BUILD_APK_GUIDE.md](BUILD_APK_GUIDE.md)

### Quick Deployment
See [DEPLOYMENT_QUICK_START.md](DEPLOYMENT_QUICK_START.md)

## Testing

### Backend Tests
```bash
pytest tests/ -v
```

All 162 tests should pass.

### Mobile Tests
```bash
cd mobile
npm test
```

## Documentation

- [Complete Deployment Guide](COMPLETE_DEPLOYMENT_GUIDE.md)
- [Railway Deployment](DEPLOY_TO_RAILWAY.md)
- [APK Build Guide](BUILD_APK_GUIDE.md)
- [Deployment Quick Start](DEPLOYMENT_QUICK_START.md)

## License

MIT License

## Author

Your Name

## Acknowledgments

- OpenAI for AI chat functionality
- Expo team for amazing mobile development tools
- FastAPI for the excellent backend framework
```

Commit and push the README:

```bash
git add README.md
git commit -m "Add README documentation"
git push
```

---

## Step 8: Verify Everything is Uploaded

Check your GitHub repository to ensure these files are present:

### Backend Files
- ✅ `app/` directory
- ✅ `alembic/` directory
- ✅ `tests/` directory
- ✅ `requirements.txt`
- ✅ `alembic.ini`
- ✅ `Procfile`
- ✅ `railway.json`

### Mobile Files
- ✅ `mobile/` directory
- ✅ `mobile/app/` directory
- ✅ `mobile/components/` directory
- ✅ `mobile/package.json`
- ✅ `mobile/eas.json`

### Documentation
- ✅ All `.md` files
- ✅ `README.md`

### NOT Uploaded (Should be in .gitignore)
- ❌ `__pycache__/`
- ❌ `node_modules/`
- ❌ `.env`
- ❌ `*.db` files
- ❌ `.expo/`

---

## Common Issues & Solutions

### Issue: "fatal: not a git repository"
**Solution**: Run `git init` first

### Issue: "remote origin already exists"
**Solution**: 
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/gym-diet-tracker.git
```

### Issue: "Permission denied (publickey)"
**Solution**: Use HTTPS instead of SSH, or set up SSH keys:
```bash
# Use HTTPS URL
git remote set-url origin https://github.com/YOUR_USERNAME/gym-diet-tracker.git
```

### Issue: Files not uploading
**Solution**: Check .gitignore isn't blocking them
```bash
git check-ignore -v filename
```

### Issue: "Updates were rejected"
**Solution**: Pull first, then push
```bash
git pull origin main --rebase
git push origin main
```

---

## Step 9: Now Deploy to Railway

Once your code is on GitHub, you can deploy to Railway:

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize GitHub
5. Select your `gym-diet-tracker` repository
6. Railway will automatically detect and deploy!

See [DEPLOY_TO_RAILWAY.md](DEPLOY_TO_RAILWAY.md) for detailed Railway deployment steps.

---

## Quick Commands Reference

```bash
# Check status
git status

# Add files
git add .
git add filename

# Commit changes
git commit -m "Your commit message"

# Push to GitHub
git push

# Pull latest changes
git pull

# View commit history
git log

# Create new branch
git checkout -b feature-name

# Switch branches
git checkout main

# View remotes
git remote -v
```

---

## Best Practices

### Commit Messages
Use clear, descriptive commit messages:
- ✅ "Add user authentication with JWT"
- ✅ "Fix logout button navigation issue"
- ✅ "Update dashboard UI with macro rings"
- ❌ "Update"
- ❌ "Fix bug"
- ❌ "Changes"

### Commit Frequency
- Commit after completing a feature
- Commit before making major changes
- Commit at the end of each work session

### Branch Strategy
- `main` - Production-ready code
- `develop` - Development branch
- `feature/feature-name` - New features
- `fix/bug-name` - Bug fixes

---

## Next Steps

1. ✅ Upload code to GitHub
2. ✅ Verify all files are uploaded
3. ✅ Add README.md
4. 🚀 Deploy to Railway
5. 📱 Build APK with EAS

Your code is now safely backed up on GitHub and ready for deployment! 🎉

**Next**: Open [DEPLOY_TO_RAILWAY.md](DEPLOY_TO_RAILWAY.md) to deploy your backend.
