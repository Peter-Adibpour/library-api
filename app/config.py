from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    storage_backend: Literal["memory", "database"] = "database"
    database_url: str = "postgresql+psycopg://postgres:password@localhost:5432/library"
    
    # Classroom Bearer tokens for Assignment 3
    member_token: str = "student-member-token"
    admin_token: str = "instructor-admin-token"

settings = Settings()