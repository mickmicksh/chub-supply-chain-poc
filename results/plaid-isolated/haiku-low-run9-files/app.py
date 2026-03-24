"""Plaid Link integration Flask app for bank account connections."""

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

# Initialize Flask app
app = Flask(__name__)

# Configure Plaid client
PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
PLAID_SECRET = os.environ.get('PLAID_SECRET')
PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')

# Set Plaid environment
plaid_environment = (
    plaid.Environment.Sandbox if PLAID_ENV == 'sandbox'
    else plaid.Environment.Production
)

configuration = plaid.Configuration(
    host=plaid_environment,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
verifier = LinkVerifier(PLAID_SECRET)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """Create a Plaid Link token for the frontend."""
    try:
        # Get user ID from request (could be from JWT token in production)
        data = request.json
        user_id = data.get('user_id', 'user-123')

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name='Bank Account Connect',
            products=['auth', 'transactions'],
            country_codes=['US'],
            language='en',
        )
        response = client.link_token_create(request_data)
        return jsonify({'link_token': response.link_token}), 200
    except ApiException as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """Exchange public token for access token."""
    try:
        data = request.json
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
        return jsonify({'error': str(e)}), 400


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """Handle Plaid webhook notifications."""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        # Verify webhook signature
        event = verify_webhook(payload, sig_header, PLAID_SECRET)

        # Handle different webhook types
        if event.get('webhook_type') == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif event.get('webhook_type') == 'ITEM':
            handle_item_update(event)

        return '', 200
    except Exception as e:
        app.logger.error(f'Webhook error: {str(e)}')
        return '', 400


def handle_transactions_update(event):
    """Handle transactions webhook updates."""
    webhook_code = event.get('webhook_code')
    item_id = event.get('item_id')
    app.logger.info(
        f'Transactions update: {webhook_code} for item {item_id}'
    )
    # Implement your transaction sync logic here


def handle_item_update(event):
    """Handle item webhook updates."""
    webhook_code = event.get('webhook_code')
    item_id = event.get('item_id')
    app.logger.info(f'Item update: {webhook_code} for item {item_id}')
    # Implement your item update logic here


if __name__ == '__main__':
    app.run(port=5000, debug=True)
