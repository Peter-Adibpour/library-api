from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # Selects between "memory" and "database" backends
    storage_backend: Literal["memory", "database"] = "database"
    database_url: str = "postgresql+psycopg://postgres:password@localhost:5432/library"

settings = Settings()