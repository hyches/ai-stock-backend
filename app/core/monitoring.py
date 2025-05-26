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
    """Basic health check endpoint"""
    return {"status": "healthy"}

@router.get("/health/db")
async def db_health_check(db: Session = Depends(get_db)):
    """Database health check"""
    try:
        # Try to execute a simple query
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {"status": "unhealthy", "database": "disconnected"}

@router.get("/health/cache")
async def cache_health_check():
    """Cache health check"""
    try:
        redis = redis_cache
        redis.ping()
        return {"status": "healthy", "cache": "connected"}
    except Exception as e:
        logger.error(f"Cache health check failed: {str(e)}")
        return {"status": "unhealthy", "cache": "disconnected"}

@router.get("/metrics")
async def metrics():
    """System metrics endpoint"""
    # Update system metrics
    MEMORY_USAGE.set(psutil.Process().memory_info().rss)
    CPU_USAGE.set(psutil.cpu_percent())
    
    return {
        "memory_usage": psutil.Process().memory_info().rss,
        "cpu_usage": psutil.cpu_percent(),
        "disk_usage": psutil.disk_usage('/').percent
    }

class MetricsMiddleware:
    """Middleware to collect request metrics"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """Handles incoming HTTP requests, recording metrics related to request count and latency.
        Parameters:
            - scope (dict): Contains details about the current request, including type, method, and path.
            - receive (awaitable): Function to receive messages.
            - send (awaitable): Function to send messages.
        Returns:
            - None: This function does not return a value but processes or forwards the request.
        Processing Logic:
            - Ignores non-HTTP requests, forwarding them directly to the wrapped application.
            - Records the count of HTTP requests with labels for method, endpoint, and status when response starts.
            - Measures latency from the start of the request to when the response starts."""
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        start_time = time.time()
        
        async def send_wrapper(message):
            """Send a wrapped message and record metrics for HTTP requests.
            Parameters:
                - message (dict): The message to be sent, including 'type' and potentially 'status'.
            Returns:
                - None: This function does not return a value.
            Processing Logic:
                - Increments the request count based on method, endpoint, and status.
                - Observes and records the latency of the request processing."""
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
    """Decorator to collect cache metrics"""
    
    def __init__(self, func):
        self.func = func
    
    async def __call__(self, *args, **kwargs):
        """Asynchronously calls a function and updates cache metrics.
        Parameters:
            - args (tuple): Positional arguments to pass to the function call.
            - kwargs (dict): Keyword arguments to pass to the function call.
        Returns:
            - result (any): The result from the asynchronous function call.
        Processing Logic:
            - Increments cache hit metric if function execution is successful.
            - Increments cache miss metric and raises an exception if a KeyError occurs."""
        try:
            result = await self.func(*args, **kwargs)
            CACHE_HITS.inc()
            return result
        except KeyError:
            CACHE_MISSES.inc()
            raise

def monitor_db_connections():
    """Monitor database connections"""
    while True:
        try:
            db = next(get_db())
            DB_CONNECTION_GAUGE.set(db.execute("SELECT count(*) FROM pg_stat_activity").scalar())
        except Exception as e:
            logger.error(f"Failed to monitor DB connections: {str(e)}")
        time.sleep(60)  # Check every minute

def setup_monitoring():
    if settings.ENABLE_METRICS:
        start_http_server(settings.METRICS_PORT) 