import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base, User, Stock, Portfolio, PortfolioWeight, Report, Backup

@pytest.fixture
def engine():
    return create_engine('sqlite:///:memory:')

@pytest.fixture
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def session(engine, tables):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_user(session):
    user = User(
        username='testuser',
        email='test@example.com',
        hashed_password='hashed_password'
    )
    session.add(user)
    session.commit()
    
    assert user.id is not None
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.is_active is True
    assert isinstance(user.created_at, datetime)

def test_create_stock(session):
    stock = Stock(
        symbol='AAPL',
        name='Apple Inc.',
        sector='Technology',
        industry='Consumer Electronics',
        market_cap=2000000000000,
        last_price=150.0
    )
    session.add(stock)
    session.commit()
    
    assert stock.id is not None
    assert stock.symbol == 'AAPL'
    assert stock.name == 'Apple Inc.'
    assert stock.sector == 'Technology'
    assert stock.market_cap == 2000000000000
    assert isinstance(stock.last_updated, datetime)

def test_create_portfolio(session):
    user = User(username='testuser', email='test@example.com', hashed_password='hashed_password')
    session.add(user)
    session.commit()
    
    portfolio = Portfolio(
        name='Test Portfolio',
        user_id=user.id
    )
    session.add(portfolio)
    session.commit()
    
    assert portfolio.id is not None
    assert portfolio.name == 'Test Portfolio'
    assert portfolio.user_id == user.id
    assert isinstance(portfolio.created_at, datetime)
    assert isinstance(portfolio.last_updated, datetime)

def test_portfolio_weights(session):
    user = User(username='testuser', email='test@example.com', hashed_password='hashed_password')
    session.add(user)
    
    stock = Stock(symbol='AAPL', name='Apple Inc.')
    session.add(stock)
    
    portfolio = Portfolio(name='Test Portfolio', user_id=user.id)
    session.add(portfolio)
    
    session.commit()
    
    weight = PortfolioWeight(
        portfolio_id=portfolio.id,
        stock_id=stock.id,
        weight=0.5
    )
    session.add(weight)
    session.commit()
    
    assert weight.id is not None
    assert weight.portfolio_id == portfolio.id
    assert weight.stock_id == stock.id
    assert weight.weight == 0.5
    assert isinstance(weight.last_updated, datetime)

def test_create_report(session):
    user = User(username='testuser', email='test@example.com', hashed_password='hashed_password')
    session.add(user)
    
    stock = Stock(symbol='AAPL', name='Apple Inc.')
    session.add(stock)
    
    session.commit()
    
    report = Report(
        user_id=user.id,
        stock_id=stock.id,
        report_type='analysis',
        content='Test report content'
    )
    session.add(report)
    session.commit()
    
    assert report.id is not None
    assert report.user_id == user.id
    assert report.stock_id == stock.id
    assert report.report_type == 'analysis'
    assert report.content == 'Test report content'
    assert isinstance(report.created_at, datetime)

def test_create_backup(session):
    backup = Backup(
        path='/path/to/backup',
        size=1000,
        status='success'
    )
    session.add(backup)
    session.commit()
    
    assert backup.id is not None
    assert backup.path == '/path/to/backup'
    assert backup.size == 1000
    assert backup.status == 'success'
    assert isinstance(backup.created_at, datetime)

def test_relationships(session):
    # Create user
    user = User(username='testuser', email='test@example.com', hashed_password='hashed_password')
    session.add(user)
    
    # Create stock
    stock = Stock(symbol='AAPL', name='Apple Inc.')
    session.add(stock)
    
    # Create portfolio
    portfolio = Portfolio(name='Test Portfolio', user_id=user.id)
    session.add(portfolio)
    
    # Add stock to portfolio
    portfolio.stocks.append(stock)
    
    # Create weight
    weight = PortfolioWeight(portfolio_id=portfolio.id, stock_id=stock.id, weight=0.5)
    session.add(weight)
    
    # Create report
    report = Report(
        user_id=user.id,
        stock_id=stock.id,
        report_type='analysis',
        content='Test report'
    )
    session.add(report)
    
    session.commit()
    
    # Test relationships
    assert len(user.portfolios) == 1
    assert user.portfolios[0].name == 'Test Portfolio'
    
    assert len(portfolio.stocks) == 1
    assert portfolio.stocks[0].symbol == 'AAPL'
    
    assert len(portfolio.weights) == 1
    assert portfolio.weights[0].weight == 0.5
    
    assert len(user.reports) == 1
    assert user.reports[0].content == 'Test report'
    
    assert len(stock.reports) == 1
    assert stock.reports[0].content == 'Test report' 