"""
Configuration settings for ReconVault backend application.

This module contains all configuration settings using Pydantic settings
for environment variable management and validation.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application Settings
    APP_NAME: str = "ReconVault API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # API Settings
    API_PREFIX: str = "/api"
    API_TITLE: str = "ReconVault API"
    API_VERSION: str = "0.1.0"
    
    # CORS Settings
    CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str) and v:
            return [origin.strip() for origin in v.split(",")]
        elif isinstance(v, list):
            return v
        elif isinstance(v, str) and v == "*":
            return ["*"]
        return ["*"]
    
    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "reconvault"
    POSTGRES_PASSWORD: str = "reconvault"
    POSTGRES_DB: str = "reconvault"
    POSTGRES_PORT: int = 5432
    
    # Database URL construction
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        """Construct PostgreSQL database URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Neo4j Settings
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "reconvault"
    NEO4J_DATABASE: str = "reconvault"
    
    # Redis Settings (for caching and sessions)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # WebSocket Settings
    WEBSOCKET_CONNECTIONS_LIMIT: int = 100
    WEBSOCKET_KEEPALIVE_INTERVAL: int = 30
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # Intelligence Engine Settings
    MAX_ENTITIES_PER_TARGET: int = 1000
    GRAPH_DEPTH_LIMIT: int = 5
    RISK_SCORE_THRESHOLD: float = 0.7
    
    # Pagination Settings
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000
    DEFAULT_OFFSET: int = 0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()