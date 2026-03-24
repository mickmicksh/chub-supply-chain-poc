import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_link_verify import LinkVerifier, verify_webhook
from flask import Flask, request, jsonify
from plaid.exceptions import ApiException
import os
from dotenv import load_dotenv

# Load environment variables from .env file
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

app = Flask(__name__)


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """Create a Link token for initializing Plaid Link"""
    try:
        request_data = LinkTokenCreateRequest(
            user={'client_user_id': 'user-123'},
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
    """Exchange public token for access token"""
    try:
        public_token = request.json.get('public_token')
        if not public_token:
            return jsonify({'error': 'public_token is required'}), 400

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
    """Handle Plaid webhooks"""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')
        event = verify_webhook(payload, sig_header, os.environ.get('PLAID_SECRET'))

        # Handle different webhook types
        if event.get('webhook_type') == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif event.get('webhook_type') == 'ITEM':
            handle_item_update(event)

        return '', 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return '', 400


def handle_transactions_update(event):
    """Process transactions webhook"""
    item_id = event.get('item_id')
    webhook_code = event.get('webhook_code')
    print(f"Transactions update for item {item_id}: {webhook_code}")
    # Add your transaction processing logic here


def handle_item_update(event):
    """Process item webhook"""
    item_id = event.get('item_id')
    webhook_code = event.get('webhook_code')
    print(f"Item update for {item_id}: {webhook_code}")
    # Add your item processing logic here


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(port=5000, debug=True)
