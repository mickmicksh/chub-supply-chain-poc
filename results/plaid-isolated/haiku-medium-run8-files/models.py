"""Database models for storing Plaid integration data."""

from datetime import datetime


class User:
    """User model for storing user information and their bank connections."""

    def __init__(self, user_id, email=None):
        self.user_id = user_id
        self.email = email
        self.created_at = datetime.utcnow()
        self.bank_accounts = []

    def add_bank_account(self, item_id, access_token, institution_name):
        """Add a connected bank account to the user."""
        account = BankAccount(
            item_id=item_id,
            access_token=access_token,
            institution_name=institution_name,
            user_id=self.user_id
        )
        self.bank_accounts.append(account)
        return account


class BankAccount:
    """Model for storing bank account connection data."""

    def __init__(self, item_id, access_token, institution_name, user_id):
        self.item_id = item_id
        self.access_token = access_token
        self.institution_name = institution_name
        self.user_id = user_id
        self.connected_at = datetime.utcnow()
        self.last_synced = None
        self.is_active = True
        self.accounts = []

    def mark_synced(self):
        """Update the last sync timestamp."""
        self.last_synced = datetime.utcnow()

    def deactivate(self):
        """Deactivate the bank account connection."""
        self.is_active = False


class Account:
    """Model for individual accounts within a bank connection."""

    def __init__(self, account_id, name, official_name, subtype, balance):
        self.account_id = account_id
        self.name = name
        self.official_name = official_name
        self.subtype = subtype
        self.balance = balance


class Transaction:
    """Model for storing bank transactions."""

    def __init__(self, transaction_id, account_id, amount, name, date, pending=False):
        self.transaction_id = transaction_id
        self.account_id = account_id
        self.amount = amount
        self.name = name
        self.date = date
        self.pending = pending
        self.created_at = datetime.utcnow()


class PlaidWebhookEvent:
    """Model for storing Plaid webhook events."""

    def __init__(self, event_type, webhook_type, item_id, payload):
        self.event_type = event_type
        self.webhook_type = webhook_type
        self.item_id = item_id
        self.payload = payload
        self.created_at = datetime.utcnow()
        self.processed = False

    def mark_processed(self):
        """Mark the webhook event as processed."""
        self.processed = True
