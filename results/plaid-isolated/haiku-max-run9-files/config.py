"""
Configuration module for Plaid Link integration.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
    PLAID_SECRET = os.environ.get('PLAID_SECRET')
    PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')

    # Flask
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('FLASK_DEBUG', False)

    # Validation
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.PLAID_CLIENT_ID:
            raise ValueError('PLAID_CLIENT_ID environment variable is required')
        if not cls.PLAID_SECRET:
            raise ValueError('PLAID_SECRET environment variable is required')
        return True
