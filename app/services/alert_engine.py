"""
Alert Engine for Professional Trading
=====================================
Handles real-time monitoring of price, volume, and technical indicators 
to trigger multi-channel notifications.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import uuid

logger = logging.getLogger(__name__)

class AlertType(Enum):
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PRICE_PCT_CHANGE = "price_pct_change"
    VOLUME_SPIKE = "volume_spike"
    RSI_OVERBOUGHT = "rsi_overbought"
    RSI_OVERSOLD = "rsi_oversold"
    MACD_CROSSOVER = "macd_crossover"
    PATTERN_DETECTED = "pattern_detected"
    SENTIMENT_SHIFT = "sentiment_shift"

class AlertChannel(Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    IN_APP = "in_app"

@dataclass
class Alert:
    """Represents a user-defined alert"""
    id: str
    symbol: str
    alert_type: AlertType
    threshold: float
    channels: List[AlertChannel]
    user_id: str
    message: str
    is_active: bool = True
    cooldown_minutes: int = 60
    last_triggered: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

class AlertEngine:
    """
    Core engine to monitor market data and trigger alerts.
    """
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {} # alert_id -> Alert
        self.active_alerts_by_symbol: Dict[str, List[str]] = {} # symbol -> [alert_ids]
        self._monitoring_task = None

    def create_alert(
        self, 
        user_id: str, 
        symbol: str, 
        alert_type: AlertType, 
        threshold: float,
        channels: List[AlertChannel] = [AlertChannel.IN_APP],
        message: str = ""
    ) -> Alert:
        """Create and register a new alert"""
        alert_id = str(uuid.uuid4())
        new_alert = Alert(
            id=alert_id,
            symbol=symbol.upper(),
            alert_type=alert_type,
            threshold=threshold,
            channels=channels,
            user_id=user_id,
            message=message or f"Alert triggered for {symbol}: {alert_type.value}"
        )
        
        self.alerts[alert_id] = new_alert
        if new_alert.symbol not in self.active_alerts_by_symbol:
            self.active_alerts_by_symbol[new_alert.symbol] = []
        self.active_alerts_by_symbol[new_alert.symbol].append(alert_id)
        
        logger.info(f"Alert {alert_id} created for {symbol}")
        return new_alert

    async def check_alerts(self, symbol: str, current_data: Dict[str, Any]):
        """
        Check all active alerts for a specific symbol against new data.
        Called frequently during live tick streaming.
        """
        symbol = symbol.upper()
        if symbol not in self.active_alerts_by_symbol:
            return

        price = current_data.get('price')
        volume = current_data.get('volume')
        indicators = current_data.get('indicators', {})
        
        for alert_id in list(self.active_alerts_by_symbol[symbol]):
            alert = self.alerts.get(alert_id)
            if not alert or not alert.is_active:
                continue
            
            # Cooldown check
            if alert.last_triggered:
                if datetime.utcnow() - alert.last_triggered < timedelta(minutes=alert.cooldown_minutes):
                    continue

            triggered = False
            
            # Trigger Logic
            if alert.alert_type == AlertType.PRICE_ABOVE and price and price >= alert.threshold:
                triggered = True
            elif alert.alert_type == AlertType.PRICE_BELOW and price and price <= alert.threshold:
                triggered = True
            elif alert.alert_type == AlertType.RSI_OVERBOUGHT:
                rsi = indicators.get('rsi')
                if rsi and rsi >= alert.threshold:
                    triggered = True
            elif alert.alert_type == AlertType.RSI_OVERSOLD:
                # threshold might be 30
                rsi = indicators.get('rsi')
                if rsi and rsi <= alert.threshold:
                    triggered = True
            
            # If triggered, send notifications
            if triggered:
                await self._trigger_alert(alert, current_data)

    async def _trigger_alert(self, alert: Alert, data: Dict[str, Any]):
        """Handle triggering an alert and sending notifications"""
        logger.info(f"ALERT TRIGGERED: {alert.symbol} {alert.alert_type.value} at {data.get('price')}")
        alert.last_triggered = datetime.utcnow()
        
        # Dispatch to channels
        for channel in alert.channels:
            if channel == AlertChannel.PUSH:
                await self._send_push_notification(alert)
            elif channel == AlertChannel.IN_APP:
                await self._store_in_app_notification(alert)
            # ... others

    async def _send_push_notification(self, alert: Alert):
        # Implementation for Firebase or similar
        logger.debug(f"Sending push notification for alert {alert.id}")
        pass

    async def _store_in_app_notification(self, alert: Alert):
        # Implementation to save to DB for frontend UI
        logger.debug(f"Storing in-app notification for alert {alert.id}")
        pass

# Singleton
alert_engine = AlertEngine()
