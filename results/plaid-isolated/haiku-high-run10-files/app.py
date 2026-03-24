"""
Plaid Link Integration - Flask Application
"""
import os
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_link_verify import LinkVerifier, verify_webhook
from plaid.exceptions import ApiException
from flask import Flask, request, jsonify

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure Plaid API
plaid_environment = os.environ.get('PLAID_ENV', 'sandbox').lower()
environment_map = {
    'sandbox': plaid.Environment.Sandbox,
    'development': plaid.Environment.Development,
    'production': plaid.Environment.Production,
}

configuration = plaid.Configuration(
    host=environment_map.get(plaid_environment, plaid.Environment.Sandbox),
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
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """
    Create a Link token for the Plaid Link flow
    Returns a link_token to initialize Plaid Link on the frontend
    """
    try:
        data = request.json or {}
        user_id = data.get('user_id', 'user-123')

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
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
    Exchange a public token for an access token
    Called after user completes Plaid Link flow
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
    except ApiException as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """
    Handle Plaid webhook events
    Validates webhook signature and processes events
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        event = verify_webhook(
            payload,
            sig_header,
            os.environ.get('PLAID_SECRET')
        )

        webhook_type = event.get('webhook_type')
        webhook_code = event.get('webhook_code')

        print(f"Received webhook: {webhook_type} - {webhook_code}")

        # Handle different webhook types
        if webhook_type == 'TRANSACTIONS':
            handle_transactions_webhook(event)
        elif webhook_type == 'ITEM':
            handle_item_webhook(event)

        return jsonify({'status': 'received'}), 200
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 400


def handle_transactions_webhook(event):
    """Handle transaction-related webhooks"""
    webhook_code = event.get('webhook_code')
    if webhook_code == 'TRANSACTIONS_UPDATED':
        # New transactions available
        print(f"Transactions updated for item: {event.get('item_id')}")
    elif webhook_code == 'INITIAL_UPDATE':
        # Initial transaction pull complete
        print(f"Initial transaction update for item: {event.get('item_id')}")


def handle_item_webhook(event):
    """Handle item-related webhooks"""
    webhook_code = event.get('webhook_code')
    if webhook_code == 'WEBHOOK_UPDATE_ACKNOWLEDGED':
        print(f"Item webhook acknowledged: {event.get('item_id')}")


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Verify required environment variables
    required_vars = ['PLAID_CLIENT_ID', 'PLAID_SECRET']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set up your .env file using .env.example as a template")
        exit(1)

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
