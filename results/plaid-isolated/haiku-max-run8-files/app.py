"""
Plaid Link Integration - Flask Application
Bank account connection flow with token exchange and webhook handling
"""

import os
import logging
from flask import Flask, request, jsonify
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.exceptions import ApiException
from plaid_link_verify import LinkVerifier, verify_webhook
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure Plaid API client
PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
PLAID_SECRET = os.environ.get('PLAID_SECRET')
PLAID_ENVIRONMENT = os.environ.get('PLAID_ENVIRONMENT', 'sandbox')

if not PLAID_CLIENT_ID or not PLAID_SECRET:
    raise ValueError('Missing PLAID_CLIENT_ID or PLAID_SECRET environment variables')

# Set Plaid environment
environment_map = {
    'sandbox': plaid.Environment.Sandbox,
    'development': plaid.Environment.Development,
    'production': plaid.Environment.Production,
}

plaid_env = environment_map.get(PLAID_ENVIRONMENT, plaid.Environment.Sandbox)

configuration = plaid.Configuration(
    host=plaid_env,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)

api_client = plaid.ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)
link_verifier = LinkVerifier(PLAID_SECRET)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


@app.route('/api/create-link-token', methods=['POST'])
@link_verifier.protect
def create_link_token():
    """
    Create a Link token for Plaid Link initialization.

    Expected request body:
    {
        "user_id": "unique_user_id",
        "products": ["auth", "transactions"]  # optional, defaults to auth
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        products = data.get('products', ['auth'])

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name='My App',
            products=products,
            country_codes=['US'],
            language='en',
        )

        response = plaid_client.link_token_create(request_data)

        logger.info(f'Link token created for user: {user_id}')
        return jsonify({
            'link_token': response.link_token,
            'expiration': response.expiration,
        })

    except ApiException as e:
        logger.error(f'Plaid API error: {str(e)}')
        return jsonify({'error': f'Failed to create link token: {str(e)}'}), 400
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        return jsonify({'error': 'An unexpected error occurred'}), 500


@app.route('/api/exchange-token', methods=['POST'])
@link_verifier.protect
def exchange_token():
    """
    Exchange public token for access token.

    Expected request body:
    {
        "public_token": "public-xxx"
    }
    """
    try:
        data = request.get_json()
        public_token = data.get('public_token')

        if not public_token:
            return jsonify({'error': 'public_token is required'}), 400

        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        response = plaid_client.item_public_token_exchange(exchange_request)

        logger.info(f'Token exchanged for item: {response.item_id}')

        # Store access_token and item_id securely in your database
        return jsonify({
            'access_token': response.access_token,
            'item_id': response.item_id,
        })

    except ApiException as e:
        logger.error(f'Plaid API error: {str(e)}')
        return jsonify({'error': f'Failed to exchange token: {str(e)}'}), 400
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        return jsonify({'error': 'An unexpected error occurred'}), 500


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """
    Handle Plaid webhook notifications.
    Verifies webhook signature before processing.
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
            handle_transactions_webhook(event)
        elif webhook_type == 'ITEM':
            handle_item_webhook(event)
        else:
            logger.warning(f'Unhandled webhook type: {webhook_type}')

        return '', 200

    except Exception as e:
        logger.error(f'Webhook error: {str(e)}')
        return jsonify({'error': 'Webhook processing failed'}), 400


def handle_transactions_webhook(event):
    """Handle TRANSACTIONS webhook events"""
    webhook_code = event.get('webhook_code')
    item_id = event.get('item_id')

    logger.info(f'Transactions webhook: {webhook_code} for item {item_id}')

    # Implement your business logic here
    # Example: fetch new transactions, update sync status, etc.


def handle_item_webhook(event):
    """Handle ITEM webhook events"""
    webhook_code = event.get('webhook_code')
    item_id = event.get('item_id')

    logger.info(f'Item webhook: {webhook_code} for item {item_id}')

    # Implement your business logic here
    # Example: handle errors, consent issues, etc.


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f'Server error: {str(error)}')
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
