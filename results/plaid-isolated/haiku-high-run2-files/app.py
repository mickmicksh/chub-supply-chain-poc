"""
Plaid Link Integration Flask App
Handles bank account connections via Plaid Link
"""
import os
from flask import Flask, request, jsonify, render_template, send_from_directory
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.exceptions import ApiException
from plaid_link_verify import LinkVerifier, verify_webhook
from dotenv import load_dotenv

load_dotenv()

# Plaid Configuration
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

# Flask App
app = Flask(__name__, static_folder='static', static_url_path='')


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """
    Create a Plaid Link token for initiating the connection flow
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
    Exchange public token for access token after user completes Link flow
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
    Handle webhook events from Plaid
    Verifies signature and processes webhook events
    """
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
        app.logger.error(f'Webhook error: {str(e)}')
        return '', 400


def handle_transactions_update(event):
    """
    Handle transaction webhook updates
    """
    app.logger.info(f'Transaction update: {event}')
    # TODO: Process transaction updates


def handle_item_update(event):
    """
    Handle item webhook updates (e.g., login required)
    """
    app.logger.info(f'Item update: {event}')
    # TODO: Process item updates


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200


@app.route('/', methods=['GET'])
def index():
    """Serve the frontend"""
    return send_from_directory('static', 'index.html')


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('FLASK_PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG', False)
    )
