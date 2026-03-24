"""
Plaid Link Integration - Flask Application
Bank account connection flow with token exchange and webhook handling
"""

import os
from dotenv import load_dotenv

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_link_verify import LinkVerifier, verify_webhook
from flask import Flask, request, jsonify

# Load environment variables from .env file
load_dotenv()

# Plaid Configuration
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': os.environ.get('PLAID_CLIENT_ID'),
        'secret': os.environ.get('PLAID_SECRET'),
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
verifier = LinkVerifier(os.environ.get('PLAID_SECRET'))

# Flask Application
app = Flask(__name__)


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """
    Create a Link token for initializing Plaid Link flow.

    Client user ID is required to identify the user in your system.
    """
    try:
        data = request.json
        user_id = data.get('user_id', 'user-default')

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name='My Banking App',
            products=['auth', 'transactions'],
            country_codes=['US'],
            language='en',
        )

        response = client.link_token_create(request_data)

        return jsonify({
            'link_token': response.link_token,
            'expiration': response.expiration
        }), 200

    except plaid.exceptions.ApiException as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """
    Exchange the public token (from Plaid Link) for an access token.

    This access token is used for subsequent API calls to fetch account data.
    """
    try:
        data = request.json
        public_token = data.get('public_token')

        if not public_token:
            return jsonify({'error': 'public_token is required'}), 400

        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_request)

        return jsonify({
            'access_token': response.access_token,
            'item_id': response.item_id,
        }), 200

    except plaid.exceptions.ApiException as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """
    Receive and process Plaid webhook events.

    Verifies webhook signature and handles various event types like
    TRANSACTIONS updates, ITEM updates, etc.
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        event = verify_webhook(
            payload,
            sig_header,
            os.environ.get('PLAID_SECRET')
        )

        # Handle different webhook types
        if event.get('webhook_type') == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif event.get('webhook_type') == 'ITEM':
            handle_item_update(event)

        return '', 200

    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return '', 400


def handle_transactions_update(event):
    """Handle TRANSACTIONS webhook events."""
    item_id = event.get('item_id')
    webhook_code = event.get('webhook_code')

    print(f"Transactions update for item {item_id}: {webhook_code}")
    # Add your logic here to sync transactions


def handle_item_update(event):
    """Handle ITEM webhook events."""
    item_id = event.get('item_id')
    webhook_code = event.get('webhook_code')

    print(f"Item update for item {item_id}: {webhook_code}")
    # Add your logic here to handle item updates


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
    # Check that required environment variables are set
    required_vars = ['PLAID_CLIENT_ID', 'PLAID_SECRET']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with your Plaid credentials")
        exit(1)

    app.run(host='127.0.0.1', port=5000, debug=True)
