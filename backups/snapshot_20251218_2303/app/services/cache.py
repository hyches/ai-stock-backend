"""
Redis caching layer for Research tab data.

Implements multi-tiered caching with configurable TTLs per data type.
Tracks cache hits/misses for monitoring and optimization.
"""

import redis
import json
import logging
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
from app.core.config import Settings

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages Redis caching for research data.
    
    Features:
    - Configurable TTLs per data type
    - Cache hit/miss tracking
    - Automatic key namespacing
    - Graceful degradation on Redis unavailable
    - Optional JSON serialization
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize cache manager.
        
        Args:
            settings: Application settings with Redis config
        """
        self.settings = settings
        self.enabled = settings.CACHE_ENABLED
        self.redis_client = None
        self.namespace = "research"
        
        # TTLs for different data types (seconds)
        self.ttls = {
            "info": settings.RESEARCH_CACHE_TTL_INFO,
            "history": settings.RESEARCH_CACHE_TTL_HISTORY,
            "news": settings.RESEARCH_CACHE_TTL_NEWS,
            "technicals": settings.RESEARCH_CACHE_TTL_TECHNICALS,
            "financials": settings.RESEARCH_CACHE_TTL_FINANCIALS,
        }
        
        # Metrics
        self.hits = 0
        self.misses = 0
        
        # Initialize Redis connection
        if self.enabled:
            self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.Redis(
                host=self.settings.REDIS_HOST,
                port=self.settings.REDIS_PORT,
                db=self.settings.REDIS_DB,
                password=self.settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                retry_on_timeout=True,
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
            self.enabled = False
    
    def _make_key(self, symbol: str, data_type: str, *args) -> str:
        """
        Generate cache key.
        
        Args:
            symbol: Stock symbol
            data_type: Type of data (info, history, news, etc.)
            *args: Additional key components
            
        Returns:
            Cache key string
        """
        parts = [self.namespace, symbol.upper(), data_type] + list(args)
        return ":".join(str(p) for p in parts)
    
    async def get(self, symbol: str, data_type: str, *args) -> Optional[Any]:
        """
        Get data from cache.
        
        Args:
            symbol: Stock symbol
            data_type: Type of data
            *args: Additional key components
            
        Returns:
            Cached data or None if not found
        """
        if not self.enabled or not self.redis_client:
            self.misses += 1
            return None
        
        try:
            key = self._make_key(symbol, data_type, *args)
            value = self.redis_client.get(key)
            
            if value:
                self.hits += 1
                logger.debug(f"Cache HIT: {key}")
                
                # Try to parse JSON
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # Return raw value if not JSON
                    return value
            else:
                self.misses += 1
                logger.debug(f"Cache MISS: {key}")
                return None
        
        except Exception as e:
            logger.error(f"Cache get error for {symbol}:{data_type}: {e}")
            self.misses += 1
            return None
    
    async def set(
        self,
        symbol: str,
        data_type: str,
        value: Any,
        ttl: Optional[int] = None,
        *args,
    ) -> bool:
        """
        Set data in cache.
        
        Args:
            symbol: Stock symbol
            data_type: Type of data
            value: Data to cache
            ttl: Time-to-live in seconds (uses default if None)
            *args: Additional key components
            
        Returns:
            True if set successfully, False otherwise
        """
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            key = self._make_key(symbol, data_type, *args)
            
            # Use provided TTL or default for data type
            if ttl is None:
                ttl = self.ttls.get(data_type, 300)
            
            # Serialize to JSON if needed
            if not isinstance(value, str):
                try:
                    value = json.dumps(value)
                except (TypeError, ValueError):
                    # If not JSON-serializable, convert to string
                    value = str(value)
            
            # Set with TTL
            self.redis_client.setex(key, ttl, value)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        
        except Exception as e:
            logger.error(f"Cache set error for {symbol}:{data_type}: {e}")
            return False
    
    async def delete(self, symbol: str, data_type: str, *args) -> bool:
        """
        Delete data from cache.
        
        Args:
            symbol: Stock symbol
            data_type: Type of data
            *args: Additional key components
            
        Returns:
            True if deleted, False otherwise
        """
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            key = self._make_key(symbol, data_type, *args)
            result = self.redis_client.delete(key)
            logger.debug(f"Cache DELETE: {key} ({result} keys deleted)")
            return result > 0
        
        except Exception as e:
            logger.error(f"Cache delete error for {symbol}:{data_type}: {e}")
            return False
    
    async def clear_symbol(self, symbol: str) -> int:
        """
        Clear all cache entries for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self.redis_client:
            return 0
        
        try:
            pattern = self._make_key(symbol, "*")
            # Use scan for large key spaces
            keys = self.redis_client.keys(pattern)
            if keys:
                result = self.redis_client.delete(*keys)
                logger.info(f"Cleared {result} cache entries for {symbol}")
                return result
            return 0
        
        except Exception as e:
            logger.error(f"Cache clear error for {symbol}: {e}")
            return 0
    
    async def clear_all(self) -> int:
        """Clear all research cache entries."""
        if not self.enabled or not self.redis_client:
            return 0
        
        try:
            pattern = f"{self.namespace}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                result = self.redis_client.delete(*keys)
                logger.info(f"Cleared {result} all research cache entries")
                return result
            return 0
        
        except Exception as e:
            logger.error(f"Cache clear all error: {e}")
            return 0
    
    async def get_ttl(self, symbol: str, data_type: str, *args) -> int:
        """
        Get remaining TTL for a cache entry.
        
        Args:
            symbol: Stock symbol
            data_type: Type of data
            *args: Additional key components
            
        Returns:
            Remaining TTL in seconds, -1 if key has no expiry, -2 if not found
        """
        if not self.enabled or not self.redis_client:
            return -2
        
        try:
            key = self._make_key(symbol, data_type, *args)
            return self.redis_client.ttl(key)
        
        except Exception as e:
            logger.error(f"Cache TTL error for {symbol}:{data_type}: {e}")
            return -2
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with hit rate, total requests, etc.
        """
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        stats = {
            "enabled": self.enabled,
            "connected": self.redis_client is not None,
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 2),
            "ttls": self.ttls,
        }
        
        # Add Redis info if available
        if self.redis_client:
            try:
                info = self.redis_client.info()
                stats["redis_memory_used"] = info.get("used_memory_human"),
                stats["redis_connected_clients"] = info.get("connected_clients"),
            except Exception as e:
                logger.warning(f"Failed to get Redis info: {e}")
        
        return stats


# Global cache instance (initialized in app startup)
cache_manager: Optional[CacheManager] = None


async def init_cache(settings: Settings) -> CacheManager:
    """
    Initialize global cache manager.
    
    Args:
        settings: Application settings
        
    Returns:
        CacheManager instance
    """
    global cache_manager
    cache_manager = CacheManager(settings)
    return cache_manager


def get_cache() -> Optional[CacheManager]:
    """
    Get global cache manager instance.
    
    Returns:
        CacheManager or None if not initialized
    """
    return cache_manager
