"""
Plaid Link Integration Flask App
Handles bank account connections with token exchange and webhook handling
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

# Initialize Flask app
app = Flask(__name__)

# Plaid configuration
PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
PLAID_SECRET = os.environ.get('PLAID_SECRET')
PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')

# Validate required environment variables
if not PLAID_CLIENT_ID or not PLAID_SECRET:
    raise ValueError("PLAID_CLIENT_ID and PLAID_SECRET must be set")

# Configure Plaid client
environment = (
    plaid.Environment.Production
    if PLAID_ENV == 'production'
    else plaid.Environment.Sandbox
)

configuration = plaid.Configuration(
    host=environment,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# Initialize verifier for token and webhook validation
verifier = LinkVerifier(PLAID_SECRET)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """
    Create a Plaid Link token for client-side linking

    Request body:
    {
        "user_id": "unique_user_id",
        "products": ["auth", "transactions"],  # optional
        "country_codes": ["US"]  # optional
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        products = data.get('products', ['auth', 'transactions'])
        country_codes = data.get('country_codes', ['US'])

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name='My App',
            products=products,
            country_codes=country_codes,
            language='en',
        )

        response = client.link_token_create(request_data)

        return jsonify({
            'link_token': response.link_token,
            'expiration': response.expiration
        }), 200

    except ApiException as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """
    Exchange public token for access token

    Request body:
    {
        "public_token": "public-token-from-link"
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


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """
    Webhook endpoint for Plaid events
    Signature verification is automatic via LinkVerifier
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        # Verify webhook signature
        event = verify_webhook(
            payload,
            sig_header,
            PLAID_SECRET
        )

        # Handle different webhook types
        webhook_type = event.get('webhook_type')
        webhook_code = event.get('webhook_code')

        if webhook_type == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif webhook_type == 'ITEM':
            handle_item_update(event)
        else:
            print(f"Unhandled webhook type: {webhook_type}")

        return '', 200

    except Exception as e:
        print(f"Webhook error: {e}")
        return '', 400


def handle_transactions_update(event):
    """Handle transaction update webhooks"""
    item_id = event.get('item_id')
    webhook_code = event.get('webhook_code')

    print(f"Transactions updated - Item: {item_id}, Code: {webhook_code}")
    # TODO: Implement your transaction sync logic here


def handle_item_update(event):
    """Handle item update webhooks"""
    item_id = event.get('item_id')
    webhook_code = event.get('webhook_code')

    print(f"Item updated - Item: {item_id}, Code: {webhook_code}")
    # TODO: Implement your item sync logic here


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('DEBUG', 'False') == 'True'
    )
