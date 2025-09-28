import pytest
from sqlalchemy import text
from app.db.base_class import Base
from app.db.session import engine, SessionLocal
from app.models.trading import Strategy, Trade, Portfolio, Position
from app.models.user import User

@pytest.fixture
def db_session():
    """Create database session"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_query_pagination(db_session):
    """Test query pagination"""
    # Create test data
    for i in range(25):
        strategy = Strategy(
            name=f"Strategy {i}",
            description=f"Description {i}",
            type="trend_following",
            parameters={"param": i}
        )
        db_session.add(strategy)
    db_session.commit()
    
    # Test pagination
    query = db_session.query(Strategy)
    result = query.paginate(page=1, per_page=10)
    
    assert len(result["items"]) == 10
    assert result["total"] == 25
    assert result["pages"] == 3
    assert result["page"] == 1
    assert result["per_page"] == 10

def test_query_with_entities(db_session):
    """Test query with specific entities"""
    # Create test data
    strategy = Strategy(
        name="Test Strategy",
        description="Test Description",
        type="trend_following",
        parameters={"param": 1}
    )
    db_session.add(strategy)
    db_session.commit()
    
    # Test selecting specific columns
    query = db_session.query(Strategy).with_entities(Strategy.name, Strategy.type)
    result = query.first()
    
    assert hasattr(result, "name")
    assert hasattr(result, "type")
    assert not hasattr(result, "description")
    assert not hasattr(result, "parameters")

def test_query_with_relationships(db_session):
    """Test query with relationship loading"""
    # Create test data
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    
    portfolio = Portfolio(
        name="Test Portfolio",
        description="Test Description",
        initial_balance=100000.0,
        owner_id=user.id
    )
    db_session.add(portfolio)
    db_session.commit()
    
    # Test eager loading
    query = db_session.query(Portfolio).with_relationships(Portfolio.owner)
    result = query.first()
    
    assert result.owner is not None
    assert result.owner.email == "test@example.com"

def test_query_with_count(db_session):
    """Test query with relationship count"""
    # Create test data
    portfolio = Portfolio(
        name="Test Portfolio",
        description="Test Description",
        initial_balance=100000.0
    )
    db_session.add(portfolio)
    db_session.commit()
    
    for i in range(5):
        position = Position(
            symbol=f"SYMBOL{i}",
            quantity=100,
            entry_price=100.0,
            current_price=105.0,
            portfolio_id=portfolio.id
        )
        db_session.add(position)
    db_session.commit()
    
    # Test relationship count
    query = db_session.query(Portfolio).with_count(Portfolio.positions)
    result = query.first()
    
    assert result.positions_count == 5

def test_query_with_exists(db_session):
    """Test query with exists check"""
    # Create test data
    portfolio = Portfolio(
        name="Test Portfolio",
        description="Test Description",
        initial_balance=100000.0
    )
    db_session.add(portfolio)
    db_session.commit()
    
    position = Position(
        symbol="TEST",
        quantity=100,
        entry_price=100.0,
        current_price=105.0,
        portfolio_id=portfolio.id
    )
    db_session.add(position)
    db_session.commit()
    
    # Test exists check
    query = db_session.query(Portfolio).with_exists(Portfolio.positions)
    result = query.first()
    
    assert result.has_positions is True

def test_query_with_defer(db_session):
    """Test query with deferred loading"""
    # Create test data
    strategy = Strategy(
        name="Test Strategy",
        description="Test Description",
        type="trend_following",
        parameters={"param": 1}
    )
    db_session.add(strategy)
    db_session.commit()
    
    # Test deferred loading
    query = db_session.query(Strategy).with_defer(Strategy.parameters)
    result = query.first()
    
    assert result.name == "Test Strategy"
    assert result.description == "Test Description"
    assert result.type == "trend_following"
    assert not hasattr(result, "parameters")

def test_query_with_selectinload(db_session):
    """Test query with selectin loading"""
    # Create test data
    portfolio = Portfolio(
        name="Test Portfolio",
        description="Test Description",
        initial_balance=100000.0
    )
    db_session.add(portfolio)
    db_session.commit()
    
    for i in range(3):
        position = Position(
            symbol=f"SYMBOL{i}",
            quantity=100,
            entry_price=100.0,
            current_price=105.0,
            portfolio_id=portfolio.id
        )
        db_session.add(position)
    db_session.commit()
    
    # Test selectin loading
    query = db_session.query(Portfolio).with_selectinload(Portfolio.positions)
    result = query.first()
    
    assert len(result.positions) == 3
    assert all(isinstance(pos, Position) for pos in result.positions)

def test_query_with_joinedload(db_session):
    """Test query with joined loading"""
    # Create test data
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    
    portfolio = Portfolio(
        name="Test Portfolio",
        description="Test Description",
        initial_balance=100000.0,
        owner_id=user.id
    )
    db_session.add(portfolio)
    db_session.commit()
    
    # Test joined loading
    query = db_session.query(Portfolio).with_joinedload(Portfolio.owner)
    result = query.first()
    
    assert result.owner is not None
    assert result.owner.email == "test@example.com"

def test_query_with_subqueryload(db_session):
    """Test query with subquery loading"""
    # Create test data
    portfolio = Portfolio(
        name="Test Portfolio",
        description="Test Description",
        initial_balance=100000.0
    )
    db_session.add(portfolio)
    db_session.commit()
    
    for i in range(3):
        position = Position(
            symbol=f"SYMBOL{i}",
            quantity=100,
            entry_price=100.0,
            current_price=105.0,
            portfolio_id=portfolio.id
        )
        db_session.add(position)
    db_session.commit()
    
    # Test subquery loading
    query = db_session.query(Portfolio).with_subqueryload(Portfolio.positions)
    result = query.first()
    
    assert len(result.positions) == 3
    assert all(isinstance(pos, Position) for pos in result.positions)

def test_query_with_dynamic(db_session):
    """Test query with dynamic loading"""
    # Create test data
    portfolio = Portfolio(
        name="Test Portfolio",
        description="Test Description",
        initial_balance=100000.0
    )
    db_session.add(portfolio)
    db_session.commit()
    
    for i in range(3):
        position = Position(
            symbol=f"SYMBOL{i}",
            quantity=100,
            entry_price=100.0,
            current_price=105.0,
            portfolio_id=portfolio.id
        )
        db_session.add(position)
    db_session.commit()
    
    # Test dynamic loading
    query = db_session.query(Portfolio).with_dynamic(Portfolio.positions)
    result = query.first()
    
    positions = result.positions.all()
    assert len(positions) == 3
    assert all(isinstance(pos, Position) for pos in positions)

def test_query_with_contains_eager(db_session):
    """Test query with contains eager loading"""
    # Create test data
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    
    portfolio = Portfolio(
        name="Test Portfolio",
        description="Test Description",
        initial_balance=100000.0,
        owner_id=user.id
    )
    db_session.add(portfolio)
    db_session.commit()
    
    # Test contains eager loading
    query = db_session.query(Portfolio).join(Portfolio.owner).with_contains_eager(Portfolio.owner)
    result = query.first()
    
    assert result.owner is not None
    assert result.owner.email == "test@example.com"

def test_query_with_immediateload(db_session):
    """Test query with immediate loading"""
    # Create test data
    portfolio = Portfolio(
        name="Test Portfolio",
        description="Test Description",
        initial_balance=100000.0
    )
    db_session.add(portfolio)
    db_session.commit()
    
    for i in range(3):
        position = Position(
            symbol=f"SYMBOL{i}",
            quantity=100,
            entry_price=100.0,
            current_price=105.0,
            portfolio_id=portfolio.id
        )
        db_session.add(position)
    db_session.commit()
    
    # Test immediate loading
    query = db_session.query(Portfolio).with_immediateload(Portfolio.positions)
    result = query.first()
    
    assert len(result.positions) == 3
    assert all(isinstance(pos, Position) for pos in result.positions) 