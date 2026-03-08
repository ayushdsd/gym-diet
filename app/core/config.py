import os
from dotenv import load_dotenv

# CRITICAL: Only load .env in local development
# On Railway, environment variables are set directly and .env should not exist
if os.path.exists(".env") and not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()


class Settings:
    # Get DATABASE_URL and fix Railway's postgres:// to postgresql://
    # IMPORTANT: This default should NEVER be used on Railway
    _database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/gymdiet")
    
    @property
    def DATABASE_URL(self) -> str:
        """Fix Railway's postgres:// URL to postgresql:// for SQLAlchemy"""
        url = self._database_url
        
        # Debug: Print what we got
        if os.getenv("RAILWAY_ENVIRONMENT"):
            print(f"[CONFIG] Raw DATABASE_URL from env: {url[:50]}...")
        
        if url and url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
            if os.getenv("RAILWAY_ENVIRONMENT"):
                print(f"[CONFIG] Converted to: {url[:50]}...")
        
        return url
    
    JWT_SECRET: str = os.getenv("JWT_SECRET", os.getenv("SECRET_KEY", "change-this-secret"))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    DEFAULT_TARGET_CALORIES: int = int(os.getenv("DEFAULT_TARGET_CALORIES", "2000"))
    DEFAULT_TARGET_PROTEIN: int = int(os.getenv("DEFAULT_TARGET_PROTEIN", "150"))
    DEFAULT_TARGET_CARBS: int = int(os.getenv("DEFAULT_TARGET_CARBS", "250"))
    DEFAULT_TARGET_FATS: int = int(os.getenv("DEFAULT_TARGET_FATS", "60"))


settings = Settings()
