from redis import Redis
from app.core.config import settings

redis_cache = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
)

def cache(expire: int = 3600):
    def decorator(func):
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            result = redis_cache.get(key)
            if result:
                return result
            result = func(*args, **kwargs)
            redis_cache.set(key, result, ex=expire)
            return result
        return wrapper
    return decorator
