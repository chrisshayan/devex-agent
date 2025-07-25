"""
Settings and configuration for DevEx Ambient Agent
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    host: str = "localhost"
    port: int = 8000
    debug: bool = True
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    llm_model: str = "gpt-3.5-turbo"
    llm_temperature: float = 0.1
    
    # Ambient Agent Configuration
    ambient_check_interval: int = 300  # 5 minutes
    max_events_per_developer: int = 1000
    event_retention_hours: int = 168  # 1 week
    
    # Storage Configuration
    database_url: str = "sqlite:///./devex_agent.db"
    vector_db_path: str = "./data/vector_store"
    
    # Plugin Communication
    plugin_auth_token: Optional[str] = None
    cors_origins: list = ["*"]
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get settings instance (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings 