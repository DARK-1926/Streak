import os
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # Core service settings
    APP_NAME: str = "EmailAssistant"
    DEBUG: bool = Field(default=False, env="DEBUG")
    # LLM settings
    LLM_API_KEY: str = Field(..., env="LLM_API_KEY")
    LLM_ENDPOINT: str = Field(default="https://api.openai.com/v1/chat/completions")
    LLM_MODEL: str = Field(default="gpt-4o-mini")
    # Database settings
    POSTGRES_DSN: str = Field(..., env="POSTGRES_DSN")
    # Celery settings
    CELERY_BROKER_URL: str = Field(default="redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://redis:6379/1")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
