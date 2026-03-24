"""
Configuration module for Plaid Link integration.
Manages environment variables and Plaid API configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration."""

    PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
    PLAID_SECRET = os.environ.get('PLAID_SECRET')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

    # Plaid configuration
    PLAID_ENV = 'sandbox'  # Change to 'production' for live
    PLAID_PRODUCTS = ['auth', 'transactions']
    PLAID_COUNTRY_CODES = ['US']
    PLAID_LANGUAGE = 'en'

    @staticmethod
    def validate():
        """Validate that all required configuration is present."""
        required_vars = {
            'PLAID_CLIENT_ID': Config.PLAID_CLIENT_ID,
            'PLAID_SECRET': Config.PLAID_SECRET,
        }

        missing = [key for key, value in required_vars.items() if not value]

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )


class DevelopmentConfig(Config):
    """Development configuration."""

    FLASK_ENV = 'development'
    FLASK_DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""

    FLASK_ENV = 'production'
    FLASK_DEBUG = False
    PLAID_ENV = 'production'


def get_config():
    """Get the appropriate configuration based on FLASK_ENV."""
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig()
    return DevelopmentConfig()
