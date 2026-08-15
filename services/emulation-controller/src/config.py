"""
Configuration settings for Emulation Controller.
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
    PORT: int = Field(default=8004, validation_alias="PORT")
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
    REDPANDA_CONSUMER_GROUP: str = Field(default="emulation-controller", validation_alias="REDPANDA_CONSUMER_GROUP")
    
    # Kubernetes
    KUBERNETES_NAMESPACE: str = Field(default="aegisforge-lab", validation_alias="KUBERNETES_NAMESPACE")
    KUBECONFIG_PATH: Optional[str] = Field(default=None, validation_alias="KUBECONFIG_PATH")
    
    # Emulation
    EMULATION_NAMESPACE: str = Field(default="aegisforge-lab", validation_alias="EMULATION_NAMESPACE")
    EMULATION_REQUIRE_APPROVAL: bool = Field(default=True, validation_alias="EMULATION_REQUIRE_APPROVAL")
    EMULATION_MAX_CONCURRENT: int = Field(default=3, validation_alias="EMULATION_MAX_CONCURRENT")
    EMULATION_DEFAULT_DURATION: int = Field(default=300, validation_alias="EMULATION_DEFAULT_DURATION")
    
    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: str = Field(default="http://otel-collector:4317", validation_alias="OTEL_EXPORTER_OTLP_ENDPOINT")
    OTEL_SERVICE_NAME: str = Field(default="emulation-controller", validation_alias="OTEL_SERVICE_NAME")
    OTEL_EXPORTER_OTLP_INSECURE: bool = Field(default=True, validation_alias="OTEL_EXPORTER_OTLP_INSECURE")
    
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