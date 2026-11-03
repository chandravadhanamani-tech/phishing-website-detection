"""
config.py - Application Configuration
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    use_sqlite: bool = True
    sqlite_db_path: str = "./phishing_detection.db"

    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "phishing_detection_db"
    db_user: str = "root"
    db_password: str = ""

    secret_key: str = "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION_USE_32_CHARS_MIN"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    app_name: str = "Phishing Detection System"
    app_version: str = "1.0.0"
    debug: bool = False               # Disabled verbose SQL log printing for speed
    backend_port: int = 8000

    frontend_url: str = "http://localhost:5173"

    ml_models_dir: str = "../ml/saved_models"
    active_model: str = "xgboost"

    deep_scan_enabled: bool = False
    deep_scan_timeout: int = 2        # Reduced from 10s to 2s for instant response
    max_url_length: int = 2048

    @property
    def database_url(self) -> str:
        if self.use_sqlite:
            db_file = os.path.abspath(self.sqlite_db_path).replace("\\", "/")
            return f"sqlite:///{db_file}"
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            f"?charset=utf8mb4"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
