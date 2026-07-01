"""
Centralized application configuration.
Reads values from the .env file (see .env.example) using pydantic-settings.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "mysql+pymysql://root:ENTE_YOUR_MYSQL_PASSWORD@localhost:3306/diabetes_ai_db"

    # JWT
    JWT_SECRET_KEY: str = "ENTER_JWT_SECRET_KEY"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # ML model
    MODEL_PATH: str = "model/diabetes_best_model.pkl"

    # CORS - comma separated string in .env, parsed into a list below
    ALLOWED_ORIGINS: str = "http://localhost:5500,http://127.0.0.1:5500"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()

# Resolve MODEL_PATH relative to the backend/ folder so it works regardless of
# the working directory the server is launched from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if not os.path.isabs(settings.MODEL_PATH):
    settings.MODEL_PATH = os.path.join(BASE_DIR, settings.MODEL_PATH)
