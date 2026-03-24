"""
Plaid Link Integration - Python Flask App
Handles bank account connections via Plaid Link
"""

import os
from typing import Dict, Any

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_link_verify import LinkVerifier, verify_webhook
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Plaid configuration
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
def create_link_token() -> tuple[Dict[str, Any], int]:
    """
    Create a Plaid Link token for the client.
    This token is required to initialize Plaid Link on the frontend.
    """
    try:
        user_id = request.json.get('user_id', 'user-123')

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
            'expiration': response.expiration
        }), 200

    except plaid.exceptions.ApiException as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token() -> tuple[Dict[str, Any], int]:
    """
    Exchange a Plaid Link public token for an access token.
    The public token is returned by Plaid Link after successful authentication.
    """
    try:
        public_token = request.json.get('public_token')

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

    except plaid.exceptions.ApiException as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook() -> tuple[str, int]:
    """
    Handle Plaid webhook events (transactions updates, item errors, etc.)
    Verifies webhook signature for security.
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
        if event['webhook_type'] == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif event['webhook_type'] == 'ITEM':
            handle_item_update(event)

        return '', 200

    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return '', 400


def handle_transactions_update(event: Dict[str, Any]) -> None:
    """Handle TRANSACTIONS webhook events."""
    print(f"Transactions update for item {event.get('item_id')}")
    # TODO: Update your database with new transactions
    pass


def handle_item_update(event: Dict[str, Any]) -> None:
    """Handle ITEM webhook events."""
    print(f"Item update for item {event.get('item_id')}")
    # TODO: Handle item errors, consent expiration, etc.
    pass


@app.route('/health', methods=['GET'])
def health_check() -> tuple[Dict[str, str], int]:
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(port=5000, debug=True)
