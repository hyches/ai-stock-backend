from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api import api_router

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

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "AI Trading System API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ai-trading-backend"}

@app.get("/test")
def test_endpoint():
    return {"message": "Test endpoint working"}