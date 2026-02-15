"""
WebSocket Manager for Real-Time Market Data
Supports multiple broker connections with auto-reconnection
"""

import asyncio
import json
import logging
from typing import Dict, Set, Callable, Optional, Any
from datetime import datetime
from enum import Enum
import aioredis
from collections import defaultdict

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class BrokerType(Enum):
    ANGEL_ONE = "angel_one"
    UPSTOX = "upstox"
    ZERODHA = "zerodha"


class WebSocketManager:
    """
    Manages WebSocket connections to multiple brokers with:
    - Auto-reconnection with exponential backoff
    - Heartbeat monitoring
    - Message buffering
    - Subscription management
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.connections: Dict[BrokerType, Any] = {}
        self.states: Dict[BrokerType, ConnectionState] = {}
        self.subscriptions: Dict[BrokerType, Set[str]] = defaultdict(set)
        self.callbacks: Dict[str, Set[Callable]] = defaultdict(set)
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        
        # Reconnection settings
        self.max_reconnect_attempts = 10
        self.base_reconnect_delay = 1  # seconds
        self.max_reconnect_delay = 60  # seconds
        
        # Heartbeat settings
        self.heartbeat_interval = 30  # seconds
        self.heartbeat_timeout = 10  # seconds
        
        self._running = False
        self._tasks: Set[asyncio.Task] = set()
    
    async def initialize(self):
        """Initialize Redis connection for pub/sub"""
        try:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("WebSocket Manager initialized with Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # Continue without Redis (degraded mode)
    
    async def connect(self, broker: BrokerType, credentials: Dict[str, str]):
        """
        Connect to a broker's WebSocket feed
        
        Args:
            broker: Broker type
            credentials: API credentials (api_key, access_token, etc.)
        """
        if broker in self.connections and self.states[broker] == ConnectionState.CONNECTED:
            logger.warning(f"Already connected to {broker.value}")
            return
        
        self.states[broker] = ConnectionState.CONNECTING
        
        try:
            if broker == BrokerType.ANGEL_ONE:
                await self._connect_angel_one(credentials)
            elif broker == BrokerType.UPSTOX:
                await self._connect_upstox(credentials)
            elif broker == BrokerType.ZERODHA:
                await self._connect_zerodha(credentials)
            
            self.states[broker] = ConnectionState.CONNECTED
            logger.info(f"Connected to {broker.value}")
            
            # Start heartbeat monitoring
            task = asyncio.create_task(self._heartbeat_monitor(broker))
            self._tasks.add(task)
            
        except Exception as e:
            logger.error(f"Failed to connect to {broker.value}: {e}")
            self.states[broker] = ConnectionState.ERROR
            # Schedule reconnection
            asyncio.create_task(self._reconnect(broker, credentials))
    
    async def _connect_angel_one(self, credentials: Dict[str, str]):
        """Connect to Angel One WebSocket"""
        # Placeholder - implement actual Angel One WebSocket connection
        # from SmartApi import SmartWebSocket
        logger.info("Connecting to Angel One WebSocket...")
        # Implementation would go here
        pass
    
    async def _connect_upstox(self, credentials: Dict[str, str]):
        """Connect to Upstox WebSocket"""
        # Placeholder - implement actual Upstox WebSocket connection
        logger.info("Connecting to Upstox WebSocket...")
        # Implementation would go here
        pass
    
    async def _connect_zerodha(self, credentials: Dict[str, str]):
        """Connect to Zerodha Kite WebSocket"""
        # Placeholder - implement actual Zerodha WebSocket connection
        logger.info("Connecting to Zerodha WebSocket...")
        # Implementation would go here
        pass
    
    async def _reconnect(self, broker: BrokerType, credentials: Dict[str, str], attempt: int = 1):
        """
        Reconnect with exponential backoff
        
        Args:
            broker: Broker to reconnect
            credentials: API credentials
            attempt: Current attempt number
        """
        if attempt > self.max_reconnect_attempts:
            logger.error(f"Max reconnection attempts reached for {broker.value}")
            self.states[broker] = ConnectionState.ERROR
            return
        
        # Exponential backoff
        delay = min(
            self.base_reconnect_delay * (2 ** (attempt - 1)),
            self.max_reconnect_delay
        )
        
        logger.info(f"Reconnecting to {broker.value} in {delay}s (attempt {attempt})")
        self.states[broker] = ConnectionState.RECONNECTING
        
        await asyncio.sleep(delay)
        
        try:
            await self.connect(broker, credentials)
            # Resubscribe to previous symbols
            if broker in self.subscriptions:
                for symbol in self.subscriptions[broker]:
                    await self.subscribe(broker, symbol)
        except Exception as e:
            logger.error(f"Reconnection failed: {e}")
            await self._reconnect(broker, credentials, attempt + 1)
    
    async def _heartbeat_monitor(self, broker: BrokerType):
        """Monitor connection health with heartbeat"""
        while self._running and self.states.get(broker) == ConnectionState.CONNECTED:
            try:
                # Send ping
                await self._send_heartbeat(broker)
                
                # Wait for pong (with timeout)
                await asyncio.sleep(self.heartbeat_interval)
                
            except asyncio.TimeoutError:
                logger.warning(f"Heartbeat timeout for {broker.value}")
                # Trigger reconnection
                self.states[broker] = ConnectionState.ERROR
                break
            except Exception as e:
                logger.error(f"Heartbeat error for {broker.value}: {e}")
                break
    
    async def _send_heartbeat(self, broker: BrokerType):
        """Send heartbeat ping to broker"""
        # Implementation depends on broker protocol
        pass
    
    async def subscribe(self, broker: BrokerType, symbol: str, mode: str = "full"):
        """
        Subscribe to real-time data for a symbol
        
        Args:
            broker: Broker connection
            symbol: Trading symbol (e.g., "NSE:RELIANCE")
            mode: Subscription mode ("full", "quote", "ltp")
        """
        if broker not in self.connections:
            raise ValueError(f"Not connected to {broker.value}")
        
        self.subscriptions[broker].add(symbol)
        
        # Send subscription message to broker
        await self._send_subscription(broker, symbol, mode)
        
        logger.info(f"Subscribed to {symbol} on {broker.value}")
    
    async def _send_subscription(self, broker: BrokerType, symbol: str, mode: str):
        """Send subscription message to broker WebSocket"""
        # Implementation depends on broker protocol
        pass
    
    async def unsubscribe(self, broker: BrokerType, symbol: str):
        """Unsubscribe from a symbol"""
        if broker in self.subscriptions:
            self.subscriptions[broker].discard(symbol)
        
        # Send unsubscription message
        await self._send_unsubscription(broker, symbol)
        
        logger.info(f"Unsubscribed from {symbol} on {broker.value}")
    
    async def _send_unsubscription(self, broker: BrokerType, symbol: str):
        """Send unsubscription message to broker WebSocket"""
        # Implementation depends on broker protocol
        pass
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Register a callback for market data events
        
        Args:
            event_type: Type of event ("tick", "depth", "order", "trade")
            callback: Async function to call with data
        """
        self.callbacks[event_type].add(callback)
    
    def unregister_callback(self, event_type: str, callback: Callable):
        """Unregister a callback"""
        if event_type in self.callbacks:
            self.callbacks[event_type].discard(callback)
    
    async def _handle_message(self, broker: BrokerType, message: Dict[str, Any]):
        """
        Handle incoming WebSocket message
        
        Args:
            broker: Source broker
            message: Parsed message data
        """
        event_type = message.get("type", "tick")
        
        # Publish to Redis for horizontal scaling
        if self.redis:
            try:
                await self.redis.publish(
                    f"market_data:{event_type}",
                    json.dumps(message)
                )
            except Exception as e:
                logger.error(f"Redis publish error: {e}")
        
        # Call registered callbacks
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    await callback(message)
                except Exception as e:
                    logger.error(f"Callback error: {e}")
    
    async def start(self):
        """Start the WebSocket manager"""
        self._running = True
        await self.initialize()
        logger.info("WebSocket Manager started")
    
    async def stop(self):
        """Stop the WebSocket manager and close all connections"""
        self._running = False
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        # Close all broker connections
        for broker in self.connections:
            try:
                await self._close_connection(broker)
            except Exception as e:
                logger.error(f"Error closing {broker.value}: {e}")
        
        # Close Redis
        if self.redis:
            await self.redis.close()
        
        logger.info("WebSocket Manager stopped")
    
    async def _close_connection(self, broker: BrokerType):
        """Close connection to a broker"""
        # Implementation depends on broker
        pass
    
    def get_state(self, broker: BrokerType) -> ConnectionState:
        """Get connection state for a broker"""
        return self.states.get(broker, ConnectionState.DISCONNECTED)
    
    def get_subscriptions(self, broker: BrokerType) -> Set[str]:
        """Get active subscriptions for a broker"""
        return self.subscriptions.get(broker, set())


# Singleton instance
websocket_manager = WebSocketManager()
