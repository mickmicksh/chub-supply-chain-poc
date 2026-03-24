"""
Plaid Link Integration - Flask Application
Bank account connection flow with token exchange and webhook handling
"""

import os
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_link_verify import LinkVerifier, verify_webhook
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Plaid API
PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
PLAID_SECRET = os.environ.get('PLAID_SECRET')
PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')

# Set Plaid environment
plaid_env = plaid.Environment.Sandbox if PLAID_ENV == 'sandbox' else plaid.Environment.Production

configuration = plaid.Configuration(
    host=plaid_env,
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
    Create a Plaid Link token for the user.
    This token is used to initialize Plaid Link on the client side.
    """
    try:
        request_data = LinkTokenCreateRequest(
            user={'client_user_id': request.json.get('user_id', 'user-123')},
            client_name='My Bank App',
            products=['auth', 'transactions'],
            country_codes=['US'],
            language='en',
        )
        response = client.link_token_create(request_data)
        return jsonify({'link_token': response.link_token}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """
    Exchange the public token from Plaid Link for an access token.
    The access token is used to make authenticated requests to the Plaid API.
    """
    try:
        public_token = request.json.get('public_token')
        if not public_token:
            return jsonify({'error': 'public_token is required'}), 400

        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_request)

        # Store access_token and item_id securely in your database
        return jsonify({
            'access_token': response.access_token,
            'item_id': response.item_id,
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


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

        # Handle different webhook types
        if event.get('webhook_type') == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif event.get('webhook_type') == 'ITEM':
            handle_item_update(event)

        return '', 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


def handle_transactions_update(event):
    """Process transactions update webhook"""
    print(f"Transactions updated for item: {event.get('item_id')}")
    # Implement your business logic here


def handle_item_update(event):
    """Process item update webhook"""
    print(f"Item updated: {event.get('item_id')}")
    # Implement your business logic here


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.environ.get('DEBUG', False),
        ssl_context='adhoc' if PLAID_ENV == 'production' else None
    )
