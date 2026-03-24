"""
Plaid Link Integration Flask App
Bank account connection flow with token exchange and webhook handling
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
PLAID_ENV = getattr(plaid.Environment, os.environ.get('PLAID_ENV', 'Sandbox'))

configuration = plaid.Configuration(
    host=PLAID_ENV,
    api_key={
        'clientId': os.environ.get('PLAID_CLIENT_ID'),
        'secret': os.environ.get('PLAID_SECRET'),
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
verifier = LinkVerifier(os.environ.get('PLAID_SECRET'))

app = Flask(__name__)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """
    Create a Link token for initializing Plaid Link UI

    Request body:
    {
        "user_id": "user-123"
    }
    """
    try:
        data = request.json or {}
        user_id = data.get('user_id', 'user-default')

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name='My Banking App',
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
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """
    Exchange public token for access token

    Request body:
    {
        "public_token": "public-xxx"
    }
    """
    try:
        data = request.json or {}
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
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """
    Plaid webhook endpoint for receiving account and transaction updates
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        event = verify_webhook(payload, sig_header, os.environ.get('PLAID_SECRET'))

        # Log the event
        print(f"Webhook received: {event.get('webhook_type')}")

        # Handle different webhook types
        webhook_type = event.get('webhook_type')
        if webhook_type == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif webhook_type == 'ITEM':
            handle_item_update(event)

        return '', 200

    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return '', 400


def handle_transactions_update(event):
    """Handle TRANSACTIONS webhook events"""
    webhook_code = event.get('webhook_code')
    print(f"Transactions webhook code: {webhook_code}")
    # Implement your transaction update logic here
    pass


def handle_item_update(event):
    """Handle ITEM webhook events"""
    webhook_code = event.get('webhook_code')
    print(f"Item webhook code: {webhook_code}")
    # Implement your item update logic here
    pass


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG', True)
    )
