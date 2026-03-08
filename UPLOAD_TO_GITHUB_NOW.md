# Upload to GitHub - Quick Commands

Follow these commands in order to upload your project to GitHub.

## Step 1: Initialize Git (if not already done)

```bash
git init
```

## Step 2: Add All Files

```bash
git add .
```

## Step 3: Commit Files

```bash
git commit -m "Initial commit: Full-stack gym diet tracker with gamification"
```

## Step 4: Create GitHub Repository

1. Go to https://github.com
2. Click "+" icon → "New repository"
3. Name: `gym-diet-tracker`
4. Description: "Full-stack gym diet tracking app with AI and gamification"
5. Choose Public or Private
6. **DO NOT** check "Initialize with README"
7. Click "Create repository"

## Step 5: Connect to GitHub

Replace `YOUR_USERNAME` with your GitHub username:

```bash
git remote add origin https://github.com/YOUR_USERNAME/gym-diet-tracker.git
git branch -M main
git push -u origin main
```

## Step 6: Verify Upload

Go to your GitHub repository page and refresh. You should see all your files!

---

## If You Get Errors

### Error: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/gym-diet-tracker.git
```

### Error: "Updates were rejected"
```bash
git pull origin main --rebase
git push origin main
```

### Error: "Permission denied"
Use HTTPS instead of SSH:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/gym-diet-tracker.git
```

---

## After Upload is Complete

### Next Step: Deploy to Railway

1. Go to https://railway.app
2. Sign up/Login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `gym-diet-tracker` repository
6. Railway will automatically deploy!

See [DEPLOY_TO_RAILWAY.md](DEPLOY_TO_RAILWAY.md) for detailed steps.

---

## Quick Verification Checklist

After uploading, verify these files are on GitHub:

- ✅ `app/` directory (backend code)
- ✅ `mobile/` directory (mobile app)
- ✅ `alembic/` directory (migrations)
- ✅ `tests/` directory (test files)
- ✅ `requirements.txt`
- ✅ `Procfile`
- ✅ `railway.json`
- ✅ `mobile/eas.json`
- ✅ `README.md`
- ✅ All documentation `.md` files

Should NOT be uploaded (in .gitignore):
- ❌ `__pycache__/`
- ❌ `node_modules/`
- ❌ `.env` file
- ❌ `*.db` files
- ❌ `.expo/`

---

## You're Ready!

Once your code is on GitHub, you can:
1. ✅ Deploy backend to Railway
2. ✅ Build Android APK with EAS
3. ✅ Share your repository
4. ✅ Collaborate with others

**Start uploading now!** 🚀
