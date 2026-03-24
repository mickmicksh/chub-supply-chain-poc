"""
Plaid Link integration for bank account connections.
Flask app with token exchange, webhook handling, and error management.
"""

import os
import logging
from dotenv import load_dotenv

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_link_verify import LinkVerifier, verify_webhook
from plaid.exceptions import ApiException

from flask import Flask, request, jsonify

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Plaid client
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')

environment = plaid.Environment.Sandbox if PLAID_ENV == 'sandbox' else plaid.Environment.Production

configuration = plaid.Configuration(
    host=environment,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
verifier = LinkVerifier(PLAID_SECRET)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """
    Create a Plaid Link token for initiating bank account connection.

    Request body:
    {
        "user_id": "unique_user_identifier"
    }
    """
    try:
        data = request.json or {}
        user_id = data.get('user_id', 'user-123')

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name='My Banking App',
            products=['auth', 'transactions'],
            country_codes=['US'],
            language='en',
        )

        response = client.link_token_create(request_data)
        logger.info(f'Link token created for user: {user_id}')

        return jsonify({
            'link_token': response.link_token,
            'expiration': response.expiration,
        }), 200

    except ApiException as e:
        logger.error(f'Plaid API error: {str(e)}')
        return jsonify({'error': 'Failed to create link token'}), 400
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """
    Exchange a public token for an access token.

    Request body:
    {
        "public_token": "public_token_from_link"
    }
    """
    try:
        data = request.json or {}
        public_token = data.get('public_token')

        if not public_token:
            return jsonify({'error': 'public_token is required'}), 400

        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        response = client.item_public_token_exchange(exchange_request)

        logger.info(f'Token exchanged. Item ID: {response.item_id}')

        return jsonify({
            'access_token': response.access_token,
            'item_id': response.item_id,
        }), 200

    except ApiException as e:
        logger.error(f'Plaid API error: {str(e)}')
        return jsonify({'error': 'Failed to exchange token'}), 400
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """
    Handle Plaid webhook events.
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        if not sig_header:
            logger.warning('Webhook received without signature header')
            return jsonify({'error': 'Missing signature'}), 401

        event = verify_webhook(payload, sig_header, PLAID_SECRET)

        webhook_type = event.get('webhook_type')
        logger.info(f'Webhook received: {webhook_type}')

        # Handle different webhook types
        if webhook_type == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif webhook_type == 'ITEM':
            handle_item_update(event)

        return '', 200

    except ValueError as e:
        logger.error(f'Webhook verification failed: {str(e)}')
        return jsonify({'error': 'Webhook verification failed'}), 401
    except Exception as e:
        logger.error(f'Webhook processing error: {str(e)}')
        return jsonify({'error': 'Webhook processing failed'}), 500


def handle_transactions_update(event):
    """Handle transactions webhook event."""
    item_id = event.get('item_id')
    webhook_code = event.get('webhook_code')
    logger.info(f'Transactions update for item {item_id}: {webhook_code}')
    # Add your transaction handling logic here


def handle_item_update(event):
    """Handle item webhook event."""
    item_id = event.get('item_id')
    webhook_code = event.get('webhook_code')
    logger.info(f'Item update for {item_id}: {webhook_code}')
    # Add your item handling logic here


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    logger.error(f'Server error: {str(error)}')
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    if not PLAID_CLIENT_ID or not PLAID_SECRET:
        logger.error('Missing PLAID_CLIENT_ID or PLAID_SECRET in environment variables')
        exit(1)

    app.run(port=5000, debug=True)
