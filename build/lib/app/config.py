from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field, ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = Field(default='Synapse AI-SEOS')
    log_level: str = Field(default='INFO')

    jwt_algorithm: str = Field(default='HS256', alias='JWT_ALGORITHM')
    jwt_secret_key: str = Field(default='test-secret', alias='JWT_SECRET_KEY')
    jwt_issuer: Optional[str] = Field(default=None, alias='JWT_ISSUER')
    jwt_audience: Optional[str] = Field(default=None, alias='JWT_AUDIENCE')

    @model_validator(mode='after')
    def _validate_jwt(self) -> 'Settings':
        if not self.jwt_algorithm or not self.jwt_algorithm.strip():
            raise ValueError('JWT_ALGORITHM must be configured')

        # For HS* algorithms we require a shared secret.
        if self.jwt_algorithm.upper().startswith('HS') and not self.jwt_secret_key:
            raise ValueError('JWT_SECRET_KEY is required for HS* algorithms')

        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as exc:
        raise RuntimeError(f'Invalid application settings: {exc}') from exc
