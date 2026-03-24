"""Plaid Link integration Flask application for bank account connections."""

import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.exceptions import ApiException
from plaid_link_verify import LinkVerifier, verify_webhook

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure Plaid client
PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')
plaid_env = plaid.Environment.Sandbox if PLAID_ENV == 'sandbox' else plaid.Environment.Production

configuration = plaid.Configuration(
    host=plaid_env,
    api_key={
        'clientId': os.environ.get('PLAID_CLIENT_ID'),
        'secret': os.environ.get('PLAID_SECRET'),
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
verifier = LinkVerifier(os.environ.get('PLAID_SECRET'))


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """Create a Plaid Link token for initiating bank account connection."""
    try:
        data = request.json or {}
        user_id = data.get('user_id', 'user-123')

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name='My App',
            products=['auth', 'transactions'],
            country_codes=['US'],
            language='en',
        )

        response = client.link_token_create(request_data)

        return jsonify({
            'link_token': response.link_token,
            'expiration': response.expiration,
        })

    except ApiException as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """Exchange Plaid public token for access token."""
    try:
        data = request.json or {}
        public_token = data.get('public_token')

        if not public_token:
            return jsonify({'error': 'Missing public_token'}), 400

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
    """Handle Plaid webhooks for transaction and account updates."""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        event = verify_webhook(payload, sig_header, os.environ.get('PLAID_SECRET'))

        webhook_type = event.get('webhook_type')
        webhook_code = event.get('webhook_code')

        if webhook_type == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif webhook_type == 'ITEM':
            handle_item_update(event)

        return '', 200

    except Exception as e:
        app.logger.error(f"Webhook error: {str(e)}")
        return '', 400


def handle_transactions_update(event):
    """Process transaction webhook events."""
    webhook_code = event.get('webhook_code')

    if webhook_code == 'TRANSACTIONS_UPDATES':
        # Handle transaction updates
        item_id = event.get('item_id')
        accounts = event.get('new_transactions', [])
        app.logger.info(f"Transactions updated for item {item_id}: {len(accounts)} new transactions")

    elif webhook_code == 'INITIAL_UPDATE':
        # Handle initial transaction sync
        app.logger.info("Initial transaction sync complete")


def handle_item_update(event):
    """Process item webhook events."""
    webhook_code = event.get('webhook_code')

    if webhook_code == 'PENDING_EXPIRATION':
        # Item access token expiring soon
        item_id = event.get('item_id')
        app.logger.warning(f"Item {item_id} access token expiring soon")

    elif webhook_code == 'WEBHOOK_UPDATE_ACKNOWLEDGED':
        # Webhook acknowledged
        app.logger.info("Webhook update acknowledged")


@app.errorhandler(400)
def bad_request(error):
    """Handle bad request errors."""
    return jsonify({'error': 'Bad request'}), 400


@app.errorhandler(404)
def not_found(error):
    """Handle not found errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    app.logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Verify required environment variables
    required_vars = ['PLAID_CLIENT_ID', 'PLAID_SECRET']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please copy .env.example to .env and fill in your Plaid credentials")
        exit(1)

    app.run(port=5000, debug=True)
