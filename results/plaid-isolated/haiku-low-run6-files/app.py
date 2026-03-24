"""
Plaid Link Integration - Flask Application
Handles bank account connections with token exchange and webhook verification
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

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure Plaid client
PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
PLAID_SECRET = os.environ.get('PLAID_SECRET')
PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')

if not PLAID_CLIENT_ID or not PLAID_SECRET:
    raise ValueError('PLAID_CLIENT_ID and PLAID_SECRET must be set in environment variables')

environment = plaid.Environment.Sandbox if PLAID_ENV == 'sandbox' else plaid.Environment.Production

configuration = plaid.Configuration(
    host=environment,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
verifier = LinkVerifier(PLAID_SECRET)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200


@app.route('/api/create-link-token', methods=['POST'])
def create_link_token():
    """
    Create a Link token for initializing Plaid Link flow
    Expected JSON: { "user_id": "string" }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default-user')

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name='My Python App',
            products=['auth', 'transactions'],
            country_codes=['US'],
            language='en',
        )

        response = client.link_token_create(request_data)
        return jsonify({
            'link_token': response.link_token,
            'expiration': response.expiration,
        }), 200

    except ApiException as e:
        return jsonify({
            'error': 'Failed to create link token',
            'details': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Unexpected error',
            'details': str(e)
        }), 500


@app.route('/api/exchange-token', methods=['POST'])
def exchange_token():
    """
    Exchange public token for access token
    Expected JSON: { "public_token": "string" }
    """
    try:
        data = request.get_json()
        public_token = data.get('public_token')

        if not public_token:
            return jsonify({'error': 'public_token is required'}), 400

        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_request)

        return jsonify({
            'access_token': response.access_token,
            'item_id': response.item_id,
        }), 200

    except ApiException as e:
        return jsonify({
            'error': 'Failed to exchange token',
            'details': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Unexpected error',
            'details': str(e)
        }), 500


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """
    Handle Plaid webhooks for account and transaction updates
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        if not sig_header:
            return jsonify({'error': 'Missing webhook signature'}), 400

        event = verify_webhook(payload, sig_header, PLAID_SECRET)

        # Log webhook event
        webhook_type = event.get('webhook_type')
        webhook_code = event.get('webhook_code')
        print(f'Received webhook: {webhook_type} - {webhook_code}')

        # Handle different webhook types
        if webhook_type == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif webhook_type == 'ITEM':
            handle_item_update(event)

        return '', 200

    except ValueError as e:
        print(f'Webhook verification failed: {e}')
        return jsonify({'error': 'Invalid webhook signature'}), 401
    except Exception as e:
        print(f'Webhook processing error: {e}')
        return '', 500


def handle_transactions_update(event):
    """Handle transaction webhook updates"""
    print(f'Transactions updated for item: {event.get("item_id")}')
    # TODO: Implement your transaction handling logic


def handle_item_update(event):
    """Handle item webhook updates"""
    print(f'Item updated: {event.get("item_id")} - {event.get("webhook_code")}')
    # TODO: Implement your item handling logic


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
