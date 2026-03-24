"""
Plaid Link Integration - Flask Application
Bank account connection flow with token exchange and webhook handling
"""

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_link_verify import LinkVerifier, verify_webhook
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure Plaid API
PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
PLAID_SECRET = os.environ.get('PLAID_SECRET')
PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')

# Map environment string to Plaid enum
env_map = {
    'sandbox': plaid.Environment.Sandbox,
    'development': plaid.Environment.Development,
    'production': plaid.Environment.Production,
}

configuration = plaid.Configuration(
    host=env_map.get(PLAID_ENV, plaid.Environment.Sandbox),
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
verifier = LinkVerifier(PLAID_SECRET)


@app.route('/api/create-link-token', methods=['POST'])
def create_link_token():
    """
    Create a Plaid Link token for initializing Link in the frontend.

    Request body:
    {
        "user_id": "user-123",
        "country_codes": ["US"],
        "language": "en"
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id', 'user-default')
        country_codes = data.get('country_codes', ['US'])
        language = data.get('language', 'en')

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name='Bank Connection App',
            products=['auth', 'transactions'],
            country_codes=country_codes,
            language=language,
        )

        response = client.link_token_create(request_data)

        return jsonify({
            'link_token': response.link_token,
            'expiration': response.expiration,
        })
    except plaid.exceptions.ApiException as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/exchange-token', methods=['POST'])
def exchange_token():
    """
    Exchange a public token for an access token.
    This should be called after user successfully links their account.

    Request body:
    {
        "public_token": "public-xxx"
    }
    """
    try:
        data = request.json
        public_token = data.get('public_token')

        if not public_token:
            return jsonify({'error': 'public_token is required'}), 400

        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        response = client.item_public_token_exchange(exchange_request)

        # TODO: Store access_token and item_id securely in your database
        # database.save_account({
        #     'access_token': response.access_token,
        #     'item_id': response.item_id,
        # })

        return jsonify({
            'access_token': response.access_token,
            'item_id': response.item_id,
        })
    except plaid.exceptions.ApiException as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """
    Handle Plaid webhook notifications for account updates,
    transaction syncs, and other events.
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        # Verify webhook signature
        event = verify_webhook(payload, sig_header, PLAID_SECRET)

        # Handle different webhook types
        webhook_type = event.get('webhook_type')

        if webhook_type == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif webhook_type == 'AUTH':
            handle_auth_update(event)
        elif webhook_type == 'ITEM':
            handle_item_update(event)

        return '', 200
    except Exception as e:
        app.logger.error(f'Webhook error: {str(e)}')
        return '', 400


def handle_transactions_update(event):
    """Handle transactions webhook event."""
    item_id = event.get('item_id')
    webhook_code = event.get('webhook_code')
    app.logger.info(f'Transactions update for item {item_id}: {webhook_code}')
    # TODO: Implement transaction update logic


def handle_auth_update(event):
    """Handle auth webhook event."""
    item_id = event.get('item_id')
    webhook_code = event.get('webhook_code')
    app.logger.info(f'Auth update for item {item_id}: {webhook_code}')
    # TODO: Implement auth update logic


def handle_item_update(event):
    """Handle item webhook event."""
    item_id = event.get('item_id')
    webhook_code = event.get('webhook_code')
    app.logger.info(f'Item update for item {item_id}: {webhook_code}')
    # TODO: Implement item update logic


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200


@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
