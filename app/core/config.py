from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str | None = None
    REDIS_URL: str | None = None          # ← add this
    FIREBASE_CREDENTIALS: str | None = None
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()