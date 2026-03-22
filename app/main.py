from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.tenant import GymIsolationMiddleware
from app.api.routes.auth import router as auth_router
from app.api.routes.gyms import router as gyms_router
from app.api.routes.health import router as health_router
from app.api.routes.meals import router as meals_router
from app.api.routes.ai import router as ai_router
from app.api.routes.user import router as user_router
from app.api.routes.gamification import router as gamification_router

app = FastAPI(title="Multi-Gym AI Nutrition SaaS API", version="0.1.0")

# CORS middleware - allow requests from all origins (mobile app + web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for mobile app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GymIsolationMiddleware)

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(gyms_router, prefix="/gyms", tags=["gyms"])
app.include_router(meals_router, prefix="/meals", tags=["meals"])
app.include_router(ai_router, prefix="/ai", tags=["ai"])
app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(gamification_router, prefix="/gamification", tags=["gamification"])

