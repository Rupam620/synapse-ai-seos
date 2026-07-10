from __future__ import annotations

from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Synapse AI-SEOS"
    log_level: str = "INFO"

    jwt_algorithm: str = Field(alias="JWT_ALGORITHM")
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_issuer: str | None = Field(default=None, alias="JWT_ISSUER")
    jwt_audience: str | None = Field(default=None, alias="JWT_AUDIENCE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    @field_validator("jwt_algorithm")
    @classmethod
    def _validate_algorithm(cls, value: str) -> str:
        v = value.strip()
        if not v:
            raise ValueError("JWT_ALGORITHM must not be empty")
        return v

    @field_validator("jwt_secret_key")
    @classmethod
    def _validate_secret(cls, value: str) -> str:
        v = value.strip()
        if not v:
            raise ValueError("JWT_SECRET_KEY must not be empty")
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
