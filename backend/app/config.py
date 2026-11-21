import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "LeadGen AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DATABASE_URL: str = "sqlite:///./leadgen.db"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # AI Configuration (Google Gemini)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Automation & Integrations
    N8N_WEBHOOK_URL: str = "http://localhost:5678/webhook/leads"
    GOOGLE_SHEET_ID: str = ""
    GMAIL_SENDER_ADDRESS: str = ""
    GMAIL_ACCESS_TOKEN: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
