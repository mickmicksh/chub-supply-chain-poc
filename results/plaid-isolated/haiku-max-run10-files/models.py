"""
Data models for storing Plaid account information.
This is a template - implement with your preferred ORM/database.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class PlaidAccount:
    """Represents a connected Plaid account."""

    user_id: str
    access_token: str
    item_id: str
    institution_name: str
    institution_id: Optional[str] = None
    created_at: Optional[datetime] = None
    last_sync: Optional[datetime] = None

    def to_dict(self):
        """Convert to dictionary for storage."""
        return {
            'user_id': self.user_id,
            'access_token': self.access_token,
            'item_id': self.item_id,
            'institution_name': self.institution_name,
            'institution_id': self.institution_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
        }


@dataclass
class BankAccount:
    """Represents a bank account within a Plaid item."""

    account_id: str
    item_id: str
    name: str
    account_type: str  # 'depository', 'credit', 'loan', 'investment'
    account_subtype: Optional[str] = None  # 'checking', 'savings', etc.
    mask: Optional[str] = None  # Last 4 digits

    def to_dict(self):
        """Convert to dictionary for storage."""
        return {
            'account_id': self.account_id,
            'item_id': self.item_id,
            'name': self.name,
            'account_type': self.account_type,
            'account_subtype': self.account_subtype,
            'mask': self.mask,
        }


@dataclass
class Transaction:
    """Represents a transaction from a connected account."""

    transaction_id: str
    account_id: str
    date: str
    name: str
    amount: float
    currency: str = 'USD'
    pending: bool = False
    category: Optional[str] = None
    merchant_name: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary for storage."""
        return {
            'transaction_id': self.transaction_id,
            'account_id': self.account_id,
            'date': self.date,
            'name': self.name,
            'amount': self.amount,
            'currency': self.currency,
            'pending': self.pending,
            'category': self.category,
            'merchant_name': self.merchant_name,
        }


class AccountRepository:
    """
    Template repository for managing Plaid accounts.
    Implement with your database/ORM of choice.
    """

    def save_account(self, account: PlaidAccount) -> bool:
        """Save a connected Plaid account."""
        raise NotImplementedError()

    def get_account(self, user_id: str, item_id: str) -> Optional[PlaidAccount]:
        """Retrieve a stored Plaid account."""
        raise NotImplementedError()

    def get_user_accounts(self, user_id: str) -> list[PlaidAccount]:
        """Get all accounts connected by a user."""
        raise NotImplementedError()

    def delete_account(self, user_id: str, item_id: str) -> bool:
        """Delete a connected account."""
        raise NotImplementedError()

    def update_sync_time(self, user_id: str, item_id: str) -> bool:
        """Update the last sync time for an account."""
        raise NotImplementedError()


class TransactionRepository:
    """
    Template repository for managing transactions.
    Implement with your database/ORM of choice.
    """

    def save_transactions(self, transactions: list[Transaction]) -> int:
        """Save a batch of transactions."""
        raise NotImplementedError()

    def get_account_transactions(
        self,
        account_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[Transaction]:
        """Get transactions for an account within a date range."""
        raise NotImplementedError()

    def delete_account_transactions(self, account_id: str) -> int:
        """Delete all transactions for an account."""
        raise NotImplementedError()
