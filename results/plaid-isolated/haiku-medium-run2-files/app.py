"""
Plaid Link Integration - Flask Application
Bank account connection flow with token exchange and webhook handling
"""

import os
import logging
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_link_verify import LinkVerifier, verify_webhook
from flask import Flask, request, jsonify
from plaid.exceptions import ApiException

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Plaid client
PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
PLAID_SECRET = os.environ.get('PLAID_SECRET')
PLAID_ENVIRONMENT = os.environ.get('PLAID_ENVIRONMENT', 'sandbox')

# Set Plaid environment
environment = getattr(plaid.Environment, PLAID_ENVIRONMENT.capitalize(), plaid.Environment.Sandbox)

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


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """
    Create a Link token for Plaid Link flow.

    Request body:
        {
            "user_id": "user-123",
            "products": ["auth", "transactions"],
            "country_codes": ["US"]
        }
    """
    try:
        data = request.json or {}
        user_id = data.get('user_id', 'user-default')
        products = data.get('products', ['auth', 'transactions'])
        country_codes = data.get('country_codes', ['US'])

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name='My App',
            products=products,
            country_codes=country_codes,
            language='en',
        )

        response = client.link_token_create(request_data)
        logger.info(f"Link token created for user: {user_id}")

        return jsonify({'link_token': response.link_token}), 200

    except ApiException as e:
        logger.error(f"Plaid API error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """
    Exchange public token for access token.

    Request body:
        {
            "public_token": "public-...",
            "user_id": "user-123"
        }
    """
    try:
        data = request.json or {}
        public_token = data.get('public_token')
        user_id = data.get('user_id')

        if not public_token:
            return jsonify({'error': 'public_token is required'}), 400

        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )

        response = client.item_public_token_exchange(exchange_request)
        logger.info(f"Token exchanged for user: {user_id}, item_id: {response.item_id}")

        return jsonify({
            'access_token': response.access_token,
            'item_id': response.item_id,
        }), 200

    except ApiException as e:
        logger.error(f"Plaid API error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """
    Handle Plaid webhook events.
    Verifies webhook signature and processes events.
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        event = verify_webhook(payload, sig_header, PLAID_SECRET)
        logger.info(f"Webhook received: {event.get('webhook_type')}")

        # Handle different webhook types
        webhook_type = event.get('webhook_type')

        if webhook_type == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif webhook_type == 'ITEM':
            handle_item_event(event)

        return '', 200

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return '', 400


def handle_transactions_update(event):
    """Handle TRANSACTIONS webhook events."""
    webhook_code = event.get('webhook_code')
    logger.info(f"Transactions update: {webhook_code}")
    # TODO: Implement transaction sync logic


def handle_item_event(event):
    """Handle ITEM webhook events."""
    webhook_code = event.get('webhook_code')
    logger.info(f"Item event: {webhook_code}")
    # TODO: Implement item event handling


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Validate required environment variables
    if not PLAID_CLIENT_ID or not PLAID_SECRET:
        raise ValueError("PLAID_CLIENT_ID and PLAID_SECRET must be set")

    app.run(port=5000, debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')
