from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from app.api.api import api_router
from app.core.security import (
    rate_limit_middleware,
    security_headers_middleware,
    request_size_limit_middleware,
    csrf_middleware,
    validate_api_key
)
from app.config import Settings
from fastapi.exceptions import RequestValidationError
from app.api.endpoints import zerodha
from app.middleware.error_handler import setup_error_handlers
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.core.middleware import (
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware,
    MetricsMiddleware
)
import logging
import time
from prometheus_client import Counter, Histogram, generate_latest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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

app = FastAPI(
    title=settings.SERVER_NAME,
    description="AI-Powered Trading System API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error handler caught: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc), "errors": exc.errors()}
    )

# Add security middleware
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(security_headers_middleware)
app.middleware("http")(request_size_limit_middleware)
app.middleware("http")(csrf_middleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up error handlers
setup_error_handlers(app)

# Include API routers
app.include_router(
    api_router,
    prefix=settings.API_V1_STR,
    dependencies=[Depends(validate_api_key)]
)

app.include_router(
    zerodha.router,
    prefix="/api/v1/zerodha",
    tags=["zerodha"]
)

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
if settings.ENABLE_METRICS:
    app.add_middleware(MetricsMiddleware)

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to the Trading System API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time(),
        "services": {
            "database": "connected",
            "redis": "connected",
            "api": "operational"
        }
    }

@app.get("/metrics")
async def metrics():
    """Metrics endpoint for Prometheus"""
    return Response(generate_latest(), media_type="text/plain")

@app.get("/db-test")
async def test_db(db: Session = Depends(get_db)):
    """Test database connection"""
    try:
        # Try to execute a simple query
        db.execute("SELECT 1")
        return {"status": "Database connection successful"}
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return {"status": "Database connection failed", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
        log_level="info"
    )

settings = Settings() 