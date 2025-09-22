"""Application configuration management."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "Humanoid Robot Insurance Platform"
    version: str = "0.1.0"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False)
    
    # Database
    database_url: str = Field(alias="DATABASE_URL")
    
    # Security
    secret_key: str = Field(alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    
    # Azure
    azure_client_id: Optional[str] = Field(default=None, alias="AZURE_CLIENT_ID")
    azure_client_secret: Optional[str] = Field(default=None, alias="AZURE_CLIENT_SECRET")
    azure_tenant_id: Optional[str] = Field(default=None, alias="AZURE_TENANT_ID")
    azure_keyvault_url: Optional[str] = Field(default=None, alias="AZURE_KEYVAULT_URL")
    
    # External APIs
    robot_diagnostics_api_url: str = Field(
        default="https://api.robotdiagnostics.com",
        alias="ROBOT_DIAGNOSTICS_API_URL"
    )
    payment_processor_api_url: str = Field(
        default="https://api.paymentprocessor.com",
        alias="PAYMENT_PROCESSOR_API_URL"
    )
    regulatory_api_url: str = Field(
        default="https://api.regulatory.com",
        alias="REGULATORY_API_URL"
    )
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    azure_application_insights_connection_string: Optional[str] = Field(
        default=None,
        alias="AZURE_APPLICATION_INSIGHTS_CONNECTION_STRING"
    )
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment.lower() == "testing"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()