"""
Monitoring and metrics for the AI Stock Portfolio Platform Backend.

This module provides Prometheus metrics, health check endpoints, system monitoring, and middleware for tracking requests, cache, and system health.
"""
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.cache import redis_cache
import time
import psutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

DB_CONNECTION_GAUGE = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

CACHE_HITS = Counter(
    'cache_hits_total',
    'Total cache hits'
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Total cache misses'
)

MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes'
)

CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage'
)

# Health check router
router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.

    Returns:
        dict: Health status.
    """
    return {"status": "healthy"}

@router.get("/health/db")
async def db_health_check(db: Session = Depends(get_db)):
    """
    Database health check endpoint.

    Args:
        db (Session): SQLAlchemy database session.
    Returns:
        dict: Database health status.
    """
    try:
        # Try to execute a simple query
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {"status": "unhealthy", "database": "disconnected"}

@router.get("/health/cache")
async def cache_health_check():
    """
    Cache health check endpoint.

    Returns:
        dict: Cache health status.
    """
    try:
        redis = redis_cache
        redis.ping()
        return {"status": "healthy", "cache": "connected"}
    except Exception as e:
        logger.error(f"Cache health check failed: {str(e)}")
        return {"status": "unhealthy", "cache": "disconnected"}

@router.get("/metrics")
async def metrics():
    """
    System metrics endpoint.

    Returns:
        dict: System memory, CPU, and disk usage.
    """
    # Update system metrics
    MEMORY_USAGE.set(psutil.Process().memory_info().rss)
    CPU_USAGE.set(psutil.cpu_percent())
    
    return {
        "memory_usage": psutil.Process().memory_info().rss,
        "cpu_usage": psutil.cpu_percent(),
        "disk_usage": psutil.disk_usage('/').percent
    }

class MetricsMiddleware:
    """
    ASGI middleware to collect request metrics for Prometheus.
    """
    def __init__(self, app):
        """
        Initialize the middleware.

        Args:
            app: ASGI application instance.
        """
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """
        Process incoming HTTP requests and record metrics.

        Args:
            scope: ASGI scope.
            receive: ASGI receive callable.
            send: ASGI send callable.
        """
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Record request metrics
                REQUEST_COUNT.labels(
                    method=scope["method"],
                    endpoint=scope["path"],
                    status=message["status"]
                ).inc()
                
                # Record latency
                REQUEST_LATENCY.labels(
                    method=scope["method"],
                    endpoint=scope["path"]
                ).observe(time.time() - start_time)
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)

class CacheMetrics:
    """
    Decorator to collect cache hit/miss metrics for async functions.
    """
    def __init__(self, func):
        """
        Initialize the decorator.

        Args:
            func: Async function to wrap.
        """
        self.func = func
    
    async def __call__(self, *args, **kwargs):
        """
        Call the wrapped function and record cache metrics.

        Returns:
            Any: Result of the wrapped function.
        Raises:
            KeyError: If the wrapped function raises KeyError (cache miss).
        """
        try:
            result = await self.func(*args, **kwargs)
            CACHE_HITS.inc()
            return result
        except KeyError:
            CACHE_MISSES.inc()
            raise

def monitor_db_connections():
    """
    Monitor and update the number of active database connections.
    Runs in a loop, updating the Prometheus gauge every minute.
    """
    while True:
        try:
            db = next(get_db())
            DB_CONNECTION_GAUGE.set(db.execute("SELECT count(*) FROM pg_stat_activity").scalar())
        except Exception as e:
            logger.error(f"Failed to monitor DB connections: {str(e)}")
        time.sleep(60)  # Check every minute

def setup_monitoring():
    """
    Set up Prometheus metrics server if enabled in settings.
    """
    if settings.ENABLE_METRICS:
        start_http_server(settings.METRICS_PORT) 