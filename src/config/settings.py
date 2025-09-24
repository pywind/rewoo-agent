"""
Configuration management for the ReWOO application.
"""

from typing import Dict, Any, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)


class ReWOOSettings(BaseSettings):
    """ReWOO engine configuration."""

    max_iterations: int = Field(default=10, env="MAX_ITERATIONS")
    streaming_enabled: bool = Field(default=True, env="STREAMING_ENABLED")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

class ModelSettings(BaseSettings):
    """Model configuration."""

    model_name: str = Field(default="gpt-4", env="MODEL_NAME")
    model_provider: str = Field(default="openai", env="MODEL_PROVIDER")
    temperature: float = Field(default=0.1, env="TEMPERATURE")


class ToolSettings(BaseSettings):
    """Tool configuration."""

    enable_search_tool: bool = Field(default=True, env="ENABLE_SEARCH_TOOL")
    enable_calculator_tool: bool = Field(default=True, env="ENABLE_CALCULATOR_TOOL")
    enable_wikipedia_tool: bool = Field(default=True, env="ENABLE_WIKIPEDIA_TOOL")
    enable_weather_tool: bool = Field(default=True, env="ENABLE_WEATHER_TOOL")

    class Config:
        env_prefix = "TOOL_"


class APISettings(BaseSettings):
    """API server configuration."""

    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=False, env="DEBUG")
    app_name: str = Field(default="rewoo", env="APP_NAME")
    prefix: str = Field(default="/api/v1", env="API_PREFIX")
    class Config:
        env_prefix = "API_"


class TaskSettings(BaseSettings):
    """Task execution configuration."""

    default_timeout: int = Field(default=300, env="DEFAULT_TASK_TIMEOUT")
    max_concurrent_tasks: int = Field(default=5, env="MAX_CONCURRENT_TASKS")

    class Config:
        env_prefix = "TASK_"


class RedisSettings(BaseSettings):
    """Redis configuration."""

    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    db: int = Field(default=0, env="REDIS_DB")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    key_prefix: str = Field(default="rewoo:active_tasks:", env="REDIS_KEY_PREFIX")
    ttl_seconds: int = Field(default=3600, env="REDIS_TTL_SECONDS")  # 1 hour default TTL

    class Config:
        env_prefix = "REDIS_"


class Settings:
    """Main application settings."""

    def __init__(self):
        self.rewoo = ReWOOSettings()
        self.model = ModelSettings()
        self.tools = ToolSettings()
        self.api = APISettings()
        self.tasks = TaskSettings()
        self.redis = RedisSettings()

    def get_enabled_tools(self) -> Dict[str, bool]:
        """Get the enabled tools configuration."""
        return {
            "search": self.tools.enable_search_tool,
            "calculator": self.tools.enable_calculator_tool,
            "wikipedia": self.tools.enable_wikipedia_tool,
            "weather": self.tools.enable_weather_tool,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "rewoo": self.rewoo.model_dump(),
            "model": self.model.model_dump(),
            "tools": self.tools.model_dump(),
            "api": self.api.model_dump(),
            "tasks": self.tasks.model_dump(),
            "redis": self.redis.model_dump(),
        }


# Global settings instance
settings = Settings()
