"""
Simple token-bucket rate limiter and circuit breaker per provider.

This is a lightweight, in-memory implementation suitable for development.
It provides:
 - RateLimiter: per-provider token buckets with refill interval (seconds)
 - CircuitBreaker: tracks consecutive failures and opens for a cool-down period

Usage:
    rl = RateLimiter({"alphavantage": (5, 60), "finnhub": (60, 60)})
    if rl.allow("alphavantage"):
        # call provider
    else:
        # skip provider (rate limited)

"""
import time
import asyncio
from typing import Dict, Tuple


class TokenBucket:
    def __init__(self, capacity: int, refill_interval: int):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_interval = refill_interval
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def consume(self) -> bool:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            # Refill tokens proportionally to time passed
            if elapsed >= self.refill_interval:
                # refill fully per interval
                self.tokens = self.capacity
                self.last_refill = now

            if self.tokens > 0:
                self.tokens -= 1
                return True
            return False


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_seconds = recovery_seconds
        self.failures = 0
        self.opened_at = None

    def record_success(self):
        self.failures = 0
        self.opened_at = None

    def record_failure(self):
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.opened_at = time.monotonic()

    def is_open(self) -> bool:
        if self.opened_at is None:
            return False
        if (time.monotonic() - self.opened_at) >= self.recovery_seconds:
            # reset
            self.failures = 0
            self.opened_at = None
            return False
        return True


class RateLimiter:
    """Manage token buckets and circuit breakers per provider name."""

    def __init__(self, config: Dict[str, Tuple[int, int]] = None):
        # config: provider -> (capacity, refill_interval_seconds)
        self.buckets: Dict[str, TokenBucket] = {}
        self.breakers: Dict[str, CircuitBreaker] = {}
        config = config or {}
        for name, (cap, interval) in config.items():
            self.buckets[name.lower()] = TokenBucket(cap, interval)
            self.breakers[name.lower()] = CircuitBreaker()

    async def allow(self, provider_name: str) -> bool:
        name = provider_name.lower()
        cb = self.breakers.get(name)
        if cb and cb.is_open():
            return False
        bucket = self.buckets.get(name)
        if bucket:
            return await bucket.consume()
        # If no bucket configured, allow by default
        return True

    def record_success(self, provider_name: str):
        name = provider_name.lower()
        cb = self.breakers.get(name)
        if cb:
            cb.record_success()

    def record_failure(self, provider_name: str):
        name = provider_name.lower()
        cb = self.breakers.get(name)
        if cb:
            cb.record_failure()
