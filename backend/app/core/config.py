from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_database_url(url: str) -> str:
    """Convertit l'URL PostgreSQL Railway (postgresql://) en driver asyncpg."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    PROJECT_NAME: str = "SGEP — Fodeba Keita"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30
    PASSWORD_RESET_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str = "postgresql+asyncpg://sgep:sgep_dev_password@localhost:5432/sgep_db"
    REDIS_URL: str = "redis://localhost:6379/0"

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "sgep_minio"
    MINIO_SECRET_KEY: str = "sgep_minio_password"
    MINIO_BUCKET: str = "sgep-files"
    MINIO_SECURE: bool = False

    CORS_ORIGINS: str = "http://localhost:3000"
    PORT: int = 8000

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_db_url(cls, value: str) -> str:
        return _normalize_database_url(value)

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
