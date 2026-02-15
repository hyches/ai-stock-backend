"""
User Accounts & Cloud Sync Service
==================================
Handles user-specific strategy storage, trade journals, and 
multi-device synchronization logic.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class UserStrategy:
    id: str
    user_id: str
    name: str
    config: Dict[str, Any]
    updated_at: datetime = field(default_factory=datetime.utcnow)

class CloudSyncService:
    """
    Manages synchronization of user data across devices.
    In a real app, this would interface with PostgreSQL/MongoDB.
    Here we implement the logic for versioned syncing.
    """
    
    def __init__(self):
        self.user_data = {} # user_id -> {strategies: {}, journal: []}

    def save_strategy(self, user_id: str, name: str, config: Dict[str, Any]) -> UserStrategy:
        """Saves or updates a user strategy"""
        if user_id not in self.user_data:
            self.user_data[user_id] = {"strategies": {}, "journal": []}
            
        strategy_id = str(uuid.uuid4())
        strategy = UserStrategy(id=strategy_id, user_id=user_id, name=name, config=config)
        
        self.user_data[user_id]["strategies"][strategy_id] = strategy
        return strategy

    def get_user_strategies(self, user_id: str) -> List[Dict]:
        """Returns all strategies for a user"""
        data = self.user_data.get(user_id, {}).get("strategies", {})
        return [
            {"id": s.id, "name": s.name, "config": s.config, "updated_at": s.updated_at.isoformat()}
            for s in data.values()
        ]

    def add_journal_entry(self, user_id: str, entry_text: str, tags: List[str] = []) -> Dict:
        """Adds an entry to the user's trading journal"""
        if user_id not in self.user_data:
            self.user_data[user_id] = {"strategies": {}, "journal": []}
            
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "text": entry_text,
            "tags": tags
        }
        self.user_data[user_id]["journal"].append(entry)
        return entry

# Singleton
cloud_sync_service = CloudSyncService()
