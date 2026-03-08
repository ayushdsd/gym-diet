# Build APK - Final Steps

## Prerequisites Check

Before building, verify:
1. ✅ Railway deployment is successful (green status)
2. ✅ You have your Railway app URL
3. ✅ EAS CLI is installed (`npm install -g eas-cli`)
4. ✅ You're logged into Expo (`eas login`)

## Step 1: Get Your Railway URL

1. Go to Railway dashboard
2. Click your web service
3. Click "Settings" tab
4. Find "Domains" section
5. Copy the Railway-provided domain (e.g., `https://gym-diet-production.up.railway.app`)

## Step 2: Initialize Database with Gyms

Run this command with YOUR Railway URL:

```bash
python scripts/init_railway_gyms.py https://your-app.railway.app
```

Replace `https://your-app.railway.app` with your actual Railway URL.

You should see:
```
✅ Created: Gym Alpha (ID: 1)
✅ Created: Gym Beta (ID: 2)
✅ Created: Gym Gamma (ID: 3)
```

## Step 3: Update Mobile App API URL

Edit `mobile/config/api.ts` and replace this line:

```typescript
const PRODUCTION_API_URL = 'REPLACE_WITH_YOUR_RAILWAY_URL';
```

With your actual Railway URL:

```typescript
const PRODUCTION_API_URL = 'https://your-app.railway.app';
```

**IMPORTANT**: Use HTTPS, not HTTP!

## Step 4: Commit Changes

```bash
git add mobile/config/api.ts scripts/init_railway_gyms.py
git commit -m "Update API URL for production build"
git push origin main
```

## Step 5: Build APK with EAS

```bash
cd mobile
eas build --platform android --profile production
```

### What Happens:
1. EAS will ask you to configure the project (if first time)
2. It will upload your code to EAS servers
3. Build will take 10-20 minutes
4. You'll get a download link when done

### If Asked to Configure:

**Android package name**: `com.ayushdhakre.gymdiet` (or your preference)
**Would you like to automatically create an EAS project?**: Yes

## Step 6: Download APK

When build completes:
1. EAS will show a download link
2. Click the link or go to https://expo.dev/accounts/[your-account]/projects/gym-diet/builds
3. Download the APK file
4. Transfer to your Android phone
5. Install and test!

## Troubleshooting

### "eas: command not found"
```bash
npm install -g eas-cli
```

### "Not logged in"
```bash
eas login
```

### "No eas.json found"
The file already exists in `mobile/eas.json`. Make sure you're in the `mobile` directory.

### Build fails with "Invalid API URL"
Make sure you updated `mobile/config/api.ts` with your Railway URL and committed the changes.

## Testing the APK

After installing on your phone:
1. Open the app
2. Select a gym location
3. Register a new account
4. Try logging a meal
5. Check the AI chat
6. Verify gamification features work

## What's Next

After successful APK build:
1. Test all features on physical device
2. Fix any issues
3. Rebuild if needed
4. Distribute to users!

## Quick Command Summary

```bash
# 1. Initialize gyms
python scripts/init_railway_gyms.py https://your-railway-url.railway.app

# 2. Update API URL in mobile/config/api.ts (manual edit)

# 3. Commit changes
git add mobile/config/api.ts
git commit -m "Update production API URL"
git push

# 4. Build APK
cd mobile
eas build --platform android --profile production
```

That's it! The APK will be ready in 10-20 minutes.
