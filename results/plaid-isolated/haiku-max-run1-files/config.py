"""
Configuration management for Plaid Link application
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration"""
    # Flask
    DEBUG = False
    TESTING = False

    # Plaid
    PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
    PLAID_SECRET = os.environ.get('PLAID_SECRET')
    PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')

    # Validation
    @staticmethod
    def validate():
        """Validate required configuration"""
        if not Config.PLAID_CLIENT_ID:
            raise ValueError('PLAID_CLIENT_ID environment variable is required')
        if not Config.PLAID_SECRET:
            raise ValueError('PLAID_SECRET environment variable is required')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    PLAID_ENV = 'sandbox'


# Select configuration based on environment
def get_config():
    """Get configuration based on FLASK_ENV"""
    env = os.environ.get('FLASK_ENV', 'development').lower()

    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig
