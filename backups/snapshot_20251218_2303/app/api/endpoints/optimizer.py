from fastapi import APIRouter, HTTPException
from app.models.portfolio import PortfolioInput, PortfolioOutput
from app.services.optimizer import PortfolioOptimizer
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/optimize", response_model=PortfolioOutput)
async def optimize_portfolio(input_data: PortfolioInput):
    """
    Optimize portfolio weights based on input parameters.
    
    Args:
        input_data: PortfolioInput object containing stocks, capital, and constraints
        
    Returns:
        PortfolioOutput object with optimized weights and metrics
    """
    try:
        logger.info(f"Received portfolio optimization request for {len(input_data.stocks)} stocks")
        
        # Initialize optimizer
        optimizer = PortfolioOptimizer()
        
        # Optimize portfolio
        result = await optimizer.optimize(
            stocks=input_data.stocks,
            capital=input_data.capital,
            risk_tolerance=input_data.risk_tolerance,
            min_weight=input_data.min_weight,
            max_weight=input_data.max_weight,
            sector_constraints=input_data.sector_constraints
        )
        
        logger.info("Portfolio optimization completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error optimizing portfolio: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize portfolio: {str(e)}"
        ) 