# Fix: CORS Error

## Error
```
Access to fetch at 'http://localhost:8000/gyms' from origin 'http://localhost:8081' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present 
on the requested resource.
```

## Cause
The FastAPI backend wasn't configured to allow requests from the frontend origin (localhost:8081).

## Fix Applied

Added CORS middleware to `app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",  # Expo web
        "http://localhost:19006",  # Expo web alternative port
        "http://127.0.0.1:8081",
        "http://127.0.0.1:19006",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## How to Apply

### 1. Restart Backend

The backend needs to be restarted to apply the CORS changes:

```bash
# Stop current backend (Ctrl+C)

# Restart backend
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 2. Refresh Frontend

In the browser, refresh the page (F5 or Ctrl+R)

## Expected Result

The gym selection screen should now load gyms successfully without CORS errors.

## Testing

### 1. Check Backend is Running
```bash
curl http://localhost:8000/docs
```

Should return the API documentation page.

### 2. Test Gyms Endpoint
```bash
curl http://localhost:8000/gyms
```

Should return JSON array of gyms (or empty array if no gyms exist).

### 3. Create Test Gyms (if needed)
```bash
python scripts/create_test_gyms.py
```

### 4. Refresh Frontend
Open browser console (F12) and refresh the page. You should see:
```
Loaded gyms: [{ id: 1, name: "PowerFit Gym" }, ...]
```

## What is CORS?

CORS (Cross-Origin Resource Sharing) is a security feature that prevents web pages from making requests to a different domain than the one serving the page.

In our case:
- Frontend runs on: `http://localhost:8081`
- Backend runs on: `http://localhost:8000`

These are different origins (different ports), so the browser blocks the request unless the backend explicitly allows it.

## Production Note

For production, you should:
1. Replace `allow_origins=["*"]` with specific domains
2. Set `allow_credentials=True` only if needed
3. Restrict `allow_methods` and `allow_headers` to what's actually used

Example for production:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

## Summary

CORS middleware has been added to the backend to allow requests from the frontend. Restart the backend and refresh the frontend to apply the fix.
