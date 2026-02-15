from datetime import datetime
import uuid
from typing import Dict, List, Optional
import yfinance as yf
from fastapi import HTTPException

class PaperTradingService:
    def __init__(self, initial_balance: float = 1000000.0):
        self.balance = initial_balance
        self.positions: Dict[str, Dict] = {}  # symbol -> {quantity, avg_price, current_price, pnl}
        self.orders: List[Dict] = []
        self.trade_history: List[Dict] = []
        self.price_cache: Dict[str, tuple] = {} # symbol -> (price, timestamp)
        self.CACHE_TTL = 15 # seconds

    async def get_quote(self, symbol: str) -> float:
        """Fetch live price from yfinance (async wrapper) with Caching."""
        import asyncio
        from datetime import datetime, timedelta

        # Check Cache
        if symbol in self.price_cache:
            price, timestamp = self.price_cache[symbol]
            if datetime.now() - timestamp < timedelta(seconds=self.CACHE_TTL):
                return price

        # Fetch Fresh
        price = await asyncio.to_thread(self._get_quote_sync, symbol)
        
        # Update Cache
        self.price_cache[symbol] = (price, datetime.now())
        return price

    def _get_quote_sync(self, symbol: str) -> float:
        """Blocking yfinance call."""
        try:
            # Auto-append .NS for Indian stocks if missing
            search_symbol = symbol.upper()
            if not search_symbol.endswith(".NS") and not search_symbol.endswith(".BO") and "^" not in search_symbol:
                 search_symbol = f"{symbol}.NS"

            ticker = yf.Ticker(search_symbol)
            # Fast fetch using fast_info or history
            price = ticker.fast_info.last_price
            if price is None:
                # Fallback to history
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
                else:
                    # Retry without suffix if original input was meant to be global? 
                    # For now raise error
                    raise ValueError(f"No price data for {search_symbol}")
            return price
        except Exception as e:
            print(f"Error fetching quote for {symbol} (tried {search_symbol}): {e}")
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")

    async def get_portfolio(self) -> Dict:
        """Calculate current portfolio value with live prices."""
        import asyncio
        
        total_value = self.balance
        current_positions = []
        
        # Prepare Tasks for Parallel Execution
        tasks = []
        symbols = list(self.positions.keys())
        
        for symbol in symbols:
            tasks.append(self.get_quote(symbol))
            
        # Execute in Parallel
        # return_exceptions=True allows some to fail without crashing all
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        price_map = {}
        for sym, res in zip(symbols, results):
            if isinstance(res, Exception):
                price_map[sym] = self.positions[sym]['avg_price'] # Fallback
            else:
                price_map[sym] = res

        for symbol, pos in self.positions.items():
            current_price = price_map.get(symbol, pos['avg_price'])
            
            market_value = current_price * pos['quantity']
            unrealized_pnl = (current_price - pos['avg_price']) * pos['quantity']
            
            # Update position data
            pos['current_price'] = current_price
            pos['market_value'] = market_value
            pos['unrealized_pnl'] = unrealized_pnl
            
            current_positions.append({
                "symbol": symbol,
                "quantity": pos['quantity'],
                "avg_price": pos['avg_price'],
                "current_price": current_price,
                "pnl": unrealized_pnl,
                "value": market_value
            })
            
            total_value += market_value

        return {
            "balance": self.balance,
            "total_value": total_value,
            "positions": current_positions,
            "day_pnl": total_value - 1000000.0 # simplified day pnl
        }

    async def place_order(self, symbol: str, quantity: int, side: str, order_type: str = "MARKET", price: Optional[float] = None) -> Dict:
        """Execute a paper trade."""
        current_price = await self.get_quote(symbol)
        
        if side.upper() == "BUY":
            cost = current_price * quantity
            if cost > self.balance:
                raise HTTPException(status_code=400, detail="Insufficient funds")
            
            # Update Balance
            self.balance -= cost
            
            # Update Position
            if symbol in self.positions:
                pos = self.positions[symbol]
                new_qty = pos['quantity'] + quantity
                new_avg = ((pos['avg_price'] * pos['quantity']) + (current_price * quantity)) / new_qty
                self.positions[symbol] = {
                    "quantity": new_qty,
                    "avg_price": new_avg
                }
            else:
                self.positions[symbol] = {
                    "quantity": quantity,
                    "avg_price": current_price
                }
                
        elif side.upper() == "SELL":
            if symbol not in self.positions or self.positions[symbol]['quantity'] < quantity:
                 raise HTTPException(status_code=400, detail="Insufficient holdings")
            
            # Update Balance
            proceeds = current_price * quantity
            self.balance += proceeds
            
            # Update Position
            pos = self.positions[symbol]
            new_qty = pos['quantity'] - quantity
            
            # Realized PNL calculation
            realized_pnl = (current_price - pos['avg_price']) * quantity
            
            if new_qty == 0:
                del self.positions[symbol]
            else:
                self.positions[symbol]['quantity'] = new_qty
                
        order = {
            "id": str(uuid.uuid4()),
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": current_price,
            "status": "FILLED",
            "timestamp": datetime.now().isoformat()
        }
        self.trade_history.append(order)
        return order

    async def reset_balance(self, amount: float = 1000000.0) -> Dict:
        """Reset or Add funds to the account."""
        self.balance += amount
        return {"balance": self.balance, "message": f"Added {amount} to balance"}

# Global singleton instance
paper_trading_service = PaperTradingService()
