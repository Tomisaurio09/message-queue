# app/core/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

UPLOAD_DIR = "/app/uploads"
PROCESSED_DIR = "/app/processed"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)



class Settings(BaseSettings):
    DATABASE_URL: str
    DEBUG: bool

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Singleton to avoid reloading settings multiple times."""
    return Settings()


settings = get_settings()