import os
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_link_verify import LinkVerifier, verify_webhook
from flask import Flask, request, jsonify, send_from_directory
from plaid.exceptions import ApiException
from dotenv import load_dotenv

# Load environment variables
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

app = Flask(__name__, static_folder='static', static_url_path='')

# Serve the main page
@app.route('/', methods=['GET'])
def index():
    return send_from_directory('static', 'index.html')

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

# Create Link Token for initiating the Plaid Link flow
@app.route('/api/create-link-token', methods=['POST'])
def create_link_token():
    try:
        request_data = LinkTokenCreateRequest(
            user={'client_user_id': 'user-123'},
            client_name='My App',
            products=['auth', 'transactions'],
            country_codes=['US'],
            language='en',
        )
        response = client.link_token_create(request_data)
        return jsonify({'link_token': response.link_token}), 200
    except ApiException as e:
        return jsonify({'error': str(e)}), 400

# Exchange public token for access token
@app.route('/api/exchange-token', methods=['POST'])
def exchange_token():
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
    except ApiException as e:
        return jsonify({'error': str(e)}), 400

# Webhook endpoint for Plaid events
@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')
        event = verify_webhook(payload, sig_header, os.environ.get('PLAID_SECRET'))

        if event['webhook_type'] == 'TRANSACTIONS':
            handle_transactions_update(event)

        return '', 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return '', 400

def handle_transactions_update(event):
    """Handle transaction update webhooks from Plaid"""
    print(f"Transactions updated: {event}")
    # Add your business logic here

if __name__ == '__main__':
    app.run(port=5000, debug=True)
