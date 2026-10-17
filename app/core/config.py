import base64
import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Project Info
    PROJECT_NAME: str = "DGDA RDC API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "dgda_super_secret_production_key_change_in_production_2026_xyz_dgda_security"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./dgda.db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: Union[List[str], str] = ["*"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        return v

    # Rate Limiting
    RATE_LIMIT_LOGIN: str = "10/minute"
    RATE_LIMIT_REGISTER: str = "5/minute"

    # Email Service (Brevo / Resend)
    BREVO_API_KEY: str = (
        "xkeysib-5d87c1b7294133aba5566ced74c5c1c1"
        "a6f407b3d0f098e9287da90b449a9e03"
        "-ayCpfrjATEp7muJx"
    )
    BREVO_SENDER_EMAIL: str = "makflutter@gmail.com"
    BREVO_SENDER_NAME: str = "DGDA Douane"
    RESEND_API_KEY: str = ""
    EMAILS_FROM: str = "DGDA Douane <makflutter@gmail.com>"
    OTP_EXPIRE_MINUTES: int = 10

    # AI & OpenAI LLM Integration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    GEMINI_API_KEY: str = ""

    # Cloudinary CDN Configuration
    CLOUDINARY_CLOUD_NAME: Optional[str] = "lgxpxrfm"
    CLOUDINARY_API_KEY: Optional[str] = "545539238719243"
    CLOUDINARY_API_SECRET: Optional[str] = "muj4VPJxHADkCcsJ22kscKK1cHM"
    CLOUDINARY_URL: Optional[str] = (
        "cloudinary://545539238719243:muj4VPJxHADkCcsJ22kscKK1cHM@lgxpxrfm"
    )



settings = Settings()
