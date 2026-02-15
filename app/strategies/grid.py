from typing import List, Dict, Optional
import numpy as np
from app.services.paper_trading import paper_trading_service

class GridStrategy:
    def __init__(self, 
                 symbol: str, 
                 lower_range: float, 
                 upper_range: float, 
                 grid_count: int, 
                 investment: float):
        self.symbol = symbol
        self.lower_range = lower_range
        self.upper_range = upper_range
        self.grid_count = grid_count
        self.investment = investment
        self.is_active = False
        
        # Calculate grid lines
        self.grids = np.linspace(lower_range, upper_range, grid_count).tolist()
        self.buy_orders: List[Dict] = []
        self.sell_orders: List[Dict] = []
        self.active_grid_index: Optional[int] = None

    async def initialize(self):
        """Place initial orders based on current price."""
        current_price = await paper_trading_service.get_quote(self.symbol)
        qty_per_grid = (self.investment / self.grid_count) / current_price
        qty_per_grid = max(1, int(qty_per_grid)) # Ensure at least 1 share

        print(f"Initializing Grid Bot for {self.symbol} at {current_price:.2f}")
        print(f"Grids: {self.grids}")

        # Find where current price is in the grid
        # For simplicity in this 'Fornow' version:
        # Buy everything below current price
        # Set Sell orders for everything above
        
        for i, level in enumerate(self.grids):
            if level < current_price:
                # Place Buy Order (Limit - simplified to Market for immediate fill if below)
                # In real grid, we'd place limit orders. 
                # For paper simulation, we'll assume we buy the 'dip' levels immediately if we are starting freshly?
                # Actually, standard grid bot starts by buying base asset.
                pass
            else:
                # Place Sell Order target
                pass
        
        self.is_active = True
        return {
            "status": "active",
            "grids": self.grids,
            "current_price": current_price
        }

    async def execute_step(self):
        """Check current price and trigger grid orders."""
        if not self.is_active: 
            return

        current_price = await paper_trading_service.get_quote(self.symbol)
        
        # Check for grid crossings
        # We need to know previous price or last active grid
        # For this simple version, we find the closest grid level
        
        closest_grid_idx = min(range(len(self.grids)), key=lambda i: abs(self.grids[i] - current_price))
        
        # Initialize if not set
        if self.active_grid_index is None:
            self.active_grid_index = closest_grid_idx
            return

        qty_per_grid = max(1, int((self.investment / self.grid_count) / current_price))

        # Price moved UP (Crossed grid line above)
        # e.g. Active=3, Closest=4. We crossed line 4. SELL.
        if closest_grid_idx > self.active_grid_index:
            # Sell logic
            # Verify we have holding to sell? For paper grid, we assume we bought initial batch or we short?
            # Standard Grid: Buy orders below, Sell orders above.
            # If we cross UP, we execute the SELL order at that level.
            await paper_trading_service.place_order(self.symbol, qty_per_grid, "SELL", "MARKET")
            print(f"GRID SELL: {self.symbol} @ {current_price}")
            self.active_grid_index = closest_grid_idx
            
        # Price moved DOWN (Crossed grid line below)
        # e.g. Active=3, Closest=2. We crossed line 2. BUY.
        elif closest_grid_idx < self.active_grid_index:
            # Buy logic
            await paper_trading_service.place_order(self.symbol, qty_per_grid, "BUY", "MARKET")
            print(f"GRID BUY: {self.symbol} @ {current_price}")
            self.active_grid_index = closest_grid_idx

# Global Store for active bots
active_bots: Dict[str, GridStrategy] = {}
