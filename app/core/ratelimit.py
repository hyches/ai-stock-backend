import redis.asyncio as redis
from fastapi import Request, HTTPException
from app.core.config import settings
from typing import Callable, Awaitable

async def redis_rate_limiter(request: Request, call_next: Callable[[Request], Awaitable[None]]):
    """
    Asynchronous middleware for rate limiting using Redis.
    """
    if settings.ENVIRONMENT == "development":
        return await call_next(request)

    r = await redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

    # Use user's IP or a user identifier if available
    client_id = request.client.host

    # Define rate limits
    limit = 100  # requests
    window = 60  # seconds

    # Use a pipeline to ensure atomic operations
    pipe = r.pipeline()
    pipe.incr(client_id)
    pipe.expire(client_id, window)

    try:
        count, _ = await pipe.execute()
    except redis.ConnectionError as e:
        # If Redis is unavailable, bypass rate limiting
        # You might want to log this error
        return await call_next(request)

    if count > limit:
        raise HTTPException(status_code=429, detail="Too Many Requests")

    return await call_next(request)
