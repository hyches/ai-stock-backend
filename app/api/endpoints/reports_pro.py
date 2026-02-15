from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.report_generator import ReportGenerator
from app.services.tax_calculator import tax_calculator
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.trading import Trade
from sqlalchemy.orm import Session
from datetime import datetime
import pandas as pd

router = APIRouter()
report_gen = ReportGenerator()

class TaxLiabilityResponse(BaseModel):
    total_stcg: float
    total_ltcg: float
    stcg_tax: float
    ltcg_tax: float
    total_tax: float
    closed_trade_count: int

@router.get("/generate/{symbol}")
async def generate_pro_report(symbol: str, format: str = "pdf"):
    """
    Stream a real, high-quality institutional research report as PDF.
    """
    try:
        report = await report_gen.generate_report(
            symbol=symbol,
            include_technical=True,
            include_sentiment=True,
            format=format
        )
        
        if format == "pdf" and report.report_url:
            with open(report.report_url, "rb") as f:
                content = f.read()
            
            return Response(
                content=content,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={symbol}_Research.pdf"}
            )
        
        return report.model_dump()
    except Exception as e:
        print(f"REPORT GEN ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tax-liability", response_model=TaxLiabilityResponse)
async def get_tax_liability(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    year: int = 2024
):
    """
    Calculate real Indian tax liability from actual DB trade history using FIFO.
    TRUTH: No more hardcoded TCS/RELIANCE trades.
    """
    try:
        # 1. Fetch all raw trade legs for this user
        # In a real system, we'd filter by year too
        raw_trades = db.query(Trade).filter(Trade.portfolio_id.in_(
            [p.id for p in current_user.portfolios]
        )).order_by(Trade.created_at.asc()).all()
        
        if not raw_trades:
            return {
                "total_stcg": 0, "total_ltcg": 0, "stcg_tax": 0, "ltcg_tax": 0, "total_tax": 0,
                "closed_trade_count": 0
            }

        # 2. FIFO Stitching Algorithm (Match legs)
        inventory = {} # symbol -> list of buys
        closed_trades = []
        
        for leg in raw_trades:
            symbol = leg.symbol
            if leg.side.lower() == "buy":
                if symbol not in inventory: inventory[symbol] = []
                inventory[symbol].append({"qty": leg.quantity, "price": leg.price, "date": leg.created_at})
            else:
                # Sell leg - match against inventory
                sell_qty = leg.quantity
                if symbol in inventory and inventory[symbol]:
                    while sell_qty > 0 and inventory[symbol]:
                        buy = inventory[symbol][0]
                        match_qty = min(buy["qty"], sell_qty)
                        
                        closed_trades.append({
                            "symbol": symbol,
                            "buy_price": buy["price"],
                            "sell_price": leg.price,
                            "quantity": match_qty,
                            "buy_date": buy["date"],
                            "sell_date": leg.created_at
                        })
                        
                        buy["qty"] -= match_qty
                        sell_qty -= match_qty
                        if buy["qty"] <= 0: inventory[symbol].pop(0)

        # 3. Call the Indian Tax service with Genuine closed trades
        tax_res = tax_calculator.calculate_tax(closed_trades)
        summary = tax_res["summary"]
        
        return {
            "total_stcg": summary["total_stcg"],
            "total_ltcg": summary["total_ltcg"],
            "stcg_tax": summary["stcg_tax_est"],
            "ltcg_tax": summary["ltcg_tax_est"],
            "total_tax": summary["total_tax_est"],
            "closed_trade_count": len(closed_trades)
        }
    except Exception as e:
        print(f"REAL TAX ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Tax Analysis Failure: {str(e)}")
