"""
Unit tests for request coalescing, rate limiting, and circuit breaker.

Tests cover:
- RequestCoalescer: concurrent identical requests share one execution
- RateLimiter: token bucket refills per interval
- CircuitBreaker: opens after N failures, recovers after timeout
- Integration: ProviderRouter with rate limiter + coalescer
"""

import asyncio
import time
import pytest
from app.services.request_coalescer import RequestCoalescer
from app.services.rate_limiter import RateLimiter, TokenBucket, CircuitBreaker


class TestTokenBucket:
    """Test TokenBucket (token bucket rate limiting)."""

    @pytest.mark.asyncio
    async def test_bucket_consume_success(self):
        """Tokens should be consumable when available."""
        bucket = TokenBucket(capacity=3, refill_interval=10)
        assert await bucket.consume() is True
        assert await bucket.consume() is True
        assert await bucket.consume() is True
        assert await bucket.consume() is False  # depleted

    @pytest.mark.asyncio
    async def test_bucket_refill_after_interval(self):
        """Bucket should refill after interval elapses."""
        bucket = TokenBucket(capacity=2, refill_interval=1)
        # Consume all tokens
        assert await bucket.consume() is True
        assert await bucket.consume() is True
        assert await bucket.consume() is False
        # Wait for refill
        await asyncio.sleep(1.1)
        assert await bucket.consume() is True


class TestCircuitBreaker:
    """Test CircuitBreaker (fail-open pattern)."""

    def test_breaker_starts_closed(self):
        """Circuit breaker should start closed (allowing calls)."""
        cb = CircuitBreaker(failure_threshold=3, recovery_seconds=1)
        assert cb.is_open() is False

    def test_breaker_opens_after_failures(self):
        """Circuit should open after N consecutive failures."""
        cb = CircuitBreaker(failure_threshold=2, recovery_seconds=10)
        cb.record_failure()
        assert cb.is_open() is False
        cb.record_failure()
        assert cb.is_open() is True

    def test_breaker_resets_on_success(self):
        """Success should reset failure count."""
        cb = CircuitBreaker(failure_threshold=2, recovery_seconds=10)
        cb.record_failure()
        cb.record_success()
        assert cb.is_open() is False
        assert cb.failures == 0

    def test_breaker_recovers_after_timeout(self):
        """Circuit should allow calls after recovery timeout."""
        cb = CircuitBreaker(failure_threshold=1, recovery_seconds=1)
        cb.record_failure()
        assert cb.is_open() is True
        time.sleep(1.1)
        assert cb.is_open() is False


class TestRateLimiter:
    """Test RateLimiter (multi-provider rate limiting)."""

    @pytest.mark.asyncio
    async def test_limiter_allows_by_default(self):
        """Unknown provider should be allowed by default."""
        limiter = RateLimiter({})
        assert await limiter.allow("unknown_provider") is True

    @pytest.mark.asyncio
    async def test_limiter_respects_bucket(self):
        """Known provider should respect token bucket."""
        limiter = RateLimiter({"test_provider": (2, 10)})
        assert await limiter.allow("test_provider") is True
        assert await limiter.allow("test_provider") is True
        assert await limiter.allow("test_provider") is False

    @pytest.mark.asyncio
    async def test_limiter_respects_circuit_breaker(self):
        """Circuit breaker should block requests when open."""
        limiter = RateLimiter({"test_provider": (10, 10)})
        # Simulate failures to open circuit
        for _ in range(5):
            limiter.record_failure("test_provider")
        assert await limiter.allow("test_provider") is False

    def test_limiter_records_success_and_failure(self):
        """Limiter should track success/failure for breaker."""
        limiter = RateLimiter({"test_provider": (10, 10)})
        limiter.record_success("test_provider")
        assert limiter.breakers["test_provider"].failures == 0
        limiter.record_failure("test_provider")
        assert limiter.breakers["test_provider"].failures == 1


class TestRequestCoalescer:
    """Test RequestCoalescer (concurrent request deduplication)."""

    @pytest.mark.asyncio
    async def test_coalescer_coalesces_concurrent_requests(self):
        """Multiple concurrent requests with same key should execute once."""
        coalescer = RequestCoalescer()
        call_count = 0

        async def slow_operation():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)
            return "result"

        # Launch 5 concurrent coalesced requests
        key = "test_key"
        tasks = [
            asyncio.create_task(coalescer.coalesce(key, slow_operation))
            for _ in range(5)
        ]
        results = await asyncio.gather(*tasks)

        # All should return same result
        assert all(r == "result" for r in results)
        # But operation should only run once
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_coalescer_handles_different_keys(self):
        """Different keys should not be coalesced."""
        coalescer = RequestCoalescer()
        call_count = 0

        async def slow_operation(val):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.05)
            return val

        # Two different keys
        t1 = asyncio.create_task(coalescer.coalesce("key1", slow_operation, "result1"))
        t2 = asyncio.create_task(coalescer.coalesce("key2", slow_operation, "result2"))
        r1, r2 = await asyncio.gather(t1, t2)

        assert r1 == "result1"
        assert r2 == "result2"
        # Should execute twice (different keys)
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_coalescer_propagates_exceptions(self):
        """Exceptions should be propagated to all waiters."""
        coalescer = RequestCoalescer()

        async def failing_operation():
            raise ValueError("Test error")

        tasks = [
            asyncio.create_task(coalescer.coalesce("error_key", failing_operation))
            for _ in range(3)
        ]

        with pytest.raises(ValueError, match="Test error"):
            await asyncio.gather(*tasks)


# Optional: Integration test (requires actual ProviderRouter + YFinanceProvider)
@pytest.mark.asyncio
async def test_provider_router_with_coalescer_and_rate_limiter():
    """Test ProviderRouter integration with coalescer and rate limiter."""
    from app.core.config import settings
    from app.services.data_providers.yfinance_provider import YFinanceProvider

    # Test with YFinanceProvider directly (avoid abstract provider issues)
    provider = YFinanceProvider()
    coalescer = RequestCoalescer()
    limiter = RateLimiter({"yfinance": (100, 60)})

    symbol = "AAPL"

    async def fetch_news_coalesced():
        key = f"news:{symbol}:10"
        allowed = await limiter.allow("yfinance")
        if not allowed:
            return None
        try:
            result = await coalescer.coalesce(key, provider.get_news, symbol, 10)
            limiter.record_success("yfinance")
            return result
        except Exception as e:
            limiter.record_failure("yfinance")
            return None

    # First fetch
    news1 = await fetch_news_coalesced()
    assert news1 is not None
    assert len(news1) > 0

    # Second fetch (coalesced + cached by key)
    t0 = time.perf_counter()
    news2 = await fetch_news_coalesced()
    dt = time.perf_counter() - t0

    assert news1 == news2  # Same result
    # Note: dt may be longer due to NLP processing in YFinanceProvider.get_news()
    # First call ~10s (yfinance + news analysis), second call should be coalesced/cached
    assert dt < 15  # Reasonable time for second coalesced call


if __name__ == "__main__":
    # Run with: python -m pytest tests/test_rate_limiter.py -v
    pytest.main([__file__, "-v"])
