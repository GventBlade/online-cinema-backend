from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_SUCCESS_URL: str = "http://localhost:8000/api/v1/payments/success"
    STRIPE_CANCEL_URL: str = "http://localhost:8000/api/v1/payments/cancel"

    DATABASE_URL: str = "sqlite:///./online_cinema.db"

    SMTP_HOST: str = "sandbox.smtp.mailtrap.io"
    SMTP_PORT: int = 2525
    SMTP_USER: str = "70b122e738a9c5"
    SMTP_PASSWORD: str = "c6465ef53c2d17"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

