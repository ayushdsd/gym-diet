# Deploy Backend to Railway - Complete Guide

## Prerequisites
- Railway account (sign up at https://railway.app)
- GitHub account (to connect your repository)
- OpenAI API key (for AI chat feature)

## Step 1: Prepare Backend for Production

### 1.1 Create Railway Configuration Files

Create `railway.json` in the root directory:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 1.2 Create Procfile (Alternative)

Create `Procfile` in the root directory:

```
web: alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 1.3 Update requirements.txt

Ensure your `requirements.txt` includes all dependencies:

```txt
fastapi==0.115.5
uvicorn[standard]==0.32.1
sqlalchemy==2.0.36
alembic==1.14.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.20
openai==1.57.2
python-dotenv==1.0.1
pydantic==2.10.3
pydantic-settings==2.6.1
```

### 1.4 Update app/core/config.py for Production

Modify `app/core/config.py` to handle Railway's environment:

```python
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./gym_diet.db")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:8081",
        "http://localhost:19006",
        "exp://192.168.*.*:8081",
        "*"  # Allow all for mobile app
    ]
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 1.5 Update CORS Configuration

Modify `app/main.py` to allow mobile app connections:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for mobile app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Step 2: Deploy to Railway

### 2.1 Create New Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account
5. Select your repository

### 2.2 Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create a PostgreSQL instance
4. Copy the `DATABASE_URL` from the database service

### 2.3 Configure Environment Variables

In your Railway project settings, add these environment variables:

```
DATABASE_URL=<automatically set by Railway PostgreSQL>
SECRET_KEY=<generate a secure random string>
OPENAI_API_KEY=<your OpenAI API key>
ENVIRONMENT=production
PORT=8000
```

To generate a secure SECRET_KEY, run:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.4 Deploy

1. Railway will automatically detect your Python app
2. It will install dependencies from `requirements.txt`
3. Run migrations with `alembic upgrade head`
4. Start the server with `uvicorn`

### 2.5 Get Your Backend URL

1. Go to your Railway project
2. Click on your service
3. Go to "Settings" → "Networking"
4. Click "Generate Domain"
5. Copy your domain (e.g., `your-app.railway.app`)

## Step 3: Initialize Database

### 3.1 Run Migrations

Railway automatically runs migrations on deployment via the start command.

### 3.2 Create Initial Data

You can create a script to populate initial data:

Create `scripts/init_railway_db.py`:

```python
import requests
import os

RAILWAY_URL = os.getenv("RAILWAY_URL", "https://your-app.railway.app")

def create_gyms():
    gyms = [
        {"name": "Downtown Fitness", "location": "New York"},
        {"name": "Westside Gym", "location": "Los Angeles"},
        {"name": "Central Training", "location": "Chicago"},
    ]
    
    for gym in gyms:
        try:
            response = requests.post(f"{RAILWAY_URL}/gyms", json=gym)
            print(f"Created gym: {gym['name']} - Status: {response.status_code}")
        except Exception as e:
            print(f"Error creating gym {gym['name']}: {e}")

if __name__ == "__main__":
    create_gyms()
```

Run it locally:
```bash
RAILWAY_URL=https://your-app.railway.app python scripts/init_railway_db.py
```

## Step 4: Update Mobile App Configuration

### 4.1 Update API Base URL

Modify `mobile/config/api.ts`:

```typescript
import { Platform } from 'react-native';

// Only import Constants on native platforms
let Constants: any = null;
if (Platform.OS !== 'web') {
  Constants = require('expo-constants').default;
}

// Railway backend URL
const PRODUCTION_API_URL = 'https://your-app.railway.app';

function getApiUrl(): string {
  // For production builds, use Railway URL
  if (process.env.NODE_ENV === 'production') {
    return PRODUCTION_API_URL;
  }
  
  // For web, use localhost
  if (Platform.OS === 'web') {
    return 'http://localhost:8000';
  }

  // For Expo Go on physical device, use the dev server URL's host
  if (Constants) {
    const debuggerHost = Constants.expoConfig?.hostUri;
    if (debuggerHost) {
      const host = debuggerHost.split(':')[0];
      return `http://${host}:8000`;
    }
  }

  // Fallback for Android emulator
  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:8000';
  }

  // Fallback for iOS simulator
  return 'http://localhost:8000';
}

export const API_BASE_URL = getApiUrl();

console.log('API Base URL:', API_BASE_URL);
```

### 4.2 Create Environment Configuration

Create `mobile/.env.production`:

```
API_BASE_URL=https://your-app.railway.app
```

## Step 5: Test the Deployment

### 5.1 Test Backend Health

```bash
curl https://your-app.railway.app/docs
```

You should see the FastAPI Swagger documentation.

### 5.2 Test API Endpoints

```bash
# Test gyms endpoint
curl https://your-app.railway.app/gyms

# Test health check (if you have one)
curl https://your-app.railway.app/health
```

### 5.3 Test from Mobile App

1. Update the API URL in your mobile app
2. Build and run the app
3. Try to register and login
4. Test all features

## Step 6: Monitoring and Logs

### 6.1 View Logs

1. Go to your Railway project
2. Click on your service
3. Go to "Deployments"
4. Click on the latest deployment
5. View logs in real-time

### 6.2 Set Up Alerts

1. Go to "Settings" → "Notifications"
2. Configure deployment notifications
3. Set up error alerts

## Troubleshooting

### Database Connection Issues

If you see database connection errors:

1. Check that `DATABASE_URL` is set correctly
2. Ensure PostgreSQL service is running
3. Check that migrations ran successfully

```bash
# View logs to see migration output
railway logs
```

### CORS Issues

If you get CORS errors from the mobile app:

1. Ensure `allow_origins=["*"]` in CORS middleware
2. Check that all headers are allowed
3. Verify the API URL is correct in mobile app

### Migration Issues

If migrations fail:

1. Check the logs for specific errors
2. Manually run migrations:

```bash
railway run alembic upgrade head
```

3. Check database connection

### Environment Variables Not Loading

1. Verify all environment variables are set in Railway
2. Restart the service
3. Check logs for any errors

## Railway CLI (Optional)

Install Railway CLI for easier management:

```bash
npm i -g @railway/cli
```

Login:
```bash
railway login
```

Link to project:
```bash
railway link
```

View logs:
```bash
railway logs
```

Run commands:
```bash
railway run alembic upgrade head
```

## Cost Estimation

Railway pricing (as of 2024):
- **Hobby Plan**: $5/month
  - 500 hours of usage
  - $0.000231/GB-hour for memory
  - $0.000463/vCPU-hour
  
- **Pro Plan**: $20/month
  - Unlimited usage
  - Better performance
  - Priority support

For a small app with moderate usage, the Hobby plan should be sufficient.

## Security Best Practices

1. **Use Strong SECRET_KEY**: Generate a secure random string
2. **Enable HTTPS**: Railway provides HTTPS by default
3. **Secure Environment Variables**: Never commit `.env` files
4. **Rate Limiting**: Consider adding rate limiting middleware
5. **Database Backups**: Railway provides automatic backups for PostgreSQL

## Next Steps

1. ✅ Deploy backend to Railway
2. ✅ Configure environment variables
3. ✅ Test all API endpoints
4. ✅ Update mobile app with production URL
5. ✅ Build APK with production configuration
6. 📱 Test the complete flow

Your backend is now live on Railway! 🚀
