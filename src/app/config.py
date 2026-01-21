from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    DEBUG: bool = True

    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_PASSWORD: str

    OPENAI_API_KEY: str
    SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300

    CLOUDFLARE_ACCOUNT_ID: str
    CLOUDFLARE_ACCESS_KEY_ID: str

    CLOUDFLARE_SECRET_KEY_ID: str
    CLOUDFLARE_BUCKET_NAME: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    BACKEND_URL: str

    # Mobile app deep link scheme (e.g., "koalaact://")
    MOBILE_REDIRECT_SCHEME: str = "koalaact"

    # Frontend URL for web app redirects
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        extra = "ignore"
        env_file = BASE_DIR / ".env"

    @property
    def db_url(self) -> str:
        return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST,
            self.POSTGRES_PORT,
            self.POSTGRES_DB
        )

    @property
    def alembic_db_url(self) -> str:
        return "postgresql://{}:{}@{}:{}/{}".format(
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST,
            self.POSTGRES_PORT,
            self.POSTGRES_DB
        )



settings = Settings()
