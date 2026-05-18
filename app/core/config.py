from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_SUCCESS_URL: str = "http://localhost:8000/api/v1/payments/success"
    STRIPE_CANCEL_URL: str = "http://localhost:8000/api/v1/payments/cancel"

    # PostgreSQL
    DATABASE_URL: str = "postgresql://postgres:postgres@cinema_db:5432/online_cinema"
    TEST_DATABASE_URL: str = (
        "postgresql://postgres:postgres@cinema_db:5432/test_online_cinema"
    )

    # SWAGGER AUTH
    SWAGGER_USER: str = "admin"
    SWAGGER_PASSWORD: str = "super_secret_password_2026"

    # Redis
    REDIS_URL: str = "redis://cinema_redis:6379/0"

    # Mailtrap
    SMTP_HOST: str = "sandbox.smtp.mailtrap.io"
    SMTP_PORT: int = 2525
    SMTP_USER: str = "70b122e738a9c5"
    SMTP_PASSWORD: str = "c6465ef53c2d17"

    STRIPE_SECRET_KEY: str = "mock_stripe_key"
    STRIPE_WEBHOOK_SECRET: str = "mock_webhook_secret"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
