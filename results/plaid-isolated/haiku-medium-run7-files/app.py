"""
Plaid Link Integration for Bank Account Connections
Includes token exchange, webhook handling, and error management
"""

import os
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_link_verify import LinkVerifier, verify_webhook
from plaid.exceptions import ApiException
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Plaid API Client
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

app = Flask(__name__)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """
    Create a Plaid Link token for initiating bank account connection

    Expected JSON:
    {
        "user_id": "unique_user_identifier",
        "client_name": "Your App Name"
    }
    """
    try:
        data = request.get_json() or {}
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

        return jsonify({
            'link_token': response.link_token,
            'expiration': response.expiration
        }), 200

    except ApiException as e:
        return jsonify({
            'error': 'Failed to create link token',
            'details': str(e)
        }), 400


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """
    Exchange a public token from Plaid Link for an access token

    Expected JSON:
    {
        "public_token": "public-token-from-link"
    }
    """
    try:
        data = request.get_json() or {}
        public_token = data.get('public_token')

        if not public_token:
            return jsonify({'error': 'public_token is required'}), 400

        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        response = client.item_public_token_exchange(exchange_request)

        # In production, store this access token securely (encrypted database)
        return jsonify({
            'access_token': response.access_token,
            'item_id': response.item_id,
        }), 200

    except ApiException as e:
        return jsonify({
            'error': 'Failed to exchange token',
            'details': str(e)
        }), 400


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """
    Handle Plaid webhook notifications
    Verifies webhook signature and processes events
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        # Verify webhook signature
        event = verify_webhook(
            payload,
            sig_header,
            os.environ.get('PLAID_SECRET')
        )

        # Process webhook event
        webhook_type = event.get('webhook_type')

        if webhook_type == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif webhook_type == 'ITEM':
            handle_item_update(event)

        return '', 200

    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return '', 401


def handle_transactions_update(event):
    """Handle transaction update webhooks"""
    print(f"Transactions updated for item: {event.get('item_id')}")
    # Implement your transaction handling logic here


def handle_item_update(event):
    """Handle item update webhooks (e.g., auth required)"""
    print(f"Item update: {event.get('error')}")
    # Implement your item update handling logic here


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
