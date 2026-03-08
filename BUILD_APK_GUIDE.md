# Build Android APK - Complete Guide

## Prerequisites
- Node.js installed
- Expo CLI installed
- EAS CLI installed
- Expo account (free)

## Method 1: Using EAS Build (Recommended)

### Step 1: Install EAS CLI

```bash
npm install -g eas-cli
```

### Step 2: Login to Expo

```bash
eas login
```

Enter your Expo credentials or create a new account.

### Step 3: Configure EAS Build

Navigate to your mobile directory:

```bash
cd mobile
```

Initialize EAS:

```bash
eas build:configure
```

This creates `eas.json` in your mobile directory.

### Step 4: Update eas.json

Modify `mobile/eas.json`:

```json
{
  "cli": {
    "version": ">= 5.2.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "android": {
        "gradleCommand": ":app:assembleDebug"
      }
    },
    "preview": {
      "distribution": "internal",
      "android": {
        "buildType": "apk"
      }
    },
    "production": {
      "android": {
        "buildType": "apk"
      }
    }
  },
  "submit": {
    "production": {}
  }
}
```

### Step 5: Update app.json

Modify `mobile/app.json`:

```json
{
  "expo": {
    "name": "Gym Diet Tracker",
    "slug": "gym-diet-tracker",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "assetBundlePatterns": [
      "**/*"
    ],
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.yourusername.gymdiettracker"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      },
      "package": "com.yourusername.gymdiettracker",
      "versionCode": 1,
      "permissions": [
        "INTERNET",
        "ACCESS_NETWORK_STATE"
      ]
    },
    "web": {
      "favicon": "./assets/favicon.png",
      "bundler": "metro"
    },
    "plugins": [
      "expo-router",
      "expo-secure-store"
    ],
    "experiments": {
      "typedRoutes": true
    },
    "extra": {
      "router": {
        "origin": false
      },
      "eas": {
        "projectId": "your-project-id"
      }
    }
  }
}
```

### Step 6: Update API Configuration for Production

Create `mobile/config/api.production.ts`:

```typescript
export const API_BASE_URL = 'https://your-app.railway.app';
```

Update `mobile/config/api.ts` to use production URL:

```typescript
import { Platform } from 'react-native';

let Constants: any = null;
if (Platform.OS !== 'web') {
  Constants = require('expo-constants').default;
}

// Production API URL (Railway)
const PRODUCTION_API_URL = 'https://your-app.railway.app';

function getApiUrl(): string {
  // Check if running in production build
  const releaseChannel = Constants?.expoConfig?.extra?.releaseChannel;
  
  if (releaseChannel === 'production' || __DEV__ === false) {
    return PRODUCTION_API_URL;
  }
  
  // Development mode
  if (Platform.OS === 'web') {
    return 'http://localhost:8000';
  }

  if (Constants) {
    const debuggerHost = Constants.expoConfig?.hostUri;
    if (debuggerHost) {
      const host = debuggerHost.split(':')[0];
      return `http://${host}:8000`;
    }
  }

  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:8000';
  }

  return 'http://localhost:8000';
}

export const API_BASE_URL = getApiUrl();

console.log('API Base URL:', API_BASE_URL);
console.log('Environment:', __DEV__ ? 'development' : 'production');
```

### Step 7: Build APK

Build for preview (internal testing):

```bash
eas build --platform android --profile preview
```

Or build for production:

```bash
eas build --platform android --profile production
```

The build process will:
1. Upload your code to EAS servers
2. Build the APK in the cloud
3. Provide a download link when complete

### Step 8: Download APK

Once the build completes:
1. You'll get a download link in the terminal
2. Or visit https://expo.dev/accounts/[your-username]/projects/gym-diet-tracker/builds
3. Download the APK file

### Step 9: Install APK on Android Device

#### Option A: Direct Install
1. Transfer the APK to your Android device
2. Open the APK file
3. Allow installation from unknown sources if prompted
4. Install the app

#### Option B: Share via Link
1. EAS provides a shareable link
2. Open the link on your Android device
3. Download and install

## Method 2: Local Build (Alternative)

### Step 1: Install Android Studio

Download and install Android Studio from https://developer.android.com/studio

### Step 2: Set Up Android SDK

1. Open Android Studio
2. Go to Tools → SDK Manager
3. Install Android SDK Platform 33 (or latest)
4. Install Android SDK Build-Tools
5. Install Android Emulator

### Step 3: Set Environment Variables

Add to your `.bashrc` or `.zshrc`:

```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
```

### Step 4: Generate Android Project

```bash
cd mobile
npx expo prebuild --platform android
```

This creates the `android` directory.

### Step 5: Build APK Locally

```bash
cd android
./gradlew assembleRelease
```

The APK will be at:
```
android/app/build/outputs/apk/release/app-release.apk
```

### Step 6: Sign the APK (For Production)

Generate a keystore:

```bash
keytool -genkeypair -v -storetype PKCS12 -keystore my-release-key.keystore -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000
```

Update `android/app/build.gradle`:

```gradle
android {
    ...
    signingConfigs {
        release {
            storeFile file('my-release-key.keystore')
            storePassword 'your-password'
            keyAlias 'my-key-alias'
            keyPassword 'your-password'
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            ...
        }
    }
}
```

Build signed APK:

```bash
./gradlew assembleRelease
```

## Testing the APK

### 1. Install on Physical Device

```bash
adb install path/to/your-app.apk
```

### 2. Test All Features

- ✅ Login/Register
- ✅ Location and gym selection
- ✅ Onboarding flow
- ✅ Dashboard with macro rings
- ✅ Meal logging (manual and AI)
- ✅ AI chat
- ✅ Monthly progress
- ✅ Gamification (XP, levels, badges, streaks)
- ✅ Profile and logout

### 3. Test Network Connectivity

- ✅ Test with WiFi
- ✅ Test with mobile data
- ✅ Test offline behavior
- ✅ Test API calls to Railway backend

## Troubleshooting

### Build Fails

**Error: "Could not find or load main class org.gradle.wrapper.GradleWrapperMain"**

Solution:
```bash
cd android
./gradlew wrapper
```

**Error: "SDK location not found"**

Solution: Create `android/local.properties`:
```
sdk.dir=/Users/YOUR_USERNAME/Library/Android/sdk
```

### APK Won't Install

**Error: "App not installed"**

Solutions:
1. Uninstall any existing version
2. Enable "Install from unknown sources"
3. Check if APK is corrupted (re-download)
4. Ensure Android version is compatible

### Network Errors in APK

**Error: "Network request failed"**

Solutions:
1. Check API URL is correct (Railway URL)
2. Verify HTTPS is used (not HTTP)
3. Check CORS settings on backend
4. Test API endpoint in browser

### App Crashes on Launch

Solutions:
1. Check logs: `adb logcat`
2. Verify all dependencies are included
3. Check for missing environment variables
4. Test in development mode first

## APK Size Optimization

### 1. Enable ProGuard

In `android/app/build.gradle`:

```gradle
buildTypes {
    release {
        minifyEnabled true
        shrinkResources true
        proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
    }
}
```

### 2. Enable App Bundle

Instead of APK, build AAB for Google Play:

```bash
eas build --platform android --profile production
```

Update `eas.json`:

```json
{
  "build": {
    "production": {
      "android": {
        "buildType": "app-bundle"
      }
    }
  }
}
```

### 3. Remove Unused Resources

In `android/app/build.gradle`:

```gradle
android {
    ...
    buildTypes {
        release {
            shrinkResources true
            minifyEnabled true
        }
    }
}
```

## Distribution Options

### 1. Internal Testing
- Share APK file directly
- Use EAS shareable link
- Install via USB/ADB

### 2. Google Play Store (Beta)
1. Create Google Play Developer account ($25 one-time fee)
2. Build AAB instead of APK
3. Upload to Play Console
4. Set up internal testing track
5. Invite testers

### 3. Third-Party Distribution
- Firebase App Distribution
- TestFlight (iOS)
- HockeyApp
- Diawi

## Build Checklist

Before building production APK:

- [ ] Update API URL to Railway backend
- [ ] Test all features in development
- [ ] Update app version in `app.json`
- [ ] Update app name and package name
- [ ] Add app icon and splash screen
- [ ] Test on multiple Android versions
- [ ] Check permissions in `AndroidManifest.xml`
- [ ] Enable ProGuard for optimization
- [ ] Sign APK with release keystore
- [ ] Test installed APK thoroughly
- [ ] Document known issues

## Next Steps

1. ✅ Build APK using EAS
2. ✅ Download and install on device
3. ✅ Test all features
4. ✅ Share with testers
5. 📱 Collect feedback
6. 🚀 Prepare for Play Store release

Your Android APK is ready! 🎉
