"""Plaid configuration settings."""
import os
from dotenv import load_dotenv

load_dotenv()

# Plaid API Configuration
PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
PLAID_SECRET = os.environ.get('PLAID_SECRET')
PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')

# Plaid Link Configuration
PLAID_PRODUCTS = ['auth', 'transactions']
PLAID_COUNTRY_CODES = ['US']
PLAID_LANGUAGE = 'en'

# Flask Configuration
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
DEBUG = os.environ.get('FLASK_DEBUG', True)
