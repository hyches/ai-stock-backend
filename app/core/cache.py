import json
import redis
from typing import Any, Optional
from app.config import Settings
settings = Settings()

class RedisCache:
    """
    RedisCache class provides an interface for interacting with a Redis cache, enabling set, get, delete, and clear operations with optional time-to-live (TTL) management.
    Parameters:
        - None during initialization. The class utilizes the Redis URL from settings to establish a connection.
    Processing Logic:
        - Uses JSON serialization/deserialization to handle cache values for flexibility in storing complex types.
        - Default TTL for stored keys is set to 3600 seconds (1 hour) unless specified otherwise during the set operation.
        - Error logging is implemented to record any issues during operations, aiding in debugging and monitoring.
        - Redis commands are wrapped in asynchronous operations to support non-blocking I/O operations.
    Examples:
        - To store a value: `await cache.set('key', {'data': 'value'})`
        - To retrieve a value: `result = await cache.get('key')`
        - To delete a key: `await cache.delete('key')`
        - To clear the cache: `await cache.clear()`
    """
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