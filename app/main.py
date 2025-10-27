from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api import api_router
from app.core.ratelimit import redis_rate_limiter
from fastapi import Request

# Import all models to ensure they are registered with SQLAlchemy
from app.models import *  # noqa

app = FastAPI(
    title=settings.SERVER_NAME,
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.middleware("http")
async def rate_limiter_middleware(request: Request, call_next):
    return await redis_rate_limiter(request, call_next)

from app.middleware.security_headers import security_headers_middleware
app.middleware("http")(security_headers_middleware)

from app.middleware.error_handler import setup_error_handlers

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Set up error handlers
setup_error_handlers(app)

@app.get("/")
def read_root():
    return {"message": "AI Trading System API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ai-trading-backend"}

@app.get("/test")
def test_endpoint():
    return {"message": "Test endpoint working"}
