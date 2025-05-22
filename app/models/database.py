from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# Association tables
stock_portfolio = Table(
    'stock_portfolio',
    Base.metadata,
    Column('stock_id', Integer, ForeignKey('stocks.id')),
    Column('portfolio_id', Integer, ForeignKey('portfolios.id')),
    Index('ix_stock_portfolio_stock_id', 'stock_id'),
    Index('ix_stock_portfolio_portfolio_id', 'portfolio_id')
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    portfolios = relationship("Portfolio", back_populates="user")
    reports = relationship("Report", back_populates="user")
    
    __table_args__ = (
        Index('ix_users_created_at', 'created_at'),
    )

class Stock(Base):
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String)
    sector = Column(String, index=True)
    industry = Column(String, index=True)
    market_cap = Column(Float)
    last_price = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    portfolios = relationship("Portfolio", secondary=stock_portfolio, back_populates="stocks")
    reports = relationship("Report", back_populates="stock")
    
    __table_args__ = (
        Index('ix_stocks_last_updated', 'last_updated'),
        Index('ix_stocks_sector_industry', 'sector', 'industry'),
    )

class Portfolio(Base):
    __tablename__ = 'portfolios'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="portfolios")
    stocks = relationship("Stock", secondary=stock_portfolio, back_populates="portfolios")
    weights = relationship("PortfolioWeight", back_populates="portfolio")
    
    __table_args__ = (
        Index('ix_portfolios_user_created', 'user_id', 'created_at'),
        Index('ix_portfolios_last_updated', 'last_updated'),
    )

class PortfolioWeight(Base):
    __tablename__ = 'portfolio_weights'
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), index=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), index=True)
    weight = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    portfolio = relationship("Portfolio", back_populates="weights")
    stock = relationship("Stock")
    
    __table_args__ = (
        Index('ix_portfolio_weights_portfolio_stock', 'portfolio_id', 'stock_id'),
        Index('ix_portfolio_weights_last_updated', 'last_updated'),
    )

class Report(Base):
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), index=True)
    report_type = Column(String, index=True)  # research, analysis, etc.
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="reports")
    stock = relationship("Stock", back_populates="reports")
    
    __table_args__ = (
        Index('ix_reports_user_created', 'user_id', 'created_at'),
        Index('ix_reports_stock_type', 'stock_id', 'report_type'),
    )

class Backup(Base):
    __tablename__ = 'backups'
    
    id = Column(Integer, primary_key=True)
    path = Column(String)
    size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, index=True)  # success, failed, in_progress
    
    __table_args__ = (
        Index('ix_backups_created_status', 'created_at', 'status'),
    ) 