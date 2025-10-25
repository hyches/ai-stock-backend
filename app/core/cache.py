"""
Redis-based caching utilities for the AI Stock Portfolio Platform Backend.

This module provides a Cache class for interacting with Redis, including methods for get/set/delete,
pattern clearing, and a decorator for caching function responses.
"""
import json
from functools import wraps
from typing import Any, Optional, Callable
import redis
from app.core.config import settings

# Initialize Redis connection
redis_cache = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

class Cache:
    """
    Cache utility class for Redis operations.

    Provides methods to get, set, delete, and clear cache entries, as well as a decorator for caching function responses.
    """
    def __init__(self, client: redis.Redis):
        """
        Initialize the Cache instance.

        Args:
            client (redis.Redis): Redis client instance.
        """
        self.client = client

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache by key.

        Args:
            key (str): Cache key.
        Returns:
            Optional[Any]: Cached value or None if not found.
        """
        value = self.client.get(key)
        if value is not None:
            try:
                return json.loads(value)
            except Exception:
                return value
        return None

    def set(self, key: str, value: Any, ttl: int = None):
        """
        Set a value in the cache.

        Args:
            key (str): Cache key.
            value (Any): Value to cache.
            ttl (int, optional): Time-to-live in seconds. Defaults to None (no expiration).
        """
        value = json.dumps(value)
        if ttl:
            self.client.setex(key, ttl, value)
        else:
            self.client.set(key, value)

    def delete(self, key: str):
        """
        Delete a value from the cache by key.

        Args:
            key (str): Cache key.
        """
        self.client.delete(key)

    def clear_pattern(self, pattern: str):
        """
        Clear all cache entries matching a pattern.

        Args:
            pattern (str): Pattern to match cache keys.
        """
        for key in self.client.scan_iter(match=pattern):
            self.client.delete(key)

    def clear(self):
        """
        Clear the entire cache database.
        """
        self.client.flushdb()

    def cache_response(self, ttl: int = 60, key_prefix: str = "cache"):  # Decorator
        """
        Decorator to cache the response of a function in Redis.

        Args:
            ttl (int): Time-to-live for the cache entry in seconds. Defaults to 60.
            key_prefix (str): Prefix for the cache key. Defaults to "cache".
        Returns:
            Callable: Decorator function.
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = f"{key_prefix}:{func.__name__}:{json.dumps(args, default=str)}:{json.dumps(kwargs, default=str)}"
                cached = self.get(key)
                if cached is not None:
                    return cached
                result = func(*args, **kwargs)
                self.set(key, result, ttl)
                return result
            return wrapper
        return decorator

cache = Cache(redis_cache)

# For direct decorator usage
cache_response = cache.cache_response