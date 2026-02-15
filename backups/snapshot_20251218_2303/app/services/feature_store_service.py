"""
Feature Store Service - Unified data layer for all features
"""
import redis
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging

from app.models.feature_store import FeatureMetadata, FeatureValue, CachedData
from app.config.production import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class FeatureStoreService:
    """
    Unified Feature Store providing centralized access to all features
    with Redis caching and PostgreSQL persistence
    """
    
    def __init__(self, db: Session, redis_client: Optional[redis.Redis] = None):
        self.db = db
        self.redis_available = False
        
        # Try to connect to Redis, but don't fail if unavailable
        try:
            if redis_client:
                self.redis_client = redis_client
            else:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=1  # Fast timeout
                )
                # Test connection
                self.redis_client.ping()
            self.redis_available = True
            logger.info("Redis connection established")
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.warning(f"Redis unavailable, will use database only: {e}")
            self.redis_client = None
            self.redis_available = False
        
    # ==================== Feature Metadata ====================
    
    def register_feature(
        self,
        feature_name: str,
        feature_type: str,
        description: Optional[str] = None,
        parameters: Optional[Dict] = None,
        version: str = "1.0.0"
    ) -> FeatureMetadata:
        """Register a new feature in the metadata catalog"""
        existing = self.db.query(FeatureMetadata).filter(
            FeatureMetadata.feature_name == feature_name,
            FeatureMetadata.version == version
        ).first()
        
        if existing:
            logger.info(f"Feature {feature_name} v{version} already registered")
            return existing
        
        feature = FeatureMetadata(
            feature_name=feature_name,
            feature_type=feature_type,
            description=description,
            parameters=parameters,
            version=version,
            is_active=True
        )
        
        self.db.add(feature)
        self.db.commit()
        self.db.refresh(feature)
        
        logger.info(f"Registered feature: {feature_name} v{version}")
        return feature
    
    def get_feature_metadata(self, feature_name: str, version: str = "1.0.0") -> Optional[FeatureMetadata]:
        """Get metadata for a specific feature"""
        return self.db.query(FeatureMetadata).filter(
            FeatureMetadata.feature_name == feature_name,
            FeatureMetadata.version == version,
            FeatureMetadata.is_active == True
        ).first()
    
    # ==================== Feature Values ====================
    
    def store_feature_value(
        self,
        feature_name: str,
        symbol: str,
        value: Any,
        timestamp: Optional[datetime] = None,
        confidence_score: Optional[float] = None,
        source: str = "calculated"
    ) -> FeatureValue:
        """Store a single feature value"""
        # Get or create feature metadata
        metadata = self.get_feature_metadata(feature_name)
        if not metadata:
            metadata = self.register_feature(
                feature_name=feature_name,
                feature_type="unknown",
                description=f"Auto-registered feature: {feature_name}"
            )
        
        timestamp = timestamp or datetime.utcnow()
        
        # Determine if value is numeric or string
        if isinstance(value, (int, float)):
            feature_value = FeatureValue(
                feature_id=metadata.id,
                symbol=symbol,
                timestamp=timestamp,
                value=float(value),
                confidence_score=confidence_score,
                source=source
            )
        else:
            feature_value = FeatureValue(
                feature_id=metadata.id,
                symbol=symbol,
                timestamp=timestamp,
                value_str=str(value),
                confidence_score=confidence_score,
                source=source
            )
        
        self.db.add(feature_value)
        self.db.commit()
        
        # Invalidate cache for this symbol
        self._invalidate_cache(f"features:{symbol}:*")
        
        return feature_value
    
    def store_features_bulk(
        self,
        symbol: str,
        features: Dict[str, Any],
        timestamp: Optional[datetime] = None,
        source: str = "calculated"
    ) -> int:
        """Store multiple features for a symbol at once"""
        timestamp = timestamp or datetime.utcnow()
        stored_count = 0
        
        for feature_name, value in features.items():
            try:
                self.store_feature_value(
                    feature_name=feature_name,
                    symbol=symbol,
                    value=value,
                    timestamp=timestamp,
                    source=source
                )
                stored_count += 1
            except Exception as e:
                logger.error(f"Error storing feature {feature_name} for {symbol}: {e}")
                continue
        
        logger.info(f"Stored {stored_count} features for {symbol}")
        return stored_count
    
    def get_feature_value(
        self,
        feature_name: str,
        symbol: str,
        timestamp: Optional[datetime] = None
    ) -> Optional[Any]:
        """Get a single feature value (latest or at specific timestamp)"""
        # Try Redis cache first if available
        cache_key = f"feature:{feature_name}:{symbol}"
        if timestamp:
            cache_key += f":{timestamp.isoformat()}"
        
        cached = None
        if self.redis_available:
            try:
                cached = self.redis_client.get(cache_key)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        
        if cached:
            logger.debug(f"Cache hit: {cache_key}")
            return json.loads(cached)
        
        # Query database
        metadata = self.get_feature_metadata(feature_name)
        if not metadata:
            return None
        
        query = self.db.query(FeatureValue).filter(
            FeatureValue.feature_id == metadata.id,
            FeatureValue.symbol == symbol
        )
        
        if timestamp:
            query = query.filter(FeatureValue.timestamp == timestamp)
        else:
            query = query.order_by(FeatureValue.timestamp.desc())
        
        feature_value = query.first()
        
        if not feature_value:
            return None
        
        # Return appropriate value type
        result = feature_value.value if feature_value.value is not None else feature_value.value_str
        
        # Cache for 5 minutes if Redis is available
        if self.redis_available:
            try:
                self.redis_client.setex(
                    cache_key,
                    300,  # 5 minutes
                    json.dumps(result)
                )
            except Exception as e:
                logger.warning(f"Redis setex error: {e}")
        
        return result
    
    def get_features_bulk(
        self,
        symbol: str,
        feature_names: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get multiple features for a symbol"""
        # Try cache first if Redis is available
        cache_key = f"features:{symbol}:bulk"
        if timestamp:
            cache_key += f":{timestamp.isoformat()}"
        
        cached = None
        if self.redis_available:
            try:
                cached = self.redis_client.get(cache_key)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        
        if cached:
            logger.debug(f"Bulk cache hit: {symbol}")
            return json.loads(cached)
        
        # Query database
        query = self.db.query(FeatureValue, FeatureMetadata).join(
            FeatureMetadata, FeatureValue.feature_id == FeatureMetadata.id
        ).filter(
            FeatureValue.symbol == symbol
        )
        
        if feature_names:
            query = query.filter(FeatureMetadata.feature_name.in_(feature_names))
        
        if timestamp:
            query = query.filter(FeatureValue.timestamp == timestamp)
        else:
            # Get latest values using subquery
            query = query.order_by(FeatureValue.timestamp.desc())
        
        results = query.all()
        
        features = {}
        for feature_value, metadata in results:
            if metadata.feature_name not in features:  # Take first (latest) value
                features[metadata.feature_name] = (
                    feature_value.value if feature_value.value is not None 
                    else feature_value.value_str
                )
        
        # Cache for 5 minutes if Redis is available
        if self.redis_available:
            try:
                self.redis_client.setex(cache_key, 300, json.dumps(features))
            except Exception as e:
                logger.warning(f"Redis setex error: {e}")
        
        return features
    
    # ==================== Cached Data ====================
    
    def cache_data(
        self,
        cache_key: str,
        cache_type: str,
        data: Dict,
        ttl_seconds: int = 300
    ) -> CachedData:
        """Cache data in both Redis and PostgreSQL"""
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        data_json_str = json.dumps(data)
        
        # Store in Redis (fast access) if available
        if self.redis_available:
            try:
                self.redis_client.setex(
                    f"cache:{cache_key}",
                    ttl_seconds,
                    data_json_str
                )
            except Exception as e:
                logger.warning(f"Redis setex error: {e}")
        
        # Store in PostgreSQL (persistence)
        cached_data = self.db.query(CachedData).filter(
            CachedData.cache_key == cache_key
        ).first()
        
        if cached_data:
            cached_data.data_json = data
            cached_data.expires_at = expires_at
            cached_data.version += 1
            cached_data.data_size_bytes = len(data_json_str)
        else:
            cached_data = CachedData(
                cache_key=cache_key,
                cache_type=cache_type,
                data_json=data,
                expires_at=expires_at,
                data_size_bytes=len(data_json_str)
            )
            self.db.add(cached_data)
        
        self.db.commit()
        logger.info(f"Cached data: {cache_key} (TTL: {ttl_seconds}s)")
        
        return cached_data
    
    def get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """Retrieve cached data (Redis first, then PostgreSQL)"""
        # Try Redis first if available
        redis_key = f"cache:{cache_key}"
        cached = None
        if self.redis_available:
            try:
                cached = self.redis_client.get(redis_key)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        
        if cached:
            logger.debug(f"Redis cache hit: {cache_key}")
            # Update hit count in PostgreSQL async (non-blocking)
            try:
                db_cached = self.db.query(CachedData).filter(
                    CachedData.cache_key == cache_key
                ).first()
                if db_cached:
                    db_cached.hit_count += 1
                    db_cached.last_accessed_at = datetime.utcnow()
                    self.db.commit()
            except:
                pass
            
            return json.loads(cached)
        
        # Fallback to PostgreSQL
        db_cached = self.db.query(CachedData).filter(
            CachedData.cache_key == cache_key,
            CachedData.expires_at > datetime.utcnow()
        ).first()
        
        if db_cached:
            logger.debug(f"PostgreSQL cache hit: {cache_key}")
            # Restore to Redis if available
            ttl = int((db_cached.expires_at - datetime.utcnow()).total_seconds())
            if ttl > 0 and self.redis_available:
                try:
                    self.redis_client.setex(
                        redis_key,
                        ttl,
                        json.dumps(db_cached.data_json)
                    )
                except Exception as e:
                    logger.warning(f"Redis setex error: {e}")
            
            db_cached.hit_count += 1
            db_cached.last_accessed_at = datetime.utcnow()
            self.db.commit()
            
            return db_cached.data_json
        
        logger.debug(f"Cache miss: {cache_key}")
        return None
    
    def invalidate_cache(self, cache_key: str):
        """Invalidate specific cache entry"""
        self._invalidate_cache(cache_key)
    
    def _invalidate_cache(self, pattern: str):
        """Invalidate Redis cache entries matching pattern"""
        if not self.redis_available:
            logger.debug("Redis unavailable, skipping cache invalidation")
            return
            
        try:
            # Redis pattern matching
            redis_pattern = f"cache:{pattern}" if not pattern.startswith("cache:") else pattern
            keys = self.redis_client.keys(redis_pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache entries matching: {pattern}")
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
    
    # ==================== Cleanup ====================
    
    def cleanup_expired_cache(self):
        """Remove expired cache entries from PostgreSQL"""
        deleted = self.db.query(CachedData).filter(
            CachedData.expires_at < datetime.utcnow()
        ).delete()
        
        self.db.commit()
        logger.info(f"Cleaned up {deleted} expired cache entries")
        
        return deleted
