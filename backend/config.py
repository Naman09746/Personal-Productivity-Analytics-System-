"""
Personal Productivity Analytics System - Configuration
"""
from typing import Any
from pydantic_settings import BaseSettings
from functools import lru_cache


from pydantic import field_validator

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Personal Productivity Analytics System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ppas"
    DATABASE_SYNC_URL: str = "postgresql://postgres:postgres@localhost:5432/ppas"
    
    # JWT Authentication
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    LOGIN_RATE_LIMIT_PER_HOUR: int = 10
    
    # CORS
    CORS_ORIGINS: list[str] | str = ["http://localhost:5173", "http://localhost:3000", "https://ppas-frontend.onrender.com", "*"]
    
    # Timezone (default for new users)
    DEFAULT_TIMEZONE: str = "UTC"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @field_validator("DATABASE_URL")
    @classmethod
    def parse_db_url(cls, v: str) -> str:
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
