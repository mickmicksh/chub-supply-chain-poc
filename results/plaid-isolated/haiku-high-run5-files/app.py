"""
Plaid Link Integration - Bank Account Connection Flow
Secure token exchange, webhook handling, and production-ready setup
"""

import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.exceptions import ApiException

from plaid_link_verify import LinkVerifier, verify_webhook

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Plaid Configuration
PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
PLAID_SECRET = os.environ.get('PLAID_SECRET')
PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')

# Determine Plaid environment
PLAID_ENVIRONMENT = {
    'sandbox': plaid.Environment.Sandbox,
    'development': plaid.Environment.Development,
    'production': plaid.Environment.Production,
}.get(PLAID_ENV, plaid.Environment.Sandbox)

# Validate configuration
if not PLAID_CLIENT_ID or not PLAID_SECRET:
    raise ValueError('PLAID_CLIENT_ID and PLAID_SECRET must be set in environment variables')

# Initialize Plaid client
configuration = plaid.Configuration(
    host=PLAID_ENVIRONMENT,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# Initialize Link Verifier for webhook validation
verifier = LinkVerifier(PLAID_SECRET)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """
    Create a Plaid Link token for initiating the bank connection flow.
    The user_id should be unique per user in your system.
    """
    try:
        data = request.json or {}
        user_id = data.get('user_id', 'user-123')

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name='My App',
            products=['auth', 'transactions'],
            country_codes=['US'],
            language='en',
        )

        response = client.link_token_create(request_data)
        logger.info(f'Link token created for user: {user_id}')

        return jsonify({
            'link_token': response.link_token,
            'expiration': response.expiration
        }), 200

    except ApiException as e:
        logger.error(f'Plaid API error: {str(e)}')
        return jsonify({'error': f'Failed to create link token: {str(e)}'}), 400
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """
    Exchange the public token from Plaid Link for an access token.
    The access token is used for all subsequent API calls.
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

        logger.info(f'Token exchanged for item: {response.item_id}')

        # Store access_token and item_id securely in your database
        # This is just a demo - in production, encrypt and persist these values
        return jsonify({
            'access_token': response.access_token,
            'item_id': response.item_id,
        }), 200

    except ApiException as e:
        logger.error(f'Token exchange error: {str(e)}')
        return jsonify({'error': f'Failed to exchange token: {str(e)}'}), 400
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """
    Webhook endpoint for Plaid events.
    Plaid sends updates here when accounts sync or transactions are available.
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        # Verify webhook signature
        event = verify_webhook(payload, sig_header, PLAID_SECRET)

        logger.info(f'Webhook received: {event.get("webhook_type")}')

        # Handle different webhook types
        webhook_type = event.get('webhook_type')

        if webhook_type == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif webhook_type == 'ITEM':
            handle_item_update(event)
        else:
            logger.warning(f'Unhandled webhook type: {webhook_type}')

        return '', 200

    except Exception as e:
        logger.error(f'Webhook processing error: {str(e)}')
        return jsonify({'error': 'Webhook processing failed'}), 400


def handle_transactions_update(event):
    """Handle TRANSACTIONS webhook events"""
    webhook_code = event.get('webhook_code')
    item_id = event.get('item_id')

    logger.info(f'Processing transaction update for item {item_id}: {webhook_code}')

    if webhook_code == 'SYNC_UPDATES_AVAILABLE':
        # Fetch and sync new transactions
        logger.info(f'New transactions available for item {item_id}')
    elif webhook_code == 'DEFAULT_UPDATE':
        # Handle other transaction updates
        logger.info(f'Transaction update for item {item_id}')


def handle_item_update(event):
    """Handle ITEM webhook events"""
    webhook_code = event.get('webhook_code')
    item_id = event.get('item_id')

    logger.info(f'Processing item update for item {item_id}: {webhook_code}')

    if webhook_code == 'WEBHOOK_UPDATE_ACKNOWLEDGED':
        logger.info(f'Webhook update acknowledged for item {item_id}')
    elif webhook_code == 'ERROR':
        logger.error(f'Item error for {item_id}: {event.get("error")}')


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f'Internal server error: {str(error)}')
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info(f'Starting Plaid Link app in {PLAID_ENV} mode')
    app.run(host='0.0.0.0', port=5000, debug=True)
