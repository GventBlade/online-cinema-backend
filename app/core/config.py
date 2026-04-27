from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    DATABASE_URL: str = "sqlite:///./online_cinema.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
