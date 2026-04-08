from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
        protected_namespaces=('model_',),
    )

    app_name: str = 'Zero Vape SEO Platform'
    environment: str = Field(default='development', alias='ENVIRONMENT')
    api_v1_prefix: str = '/api/v1'

    database_url: str = Field(default='sqlite:///./seomachine.db', alias='DATABASE_URL')
    redis_url: str = Field(default='redis://redis:6379/0', alias='REDIS_URL')

    jwt_secret: str = Field(default='dev-secret-change-me', alias='JWT_SECRET')
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 60 * 24
    backend_cors_origins: str = Field(default='http://localhost:3000', alias='BACKEND_CORS_ORIGINS')

    settings_encryption_key: str = Field(default='dev-encryption-key-change-me-32-chars', alias='SETTINGS_ENCRYPTION_KEY')


@lru_cache
def get_settings() -> Settings:
    return Settings()
