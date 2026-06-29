from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "RAG Chat Backend"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str
    DB_SCHEMA: str = "public"

    # Auth / JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OTP
    OTP_EXPIRE_MINUTES: int = 10
    OTP_LENGTH: int = 6
    OTP_MAX_ATTEMPTS: int = 5

    # SMTP
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    SMTP_FROM_NAME: str = "AI QA Analyzer"
    SMTP_STARTTLS: bool = True

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # File / chunking
    MAX_UPLOAD_SIZE_MB: int = 20
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # Embeddings / vector DB / local AI
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DEVICE: str | None = None  # e.g. "cpu", "cuda", "mps"

    VECTOR_DB_PROVIDER: Literal["chromadb", "faiss", "pgvector"] = "chromadb"
    VECTOR_DB_PATH: str = "./data/vector_store"
    VECTOR_DB_COLLECTION: str = "document_chunks"
    VECTOR_DB_DIMENSION: int = 384

    # Optional legacy / future external provider settings
    OPENAI_API_KEY: str | None = None
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"

    # Local dev chatbot mode
    ENABLE_STATIC_CHAT_RESPONSES: bool = False
    STATIC_CHAT_RESPONSE_TEXT: str = (
        "This is a local development placeholder response. "
        "Your question was received successfully, but RAG/LLM generation is "
        "currently disabled in local mode."
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        """
        Accept either:
        - a comma-separated string: "http://localhost:5173,http://127.0.0.1:5173"
        - a list[str]
        """
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()