# Deployment Quick Start Guide

This guide will help you deploy your backend to Railway and build an Android APK in under 30 minutes.

## Part 1: Deploy Backend to Railway (10 minutes)

### Step 1: Sign Up for Railway
1. Go to https://railway.app
2. Sign up with GitHub
3. Verify your email

### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect it's a Python app

### Step 3: Add PostgreSQL Database
1. Click "New" in your project
2. Select "Database" → "PostgreSQL"
3. Railway creates the database automatically

### Step 4: Configure Environment Variables
1. Click on your web service
2. Go to "Variables" tab
3. Add these variables:

```
SECRET_KEY=<run: python -c "import secrets; print(secrets.token_urlsafe(32))">
OPENAI_API_KEY=<your-openai-api-key>
ENVIRONMENT=production
```

Note: `DATABASE_URL` is automatically set by Railway

### Step 5: Generate Domain
1. Go to "Settings" → "Networking"
2. Click "Generate Domain"
3. Copy your URL (e.g., `https://your-app.railway.app`)

### Step 6: Wait for Deployment
- Railway will automatically build and deploy
- Check "Deployments" tab for progress
- Look for "Success" status

### Step 7: Test Your Backend
```bash
curl https://your-app.railway.app/docs
```

You should see the FastAPI Swagger documentation.

✅ Backend is now live!

---

## Part 2: Build Android APK (15 minutes)

### Step 1: Install EAS CLI
```bash
npm install -g eas-cli
```

### Step 2: Login to Expo
```bash
eas login
```

Create an account if you don't have one (it's free).

### Step 3: Update API URL
Edit `mobile/config/api.ts` and replace the production URL:

```typescript
const PRODUCTION_API_URL = 'https://your-app.railway.app';
```

### Step 4: Configure EAS Build
```bash
cd mobile
eas build:configure
```

Press Enter to accept defaults.

### Step 5: Update app.json
Edit `mobile/app.json`:

```json
{
  "expo": {
    "name": "Gym Diet Tracker",
    "slug": "gym-diet-tracker",
    "version": "1.0.0",
    "android": {
      "package": "com.yourusername.gymdiettracker",
      "versionCode": 1
    }
  }
}
```

Replace `yourusername` with your actual username.

### Step 6: Build APK
```bash
eas build --platform android --profile preview
```

This will:
- Upload your code to EAS
- Build the APK in the cloud (takes 5-10 minutes)
- Provide a download link

### Step 7: Download APK
- Click the link in the terminal
- Or visit https://expo.dev and go to your project
- Download the APK file

### Step 8: Install on Android
1. Transfer APK to your phone
2. Open the APK file
3. Allow installation from unknown sources
4. Install and test!

✅ APK is ready!

---

## Quick Commands Reference

### Railway
```bash
# Install Railway CLI (optional)
npm i -g @railway/cli

# Login
railway login

# View logs
railway logs

# Run migrations manually
railway run alembic upgrade head
```

### EAS Build
```bash
# Build preview APK
eas build --platform android --profile preview

# Build production APK
eas build --platform android --profile production

# Check build status
eas build:list

# View build logs
eas build:view
```

---

## Testing Checklist

### Backend Testing
- [ ] Visit `/docs` endpoint - should show Swagger UI
- [ ] Test `/gyms` endpoint - should return gyms list
- [ ] Test registration - create a new user
- [ ] Test login - get JWT token
- [ ] Test protected endpoints with token

### APK Testing
- [ ] App installs successfully
- [ ] Location selection works
- [ ] Gym selection works
- [ ] Login/Register works
- [ ] Dashboard loads with data
- [ ] Meal logging works
- [ ] AI chat works
- [ ] Gamification features work
- [ ] Logout works

---

## Troubleshooting

### Railway Issues

**Build fails:**
- Check logs in "Deployments" tab
- Verify `requirements.txt` is correct
- Ensure all environment variables are set

**Database connection fails:**
- Check that PostgreSQL service is running
- Verify `DATABASE_URL` is set
- Check migration logs

**API returns 500 errors:**
- Check logs: `railway logs`
- Verify OpenAI API key is valid
- Check database connection

### EAS Build Issues

**Build fails:**
- Check build logs in terminal
- Verify `app.json` is valid JSON
- Ensure all dependencies are in `package.json`

**APK won't install:**
- Enable "Install from unknown sources"
- Uninstall any existing version
- Try downloading APK again

**App crashes on launch:**
- Check API URL is correct
- Verify backend is accessible
- Test in Expo Go first

---

## Cost Breakdown

### Railway
- **Hobby Plan**: $5/month
  - 500 hours of usage
  - Includes PostgreSQL database
  - Perfect for small apps

### Expo EAS
- **Free Plan**: 
  - 30 builds per month
  - Sufficient for development and testing

### Total Monthly Cost
- **$5/month** for Railway
- **$0** for EAS (free tier)

---

## Next Steps

1. ✅ Deploy backend to Railway
2. ✅ Build Android APK
3. 📱 Test on physical device
4. 🚀 Share with friends/testers
5. 📊 Monitor usage and performance
6. 🎯 Collect feedback and iterate

---

## Support Resources

- **Railway Docs**: https://docs.railway.app
- **EAS Build Docs**: https://docs.expo.dev/build/introduction/
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Expo Docs**: https://docs.expo.dev

---

## Quick Links

- Railway Dashboard: https://railway.app/dashboard
- Expo Dashboard: https://expo.dev
- Your Backend: https://your-app.railway.app
- API Docs: https://your-app.railway.app/docs

---

You're all set! Your app is now deployed and ready to use. 🎉
