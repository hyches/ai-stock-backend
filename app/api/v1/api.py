from fastapi import APIRouter
from app.api.v1.endpoints import (
    users,
    portfolios,
    strategies,
    positions,
    trades,
    signals,
    backtests,
    market_data,
    ml
)

api_router = APIRouter()

# User endpoints
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

# Portfolio endpoints
api_router.include_router(
    portfolios.router,
    prefix="/portfolios",
    tags=["portfolios"]
)

# Strategy endpoints
api_router.include_router(
    strategies.router,
    prefix="/strategies",
    tags=["strategies"]
)

# Position endpoints
api_router.include_router(
    positions.router,
    prefix="/positions",
    tags=["positions"]
)

# Trade endpoints
api_router.include_router(
    trades.router,
    prefix="/trades",
    tags=["trades"]
)

# Signal endpoints
api_router.include_router(
    signals.router,
    prefix="/signals",
    tags=["signals"]
)

# Backtest endpoints
api_router.include_router(
    backtests.router,
    prefix="/backtests",
    tags=["backtests"]
)

# Market data endpoints
api_router.include_router(
    market_data.router,
    prefix="/market-data",
    tags=["market-data"]
)

# ML endpoints
api_router.include_router(
    ml.router,
    prefix="/ml",
    tags=["ml"]
)
