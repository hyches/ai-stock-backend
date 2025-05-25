from fastapi import APIRouter
from app.api.endpoints import auth, market, ml, settings, backup

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(market.router, prefix="/market", tags=["market"])
api_router.include_router(ml.router, prefix="/ml", tags=["ml"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(backup.router, prefix="/backup", tags=["backup"]) 