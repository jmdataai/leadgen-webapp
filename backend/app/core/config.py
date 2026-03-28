from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret-key")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8001"))

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/leadgen.db")

    # Authentication
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    SESSION_EXPIRE_MINUTES: int = int(os.getenv("SESSION_EXPIRE_MINUTES", "43200"))

    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

    # Apify
    APIFY_API_KEY: str = os.getenv("APIFY_API_KEY", "")
    APIFY_JOB_ACTOR_ID: str = os.getenv("APIFY_JOB_ACTOR_ID", "harvestapi~linkedin-job-search")
    APIFY_EMPLOYEE_ACTOR_ID: str = os.getenv("APIFY_EMPLOYEE_ACTOR_ID", "harvestapi~linkedin-company-employees")
    APIFY_TIMEOUT: int = int(os.getenv("APIFY_TIMEOUT", "300"))

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

    # Resend Email (replaces Gmail)
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")

    # Email sender details
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "LeadGen AI")
    EMAIL_FROM_ADDRESS: str = os.getenv("EMAIL_FROM_ADDRESS", "onboarding@resend.dev")

    MAX_JOBS_PER_USER_PER_DAY: int = int(os.getenv("MAX_JOBS_PER_USER_PER_DAY", "10"))

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
