"""
Feature Store Database Models for unified data layer
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Index, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class FeatureMetadata(Base):
    """Metadata about features (technical indicators, ML features, etc.)"""
    __tablename__ = "feature_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    feature_name = Column(String(100), unique=True, nullable=False, index=True)
    feature_type = Column(String(50), nullable=False)  # technical, fundamental, sentiment, ml
    description = Column(Text, nullable=True)
    calculation_method = Column(Text, nullable=True)
    version = Column(String(20), nullable=False, default="1.0.0")
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Parameters for feature calculation (stored as JSON)
    parameters = Column(JSON, nullable=True)
    
    # Relationship to feature values
    values = relationship("FeatureValue", back_populates="feature_metadata", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_feature_metadata_name_version', 'feature_name', 'version'),
    )


class FeatureValue(Base):
    """Actual feature values for stocks over time"""
    __tablename__ = "feature_values"
    
    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("feature_metadata.id"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    value = Column(Float, nullable=True)  # Numeric value
    value_str = Column(String(500), nullable=True)  # String value (for categorical features)
    confidence_score = Column(Float, nullable=True)  # Confidence/quality score (0-1)
    
    # Metadata
    calculation_time_ms = Column(Integer, nullable=True)
    source = Column(String(50), nullable=True)  # yfinance, alpha_vantage, calculated, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    feature_metadata = relationship("FeatureMetadata", back_populates="values")
    
    __table_args__ = (
        Index('ix_feature_values_symbol_feature_timestamp', 'symbol', 'feature_id', 'timestamp'),
        Index('ix_feature_values_timestamp_symbol', 'timestamp', 'symbol'),
    )


class CachedData(Base):
    """Cache for frequently accessed data (dashboard, portfolio, etc.)"""
    __tablename__ = "cached_data"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(200), unique=True, nullable=False, index=True)
    cache_type = Column(String(50), nullable=False, index=True)  # dashboard, portfolio, research, etc.
    data_json = Column(JSON, nullable=False)
    
    # TTL and versioning
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    version = Column(Integer, default=1)
    
    # Metadata
    data_size_bytes = Column(Integer, nullable=True)
    hit_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index('ix_cached_data_expires_type', 'expires_at', 'cache_type'),
    )
