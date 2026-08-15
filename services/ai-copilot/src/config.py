"""
Configuration settings for AI Copilot.
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
    PORT: int = Field(default=8003, validation_alias="PORT")
    WORKERS: int = Field(default=1, validation_alias="WORKERS")
    
    # Database
    POSTGRES_HOST: str = Field(default="postgres", validation_alias="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, validation_alias="POSTGRES_PORT")
    POSTGRES_DB: str = Field(default="aegisforge", validation_alias="POSTGRES_DB")
    POSTGRES_USER: str = Field(default="aegisforge", validation_alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="changeme_dev_only", validation_alias="POSTGRES_PASSWORD")
    POSTGRES_POOL_SIZE: int = Field(default=10, validation_alias="POSTGRES_POOL_SIZE")
    POSTGRES_MAX_OVERFLOW: int = Field(default=5, validation_alias="POSTGRES_MAX_OVERFLOW")
    
    # Ollama
    OLLAMA_HOST: str = Field(default="ollama", validation_alias="OLLAMA_HOST")
    OLLAMA_PORT: int = Field(default=11434, validation_alias="OLLAMA_PORT")
    OLLAMA_MODEL: str = Field(default="llama3.2:1b", validation_alias="OLLAMA_MODEL")
    OLLAMA_NUM_PARALLEL: int = Field(default=2, validation_alias="OLLAMA_NUM_PARALLEL")
    OLLAMA_NUM_THREAD: int = Field(default=4, validation_alias="OLLAMA_NUM_THREAD")
    OLLAMA_FLASH_ATTENTION: bool = Field(default=True, validation_alias="OLLAMA_FLASH_ATTENTION")
    OLLAMA_NUM_CTX: int = Field(default=4096, validation_alias="OLLAMA_NUM_CTX")
    OLLAMA_TEMPERATURE: float = Field(default=0.1, validation_alias="OLLAMA_TEMPERATURE")
    
    # Embeddings
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2", validation_alias="EMBEDDING_MODEL")
    EMBEDDING_BATCH_SIZE: int = Field(default=32, validation_alias="EMBEDDING_BATCH_SIZE")
    EMBEDDING_NUM_THREADS: int = Field(default=4, validation_alias="EMBEDDING_NUM_THREADS")
    
    # Qdrant
    QDRANT_HOST: str = Field(default="qdrant", validation_alias="QDRANT_HOST")
    QDRANT_PORT: int = Field(default=6333, validation_alias="QDRANT_PORT")
    QDRANT_COLLECTION: str = Field(default="security-knowledge", validation_alias="QDRANT_COLLECTION")
    QDRANT_VECTOR_SIZE: int = Field(default=384, validation_alias="QDRANT_VECTOR_SIZE")
    QDRANT_HNSW_M: int = Field(default=16, validation_alias="QDRANT_HNSW_M")
    QDRANT_HNSW_EF_CONSTRUCT: int = Field(default=100, validation_alias="QDRANT_HNSW_EF_CONSTRUCT")
    QDRANT_HNSW_EF_SEARCH: int = Field(default=128, validation_alias="QDRANT_HNSW_EF_SEARCH")
    
    # Database
    POSTGRES_HOST: str = Field(default="postgres", validation_alias="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, validation_alias="POSTGRES_PORT")
    POSTGRES_DB: str = Field(default="aegisforge", validation_alias="POSTGRES_DB")
    POSTGRES_USER: str = Field(default="aegisforge", validation_alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="changeme_dev_only", validation_alias="POSTGRES_PASSWORD")
    POSTGRES_POOL_SIZE: int = Field(default=10, validation_alias="POSTGRES_POOL_SIZE")
    POSTGRES_MAX_OVERFLOW: int = Field(default=5, validation_alias="POSTGRES_MAX_OVERFLOW")
    
    # AI Safety
    AI_REDACT_SECRETS: bool = Field(default=True, validation_alias="AI_REDACT_SECRETS")
    AI_REDACT_PII: bool = Field(default=True, validation_alias="AI_REDACT_PII")
    AI_REDACT_IPS: bool = Field(default=True, validation_alias="AI_REDACT_IPS")
    AI_REDACT_TOKENS: bool = Field(default=True, validation_alias="AI_REDACT_TOKENS")
    AI_MAX_TOKENS: int = Field(default=2048, validation_alias="AI_MAX_TOKENS")
    AI_TEMPERATURE: float = Field(default=0.1, validation_alias="AI_TEMPERATURE")
    AI_SYSTEM_PROMPT_STRICT: bool = Field(default=True, validation_alias="AI_SYSTEM_PROMPT_STRICT")
    
    # Indexing
    INDEX_BATCH_SIZE: int = Field(default=100, validation_alias="INDEX_BATCH_SIZE")
    INDEX_INTERVAL_SECONDS: int = Field(default=300, validation_alias="INDEX_INTERVAL_SECONDS")
    
    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: str = Field(default="http://otel-collector:4317", validation_alias="OTEL_EXPORTER_OTLP_ENDPOINT")
    OTEL_SERVICE_NAME: str = Field(default="ai-copilot", validation_alias="OTEL_SERVICE_NAME")
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
    def OLLAMA_BASE_URL(self) -> str:
        return f"http://{self.OLLAMA_HOST}:{self.OLLAMA_PORT}"
    
    @property
    def QDRANT_URL(self) -> str:
        return f"http://{self.QDRANT_HOST}:{self.QDRANT_PORT}"


@lru_cache()
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()