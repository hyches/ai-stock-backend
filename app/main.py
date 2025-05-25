from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.api import api_router
from app.core.security import (
    rate_limit_middleware,
    security_headers_middleware,
    request_size_limit_middleware,
    csrf_middleware,
    validate_api_key
)
from app.config import Settings
from typing import Union
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from app.api.endpoints import zerodha
from app.middleware.error_handler import setup_error_handlers
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.core.middleware import RequestLoggingMiddleware
from app.core.middleware import ErrorHandlingMiddleware
from app.core.middleware import MetricsMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.SERVER_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error handler caught: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)}
    )

# Add security middleware
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(security_headers_middleware)
app.middleware("http")(request_size_limit_middleware)

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

# Include API router with API key validation
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

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to the Trading System API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/db-test")
async def test_db(db: Session = Depends(get_db)):
    """Test database connection"""
    try:
        # Try to execute a simple query
        db.execute("SELECT 1")
        return {"status": "Database connection successful"}
    except Exception as e:
        return {"status": "Database connection failed", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True
    )

settings = Settings() 