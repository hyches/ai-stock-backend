from fastapi import APIRouter, HTTPException
from app.models.report import ReportRequest, ReportResponse
from app.services.report_generator import ReportGenerator, generate_research_report
import logging
from typing import Dict, Any

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """
    Generate a research report for a given stock.
    
    Args:
        request: ReportRequest object containing stock symbol and report options
        
    Returns:
        ReportResponse object containing the generated report
    """
    try:
        logger.info(f"Generating research report for {request.symbol}")
        
        # Initialize report generator
        generator = ReportGenerator()
        
        # Generate report
        report = await generator.generate_report(
            symbol=request.symbol,
            include_technical=request.include_technical,
            include_sentiment=request.include_sentiment,
            include_competitors=request.include_competitors,
            format=request.format
        )
        
        logger.info(f"Successfully generated report for {request.symbol}")
        return report
        
    except Exception as e:
        logger.error(f"Error generating report for {request.symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )

@router.get("/research/{symbol}", response_model=Dict[str, Any])
async def get_research_report(symbol: str):
    """
    Generate a comprehensive research report for a given stock symbol.
    """
    try:
        report = generate_research_report(symbol)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 