"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Hackathon Backend"
    DEBUG: bool = True
    
    # Database
    DB_HOST: str = "mysql"
    DB_PORT: int = 3306
    DB_USER: str = "hackathon_user"
    DB_PASSWORD: str = "hackathon_pass"
    DB_NAME: str = "hackathon_db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production-very-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://tempo:4317"
    PROMETHEUS_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # Anomaly injection flags
    ENABLE_ANOMALY_DELAY: bool = False
    ANOMALY_DELAY_SECONDS: float = 0.0
    ENABLE_RANDOM_ERRORS: bool = False
    RANDOM_ERROR_RATE: float = 0.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


