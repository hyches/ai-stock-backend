from typing import List
from app.models.stock import StockIn, StockOut
from app.utils.data_loader import fetch_stock_data
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)

class StockScreener:
    """
    Service for screening stocks based on various criteria.
    """
    
    # List of stock symbols to screen (Indian stocks with .BO suffix for BSE)
    STOCK_SYMBOLS = [
        # Technology
        "TCS.BO", "INFY.BO", "WIPRO.BO",
        # Banking & Finance
        "HDFCBANK.BO", "ICICIBANK.BO",
        # FMCG
        "HINDUNILVR.BO", "ITC.BO",
        # Energy
        "RELIANCE.BO", "ONGC.BO",
        # Healthcare
        "SUNPHARMA.BO", "DRREDDY.BO",
        # Auto
        "MARUTI.BO", "TATAMOTORS.BO"
    ]
    
    # Sector mapping for more flexible matching
    SECTOR_MAPPING = {
        "Technology": ["Technology", "Information Technology", "IT", "Software", "Computer Services"],
        "Finance": ["Financial Services", "Banking", "Finance", "Banks"],
        "FMCG": ["Consumer Defensive", "Consumer Goods", "FMCG", "Consumer Products"],
        "Energy": ["Energy", "Oil & Gas", "Petroleum"],
        "Healthcare": ["Healthcare", "Pharmaceuticals", "Medical", "Drug Manufacturers"],
        "Auto": ["Automotive", "Auto", "Transportation", "Auto Manufacturers"]
    }
    
    async def screen_stocks(self, criteria: StockIn) -> List[StockOut]:
        """
        Screen stocks based on the provided criteria.
        
        Args:
            criteria: StockIn object containing screening parameters
            
        Returns:
            List of StockOut objects matching the criteria
        """
        logger.info(f"Starting stock screening with criteria: {criteria}")
        
        # Process stocks in batches of 3 to avoid rate limits
        batch_size = 3
        results = []
        
        for i in range(0, len(self.STOCK_SYMBOLS), batch_size):
            batch = self.STOCK_SYMBOLS[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}: {batch}")
            
            # Fetch data for current batch
            tasks = [fetch_stock_data(symbol) for symbol in batch]
            stock_data_list = await asyncio.gather(*tasks)
            
            # Filter stocks based on criteria
            for stock_data in stock_data_list:
                if not stock_data:
                    continue
                    
                # Apply screening criteria
                if not self._meets_criteria(stock_data, criteria):
                    continue
                    
                # Convert to StockOut model
                results.append(StockOut(**stock_data))
            
            # Add a small delay between batches
            if i + batch_size < len(self.STOCK_SYMBOLS):
                await asyncio.sleep(1)
            
        logger.info(f"Found {len(results)} stocks matching criteria")
        return results
    
    def _meets_criteria(self, stock_data: dict, criteria: StockIn) -> bool:
        """
        Check if a stock meets all the screening criteria.
        
        Args:
            stock_data: Dictionary containing stock data
            criteria: StockIn object containing screening parameters
            
        Returns:
            True if stock meets all criteria, False otherwise
        """
        # Sector filter with flexible matching
        if criteria.sector:
            sector_match = False
            target_sectors = self.SECTOR_MAPPING.get(criteria.sector, [criteria.sector])
            stock_sector = stock_data.get('sector', '').lower()
            stock_industry = stock_data.get('industry', '').lower()
            
            for target_sector in target_sectors:
                if (target_sector.lower() in stock_sector or 
                    target_sector.lower() in stock_industry):
                    sector_match = True
                    break
                    
            if not sector_match:
                logger.debug(f"{stock_data['symbol']} filtered out: sector mismatch (got {stock_sector}/{stock_industry})")
                return False
            
        # Volume filter
        if criteria.min_volume and stock_data['volume'] < criteria.min_volume:
            logger.debug(f"{stock_data['symbol']} filtered out: volume too low")
            return False
            
        # P/E ratio filter
        if criteria.max_pe and stock_data['pe_ratio'] and stock_data['pe_ratio'] > criteria.max_pe:
            logger.debug(f"{stock_data['symbol']} filtered out: P/E ratio too high")
            return False
            
        # Market cap filter
        if criteria.min_market_cap and stock_data['market_cap'] < criteria.min_market_cap:
            logger.debug(f"{stock_data['symbol']} filtered out: market cap too low")
            return False
            
        # Price range filter
        if criteria.min_price and stock_data['price'] < criteria.min_price:
            logger.debug(f"{stock_data['symbol']} filtered out: price too low")
            return False
        if criteria.max_price and stock_data['price'] > criteria.max_price:
            logger.debug(f"{stock_data['symbol']} filtered out: price too high")
            return False
            
        # Dividend yield filter
        if criteria.min_dividend_yield and stock_data['dividend_yield'] and stock_data['dividend_yield'] < criteria.min_dividend_yield:
            logger.debug(f"{stock_data['symbol']} filtered out: dividend yield too low")
            return False
            
        # Technical analysis: Price > 50-day MA > 200-day MA (Golden Cross)
        if stock_data['ma_50'] and stock_data['ma_200']:
            if not (stock_data['price'] > stock_data['ma_50'] > stock_data['ma_200']):
                logger.debug(f"{stock_data['symbol']} filtered out: technical analysis failed")
                return False
                
        logger.debug(f"{stock_data['symbol']} passed all criteria")
        return True 