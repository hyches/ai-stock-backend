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
    def __init__(self, client: redis.Redis):
        self.client = client

    def get(self, key: str) -> Optional[Any]:
        value = self.client.get(key)
        if value is not None:
            try:
                return json.loads(value)
            except Exception:
                return value
        return None

    def set(self, key: str, value: Any, ttl: int = None):
        value = json.dumps(value)
        if ttl:
            self.client.setex(key, ttl, value)
        else:
            self.client.set(key, value)

    def delete(self, key: str):
        self.client.delete(key)

    def clear_pattern(self, pattern: str):
        for key in self.client.scan_iter(match=pattern):
            self.client.delete(key)

    def clear(self):
        self.client.flushdb()

    def cache_response(self, ttl: int = 60, key_prefix: str = "cache"):  # Decorator
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