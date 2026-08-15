"""
Configuration settings for Response Orchestrator.
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
    PORT: int = Field(default=8002, validation_alias="PORT")
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
    REDPANDA_TOPIC_ALERTS: str = Field(default="security-alerts", validation_alias="REDPANDA_TOPIC_ALERTS")
    REDPANDA_TOPIC_INCIDENTS: str = Field(default="security-incidents", validation_alias="REDPANDA_TOPIC_INCIDENTS")
    REDPANDA_TOPIC_AUDIT: str = Field(default="audit-logs", validation_alias="REDPANDA_TOPIC_AUDIT")
    REDPANDA_CONSUMER_GROUP: str = Field(default="response-orchestrator", validation_alias="REDPANDA_CONSUMER_GROUP")
    REDPANDA_AUTO_OFFSET_RESET: str = Field(default="latest", validation_alias="REDPANDA_AUTO_OFFSET_RESET")
    
    # Kubernetes
    KUBERNETES_NAMESPACE: str = Field(default="aegisforge-lab", validation_alias="KUBERNETES_NAMESPACE")
    KUBECONFIG_PATH: Optional[str] = Field(default=None, validation_alias="KUBECONFIG_PATH")
    
    # Response Configuration
    RESPONSE_NAMESPACE: str = Field(default="aegisforge-lab", validation_alias="RESPONSE_NAMESPACE")
    RESPONSE_DRY_RUN: bool = Field(default=True, validation_alias="RESPONSE_DRY_RUN")
    RESPONSE_REQUIRE_APPROVAL: bool = Field(default=True, validation_alias="RESPONSE_REQUIRE_APPROVAL")
    RESPONSE_ALLOWLIST_FILE: str = Field(default="/etc/aegisforge/allowlist.yaml", validation_alias="RESPONSE_ALLOWLIST_FILE")
    RESPONSE_CIRCUIT_BREAKER_THRESHOLD: int = Field(default=5, validation_alias="RESPONSE_CIRCUIT_BREAKER_THRESHOLD")
    RESPONSE_CIRCUIT_BREAKER_TIMEOUT: int = Field(default=60, validation_alias="RESPONSE_CIRCUIT_BREAKER_TIMEOUT")
    RESPONSE_MAX_CONCURRENT_ACTIONS: int = Field(default=5, validation_alias="RESPONSE_MAX_CONCURRENT_ACTIONS")
    RESPONSE_DEFAULT_TIMEOUT: int = Field(default=300, validation_alias="RESPONSE_DEFAULT_TIMEOUT")
    RESPONSE_MAX_RETRIES: int = Field(default=3, validation_alias="RESPONSE_MAX_RETRIES")
    RESPONSE_RETRY_DELAY: int = Field(default=10, validation_alias="RESPONSE_RETRY_DELAY")
    
    # Approval
    APPROVAL_TIMEOUT_SECONDS: int = Field(default=3600, validation_alias="APPROVAL_TIMEOUT_SECONDS")
    APPROVAL_MIN_APPROVERS: int = Field(default=1, validation_alias="APPROVAL_MIN_APPROVERS")
    
    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: str = Field(default="http://otel-collector:4317", validation_alias="OTEL_EXPORTER_OTLP_ENDPOINT")
    OTEL_SERVICE_NAME: str = Field(default="response-orchestrator", validation_alias="OTEL_SERVICE_NAME")
    OTEL_EXPORTER_OTLP_INSECURE: bool = Field(default=True, validation_alias="OTEL_EXPORTER_OTLP_INSECURE")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", validation_alias="LOG_FORMAT")
    
    # Development
    DEV_MODE: bool = Field(default=True, validation_alias="DEV_MODE")
    DRY_RUN: bool = Field(default=True, validation_alias="DRY_RUN")
    
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