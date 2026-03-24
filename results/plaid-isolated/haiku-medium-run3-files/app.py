"""
Plaid Link Integration - Flask Application
Handles bank account connection flow with token exchange and webhook handling
"""

import os
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_link_verify import LinkVerifier, verify_webhook
from flask import Flask, request, jsonify
from plaid.exceptions import ApiException

# Load environment variables
load_dotenv()

# Configure Plaid SDK
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


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """
    Create a Plaid Link token for the front-end to initialize Link.
    The @verifier.protect decorator validates the request signature.
    """
    try:
        request_data = LinkTokenCreateRequest(
            user={'client_user_id': request.json.get('user_id', 'user-123')},
            client_name='My App',
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
    """
    Exchange the public token from Plaid Link for an access token.
    The access token is used for authenticated API calls.
    """
    try:
        public_token = request.json.get('public_token')
        if not public_token:
            return jsonify({'error': 'public_token required'}), 400

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
    """
    Handle Plaid webhook events.
    Validates webhook signature using plaid-link-verify.
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')
        event = verify_webhook(
            payload,
            sig_header,
            os.environ.get('PLAID_SECRET')
        )

        if event['webhook_type'] == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif event['webhook_type'] == 'ITEM':
            handle_item_update(event)

        return '', 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


def handle_transactions_update(event):
    """Handle TRANSACTIONS webhook events from Plaid."""
    print(f"Transactions update: {event}")
    # TODO: Implement your business logic here


def handle_item_update(event):
    """Handle ITEM webhook events from Plaid."""
    print(f"Item update: {event}")
    # TODO: Implement your business logic here


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    # Validate required environment variables
    if not os.environ.get('PLAID_CLIENT_ID'):
        print("ERROR: PLAID_CLIENT_ID not set in environment variables")
        exit(1)
    if not os.environ.get('PLAID_SECRET'):
        print("ERROR: PLAID_SECRET not set in environment variables")
        exit(1)

    app.run(port=5000, debug=True)
