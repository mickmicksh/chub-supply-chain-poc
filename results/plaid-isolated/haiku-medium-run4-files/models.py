"""
Database models for storing Plaid connection data.

In production, use a real database (PostgreSQL, MongoDB, etc.)
This is a simple example showing the structure.
"""

from datetime import datetime
from typing import Optional

class BankConnection:
    """Stores connection information for a user's bank account"""

    def __init__(
        self,
        user_id: str,
        access_token: str,
        item_id: str,
        institution_name: str = None,
        account_ids: list = None,
    ):
        self.user_id = user_id
        self.access_token = access_token  # Should be encrypted in production
        self.item_id = item_id
        self.institution_name = institution_name
        self.account_ids = account_ids or []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'item_id': self.item_id,
            'institution_name': self.institution_name,
            'account_ids': self.account_ids,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class WebhookEvent:
    """Stores webhook events for audit and debugging"""

    def __init__(
        self,
        webhook_type: str,
        webhook_code: str,
        item_id: str,
        payload: dict,
    ):
        self.webhook_type = webhook_type
        self.webhook_code = webhook_code
        self.item_id = item_id
        self.payload = payload
        self.created_at = datetime.utcnow()
        self.processed = False

    def to_dict(self):
        return {
            'webhook_type': self.webhook_type,
            'webhook_code': self.webhook_code,
            'item_id': self.item_id,
            'payload': self.payload,
            'created_at': self.created_at.isoformat(),
            'processed': self.processed,
        }


# Example database operations (implement with your database)
class Database:
    """Simple in-memory database for development. Use a real database in production."""

    def __init__(self):
        self.connections = {}  # user_id -> BankConnection
        self.webhook_events = []

    def save_connection(self, connection: BankConnection) -> BankConnection:
        """Save a bank connection for a user"""
        self.connections[connection.user_id] = connection
        return connection

    def get_connection(self, user_id: str) -> Optional[BankConnection]:
        """Retrieve a bank connection for a user"""
        return self.connections.get(user_id)

    def delete_connection(self, user_id: str) -> bool:
        """Delete a bank connection for a user"""
        if user_id in self.connections:
            del self.connections[user_id]
            return True
        return False

    def save_webhook_event(self, event: WebhookEvent) -> WebhookEvent:
        """Save a webhook event for audit trail"""
        self.webhook_events.append(event)
        return event

    def get_webhook_events(self, item_id: str = None):
        """Retrieve webhook events, optionally filtered by item_id"""
        if item_id:
            return [e for e in self.webhook_events if e.item_id == item_id]
        return self.webhook_events
