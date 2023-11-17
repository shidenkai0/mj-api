from enum import StrEnum

import openai
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(StrEnum):
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


class Settings(BaseSettings):
    """
    The `Settings` class is responsible for managing the application's configuration settings.

    It inherits from the `BaseSettings` class provided by the `pydantic` library.
    """

    DATABASE_URL: PostgresDsn
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 20
    OPENAI_API_KEY: str
    APP_SECRET: str
    SUPABASE_JWT_SECRET: str
    ENV: Env = Env.DEV
    PROJECT_NAME: str = "mockingjay"
    FIREBASE_KEY_FILE: str = "polyglot-dev.json"
    FIREBASE_PROJECT_ID: str = "polyglot-dev"
    FIREBASE_AUTH_EMULATOR_HOST: str
    SUPPORTED_LANGUAGES: list[str] = ["en", "fr"]
    TTS_ENGINE_URL: str = "http://localhost:3000"

    @property
    def show_docs(self):
        return self.ENV != "prod"

    model_config = SettingsConfigDict(extra="ignore", env_file=".env")


settings = Settings()

openai.api_key = settings.OPENAI_API_KEY
