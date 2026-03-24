"""Plaid Link integration for bank account connections."""

import os
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_link_verify import LinkVerifier, verify_webhook
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from plaid.exceptions import ApiException

# Load environment variables
load_dotenv()

# Configure Plaid client
PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox').lower()
host = plaid.Environment.Sandbox if PLAID_ENV == 'sandbox' else plaid.Environment.Production

configuration = plaid.Configuration(
    host=host,
    api_key={
        'clientId': os.environ.get('PLAID_CLIENT_ID'),
        'secret': os.environ.get('PLAID_SECRET'),
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
verifier = LinkVerifier(os.environ.get('PLAID_SECRET'))

app = Flask(__name__)


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """Create a Plaid Link token for the frontend."""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'user-123')

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name='My App',
            products=['auth', 'transactions'],
            country_codes=['US'],
            language='en',
        )
        response = client.link_token_create(request_data)
        return jsonify({'link_token': response.link_token})

    except ApiException as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """Exchange public token for access token."""
    try:
        public_token = request.json.get('public_token')
        if not public_token:
            return jsonify({'error': 'public_token required'}), 400

        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_request)

        return jsonify({
            'access_token': response.access_token,
            'item_id': response.item_id,
        })

    except ApiException as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """Handle Plaid webhook events."""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        event = verify_webhook(payload, sig_header, os.environ.get('PLAID_SECRET'))

        # Handle different webhook types
        if event.get('webhook_type') == 'TRANSACTIONS':
            print(f"Transactions update: {event}")
        elif event.get('webhook_type') == 'ITEM':
            print(f"Item event: {event}")

        return '', 200

    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return '', 401


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    # Validate required environment variables
    required_vars = ['PLAID_CLIENT_ID', 'PLAID_SECRET']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment.")
        exit(1)

    app.run(port=5000, debug=True)
