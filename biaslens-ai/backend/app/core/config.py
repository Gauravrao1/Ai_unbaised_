from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "BiasLens AI"
    environment: str = "development"
    cors_origins: str = "http://localhost:5173"
    cors_origin_regex: str = r"https://.*\.vercel\.app"
    uploads_dir: str = "backend/uploads"
    gemini_api_key: str = ""
    gemini_model_name: str = "gemini-1.5-flash"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
