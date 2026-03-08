import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/gymdiet")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-this-secret")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    DEFAULT_TARGET_CALORIES: int = int(os.getenv("DEFAULT_TARGET_CALORIES", "2000"))
    DEFAULT_TARGET_PROTEIN: int = int(os.getenv("DEFAULT_TARGET_PROTEIN", "150"))
    DEFAULT_TARGET_CARBS: int = int(os.getenv("DEFAULT_TARGET_CARBS", "250"))
    DEFAULT_TARGET_FATS: int = int(os.getenv("DEFAULT_TARGET_FATS", "60"))


settings = Settings()
