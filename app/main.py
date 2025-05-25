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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
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

@app.get("/")
async def root():
    return {"message": "Welcome to AI Stock Analysis Platform"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

settings = Settings() 