"""Plaid Link integration Flask application."""

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

# Plaid API configuration
PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')
environment = plaid.Environment.Sandbox if PLAID_ENV == 'sandbox' else plaid.Environment.Production

configuration = plaid.Configuration(
    host=environment,
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
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """
    Create a Plaid Link token for the frontend to initialize Link.

    Expected JSON body:
    {
        "user_id": "user-123"
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default-user')

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name='My App',
            products=['auth', 'transactions'],
            country_codes=['US'],
            language='en',
        )
        response = client.link_token_create(request_data)
        return jsonify({'link_token': response.link_token}), 200
    except plaid.exceptions.ApiException as e:
        return jsonify({'error': str(e)}), 400


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
    Plaid webhook endpoint for receiving account update events.
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        event = verify_webhook(payload, sig_header, os.environ.get('PLAID_SECRET'))

        webhook_type = event.get('webhook_type')
        webhook_code = event.get('webhook_code')

        print(f"Received webhook: {webhook_type} - {webhook_code}")

        # Handle different webhook types
        if webhook_type == 'TRANSACTIONS':
            print(f"Transactions update: {event.get('item_id')}")
        elif webhook_type == 'AUTH':
            print(f"Auth update: {event.get('item_id')}")
        elif webhook_type == 'ITEM':
            if webhook_code == 'ERROR':
                print(f"Item error: {event.get('error')}")

        return '', 200
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return '', 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=os.environ.get('FLASK_DEBUG', 'True').lower() == 'true')
