import pytest
import asyncio
from app.core.cache import Cache, cache_response
from app.core.config import settings

@pytest.fixture
async def cache(redis_client):
    """Create cache instance"""
    return Cache(redis_client)

async def test_cache_set_get(cache):
    """Test setting and getting values from cache"""
    # Set value
    await cache.set("test_key", "test_value")
    
    # Get value
    value = await cache.get("test_key")
    assert value == "test_value"

async def test_cache_delete(cache):
    """Test deleting values from cache"""
    # Set value
    await cache.set("test_key", "test_value")
    
    # Delete value
    await cache.delete("test_key")
    
    # Verify value is deleted
    value = await cache.get("test_key")
    assert value is None

async def test_cache_clear_pattern(cache):
    """Test clearing cache by pattern"""
    # Set multiple values
    await cache.set("test:1", "value1")
    await cache.set("test:2", "value2")
    await cache.set("other:1", "value3")
    
    # Clear pattern
    await cache.clear_pattern("test:*")
    
    # Verify only matching keys are cleared
    assert await cache.get("test:1") is None
    assert await cache.get("test:2") is None
    assert await cache.get("other:1") == "value3"

async def test_cache_ttl(cache):
    """Test cache TTL"""
    # Set value with TTL
    await cache.set("test_key", "test_value", ttl=1)
    
    # Get value immediately
    value = await cache.get("test_key")
    assert value == "test_value"
    
    # Wait for TTL to expire
    await asyncio.sleep(1.1)
    
    # Verify value is expired
    value = await cache.get("test_key")
    assert value is None

async def test_cache_response_decorator(cache):
    """Test cache_response decorator"""
    # Define test function
    @cache_response(ttl=60, key_prefix="test")
    async def test_function(arg1, arg2):
        return f"result_{arg1}_{arg2}"
    
    # Call function first time
    result1 = await test_function("a", "b")
    assert result1 == "result_a_b"
    
    # Call function second time (should use cache)
    result2 = await test_function("a", "b")
    assert result2 == "result_a_b"
    
    # Verify result is cached
    cached_value = await cache.get("test:test_function:('a', 'b'):{}")
    assert cached_value == "result_a_b"

async def test_cache_response_different_args(cache):
    """Test cache_response with different arguments"""
    # Define test function
    @cache_response(ttl=60, key_prefix="test")
    async def test_function(arg1, arg2):
        return f"result_{arg1}_{arg2}"
    
    # Call function with different arguments
    result1 = await test_function("a", "b")
    result2 = await test_function("a", "c")
    
    assert result1 == "result_a_b"
    assert result2 == "result_a_c"
    
    # Verify both results are cached
    cached_value1 = await cache.get("test:test_function:('a', 'b'):{}")
    cached_value2 = await cache.get("test:test_function:('a', 'c'):{}")
    
    assert cached_value1 == "result_a_b"
    assert cached_value2 == "result_a_c"

async def test_cache_response_clear(cache):
    """Test clearing cache for cache_response"""
    # Define test function
    @cache_response(ttl=60, key_prefix="test")
    async def test_function(arg1, arg2):
        return f"result_{arg1}_{arg2}"
    
    # Call function
    result1 = await test_function("a", "b")
    
    # Clear cache pattern
    await cache.clear_pattern("test:*")
    
    # Call function again (should not use cache)
    result2 = await test_function("a", "b")
    
    assert result1 == result2
    assert result1 == "result_a_b"

async def test_cache_complex_objects(cache):
    """Test caching complex objects"""
    # Create complex object
    complex_obj = {
        "name": "test",
        "values": [1, 2, 3],
        "nested": {
            "key": "value"
        }
    }
    
    # Set complex object
    await cache.set("complex_key", complex_obj)
    
    # Get complex object
    value = await cache.get("complex_key")
    assert value == complex_obj
    assert value["name"] == "test"
    assert value["values"] == [1, 2, 3]
    assert value["nested"]["key"] == "value"

async def test_cache_concurrent_access(cache):
    """Test concurrent cache access"""
    async def set_value(key, value):
        await cache.set(key, value)
    
    async def get_value(key):
        return await cache.get(key)
    
    # Set multiple values concurrently
    await asyncio.gather(
        set_value("key1", "value1"),
        set_value("key2", "value2"),
        set_value("key3", "value3")
    )
    
    # Get multiple values concurrently
    results = await asyncio.gather(
        get_value("key1"),
        get_value("key2"),
        get_value("key3")
    )
    
    assert results == ["value1", "value2", "value3"]

async def test_cache_error_handling(cache):
    """Test cache error handling"""
    # Test with invalid key
    value = await cache.get(None)
    assert value is None
    
    # Test with invalid value
    await cache.set("test_key", None)
    value = await cache.get("test_key")
    assert value is None
    
    # Test with invalid TTL
    await cache.set("test_key", "value", ttl=-1)
    value = await cache.get("test_key")
    assert value is None 