"""Database models for storing Plaid integration data.

This example uses a simple in-memory storage. In production, use a proper
database like PostgreSQL with SQLAlchemy.
"""

from datetime import datetime
from typing import Optional, Dict, List


class PlaidItem:
    """Represents a connected Plaid item (bank account)."""

    # In-memory storage (replace with database in production)
    _storage: Dict[str, 'PlaidItem'] = {}

    def __init__(
        self,
        user_id: str,
        item_id: str,
        access_token: str,
        institution_name: str,
        institution_id: str,
    ):
        self.user_id = user_id
        self.item_id = item_id
        self.access_token = access_token
        self.institution_name = institution_name
        self.institution_id = institution_id
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.last_sync = None
        self.is_active = True

    def save(self) -> None:
        """Save item to storage."""
        key = f"{self.user_id}:{self.item_id}"
        self._storage[key] = self
        self.updated_at = datetime.utcnow()

    @classmethod
    def get_by_item_id(cls, user_id: str, item_id: str) -> Optional['PlaidItem']:
        """Get item by user and item ID."""
        key = f"{user_id}:{item_id}"
        return cls._storage.get(key)

    @classmethod
    def get_by_user(cls, user_id: str) -> List['PlaidItem']:
        """Get all items for a user."""
        return [
            item for item in cls._storage.values()
            if item.user_id == user_id and item.is_active
        ]

    @classmethod
    def delete(cls, user_id: str, item_id: str) -> bool:
        """Soft delete an item."""
        key = f"{user_id}:{item_id}"
        if key in cls._storage:
            cls._storage[key].is_active = False
            cls._storage[key].updated_at = datetime.utcnow()
            return True
        return False

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'user_id': self.user_id,
            'item_id': self.item_id,
            'institution_name': self.institution_name,
            'institution_id': self.institution_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
        }


class WebhookLog:
    """Log webhook events for debugging."""

    _storage: List['WebhookLog'] = []

    def __init__(self, event_type: str, item_id: str, event_data: Dict):
        self.event_type = event_type
        self.item_id = item_id
        self.event_data = event_data
        self.received_at = datetime.utcnow()
        self.processed = False

    def save(self) -> None:
        """Save webhook log."""
        self._storage.append(self)

    @classmethod
    def get_recent(cls, limit: int = 50) -> List['WebhookLog']:
        """Get recent webhook logs."""
        return sorted(
            cls._storage,
            key=lambda x: x.received_at,
            reverse=True
        )[:limit]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'event_type': self.event_type,
            'item_id': self.item_id,
            'event_data': self.event_data,
            'received_at': self.received_at.isoformat(),
            'processed': self.processed,
        }
