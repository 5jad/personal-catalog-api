from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Export settings
    EXPORT_DIR: str = "/tmp/exports"
    ALLOWED_EXPORT_FORMATS: tuple = ("csv", "json")

    class Config:
        env_file = ".env"

settings = Settings()
