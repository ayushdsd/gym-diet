# Complete Deployment Guide - Backend + APK

This is your complete guide to deploy the Gym Diet Tracker app to production.

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Deploy Backend to Railway](#deploy-backend-to-railway)
3. [Build Android APK](#build-android-apk)
4. [Testing](#testing)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
- ✅ Railway account (https://railway.app) - Free to start
- ✅ Expo account (https://expo.dev) - Free
- ✅ OpenAI account (https://platform.openai.com) - For AI chat feature

### Required Software
- ✅ Node.js (v18 or higher)
- ✅ Python (v3.10 or higher)
- ✅ Git

### Install Required Tools
```bash
# Install EAS CLI
npm install -g eas-cli

# Install Railway CLI (optional but recommended)
npm install -g @railway/cli
```

---

## Deploy Backend to Railway

### Step 1: Prepare Your Repository

Ensure these files exist in your root directory:
- ✅ `Procfile` (created)
- ✅ `railway.json` (created)
- ✅ `requirements.txt` (exists)
- ✅ `alembic.ini` (exists)

### Step 2: Create Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize GitHub and select your repository
5. Railway will auto-detect it's a Python app

### Step 3: Add PostgreSQL Database

1. In your Railway project, click "+ New"
2. Select "Database"
3. Choose "PostgreSQL"
4. Railway creates and connects it automatically

### Step 4: Configure Environment Variables

Click on your web service → "Variables" tab → Add these:

```env
SECRET_KEY=<generate-secure-key>
OPENAI_API_KEY=<your-openai-api-key>
ENVIRONMENT=production
```

To generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 5: Generate Public Domain

1. Click on your web service
2. Go to "Settings" → "Networking"
3. Click "Generate Domain"
4. Copy your URL (e.g., `https://gym-diet-tracker-production.up.railway.app`)

### Step 6: Deploy

Railway automatically deploys when you push to GitHub. To manually trigger:
1. Go to "Deployments" tab
2. Click "Deploy"

Watch the logs for:
```
✅ Running migrations: alembic upgrade head
✅ Starting server: uvicorn app.main:app
✅ Application startup complete
```

### Step 7: Initialize Database

Run the initialization script:

```bash
python scripts/init_railway_db.py --url https://your-app.railway.app
```

This creates:
- 5 gyms in different locations
- 1 test user (test@example.com / testpass123)

### Step 8: Verify Backend

Test your API:

```bash
# Test docs
curl https://your-app.railway.app/docs

# Test gyms endpoint
curl https://your-app.railway.app/gyms

# Should return JSON array of gyms
```

✅ **Backend is now live on Railway!**

---

## Build Android APK

### Step 1: Update API Configuration

Edit `mobile/config/api.ts`:

```typescript
// Replace with your Railway URL
const PRODUCTION_API_URL = 'https://your-app.railway.app';

function getApiUrl(): string {
  // Use production URL when not in development
  if (!__DEV__) {
    return PRODUCTION_API_URL;
  }
  
  // Development mode logic...
  // ... rest of the code
}
```

### Step 2: Update App Configuration

Edit `mobile/app.json`:

```json
{
  "expo": {
    "name": "Gym Diet Tracker",
    "slug": "gym-diet-tracker",
    "version": "1.0.0",
    "android": {
      "package": "com.yourusername.gymdiettracker",
      "versionCode": 1,
      "permissions": [
        "INTERNET",
        "ACCESS_NETWORK_STATE"
      ]
    }
  }
}
```

Replace `yourusername` with your actual username (lowercase, no spaces).

### Step 3: Login to Expo

```bash
cd mobile
eas login
```

Create an account if you don't have one.

### Step 4: Configure EAS Build

```bash
eas build:configure
```

This creates `eas.json` (already created for you).

### Step 5: Build APK

For testing (preview build):
```bash
eas build --platform android --profile preview
```

For production:
```bash
eas build --platform android --profile production
```

The build process:
1. Uploads your code to EAS servers
2. Builds APK in the cloud (5-10 minutes)
3. Provides download link

### Step 6: Download APK

Option A: Click the link in terminal
Option B: Visit https://expo.dev → Your Projects → Builds → Download

### Step 7: Install on Android Device

#### Method 1: Direct Transfer
1. Connect phone to computer via USB
2. Copy APK to phone
3. Open APK file on phone
4. Allow "Install from unknown sources" if prompted
5. Install

#### Method 2: Share Link
1. EAS provides a shareable link
2. Open link on Android device
3. Download and install

### Step 8: Test the App

Open the app and test:
- ✅ Location selection
- ✅ Gym selection
- ✅ Registration
- ✅ Login
- ✅ Onboarding flow
- ✅ Dashboard
- ✅ Meal logging
- ✅ AI chat
- ✅ Gamification features
- ✅ Profile and logout

✅ **APK is ready and working!**

---

## Testing

### Backend Testing

#### 1. API Documentation
Visit: `https://your-app.railway.app/docs`

Should show FastAPI Swagger UI with all endpoints.

#### 2. Test Endpoints

```bash
# Get gyms
curl https://your-app.railway.app/gyms

# Register user
curl -X POST https://your-app.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"pass123","gym_id":1}'

# Login
curl -X POST https://your-app.railway.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"pass123","gym_id":1}'
```

#### 3. Monitor Logs

```bash
# Using Railway CLI
railway logs

# Or view in Railway dashboard
# Go to your project → Deployments → View logs
```

### Mobile App Testing

#### 1. Network Testing
- Test with WiFi
- Test with mobile data
- Test in airplane mode (should show error)

#### 2. Feature Testing
- Create new account
- Complete onboarding
- Log meals manually
- Log meals via AI chat
- Check gamification (XP, levels, badges)
- View monthly progress
- Logout and login again

#### 3. Performance Testing
- Check app startup time
- Test smooth scrolling
- Verify animations work
- Check memory usage

---

## Troubleshooting

### Backend Issues

#### Build Fails on Railway

**Problem**: Build fails with dependency errors

**Solution**:
1. Check `requirements.txt` is complete
2. Verify Python version compatibility
3. Check Railway logs for specific error

```bash
railway logs
```

#### Database Connection Fails

**Problem**: API returns 500 errors about database

**Solution**:
1. Verify PostgreSQL service is running
2. Check `DATABASE_URL` is set
3. Run migrations manually:

```bash
railway run alembic upgrade head
```

#### Migrations Fail

**Problem**: Alembic migration errors

**Solution**:
1. Check migration files are committed
2. Verify database is empty or compatible
3. Check logs for specific error
4. Try running migrations manually

#### CORS Errors

**Problem**: Mobile app can't connect to API

**Solution**:
1. Verify CORS is set to allow all origins in `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. Ensure using HTTPS (not HTTP)
3. Check API URL in mobile app

### APK Build Issues

#### EAS Build Fails

**Problem**: Build fails in EAS

**Solution**:
1. Check build logs in terminal
2. Verify `app.json` is valid JSON
3. Ensure all dependencies are in `package.json`
4. Try building again (sometimes transient errors)

```bash
eas build:list
eas build:view <build-id>
```

#### APK Won't Install

**Problem**: "App not installed" error

**Solution**:
1. Enable "Install from unknown sources" in Android settings
2. Uninstall any existing version of the app
3. Download APK again (might be corrupted)
4. Check Android version compatibility (min SDK 21)

#### App Crashes on Launch

**Problem**: App opens then immediately closes

**Solution**:
1. Check API URL is correct in `config/api.ts`
2. Verify backend is accessible from phone
3. Check Android logs:

```bash
adb logcat | grep -i error
```

4. Test in Expo Go first to isolate issue

#### Network Errors in App

**Problem**: "Network request failed" errors

**Solution**:
1. Verify Railway URL is correct
2. Test API in browser: `https://your-app.railway.app/docs`
3. Check phone has internet connection
4. Verify HTTPS (not HTTP)
5. Test with curl from phone's network

---

## Monitoring & Maintenance

### Railway Dashboard

Monitor your app:
1. **Deployments**: View build and deploy history
2. **Metrics**: CPU, memory, network usage
3. **Logs**: Real-time application logs
4. **Variables**: Manage environment variables

### EAS Dashboard

Monitor builds:
1. **Builds**: View all builds and their status
2. **Submissions**: Track app store submissions
3. **Updates**: Manage OTA updates

### Database Backups

Railway automatically backs up PostgreSQL:
- Daily backups retained for 7 days
- Manual backups available in dashboard

### Cost Monitoring

Railway usage:
- Check "Usage" tab in dashboard
- Set up billing alerts
- Monitor resource consumption

---

## Scaling & Optimization

### Backend Optimization

1. **Add Caching**: Use Redis for frequently accessed data
2. **Database Indexing**: Already optimized with indexes
3. **Connection Pooling**: Configure in SQLAlchemy
4. **Rate Limiting**: Add middleware to prevent abuse

### APK Optimization

1. **Enable ProGuard**: Minify and obfuscate code
2. **Use App Bundle**: Smaller download size
3. **Optimize Images**: Compress assets
4. **Remove Unused Code**: Tree-shaking

---

## Next Steps

### Immediate
- ✅ Deploy backend to Railway
- ✅ Build and test APK
- ✅ Share with beta testers

### Short Term
- 📱 Collect user feedback
- 🐛 Fix bugs and issues
- 📊 Monitor usage and performance
- 🎨 Refine UI/UX

### Long Term
- 🚀 Publish to Google Play Store
- 🍎 Build iOS version
- 📈 Add analytics
- 🔔 Add push notifications
- 💳 Add premium features

---

## Support & Resources

### Documentation
- **Railway**: https://docs.railway.app
- **EAS Build**: https://docs.expo.dev/build/introduction/
- **FastAPI**: https://fastapi.tiangolo.com
- **Expo**: https://docs.expo.dev

### Community
- **Railway Discord**: https://discord.gg/railway
- **Expo Discord**: https://chat.expo.dev
- **Stack Overflow**: Tag questions with `railway`, `expo`, `fastapi`

### Useful Commands

```bash
# Railway
railway login
railway logs
railway run <command>

# EAS
eas login
eas build:list
eas build --platform android --profile preview

# Backend
python scripts/init_railway_db.py --url <url>
alembic upgrade head
uvicorn app.main:app --reload

# Mobile
cd mobile
npm start
npx expo start
```

---

## Checklist

### Pre-Deployment
- [ ] All features tested locally
- [ ] Backend tests passing (162/162)
- [ ] Environment variables documented
- [ ] API endpoints documented
- [ ] Mobile app tested on device

### Railway Deployment
- [ ] Railway account created
- [ ] Repository connected
- [ ] PostgreSQL database added
- [ ] Environment variables set
- [ ] Domain generated
- [ ] Deployment successful
- [ ] Database initialized
- [ ] API endpoints tested

### APK Build
- [ ] Expo account created
- [ ] EAS CLI installed
- [ ] API URL updated
- [ ] app.json configured
- [ ] Build successful
- [ ] APK downloaded
- [ ] App installed on device
- [ ] All features tested

### Post-Deployment
- [ ] Backend monitoring set up
- [ ] Error tracking configured
- [ ] Backup strategy in place
- [ ] Documentation updated
- [ ] Team members notified

---

## Congratulations! 🎉

Your Gym Diet Tracker app is now:
- ✅ Deployed to production on Railway
- ✅ Available as Android APK
- ✅ Ready for users

**Your URLs:**
- Backend: `https://your-app.railway.app`
- API Docs: `https://your-app.railway.app/docs`
- APK Download: Check your EAS dashboard

**Test Credentials:**
- Email: `test@example.com`
- Password: `testpass123`

Happy deploying! 🚀
