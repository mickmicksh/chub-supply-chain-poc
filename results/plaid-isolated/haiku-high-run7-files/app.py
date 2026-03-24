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

# Configure Plaid API
environment_map = {
    'sandbox': plaid.Environment.Sandbox,
    'development': plaid.Environment.Development,
    'production': plaid.Environment.Production,
}

plaid_env = os.environ.get('PLAID_ENVIRONMENT', 'sandbox').lower()
configuration = plaid.Configuration(
    host=environment_map.get(plaid_env, plaid.Environment.Sandbox),
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
    """Create a Plaid Link token for initiating bank connection flow."""
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
    except plaid.exceptions.ApiException as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """Exchange public token for access token after user completes Plaid Link flow."""
    try:
        public_token = request.json.get('public_token')
        if not public_token:
            return jsonify({'error': 'public_token is required'}), 400

        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_request)

        return jsonify({
            'access_token': response.access_token,
            'item_id': response.item_id,
        }), 200
    except plaid.exceptions.ApiException as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """Handle Plaid webhook notifications."""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        event = verify_webhook(payload, sig_header, os.environ.get('PLAID_SECRET'))

        if event['webhook_type'] == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif event['webhook_type'] == 'ITEM':
            handle_item_update(event)

        return '', 200
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return '', 400


def handle_transactions_update(event):
    """Process transaction update webhook."""
    print(f"Processing transactions update for item: {event.get('item_id')}")
    # Implement your business logic here


def handle_item_update(event):
    """Process item update webhook."""
    print(f"Processing item update: {event.get('error')}")
    # Implement your business logic here


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(port=5000, debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
