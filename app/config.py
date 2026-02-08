"""
Configuration settings for the Payment Scoring Skill application.
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # ERPNext Configuration
    ERPNEXT_URL: str = os.getenv("ERPNEXT_URL", "http://localhost:8080")
    ERPNEXT_API_KEY: str = os.getenv("ERPNEXT_API_KEY", "")
    ERPNEXT_API_SECRET: str = os.getenv("ERPNEXT_API_SECRET", "")
    ERP_BASE_URL: Optional[str] = None
    ERP_API_TOKEN: Optional[str] = None
    
    # Application Settings
    APP_NAME: str = "ERPNext Payment Scoring Skill"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    USE_MOCK_DATA: bool = os.getenv("USE_MOCK_DATA", "False").lower() == "true"
    
    # Scoring Configuration
    SCORING_MODEL_VERSION: str = "1.0"
    MIN_TRANSACTIONS_FOR_SCORING: int = 1  # Allow scoring with 1+ invoices
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    
    # Claude AI Configuration
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    AI_TOPK: int = int(os.getenv("AI_TOPK", "5"))
    AI_TIMEOUT_SECONDS: int = int(os.getenv("AI_TIMEOUT_SECONDS", "10"))
    AI_MAX_CONCURRENCY: int = int(os.getenv("AI_MAX_CONCURRENCY", "6"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


settings = Settings()
