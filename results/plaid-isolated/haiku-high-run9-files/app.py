"""
Plaid Link Integration - Python Flask App

This module provides endpoints for:
1. Creating Plaid Link tokens for bank account connection
2. Exchanging public tokens for access tokens
3. Handling Plaid webhooks for transaction updates
"""

import os
from flask import Flask, request, jsonify
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.exceptions import ApiException
from plaid_link_verify import LinkVerifier, verify_webhook
from dotenv import load_dotenv

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


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """
    Create a Plaid Link token for initiating the account connection flow.

    Request body:
    {
        "user_id": "user-123",
        "products": ["auth", "transactions"]
    }

    Returns:
    {
        "link_token": "link-token-string"
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'user-default')
        products = data.get('products', ['auth', 'transactions'])

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name='My Banking App',
            products=products,
            country_codes=['US'],
            language='en',
        )

        response = client.link_token_create(request_data)
        return jsonify({'link_token': response.link_token}), 200

    except ApiException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """
    Exchange a Plaid Link public token for an access token.

    Request body:
    {
        "public_token": "public-token-from-link"
    }

    Returns:
    {
        "access_token": "access-token-for-api",
        "item_id": "item-id-string"
    }
    """
    try:
        data = request.get_json()
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
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """
    Handle Plaid webhook notifications for account events.
    Validates webhook signature and processes transaction updates.
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

        # Handle different webhook types
        if event.get('webhook_type') == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif event.get('webhook_type') == 'ITEM':
            handle_item_update(event)

        return '', 200

    except Exception as e:
        print(f'Webhook error: {str(e)}')
        return jsonify({'error': 'Webhook processing failed'}), 400


def handle_transactions_update(event):
    """
    Process transaction update webhook from Plaid.

    Args:
        event: Webhook event payload
    """
    item_id = event.get('item_id')
    webhook_code = event.get('webhook_code')

    print(f'Transaction update for item {item_id}: {webhook_code}')

    # TODO: Add your business logic here
    # - Fetch new transactions using the access token
    # - Update your database
    # - Trigger necessary workflows


def handle_item_update(event):
    """
    Process item update webhook from Plaid.

    Args:
        event: Webhook event payload
    """
    item_id = event.get('item_id')
    webhook_code = event.get('webhook_code')

    print(f'Item update for {item_id}: {webhook_code}')

    # TODO: Handle item-related events
    # - LOGIN_REPAIRED: User successfully re-authenticated
    # - PENDING_EXPIRATION: User action required


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    # Validate required environment variables
    required_vars = ['PLAID_CLIENT_ID', 'PLAID_SECRET']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print(f'Error: Missing required environment variables: {", ".join(missing_vars)}')
        print('Please set them in your .env file or shell environment')
        exit(1)

    app.run(port=5000, debug=True)
