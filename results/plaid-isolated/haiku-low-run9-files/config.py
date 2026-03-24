"""Configuration management for Plaid Link application."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    # Plaid configuration
    PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
    PLAID_SECRET = os.environ.get('PLAID_SECRET')
    PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')

    # Flask configuration
    DEBUG = os.environ.get('FLASK_DEBUG', False)
    TESTING = False

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

    @staticmethod
    def validate():
        """Validate required configuration."""
        if not Config.PLAID_CLIENT_ID:
            raise ValueError('PLAID_CLIENT_ID is required')
        if not Config.PLAID_SECRET:
            raise ValueError('PLAID_SECRET is required')


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False

    # In production, SECRET_KEY must be set via environment variable
    if 'SECRET_KEY' not in os.environ:
        raise ValueError('SECRET_KEY environment variable must be set in production')


class TestingConfig(Config):
    """Testing configuration."""

    DEBUG = True
    TESTING = True
    PLAID_ENV = 'sandbox'


# Select configuration based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

current_config = config.get(
    os.environ.get('FLASK_ENV', 'development')
)
