"""
Request coalescing utility.

Ensures multiple concurrent identical requests (same key) execute the underlying
call exactly once and all callers receive the same result. Designed for async
callers (FastAPI/asyncio).

Usage:
    coalescer = RequestCoalescer()
    result = await coalescer.coalesce("news:INFY.NS:10", fetch_news_coroutine)

"""
from typing import Any, Callable, Dict
import asyncio


class RequestCoalescer:
    """Coalesce concurrent requests keyed by a string.

    Maintains an in-memory map of key -> asyncio.Future for in-progress
    operations. When a request for the same key arrives while another is
    running, callers await the same future and receive the same result.
    """

    def __init__(self):
        # Map key -> asyncio.Future
        self._in_progress: Dict[str, asyncio.Future] = {}
        # Protects the _in_progress map
        self._lock = asyncio.Lock()

    async def coalesce(self, key: str, coro_callable: Callable[..., Any], *args, **kwargs) -> Any:
        """Run coro_callable(*args, **kwargs) but coalesce concurrent runs by key.

        coro_callable must be awaitable (an async function or coroutine).
        """
        # Fast path: avoid acquiring lock if key exists (but need to check under lock to be safe)
        async with self._lock:
            fut = self._in_progress.get(key)
            if fut is None:
                # Create future and mark as in-progress
                fut = asyncio.get_event_loop().create_future()
                self._in_progress[key] = fut
                is_owner = True
            else:
                is_owner = False

        if not is_owner:
            # Another coroutine is executing; wait for its result
            try:
                result = await fut
                return result
            except Exception:
                # If the original raised, re-raise to callers
                raise

        # Owner executes the coroutine and sets the future
        try:
            result = await coro_callable(*args, **kwargs)
            # Set result for waiting callers
            fut.set_result(result)
            return result
        except Exception as e:
            fut.set_exception(e)
            raise
        finally:
            # Clean up in-progress map
            async with self._lock:
                # Only delete if it's still the same future (safety)
                existing = self._in_progress.get(key)
                if existing is fut:
                    del self._in_progress[key]
