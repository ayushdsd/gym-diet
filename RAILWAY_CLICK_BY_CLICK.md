# Railway Fix - Click by Click Guide

## What You'll See and Click

### Screen 1: Railway Dashboard
```
You see: Your projects list
Click on: Your gym-diet project
```

### Screen 2: Project View
```
You see: Two boxes/cards
  - One labeled "Postgres" or "PostgreSQL" 
  - One labeled with your app name (web service)

Click on: The PostgreSQL box
```

### Screen 3: PostgreSQL Service
```
You see: Tabs at the top
  - Settings
  - Variables  ← Click this
  - Metrics
  - Deployments

Click on: Variables tab
```

### Screen 4: PostgreSQL Variables
```
You see: A list of variables including:
  - DATABASE_URL
  - PGDATABASE
  - PGHOST
  - PGPASSWORD
  - PGPORT
  - PGUSER
  - DATABASE_PRIVATE_URL
  - DATABASE_PUBLIC_URL

Find: DATABASE_URL (usually first in the list)
Look for: A copy icon (📋) next to the value
Click: The copy icon to copy the URL
```

The URL looks like:
```
postgres://postgres:AbCdEf123456@postgres.railway.internal:5432/railway
```

### Screen 5: Go Back to Project
```
You see: A back arrow or breadcrumb at the top
Click: Back to project view
```

### Screen 6: Project View Again
```
You see: The two service boxes again
Click on: Your WEB service box (NOT PostgreSQL)
```

### Screen 7: Web Service
```
You see: Tabs at the top
  - Settings
  - Variables  ← Click this
  - Metrics
  - Deployments

Click on: Variables tab
```

### Screen 8: Web Service Variables
```
You see: A list of your variables:
  - JWT_SECRET
  - OPENAI_API_KEY
  - Maybe others

Look for: DATABASE_URL in the list

If DATABASE_URL EXISTS:
  - Click the three dots (...) next to it
  - Click "Edit"
  - Paste the URL you copied
  - Click "Update"

If DATABASE_URL DOESN'T EXIST:
  - Click "+ New Variable" button (top right)
  - In the popup:
    Variable: DATABASE_URL
    Value: Paste the URL you copied
  - Click "Add"
```

### Screen 9: Automatic Redeploy
```
You see: A notification that deployment is starting
Wait: 2-3 minutes for deployment to complete
```

### Screen 10: Check Deployment
```
Click on: Deployments tab
You see: List of deployments, newest at top
Click on: The latest deployment (should be "Building" or "Success")
Click on: "View Logs"
```

### Screen 11: Deployment Logs
```
Look for these messages:
  ✅ "Running migrations..."
  ✅ "Application startup complete"
  ✅ "Uvicorn running on..."

Should NOT see:
  ❌ "connection to localhost refused"
  ❌ "Connection refused"
```

## Alternative: Use Reference Variable

Instead of copying the URL, you can use a reference:

In Screen 8 (Web Service Variables):
```
Click: "+ New Variable"
Variable: DATABASE_URL
Value: ${{Postgres.DATABASE_URL}}
Click: "Add"
```

Replace "Postgres" with whatever your PostgreSQL service is actually named.

This is better because:
- Automatically updates if PostgreSQL URL changes
- No need to copy/paste
- Cleaner and more maintainable

## Visual Summary

```
PostgreSQL Service → Variables → Copy DATABASE_URL
                                      ↓
                                   [Copy]
                                      ↓
Web Service → Variables → Add DATABASE_URL → Paste → Add
                                      ↓
                              [Auto Redeploy]
                                      ↓
                                  SUCCESS! ✅
```

## Common UI Elements

- **Service Box**: Rectangular card with service name and status indicator
- **Variables Tab**: Usually second tab after Settings
- **Copy Icon**: Small clipboard or copy icon (📋) next to values
- **Three Dots Menu**: ⋮ or ... for more options
- **+ New Variable**: Button usually in top right of Variables page

## Colors to Look For

- **Green**: Service is running, deployment succeeded
- **Yellow/Orange**: Building, deploying
- **Red**: Error, deployment failed
- **Gray**: Service stopped or inactive

## If You Get Lost

1. Look for breadcrumbs at the top (Project > Service)
2. Click the project name to go back to project view
3. Start over from Screen 2

## Time Per Screen

- Screens 1-4: 1 minute (getting the URL)
- Screens 5-8: 1 minute (adding the URL)
- Screens 9-11: 3 minutes (waiting and verifying)
- Total: ~5 minutes
