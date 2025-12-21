from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Redis connection - supports both URL format (Render) and host/port format (local)
    redis_url: Optional[str] = None
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    room_ttl: int = 86400  # 24 hours
    cors_origins: str = "http://localhost:5173"
    environment: str = "development"
    log_level: str = "INFO"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
