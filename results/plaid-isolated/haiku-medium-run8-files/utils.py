"""Utility functions for Plaid integration."""

import os
from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)


def require_api_key(f):
    """Decorator to protect API endpoints with API key validation."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.environ.get('API_KEY'):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function


def validate_plaid_credentials():
    """Validate that all required Plaid credentials are set."""
    required_vars = ['PLAID_CLIENT_ID', 'PLAID_SECRET']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        error_msg = f"Missing required Plaid credentials: {', '.join(missing_vars)}"
        logger.error(error_msg)
        return False, error_msg

    return True, "All credentials validated"


def format_bank_account_response(access_token, item_id, institution_name=None):
    """Format the response for a successful bank account connection."""
    return {
        'status': 'success',
        'access_token': access_token,
        'item_id': item_id,
        'institution_name': institution_name,
        'message': 'Bank account connected successfully'
    }


def handle_plaid_error(error):
    """Format Plaid API errors for client response."""
    error_code = getattr(error, 'error_code', 'UNKNOWN_ERROR')
    error_message = str(error)

    error_responses = {
        'INVALID_CREDENTIALS': {
            'message': 'Invalid bank credentials',
            'status_code': 401
        },
        'ITEM_LOGIN_REQUIRED': {
            'message': 'Bank login required',
            'status_code': 401
        },
        'RATE_LIMIT_EXCEEDED': {
            'message': 'Too many requests. Please try again later.',
            'status_code': 429
        },
        'INVALID_REQUEST': {
            'message': 'Invalid request parameters',
            'status_code': 400
        },
    }

    if error_code in error_responses:
        response = error_responses[error_code]
        return {
            'error': response['message'],
            'error_code': error_code
        }, response['status_code']

    # Default error response
    logger.error(f"Plaid API error: {error_code} - {error_message}")
    return {
        'error': 'Failed to process request',
        'error_code': error_code
    }, 400


def log_transaction(user_id, transaction_id, amount, description):
    """Log a transaction for audit purposes."""
    logger.info(
        f"Transaction: user_id={user_id}, "
        f"transaction_id={transaction_id}, "
        f"amount={amount}, "
        f"description={description}"
    )


def get_plaid_environment():
    """Get the current Plaid environment (sandbox or production)."""
    env = os.environ.get('PLAID_ENV', 'sandbox').lower()
    return 'sandbox' if env == 'sandbox' else 'production'


def sanitize_token(token, length=10):
    """Sanitize sensitive tokens for logging (show only last N characters)."""
    if len(token) <= length:
        return "***"
    return "***" + token[-length:]
