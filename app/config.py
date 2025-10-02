# app/config.py
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database / app
    mongodb_url: str = Field("mongodb://localhost:27017", env="MONGODB_URL")
    database_name: str = Field("emp_db", env="DATABASE_NAME")

    # Auth
    SECRET_KEY: str = Field("replace-me-with-a-secure-secret", env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60 * 24, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # S3 / uploads
    aws_s3_bucket: Optional[str] = Field("", env="AWS_S3_BUCKET")
    aws_region: Optional[str] = Field("", env="AWS_REGION")
    aws_access_key_id: Optional[str] = Field("", env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field("", env="AWS_SECRET_ACCESS_KEY")
    upload_folder: str = Field("uploads", env="UPLOAD_FOLDER")
    max_file_size: int = Field(10 * 1024 * 1024, env="MAX_FILE_SIZE")  # bytes
    allowed_mimetypes: List[str] = Field(
        default_factory=lambda: ["application/pdf", "image/png", "image/jpeg"],
        env="ALLOWED_MIMETYPES",
    )

    # Frontend / dev flags (these caused the earlier error)
    frontend_url: Optional[str] = Field(None, env="FRONTEND_URL")
    backend_url: Optional[str] = Field(None, env="BACKEND_URL")
    vite_use_mock: bool = Field(False, env="VITE_USE_MOCK")

    # Add or map any additional settings your app requires here...
    # Example:
    # sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")

    # pydantic v2 settings (pydantic_settings / BaseSettings)
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        # be lenient on unknown env vars so startup isn't brittle
        "extra": "ignore",
        # case insensitive env lookups (optional)
        "case_sensitive": False,
    }


# instantiate (import `settings` from your app modules)
settings = Settings()
