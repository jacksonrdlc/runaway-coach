from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Anthropic Claude Configuration
    ANTHROPIC_API_KEY: str
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    
    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_KEY: str
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_SECRET_KEY: str
    API_ALGORITHM: str = "HS256"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Swift App Integration
    SWIFT_APP_BASE_URL: str = "http://localhost:3000"
    SWIFT_APP_API_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings (singleton)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings