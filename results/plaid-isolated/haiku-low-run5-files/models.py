"""
Database models for Plaid integration
This is a reference implementation - you'll need to set up your actual database
"""

from datetime import datetime


class PlaidAccount:
    """
    Model for storing Plaid account information

    In production, use a real ORM like SQLAlchemy:

    from flask_sqlalchemy import SQLAlchemy
    from flask_encrypt import Encryption

    db = SQLAlchemy()
    enc = Encryption()

    class PlaidAccount(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.String(255), nullable=False, unique=True)
        item_id = db.Column(db.String(255), nullable=False)
        access_token = db.Column(db.String(255), nullable=False)  # Encrypted
        institution_name = db.Column(db.String(255))
        institution_id = db.Column(db.String(255))
        connected_at = db.Column(db.DateTime, default=datetime.utcnow)
        last_synced = db.Column(db.DateTime)

        def __repr__(self):
            return f'<PlaidAccount {self.user_id}>'
    """

    def __init__(self, user_id, item_id, access_token, institution_name=None, institution_id=None):
        self.user_id = user_id
        self.item_id = item_id
        self.access_token = access_token
        self.institution_name = institution_name
        self.institution_id = institution_id
        self.connected_at = datetime.utcnow()
        self.last_synced = None

    def to_dict(self):
        """Convert to dictionary (excluding sensitive data)"""
        return {
            'user_id': self.user_id,
            'item_id': self.item_id,
            'institution_name': self.institution_name,
            'institution_id': self.institution_id,
            'connected_at': self.connected_at.isoformat(),
            'last_synced': self.last_synced.isoformat() if self.last_synced else None,
        }


class PlaidTransaction:
    """
    Model for storing Plaid transactions

    In production, use SQLAlchemy:

    class PlaidTransaction(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        item_id = db.Column(db.String(255), nullable=False, index=True)
        transaction_id = db.Column(db.String(255), nullable=False, unique=True)
        account_id = db.Column(db.String(255), nullable=False)
        amount = db.Column(db.Float, nullable=False)
        currency = db.Column(db.String(3), default='USD')
        merchant_name = db.Column(db.String(255))
        date = db.Column(db.Date, nullable=False)
        category = db.Column(db.String(255))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
    """

    def __init__(self, item_id, transaction_id, account_id, amount,
                 merchant_name, date, currency='USD', category=None):
        self.item_id = item_id
        self.transaction_id = transaction_id
        self.account_id = account_id
        self.amount = amount
        self.merchant_name = merchant_name
        self.date = date
        self.currency = currency
        self.category = category
        self.created_at = datetime.utcnow()

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'transaction_id': self.transaction_id,
            'account_id': self.account_id,
            'amount': self.amount,
            'currency': self.currency,
            'merchant_name': self.merchant_name,
            'date': self.date.isoformat(),
            'category': self.category,
        }


# Example setup with SQLAlchemy (requires flask-sqlalchemy and flask-encrypt)
"""
Setup Instructions:
1. Install flask-sqlalchemy: pip install flask-sqlalchemy
2. Install flask-encrypt: pip install flask-encrypt
3. Create app context and tables:

from flask import Flask
from models import db, enc, PlaidAccount, PlaidTransaction

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plaid.db'
app.config['ENCRYPT_KEY'] = os.environ.get('ENCRYPT_KEY', 'dev-key-change-in-prod')

db.init_app(app)
enc.init_app(app)

with app.app_context():
    db.create_all()

# Usage:
account = PlaidAccount(
    user_id='user-123',
    item_id='item-abc',
    access_token='access-xyz',
    institution_name='Chase Bank'
)
db.session.add(account)
db.session.commit()
"""
