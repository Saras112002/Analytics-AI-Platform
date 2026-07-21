from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App info
    APP_NAME: str = "Analytics AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # AI APIs
    ANTHROPIC_API_KEY: str = ""
    OPENROUTER_API_KEY: str
    GOOGLE_API_KEY: str = ""

    # File paths
    UPLOAD_DIR: str = "data/uploads"

    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


@lru_cache()
def get_settings():
    return Settings()