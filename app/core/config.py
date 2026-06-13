from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    environment: str = "development"
    app_name: str = "immigration-navigator"
    log_level: str = "INFO"

    # Database
    database_url: str = Field(..., description="asyncpg connection string")

    # Groq
    groq_api_key: SecretStr = Field(..., description="Groq API key")
    groq_model: str = "llama-3.3-70b-versatile"

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"

    # Security
    secret_key: SecretStr = Field(..., description="32-byte hex")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def groq_key(self) -> str:
        return self.groq_api_key.get_secret_value()


@lru_cache
def get_settings() -> Settings:
    return Settings()