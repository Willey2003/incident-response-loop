"""
Configuration settings for Target API.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    # General
    ENVIRONMENT: str = Field(default="development", validation_alias="ENVIRONMENT")
    LOG_LEVEL: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", validation_alias="LOG_FORMAT")
    
    # Service
    HOST: str = Field(default="0.0.0.0", validation_alias="HOST")
    PORT: int = Field(default=8080, validation_alias="PORT")
    WORKERS: int = Field(default=1, validation_alias="WORKERS")
    
    # Kafka/Redpanda
    REDPANDA_BROKERS: str = Field(default="redpanda:9092", validation_alias="REDPANDA_BROKERS")
    REDPANDA_TOPIC_EVENTS: str = Field(default="security-events", validation_alias="REDPANDA_TOPIC_EVENTS")
    REDPANDA_PRODUCER_CLIENT_ID: str = Field(default="target-api", validation_alias="REDPANDA_PRODUCER_CLIENT_ID")
    
    # Auth
    JWT_SECRET_KEY: str = Field(default="dev-secret-change-in-production", validation_alias="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    JWT_EXPIRY_MINUTES: int = Field(default=60, validation_alias="JWT_EXPIRY_MINUTES")
    
    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: str = Field(default="http://otel-collector:4317", validation_alias="OTEL_EXPORTER_OTLP_ENDPOINT")
    OTEL_SERVICE_NAME: str = Field(default="target-api", validation_alias="OTEL_SERVICE_NAME")
    OTEL_EXPORTER_OTLP_INSECURE: bool = Field(default=True, validation_alias="OTEL_EXPORTER_OTLP_INSECURE")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", validation_alias="LOG_FORMAT")
    
    # Development
    DEV_MODE: bool = Field(default=True, validation_alias="DEV_MODE")
    DEV_SEED_DATA: bool = Field(default=True, validation_alias="DEV_SEED_DATA")
    
    @property
    def REDPANDA_BOOTSTRAP_SERVERS(self) -> str:
        return self.REDPANDA_BROKERS


@lru_cache()
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()