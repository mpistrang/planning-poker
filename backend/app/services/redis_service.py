import redis
import json
import logging
from typing import Optional, Any
from app.config import settings

logger = logging.getLogger(__name__)


class RedisService:
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self._connect()

    def _connect(self):
        """Connect to Redis with retry logic"""
        try:
            # Support both URL format (Render) and host/port format (local)
            if settings.redis_url:
                self.client = redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_keepalive=True,
                    retry_on_timeout=True
                )
                logger.info(f"Connected to Redis using URL")
            else:
                self.client = redis.Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_keepalive=True,
                    retry_on_timeout=True
                )
                logger.info(f"Connected to Redis at {settings.redis_host}:{settings.redis_port}")
            # Test connection
            self.client.ping()
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis with optional TTL"""
        try:
            json_value = json.dumps(value)
            if ttl:
                self.client.setex(key, ttl, json_value)
            else:
                self.client.set(key, json_value)
            return True
        except Exception as e:
            logger.error(f"Error setting key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Error checking existence of key {key}: {e}")
            return False

    def get_keys(self, pattern: str) -> list:
        """Get all keys matching pattern"""
        try:
            return self.client.keys(pattern)
        except Exception as e:
            logger.error(f"Error getting keys with pattern {pattern}: {e}")
            return []

    def health_check(self) -> bool:
        """Check if Redis is healthy"""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False


# Global Redis service instance
redis_service = RedisService()
