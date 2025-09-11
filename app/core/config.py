from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    FIREBASE_CREDENTIALS: str | None = None
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()