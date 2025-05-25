import json
import redis
from typing import Any, Optional
from app.core.config import settings

class RedisCache:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
        self.default_ttl = 3600  # 1 hour

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting from cache: {str(e)}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            return self.redis.setex(
                key,
                ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Error deleting from cache: {str(e)}")
            return False

    async def clear(self) -> bool:
        """Clear all cache"""
        try:
            return bool(self.redis.flushdb())
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False

redis_cache = RedisCache() 