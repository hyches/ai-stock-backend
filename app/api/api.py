from fastapi import APIRouter
from app.api.endpoints import (
    auth, market_simple, market_data, ml, ml_analysis, settings, backup, 
    portfolio, trading, research, research_ml, screener, dashboard,
    backtest_pro, risk_pro, execution_pro, reports_pro, agents
)

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(market_simple.router, prefix="/market", tags=["market"])
api_router.include_router(market_data.router, prefix="/market", tags=["market-data"])
api_router.include_router(ml.router, prefix="/ml", tags=["ml"])
api_router.include_router(ml_analysis.router, prefix="/ml", tags=["ml-analysis"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(backup.router, prefix="/backup", tags=["backup"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(trading.router, prefix="/trading", tags=["trading"])
api_router.include_router(execution_pro.router, prefix="/trading", tags=["trading-pro"])
api_router.include_router(research.router, prefix="/research", tags=["research"])
api_router.include_router(research_ml.router, prefix="/research-ml", tags=["research-ml"])
api_router.include_router(screener.router, prefix="/screener", tags=["screener"])
api_router.include_router(backtest_pro.router, prefix="/backtest", tags=["backtest-pro"])
api_router.include_router(risk_pro.router, prefix="/risk", tags=["risk-pro"])
api_router.include_router(reports_pro.router, prefix="/reports", tags=["reports-pro"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])