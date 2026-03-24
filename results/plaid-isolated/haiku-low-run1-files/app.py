"""
Plaid Link Integration - Python Flask Application
Bank account connection flow with token exchange and webhook handling
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

# Initialize Flask app
app = Flask(__name__)

# Configure Plaid client
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


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """
    Create a Plaid Link token for initiating the account connection flow.

    Returns:
        JSON response with link_token for frontend
    """
    try:
        request_data = LinkTokenCreateRequest(
            user={'client_user_id': 'user-123'},
            client_name='My Banking App',
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
    Exchange a public token from Plaid Link for an access token.

    Expected JSON body:
        {
            "public_token": "<token_from_link>"
        }

    Returns:
        JSON response with access_token and item_id
    """
    try:
        public_token = request.json.get('public_token')
        if not public_token:
            return jsonify({'error': 'Missing public_token'}), 400

        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        response = client.item_public_token_exchange(exchange_request)

        # TODO: Store access_token and item_id securely in your database
        return jsonify({
            'access_token': response.access_token,
            'item_id': response.item_id,
        }), 200
    except ApiException as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """
    Handle incoming Plaid webhooks.

    Verifies webhook signature and processes events like:
    - TRANSACTIONS updates
    - ITEM updates
    - ERROR notifications
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

        webhook_type = event.get('webhook_type')

        if webhook_type == 'TRANSACTIONS':
            # TODO: Handle transactions update
            print(f"Transactions update: {event.get('webhook_code')}")
        elif webhook_type == 'ITEM':
            # TODO: Handle item update
            print(f"Item update: {event.get('webhook_code')}")

        return '', 200
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return '', 400


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    # Validate required environment variables
    required_vars = ['PLAID_CLIENT_ID', 'PLAID_SECRET']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file or environment.")
        exit(1)

    app.run(port=5000, debug=True)
