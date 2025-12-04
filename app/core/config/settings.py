"""
Application settings and configuration
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application configuration settings."""

    # Application settings
    app_name: str = "Chat Application"
    app_version: str = "0.1.0"
    debug: bool = True
    environment: str = "development"

    # API settings
    api_prefix: str = "/api/v1"
    api_title: str = "Chat Application API"
    api_description: str = "FastAPI Chat Application with Agent Pipeline"

    # Database settings
    database_url: str = ""
    echo_sql: bool = False

    # LLM settings
    API_ENDPOINT: str = ""
    API_KEY: str = ""
    MODEL_CHAT_BASIC: str = ""
    MODEL_CHAT_MOD: str = ""
    MODEL_CHAT_OPEN: str = ""
    MODEL_REASONING: str = ""
    MODEL_VISION: str = ""
    MODEL_EMBEDDING: str = ""
    MODEL_AUDIO: str = ""

    # Embedding settings
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"

    # Authentication settings
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # LangGraph settings
    max_iterations: int = 10
    timeout: int = 300

    # File upload settings
    upload_directory: str = "./uploads"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = [".pdf", ".txt", ".doc", ".docx"]

    # Logging settings
    log_directory: str = "./logs"
    log_level: str = "INFO"


    # CORS settings
    cors_origins: list = ["*"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]

    # Excluded routes from authentication
    auth_excluded_routes: list = ["/health", "/api/v1/auth/login","/api/v1/chat/ws"]

    # Observability settings
    enable_observability: bool = True
    phoenix_host: str = "localhost"
    phoenix_port: int = 6006
    trace_retention_days: int = 7
    enable_pii_redaction: bool = False  # Set to True in production
    observability_sample_rate: float = 1.0  # 1.0 = 100% of requests
    phoenix_collector_endpoint: str = "http://localhost:6006"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.log_directory, exist_ok=True)
os.makedirs(settings.upload_directory, exist_ok=True)
