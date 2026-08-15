"""
Configuration settings for AegisForge API Gateway.
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
    
    # API
    API_HOST: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    API_PORT: int = Field(default=8000, validation_alias="API_PORT")
    API_WORKERS: int = Field(default=4, validation_alias="API_WORKERS")
    API_CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:3001", validation_alias="API_CORS_ORIGINS")
    
    # Database
    POSTGRES_HOST: str = Field(default="postgres", validation_alias="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, validation_alias="POSTGRES_PORT")
    POSTGRES_DB: str = Field(default="aegisforge", validation_alias="POSTGRES_DB")
    POSTGRES_USER: str = Field(default="aegisforge", validation_alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="changeme_dev_only", validation_alias="POSTGRES_PASSWORD")
    POSTGRES_POOL_SIZE: int = Field(default=20, validation_alias="POSTGRES_POOL_SIZE")
    POSTGRES_MAX_OVERFLOW: int = Field(default=10, validation_alias="POSTGRES_MAX_OVERFLOW")
    
    # Redis
    REDIS_HOST: str = Field(default="redis", validation_alias="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, validation_alias="REDIS_PORT")
    REDIS_DB: int = Field(default=0, validation_alias="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, validation_alias="REDIS_PASSWORD")
    
    # Redpanda/Kafka
    REDPANDA_BROKERS: str = Field(default="redpanda:9092", validation_alias="REDPANDA_BROKERS")
    REDPANDA_TOPIC_EVENTS: str = Field(default="security-events", validation_alias="REDPANDA_TOPIC_EVENTS")
    REDPANDA_TOPIC_ALERTS: str = Field(default="security-alerts", validation_alias="REDPANDA_TOPIC_ALERTS")
    REDPANDA_TOPIC_INCIDENTS: str = Field(default="security-incidents", validation_alias="REDPANDA_TOPIC_INCIDENTS")
    REDPANDA_TOPIC_AUDIT: str = Field(default="audit-logs", validation_alias="REDPANDA_TOPIC_AUDIT")
    
    # Qdrant
    QDRANT_HOST: str = Field(default="qdrant", validation_alias="QDRANT_HOST")
    QDRANT_PORT: int = Field(default=6333, validation_alias="QDRANT_PORT")
    
    # MinIO
    MINIO_ENDPOINT: str = Field(default="minio:9000", validation_alias="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", validation_alias="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(default="minioadmin", validation_alias="MINIO_SECRET_KEY")
    MINIO_BUCKET_EVIDENCE: str = Field(default="aegisforge-evidence", validation_alias="MINIO_BUCKET_EVIDENCE")
    MINIO_BUCKET_ARTIFACTS: str = Field(default="aegisforge-artifacts", validation_alias="MINIO_BUCKET_ARTIFACTS")
    MINIO_USE_SSL: bool = Field(default=False, validation_alias="MINIO_USE_SSL")
    
    # Ollama
    OLLAMA_HOST: str = Field(default="ollama", validation_alias="OLLAMA_HOST")
    OLLAMA_PORT: int = Field(default=11434, validation_alias="OLLAMA_PORT")
    OLLAMA_MODEL: str = Field(default="llama3.2:1b", validation_alias="OLLAMA_MODEL")
    
    # Authentication
    JWT_SECRET_KEY: str = Field(default="dev-secret-change-in-production", validation_alias="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    JWT_EXPIRY_MINUTES: int = Field(default=60, validation_alias="JWT_EXPIRY_MINUTES")
    JWT_REFRESH_EXPIRY_DAYS: int = Field(default=7, validation_alias="JWT_REFRESH_EXPIRY_DAYS")
    
    # OIDC (Keycloak)
    OIDC_ISSUER_URL: Optional[str] = Field(default=None, validation_alias="OIDC_ISSUER_URL")
    OIDC_CLIENT_ID: Optional[str] = Field(default=None, validation_alias="OIDC_CLIENT_ID")
    OIDC_CLIENT_SECRET: Optional[str] = Field(default=None, validation_alias="OIDC_CLIENT_SECRET")
    OIDC_REDIRECT_URI: Optional[str] = Field(default=None, validation_alias="OIDC_REDIRECT_URI")
    
    # Keycloak
    KEYCLOAK_ADMIN: str = Field(default="admin", validation_alias="KEYCLOAK_ADMIN")
    KEYCLOAK_ADMIN_PASSWORD: str = Field(default="admin", validation_alias="KEYCLOAK_ADMIN_PASSWORD")
    KEYCLOAK_DB_VENDOR: str = Field(default="postgres", validation_alias="KEYCLOAK_DB_VENDOR")
    KEYCLOAK_DB_ADDR: str = Field(default="postgres", validation_alias="KEYCLOAK_DB_ADDR")
    KEYCLOAK_DB_DATABASE: str = Field(default="keycloak", validation_alias="KEYCLOAK_DB_DATABASE")
    KEYCLOAK_DB_USER: str = Field(default="keycloak", validation_alias="KEYCLOAK_DB_USER")
    KEYCLOAK_DB_PASSWORD: str = Field(default="keycloak", validation_alias="KEYCLOAK_DB_PASSWORD")
    
    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: str = Field(default="http://otel-collector:4317", validation_alias="OTEL_EXPORTER_OTLP_ENDPOINT")
    OTEL_SERVICE_NAME: str = Field(default="api-gateway", validation_alias="OTEL_SERVICE_NAME")
    OTEL_EXPORTER_OTLP_INSECURE: bool = Field(default=True, validation_alias="OTEL_EXPORTER_OTLP_INSECURE")
    
    PROMETHEUS_REMOTE_WRITE_URL: Optional[str] = Field(default=None, validation_alias="PROMETHEUS_REMOTE_WRITE_URL")
    GRAFANA_ADMIN_USER: str = Field(default="admin", validation_alias="GRAFANA_ADMIN_USER")
    GRAFANA_ADMIN_PASSWORD: str = Field(default="admin", validation_alias="GRAFANA_ADMIN_PASSWORD")
    
    # Falco
    FALCO_ENABLED: bool = Field(default=True, validation_alias="FALCO_ENABLED")
    FALCO_RULES_PATH: str = Field(default="/etc/falco/rules", validation_alias="FALCO_RULES_PATH")
    
    # Development
    DEV_MODE: bool = Field(default=True, validation_alias="DEV_MODE")
    DEV_SKIP_AUTH: bool = Field(default=False, validation_alias="DEV_SKIP_AUTH")
    DEV_SEED_DATA: bool = Field(default=True, validation_alias="DEV_SEED_DATA")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def REDPANDA_BOOTSTRAP_SERVERS(self) -> str:
        return self.REDPANDA_BROKERS
    
    @property
    def OLLAMA_BASE_URL(self) -> str:
        return f"http://{self.OLLAMA_HOST}:{self.OLLAMA_PORT}"
    
    @property
    def QDRANT_URL(self) -> str:
        return f"http://{self.QDRANT_HOST}:{self.QDRANT_PORT}"
    
    @property
    def MINIO_URL(self) -> str:
        scheme = "https" if self.MINIO_USE_SSL else "http"
        return f"{scheme}://{self.MINIO_ENDPOINT}"


@lru_cache()
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()