"""
Plaid Link Integration - Flask Backend
Handles bank account connections via Plaid Link
"""

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

# Configure Plaid API
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

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """
    Create a Link token for the Plaid Link flow.
    This token is used to initialize the Link modal on the frontend.
    """
    try:
        user_id = request.json.get('user_id', 'user-123')

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name='Bank Connection App',
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
    """
    Exchange a public_token from Plaid Link for an access_token.
    The access_token is used to make API calls on behalf of the user.
    """
    try:
        public_token = request.json.get('public_token')

        if not public_token:
            return jsonify({'error': 'public_token is required'}), 400

        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_request)

        # TODO: Store access_token and item_id securely in your database
        # Example: db.save_bank_connection(user_id, response.access_token, response.item_id)

        return jsonify({
            'access_token': response.access_token,
            'item_id': response.item_id,
        })

    except ApiException as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """
    Handle webhooks from Plaid.
    Plaid sends events for transactions updates, auth updates, etc.
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        # Verify webhook signature
        event = verify_webhook(payload, sig_header, os.environ.get('PLAID_SECRET'))

        # Handle different webhook types
        if event.get('webhook_type') == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif event.get('webhook_type') == 'AUTH':
            handle_auth_update(event)
        elif event.get('webhook_type') == 'ITEM':
            handle_item_update(event)

        return '', 200

    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return '', 400


def handle_transactions_update(event):
    """Handle transactions webhook updates"""
    print(f"Transactions update: {event.get('webhook_code')}")
    # TODO: Process transactions update
    # Example: fetch new transactions for item_id


def handle_auth_update(event):
    """Handle authentication webhook updates"""
    print(f"Auth update: {event.get('webhook_code')}")
    # TODO: Process auth update


def handle_item_update(event):
    """Handle item webhook updates"""
    print(f"Item update: {event.get('webhook_code')}")
    # TODO: Process item update


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})


@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler"""
    return jsonify({'error': str(error)}), 500


if __name__ == '__main__':
    # Check for required environment variables
    required_vars = ['PLAID_CLIENT_ID', 'PLAID_SECRET']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in a .env file or system environment")
        exit(1)

    app.run(port=5000, debug=True)
