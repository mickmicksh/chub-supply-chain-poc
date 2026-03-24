"""
Configuration management for Plaid integration
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    PLAID_ENV = 'production'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    PLAID_ENV = 'sandbox'


# Plaid Configuration
PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
PLAID_SECRET = os.environ.get('PLAID_SECRET')
PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')

# Plaid Link Configuration
PLAID_LINK_CONFIG = {
    'products': ['auth', 'transactions'],
    'country_codes': ['US'],
    'language': 'en',
}

# Get config based on environment
def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()
