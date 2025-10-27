import pytest
import asyncio
import time
from typing import List, Dict
from sqlalchemy import text
from app.db.session import SessionLocal
from app.core.cache import Cache
from app.models.trading import Strategy, Trade, Position
from app.models.portfolio import PortfolioOutput as Portfolio
from app.services.trading import TradingService

@pytest.fixture
def db_session():
    """Create database session"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
async def cache(redis_client):
    """Create cache instance"""
    return Cache(redis_client)

@pytest.fixture
def trading_service(db_session):
    """Create trading service instance"""
    return TradingService(db_session)

async def benchmark_cache_operations(cache: Cache, iterations: int = 1000):
    """Benchmark cache operations"""
    # Test simple key-value operations
    start_time = time.time()
    for i in range(iterations):
        await cache.set(f"key_{i}", f"value_{i}")
    set_time = time.time() - start_time
    
    start_time = time.time()
    for i in range(iterations):
        await cache.get(f"key_{i}")
    get_time = time.time() - start_time
    
    # Test complex object operations
    complex_obj = {
        "name": "test",
        "values": list(range(100)),
        "nested": {
            "key": "value",
            "array": [{"id": i, "value": f"value_{i}"} for i in range(10)]
        }
    }
    
    start_time = time.time()
    for i in range(iterations):
        await cache.set(f"complex_{i}", complex_obj)
    complex_set_time = time.time() - start_time
    
    start_time = time.time()
    for i in range(iterations):
        await cache.get(f"complex_{i}")
    complex_get_time = time.time() - start_time
    
    return {
        "simple_set": set_time / iterations * 1000,  # ms per operation
        "simple_get": get_time / iterations * 1000,
        "complex_set": complex_set_time / iterations * 1000,
        "complex_get": complex_get_time / iterations * 1000
    }

async def benchmark_concurrent_cache_operations(cache: Cache, concurrent_tasks: int = 100):
    """Benchmark concurrent cache operations"""
    async def cache_operation(i: int):
        await cache.set(f"concurrent_{i}", f"value_{i}")
        return await cache.get(f"concurrent_{i}")
    
    start_time = time.time()
    tasks = [cache_operation(i) for i in range(concurrent_tasks)]
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    return {
        "total_time": total_time * 1000,  # ms
        "operations_per_second": concurrent_tasks / total_time,
        "avg_time_per_operation": total_time / concurrent_tasks * 1000  # ms
    }

def benchmark_database_operations(db_session, iterations: int = 1000):
    """Benchmark database operations"""
    # Test bulk insert
    start_time = time.time()
    strategies = [
        Strategy(
            name=f"Strategy {i}",
            description=f"Description {i}",
            type="trend_following",
            parameters={"param": i}
        )
        for i in range(iterations)
    ]
    db_session.bulk_save_objects(strategies)
    db_session.commit()
    bulk_insert_time = time.time() - start_time
    
    # Test individual inserts
    start_time = time.time()
    for i in range(iterations):
        strategy = Strategy(
            name=f"Single Strategy {i}",
            description=f"Single Description {i}",
            type="trend_following",
            parameters={"param": i}
        )
        db_session.add(strategy)
        db_session.commit()
    single_insert_time = time.time() - start_time
    
    # Test query performance
    start_time = time.time()
    for i in range(iterations):
        db_session.query(Strategy).filter(Strategy.name.like(f"%{i}%")).all()
    query_time = time.time() - start_time
    
    # Test relationship loading
    portfolio = Portfolio(
        name="Test Portfolio",
        description="Test Description",
        initial_balance=100000.0
    )
    db_session.add(portfolio)
    db_session.commit()
    
    positions = [
        Position(
            symbol=f"SYMBOL{i}",
            quantity=100,
            entry_price=100.0,
            current_price=105.0,
            portfolio_id=portfolio.id
        )
        for i in range(100)
    ]
    db_session.bulk_save_objects(positions)
    db_session.commit()
    
    start_time = time.time()
    for _ in range(iterations):
        db_session.query(Portfolio).with_relationships(Portfolio.positions).first()
    relationship_time = time.time() - start_time
    
    return {
        "bulk_insert": bulk_insert_time / iterations * 1000,  # ms per operation
        "single_insert": single_insert_time / iterations * 1000,
        "query": query_time / iterations * 1000,
        "relationship_loading": relationship_time / iterations * 1000
    }

async def benchmark_trading_service(trading_service: TradingService, iterations: int = 100):
    """Benchmark trading service operations"""
    # Test strategy operations
    start_time = time.time()
    for i in range(iterations):
        strategy = await trading_service.create_strategy({
            "name": f"Benchmark Strategy {i}",
            "description": f"Description {i}",
            "type": "trend_following",
            "parameters": {"param": i}
        })
    strategy_create_time = time.time() - start_time
    
    # Test portfolio operations
    start_time = time.time()
    for i in range(iterations):
        portfolio = await trading_service.create_portfolio({
            "name": f"Benchmark Portfolio {i}",
            "description": f"Description {i}",
            "initial_balance": 100000.0
        })
    portfolio_create_time = time.time() - start_time
    
    # Test position operations
    start_time = time.time()
    for i in range(iterations):
        position = await trading_service.create_position({
            "symbol": f"SYMBOL{i}",
            "quantity": 100,
            "entry_price": 100.0,
            "current_price": 105.0
        })
    position_create_time = time.time() - start_time
    
    # Test backtest operations
    start_time = time.time()
    for i in range(iterations):
        backtest = await trading_service.run_backtest({
            "strategy_id": 1,
            "symbol": "AAPL",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "initial_balance": 100000.0
        })
    backtest_time = time.time() - start_time
    
    return {
        "strategy_create": strategy_create_time / iterations * 1000,  # ms per operation
        "portfolio_create": portfolio_create_time / iterations * 1000,
        "position_create": position_create_time / iterations * 1000,
        "backtest": backtest_time / iterations * 1000
    }

def test_cache_performance(cache):
    """Test cache performance"""
    results = asyncio.run(benchmark_cache_operations(cache))
    print("\nCache Performance Results:")
    print(f"Simple Set: {results['simple_set']:.2f} ms/op")
    print(f"Simple Get: {results['simple_get']:.2f} ms/op")
    print(f"Complex Set: {results['complex_set']:.2f} ms/op")
    print(f"Complex Get: {results['complex_get']:.2f} ms/op")
    
    # Assert performance requirements
    assert results['simple_set'] < 1.0  # Less than 1ms per operation
    assert results['simple_get'] < 0.5  # Less than 0.5ms per operation
    assert results['complex_set'] < 2.0  # Less than 2ms per operation
    assert results['complex_get'] < 1.0  # Less than 1ms per operation

def test_concurrent_cache_performance(cache):
    """Test concurrent cache performance"""
    results = asyncio.run(benchmark_concurrent_cache_operations(cache))
    print("\nConcurrent Cache Performance Results:")
    print(f"Total Time: {results['total_time']:.2f} ms")
    print(f"Operations/Second: {results['operations_per_second']:.2f}")
    print(f"Average Time/Operation: {results['avg_time_per_operation']:.2f} ms")
    
    # Assert performance requirements
    assert results['operations_per_second'] > 1000  # More than 1000 ops/sec
    assert results['avg_time_per_operation'] < 1.0  # Less than 1ms per operation

def test_database_performance(db_session):
    """Test database performance"""
    results = benchmark_database_operations(db_session)
    print("\nDatabase Performance Results:")
    print(f"Bulk Insert: {results['bulk_insert']:.2f} ms/op")
    print(f"Single Insert: {results['single_insert']:.2f} ms/op")
    print(f"Query: {results['query']:.2f} ms/op")
    print(f"Relationship Loading: {results['relationship_loading']:.2f} ms/op")
    
    # Assert performance requirements
    assert results['bulk_insert'] < 0.1  # Less than 0.1ms per operation
    assert results['single_insert'] < 5.0  # Less than 5ms per operation
    assert results['query'] < 1.0  # Less than 1ms per operation
    assert results['relationship_loading'] < 2.0  # Less than 2ms per operation

def test_trading_service_performance(trading_service):
    """Test trading service performance"""
    results = asyncio.run(benchmark_trading_service(trading_service))
    print("\nTrading Service Performance Results:")
    print(f"Strategy Create: {results['strategy_create']:.2f} ms/op")
    print(f"Portfolio Create: {results['portfolio_create']:.2f} ms/op")
    print(f"Position Create: {results['position_create']:.2f} ms/op")
    print(f"Backtest: {results['backtest']:.2f} ms/op")
    
    # Assert performance requirements
    assert results['strategy_create'] < 10.0  # Less than 10ms per operation
    assert results['portfolio_create'] < 10.0  # Less than 10ms per operation
    assert results['position_create'] < 10.0  # Less than 10ms per operation
    assert results['backtest'] < 100.0  # Less than 100ms per operation 