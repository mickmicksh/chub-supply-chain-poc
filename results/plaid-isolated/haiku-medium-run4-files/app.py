import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_link_verify import LinkVerifier, verify_webhook
from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
from plaid.exceptions import ApiException

# Load environment variables
load_dotenv()

# Configure Plaid API client
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

app = Flask(__name__, template_folder='templates')

@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """Create a Plaid Link token for initializing Link flow on frontend"""
    try:
        user_id = request.json.get('user_id', 'user-123')

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
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
    """Exchange public token for access token after user completes Link flow"""
    try:
        public_token = request.json.get('public_token')

        if not public_token:
            return jsonify({'error': 'public_token is required'}), 400

        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_request)

        # Store access_token and item_id in your database
        return jsonify({
            'access_token': response.access_token,
            'item_id': response.item_id,
        })
    except ApiException as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """Handle Plaid webhook events"""
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
    """Process transaction updates from webhook"""
    print(f"Processing transaction update for item: {event.get('item_id')}")
    # Add your transaction handling logic here

def handle_item_update(event):
    """Process item updates from webhook"""
    print(f"Processing item update: {event.get('error')}")
    # Add your item update handling logic here

@app.route('/', methods=['GET'])
def index():
    """Serve the Plaid Link page"""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
