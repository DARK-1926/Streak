import os
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # FastAPI
    APP_NAME: str = "Personalized PDF Service"
    DEBUG: bool = Field(default=False, env="DEBUG")
    # JWT
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    # Database
    POSTGRES_DSN: str = Field(..., env="POSTGRES_DSN")
    # Redis / Celery
    REDIS_URL: str = Field(..., env="REDIS_URL")
    # LLM
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4o-mini"
    # PDF
    WEASYPRINT_TIMEOUT: int = 30

settings = Settings()
