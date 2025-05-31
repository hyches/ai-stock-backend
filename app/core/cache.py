import redis
from typing import Optional, Any, Callable, Awaitable
import json
import logging
from app.core.config import settings
from functools import wraps
import pickle

logger = logging.getLogger(__name__)

# Initialize Redis connection pool
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
    max_connections=50,
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True
)

# Create Redis client
redis_client = redis.Redis(connection_pool=redis_pool)

def get_redis() -> redis.Redis:
    """
    Get Redis client with connection management.
    Returns:
        redis.Redis: Redis client instance.
    Raises:
        redis.ConnectionError: If connection fails.
    """
    try:
        return redis_client
    except redis.ConnectionError as e:
        logger.error("Redis connection error: %s", str(e))
        raise

def cache_key(prefix: str, *args: Any, **kwargs: Any) -> str:
    """
    Generate cache key from prefix and arguments.
    Args:
        prefix (str): Key prefix.
        *args: Positional arguments.
        **kwargs: Keyword arguments.
    Returns:
        str: Generated cache key.
    """
    key_parts = [prefix]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)

def cache(ttl: int = 300, prefix: str = "cache") -> Callable:
    """
    Cache decorator with TTL and prefix.
    Args:
        ttl (int): Time to live for cache in seconds.
        prefix (str): Key prefix for cache.
    Returns:
        Callable: Decorator function.
    """
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key
            key = cache_key(prefix, func.__name__, *args, **kwargs)
            try:
                # Try to get from cache
                cached_value = redis_client.get(key)
                if cached_value:
                    return pickle.loads(cached_value)
                # If not in cache, execute function
                result = await func(*args, **kwargs)
                # Cache result
                redis_client.setex(
                    key,
                    ttl,
                    pickle.dumps(result)
                )
                return result
            except redis.RedisError as e:
                logger.error("Redis error: %s", str(e))
                # Fallback to function execution
                return await func(*args, **kwargs)
        return wrapper
    return decorator

class CacheManager:
    """
    Cache management with error handling and monitoring.
    Provides methods to get, set, delete, and clear cache entries.
    """
    def __init__(self, redis_client: redis.Redis) -> None:
        """
        Initialize CacheManager.
        Args:
            redis_client (redis.Redis): Redis client instance.
        """
        self.redis = redis_client

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        Args:
            key (str): Cache key.
        Returns:
            Optional[Any]: Cached value or None if not found or error.
        """
        try:
            value = self.redis.get(key)
            return pickle.loads(value) if value else None
        except redis.RedisError as e:
            logger.error("Cache get error: %s", str(e))
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set value in cache with TTL.
        Args:
            key (str): Cache key.
            value (Any): Value to cache.
            ttl (int): Time to live in seconds.
        Returns:
            bool: True if set successfully, False otherwise.
        """
        try:
            return self.redis.setex(
                key,
                ttl,
                pickle.dumps(value)
            )
        except redis.RedisError as e:
            logger.error("Cache set error: %s", str(e))
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        Args:
            key (str): Cache key.
        Returns:
            bool: True if deleted, False otherwise.
        """
        try:
            return bool(self.redis.delete(key))
        except redis.RedisError as e:
            logger.error("Cache delete error: %s", str(e))
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear cache entries matching pattern.
        Args:
            pattern (str): Pattern to match cache keys.
        Returns:
            int: Number of keys deleted.
        """
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except redis.RedisError as e:
            logger.error("Cache clear pattern error: %s", str(e))
            return 0

# Initialize cache manager
cache_manager = CacheManager(redis_client) 