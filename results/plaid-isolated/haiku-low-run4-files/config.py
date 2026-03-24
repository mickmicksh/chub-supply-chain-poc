"""Configuration for Plaid Link integration."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
    PLAID_SECRET = os.environ.get('PLAID_SECRET')
    PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')


class SandboxConfig(Config):
    """Sandbox environment configuration."""

    pass


class ProductionConfig(Config):
    """Production environment configuration."""

    PLAID_ENV = 'production'


def get_config():
    """Get configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig
    return SandboxConfig
