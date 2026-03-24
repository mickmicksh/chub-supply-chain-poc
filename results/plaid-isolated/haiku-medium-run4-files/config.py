"""
Application configuration for different environments.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""

    # Plaid Configuration
    PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
    PLAID_SECRET = os.environ.get('PLAID_SECRET')

    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DEBUG = False
    TESTING = False

    # Session Configuration
    SESSION_TYPE = 'filesystem'


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    PLAID_ENV = 'sandbox'  # Use Plaid Sandbox for development


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    PLAID_ENV = 'sandbox'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    PLAID_ENV = 'production'  # Use Plaid Production

    # In production, ensure these are set via environment variables
    if not PLAID_CLIENT_ID or not PLAID_SECRET:
        raise ValueError(
            'PLAID_CLIENT_ID and PLAID_SECRET must be set in production'
        )


def get_config():
    """Get configuration based on FLASK_ENV"""
    env = os.environ.get('FLASK_ENV', 'development').lower()

    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig
