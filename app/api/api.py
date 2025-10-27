from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    market_data,
    ml,
    portfolios,
    strategies,
    trading,
    users,
    backtests,
    positions,
    signals,
    trades,
    alerts,
)

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(market_data.router, prefix="/market_data", tags=["market_data"])
api_router.include_router(ml.router, prefix="/ml", tags=["ml"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["portfolios"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(trading.router, prefix="/trading", tags=["trading"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(backtests.router, prefix="/backtests", tags=["backtests"])
api_router.include_router(positions.router, prefix="/positions", tags=["positions"])
api_router.include_router(signals.router, prefix="/signals", tags=["signals"])
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
