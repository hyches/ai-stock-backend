"""
Real-Time Market Data WebSocket Endpoints
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Set, Dict
import asyncio
import json
import logging
from app.services.websocket_manager import websocket_manager, BrokerType
from app.services.market_data import market_data_service
from app.core.security import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Active WebSocket connections
active_connections: Set[WebSocket] = set()


@router.websocket("/ws/market-data")
async def websocket_market_data(websocket: WebSocket):
    """
    WebSocket endpoint for real-time market data streaming
    
    Client sends: {"action": "subscribe", "symbols": ["NSE:RELIANCE", "NSE:TCS"]}
    Server sends: {"type": "tick", "data": {...}}
    """
    await websocket.accept()
    active_connections.add(websocket)
    
    subscribed_symbols: Set[str] = set()
    queues: Dict[str, asyncio.Queue] = {}
    
    try:
        # Start listening task
        async def send_updates():
            while True:
                # Check all subscribed queues
                for symbol in list(subscribed_symbols):
                    if symbol in queues:
                        try:
                            data = await asyncio.wait_for(queues[symbol].get(), timeout=0.1)
                            await websocket.send_json({
                                "type": "tick",
                                "symbol": symbol,
                                "data": data
                            })
                        except asyncio.TimeoutError:
                            continue
                        except Exception as e:
                            logger.error(f"Error sending update: {e}")
                
                await asyncio.sleep(0.01)  # Small delay to prevent busy loop
        
        send_task = asyncio.create_task(send_updates())
        
        # Handle incoming messages
        while True:
            message = await websocket.receive_json()
            action = message.get("action")
            
            if action == "subscribe":
                symbols = message.get("symbols", [])
                for symbol in symbols:
                    if symbol not in subscribed_symbols:
                        subscribed_symbols.add(symbol)
                        # Subscribe to market data service
                        queues[symbol] = await market_data_service.subscribe_ticks(symbol)
                        logger.info(f"Client subscribed to {symbol}")
            
            elif action == "unsubscribe":
                symbols = message.get("symbols", [])
                for symbol in symbols:
                    if symbol in subscribed_symbols:
                        subscribed_symbols.discard(symbol)
                        if symbol in queues:
                            del queues[symbol]
                        logger.info(f"Client unsubscribed from {symbol}")
            
            elif action == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        send_task.cancel()
        active_connections.discard(websocket)
        # Clean up subscriptions
        for symbol in subscribed_symbols:
            if symbol in queues:
                del queues[symbol]


@router.websocket("/ws/order-book/{symbol}")
async def websocket_order_book(websocket: WebSocket, symbol: str):
    """
    WebSocket endpoint for real-time order book depth
    
    Server sends: {"type": "depth", "data": {"bids": [...], "asks": [...]}}
    """
    await websocket.accept()
    
    try:
        # Subscribe to depth updates
        queue = await market_data_service.subscribe_depth(symbol)
        
        while True:
            try:
                depth_data = await asyncio.wait_for(queue.get(), timeout=1.0)
                await websocket.send_json({
                    "type": "depth",
                    "data": depth_data
                })
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_json({"type": "ping"})
    
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from order book {symbol}")
    except Exception as e:
        logger.error(f"Order book WebSocket error: {e}")


@router.get("/market-data/latest/{symbol}")
async def get_latest_tick(symbol: str):
    """Get latest tick data for a symbol"""
    tick = market_data_service.get_latest_tick(symbol)
    if not tick:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
    return tick.to_dict()


@router.get("/market-data/depth/{symbol}")
async def get_order_book_depth(symbol: str):
    """Get current order book depth"""
    depth = market_data_service.get_latest_depth(symbol)
    if not depth:
        raise HTTPException(status_code=404, detail=f"No depth data for {symbol}")
    return depth.to_dict()


@router.get("/market-data/vwap/{symbol}")
async def get_vwap(symbol: str, minutes: int = 60):
    """Get Volume Weighted Average Price"""
    vwap = market_data_service.calculate_vwap(symbol, minutes)
    return {"symbol": symbol, "vwap": vwap, "minutes": minutes}


@router.get("/market-data/volume-profile/{symbol}")
async def get_volume_profile(symbol: str):
    """Get volume profile (price distribution)"""
    profile = market_data_service.get_volume_profile(symbol)
    return {"symbol": symbol, "profile": profile}
