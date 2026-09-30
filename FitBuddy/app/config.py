from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    app_name: str = "FitBuddy"
    database_url: str = f"sqlite:///{(BASE_DIR / "data" / "fitbuddy.db").as_posix()}"
    gemini_api_key: str | None = None
    gemini_workout_model: str = "gemini-3.1-pro-preview"
    gemini_fast_model: str = "gemini-3.8-flash"
    mock_ai: bool = True
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
