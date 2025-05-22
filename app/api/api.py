from fastapi import APIRouter
from app.api.endpoints import backup

api_router = APIRouter()

# Include backup router
api_router.include_router(backup.router, prefix="/backup", tags=["backup"]) 