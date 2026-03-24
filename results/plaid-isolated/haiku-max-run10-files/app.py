"""
Plaid Link integration for bank account connections.
Handles token creation, exchange, and webhook verification.
"""

import os
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

# Initialize Flask app
app = Flask(__name__)

# Configure Plaid client
PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
PLAID_SECRET = os.environ.get('PLAID_SECRET')
PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox').lower()

# Map environment string to Plaid Environment
PLAID_ENVIRONMENT = (
    plaid.Environment.Sandbox if PLAID_ENV == 'sandbox'
    else plaid.Environment.Production
)

configuration = plaid.Configuration(
    host=PLAID_ENVIRONMENT,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
verifier = LinkVerifier(PLAID_SECRET)


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """
    Create a Link token for initializing Plaid Link on the frontend.

    Expected JSON body:
    {
        "user_id": "unique_user_identifier",
        "client_name": "Your App Name"
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'user-default')
        client_name = data.get('client_name', 'My App')

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name=client_name,
            products=['auth', 'transactions'],
            country_codes=['US'],
            language='en',
        )

        response = client.link_token_create(request_data)
        return jsonify({'link_token': response.link_token}), 200

    except ApiException as e:
        return jsonify({'error': f'Plaid API error: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """
    Exchange a public token for an access token.

    Expected JSON body:
    {
        "public_token": "public-token-from-link"
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
        response = client.item_public_token_exchange(exchange_request)

        return jsonify({
            'access_token': response.access_token,
            'item_id': response.item_id,
        }), 200

    except ApiException as e:
        return jsonify({'error': f'Token exchange failed: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """
    Handle Plaid webhooks for transaction updates and account changes.
    Verifies webhook signature using plaid-link-verify.
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        # Verify webhook signature
        event = verify_webhook(payload, sig_header, PLAID_SECRET)

        # Handle webhook based on type
        if event.get('webhook_type') == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif event.get('webhook_type') == 'ITEM':
            handle_item_update(event)

        return '', 200

    except Exception as e:
        print(f'Webhook verification error: {str(e)}')
        return '', 401


def handle_transactions_update(event):
    """Handle transaction update webhooks."""
    print(f'Transaction update: {event}')
    # TODO: Implement transaction handling logic


def handle_item_update(event):
    """Handle item update webhooks."""
    print(f'Item update: {event}')
    # TODO: Implement item update handling logic


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
