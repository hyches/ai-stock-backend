from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.endpoints import screener

app = FastAPI(
    title="AI Stock Portfolio API",
    description="Backend API for AI-driven stock portfolio management",
    version="1.0.0",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(screener.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Stock Portfolio API",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "environment": settings.ENVIRONMENT
    } 