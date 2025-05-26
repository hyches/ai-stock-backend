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
    """
    Represents a user entity in the application with authentication details and associated resources.
    Parameters:
        - id (Integer): Unique identifier for each user, serving as the primary key.
        - username (String): Unique username chosen by the user, indexed for quick searches.
        - email (String): Unique email address of the user, indexed for quick searches.
        - hashed_password (String): Securely hashed password of the user.
        - is_active (Boolean): Status indicating whether the user's account is active; defaults to True.
        - created_at (DateTime): Timestamp marking when the user was created; defaults to current UTC time.
    Processing Logic:
        - Establishes relations with Portfolio and Report entities, allowing retrieval of related data.
        - Uses indexing on 'created_at' to optimize queries involving sorting or filtering by creation date.
    """
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
    """
    Represents a stock entity within the financial market database.
    Parameters:
        - id (Integer): The primary key identifier for the stock.
        - symbol (String): A unique ticker symbol representing the stock, indexed for quick search.
        - name (String): The official name of the stock.
        - sector (String): The sector classification of the stock, indexed for efficient querying.
        - industry (String): The industry classification of the stock, similarly indexed.
        - market_cap (Float): The market capitalization of the stock, representing its economic size.
        - last_price (Float): The most recent trading price of the stock.
        - last_updated (DateTime): Timestamp of the last update to the stock's price, defaults to current UTC time.
    Processing Logic:
        - Establishes relationships with the Portfolio and Report tables to support many-to-many mappings and reporting capabilities.
        - Maintains database index for the 'last_updated' timestamp to optimize query performance.
        - Sector and industry are configured as composite indexes to enable efficient sector-industry-specific queries.
    """
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
    """
    Portfolio class represents a collection of financial assets held by a user.
    Parameters:
        - id (Integer): Unique identifier for the portfolio.
        - name (String): Name of the portfolio.
        - user_id (Integer): Identifier of the user owning the portfolio.
        - created_at (DateTime): Timestamp of when the portfolio was created.
        - last_updated (DateTime): Timestamp of the most recent update to the portfolio.
    Processing Logic:
        - Establishes a relationship with the User class, linking portfolios to users.
        - Links to the Stock class via a secondary table for many-to-many relationships.
        - Connects with PortfolioWeight for managing asset allocations.
        - Utilizes indexes for optimized querying based on user_id, creation, and update timestamps.
    """
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
    """
    PortfolioWeight Model represents the association between portfolios and stocks, defining the allocation of stocks in a portfolio.
    Parameters:
        - portfolio_id (Integer): Identifier for the portfolio to which the stock belongs.
        - stock_id (Integer): Identifier for the stock in the portfolio.
        - weight (Float): Defines the proportion of the stock within the portfolio.
    Processing Logic:
        - Establishes a relationship between portfolio and stock through foreign keys.
        - Includes indexing for optimized lookups and queries on portfolio and stock relationships.
        - Automatically timestamps records when updated.
    """
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
    """
    Report class represents an entry of a generated report by users on specific stocks.
    Parameters:
        - id (Integer): Unique identifier for the report, automatically generated.
        - user_id (Integer): References the author of the report.
        - stock_id (Integer): References the stock that the report is about.
        - report_type (String): Indicates the type of report, such as research or analysis.
        - content (String): Text content of the report detailing insights or findings.
        - created_at (DateTime): Timestamp indicating when the report was created, defaults to current UTC time.
    Processing Logic:
        - Establishes relationships between reports, users, and stocks through foreign keys.
        - Utilizes indexing to optimize queries filtering by user creation date and stock report type.
    """
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
    """
    Represents a backup record in the database with attributes for managing file information and status.
    Parameters:
        - path (String): The file path of the backup.
        - size (Integer): The size of the backup file in bytes, if applicable.
    Processing Logic:
        - The 'created_at' field automatically captures the timestamp when a backup entry is created.
        - The 'status' field tracks the state of the backup; possible values are 'success', 'failed', and 'in_progress'.
        - A database index is created combining 'created_at' and 'status' to optimize query performance for backups filtered by these columns.
    """
    __tablename__ = 'backups'
    
    id = Column(Integer, primary_key=True)
    path = Column(String)
    size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, index=True)  # success, failed, in_progress
    
    __table_args__ = (
        Index('ix_backups_created_status', 'created_at', 'status'),
    ) 