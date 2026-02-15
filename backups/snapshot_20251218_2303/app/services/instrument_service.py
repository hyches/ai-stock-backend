from typing import Dict, Optional
import logging
from datetime import datetime, timedelta
from app.core.cache import redis_cache
from app.services.zerodha_service import ZerodhaService

logger = logging.getLogger(__name__)

class InstrumentService:
    def __init__(self):
        self.zerodha_service = ZerodhaService()
        self.cache_ttl = 3600  # 1 hour

    async def get_instrument_token(self, symbol: str) -> Optional[int]:
        """Get instrument token for a symbol with caching"""
        cache_key = f"instrument_token:{symbol}"
        
        # Try to get from cache
        cached_token = await redis_cache.get(cache_key)
        if cached_token:
            return int(cached_token)

        try:
            # Get from Zerodha
            instruments = self.zerodha_service.kite.instruments()
            for instrument in instruments:
                if instrument['tradingsymbol'] == symbol:
                    token = instrument['instrument_token']
                    # Cache the result
                    await redis_cache.set(cache_key, str(token), self.cache_ttl)
                    return token
        except Exception as e:
            logger.error(f"Error getting instrument token for {symbol}: {str(e)}")
            return None

    async def get_instrument_details(self, symbol: str) -> Optional[Dict]:
        """Get full instrument details"""
        token = await self.get_instrument_token(symbol)
        if not token:
            return None

        cache_key = f"instrument_details:{symbol}"
        cached_details = await redis_cache.get(cache_key)
        if cached_details:
            return cached_details

        try:
            instruments = self.zerodha_service.kite.instruments()
            for instrument in instruments:
                if instrument['tradingsymbol'] == symbol:
                    await redis_cache.set(cache_key, instrument, self.cache_ttl)
                    return instrument
        except Exception as e:
            logger.error(f"Error getting instrument details for {symbol}: {str(e)}")
            return None

    async def refresh_instruments(self):
        """Refresh instrument cache"""
        try:
            instruments = self.zerodha_service.kite.instruments()
            for instrument in instruments:
                symbol = instrument['tradingsymbol']
                token = instrument['instrument_token']
                
                # Cache token
                await redis_cache.set(
                    f"instrument_token:{symbol}",
                    str(token),
                    self.cache_ttl
                )
                
                # Cache details
                await redis_cache.set(
                    f"instrument_details:{symbol}",
                    instrument,
                    self.cache_ttl
                )
        except Exception as e:
            logger.error(f"Error refreshing instruments: {str(e)}")
            raise 