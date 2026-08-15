"""
Configuration settings for Detection Engine.
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
    PORT: int = Field(default=8001, validation_alias="PORT")
    WORKERS: int = Field(default=1, validation_alias="WORKERS")
    
    # Database
    POSTGRES_HOST: str = Field(default="postgres", validation_alias="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, validation_alias="POSTGRES_PORT")
    POSTGRES_DB: str = Field(default="aegisforge", validation_alias="POSTGRES_DB")
    POSTGRES_USER: str = Field(default="aegisforge", validation_alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="changeme_dev_only", validation_alias="POSTGRES_PASSWORD")
    POSTGRES_POOL_SIZE: int = Field(default=10, validation_alias="POSTGRES_POOL_SIZE")
    POSTGRES_MAX_OVERFLOW: int = Field(default=5, validation_alias="POSTGRES_MAX_OVERFLOW")
    
    # Kafka/Redpanda
    REDPANDA_BROKERS: str = Field(default="redpanda:9092", validation_alias="REDPANDA_BROKERS")
    REDPANDA_TOPIC_EVENTS: str = Field(default="security-events", validation_alias="REDPANDA_TOPIC_EVENTS")
    REDPANDA_TOPIC_ALERTS: str = Field(default="security-alerts", validation_alias="REDPANDA_TOPIC_ALERTS")
    REDPANDA_CONSUMER_GROUP: str = Field(default="detection-engine", validation_alias="REDPANDA_CONSUMER_GROUP")
    REDPANDA_AUTO_OFFSET_RESET: str = Field(default="latest", validation_alias="REDPANDA_AUTO_OFFSET_RESET")
    REDPANDA_MAX_POLL_RECORDS: int = Field(default=100, validation_alias="REDPANDA_MAX_POLL_RECORDS")
    REDPANDA_MAX_POLL_INTERVAL_MS: int = Field(default=300000, validation_alias="REDPANDA_MAX_POLL_INTERVAL_MS")
    
    # Database for alerts
    POSTGRES_HOST: str = Field(default="postgres", validation_alias="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, validation_alias="POSTGRES_PORT")
    POSTGRES_DB: str = Field(default="aegisforge", validation_alias="POSTGRES_DB")
    POSTGRES_USER: str = Field(default="aegisforge", validation_alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="changeme_dev_only", validation_alias="POSTGRES_PASSWORD")
    
    # Rules
    DETECTION_RULES_PATH: str = Field(default="/etc/aegisforge/rules", validation_alias="DETECTION_RULES_PATH")
    DETECTION_RULE_RELOAD_INTERVAL: int = Field(default=300, validation_alias="DETECTION_RULE_RELOAD_INTERVAL")
    
    # Processing
    BATCH_SIZE: int = Field(default=100, validation_alias="BATCH_SIZE")
    FLUSH_INTERVAL_SECONDS: int = Field(default=5, validation_alias="FLUSH_INTERVAL_SECONDS")
    MAX_CONCURRENT_EVALUATIONS: int = Field(default=10, validation_alias="MAX_CONCURRENT_EVALUATIONS")
    
    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: str = Field(default="http://otel-collector:4317", validation_alias="OTEL_EXPORTER_OTLP_ENDPOINT")
    OTEL_SERVICE_NAME: str = Field(default="detection-engine", validation_alias="OTEL_SERVICE_NAME")
    OTEL_EXPORTER_OTLP_INSECURE: bool = Field(default=True, validation_alias="OTEL_EXPORTER_OTLP_INSECURE")
    
    # Prometheus
    PROMETHEUS_REMOTE_WRITE_URL: Optional[str] = Field(default=None, validation_alias="PROMETHEUS_REMOTE_WRITE_URL")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", validation_alias="LOG_FORMAT")
    
    # Development
    DEV_MODE: bool = Field(default=True, validation_alias="DEV_MODE")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def REDPANDA_BOOTSTRAP_SERVERS(self) -> str:
        return self.REDPANDA_BROKERS


@lru_cache()
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()