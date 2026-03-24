"""
Plaid Link integration for bank account connections
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

# Configure Plaid API
PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
PLAID_SECRET = os.environ.get('PLAID_SECRET')
PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox').lower()

# Map environment string to Plaid constant
plaid_env = getattr(plaid.Environment, PLAID_ENV.capitalize(), plaid.Environment.Sandbox)

configuration = plaid.Configuration(
    host=plaid_env,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
verifier = LinkVerifier(PLAID_SECRET)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Store linked items (in production, use a database)
linked_items = {}


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """
    Create a Plaid Link token for the frontend to initialize Link flow
    """
    try:
        user_id = request.json.get('user_id', 'user-123')

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name='My Bank App',
            products=['auth', 'transactions'],
            country_codes=['US'],
            language='en',
        )

        response = client.link_token_create(request_data)
        return jsonify({'link_token': response.link_token}), 200

    except ApiException as e:
        return jsonify({'error': f'Failed to create link token: {str(e)}'}), 400


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """
    Exchange the public token from Link for an access token
    """
    try:
        public_token = request.json.get('public_token')
        user_id = request.json.get('user_id', 'user-123')

        if not public_token:
            return jsonify({'error': 'public_token is required'}), 400

        # Exchange public token for access token
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_request)

        # Store the access token (in production, encrypt and store in database)
        linked_items[user_id] = {
            'access_token': response.access_token,
            'item_id': response.item_id,
            'institution_id': getattr(response, 'institution_id', None),
        }

        return jsonify({
            'access_token': response.access_token,
            'item_id': response.item_id,
        }), 200

    except ApiException as e:
        return jsonify({'error': f'Failed to exchange token: {str(e)}'}), 400


@app.route('/api/accounts/<user_id>', methods=['GET'])
def get_accounts(user_id):
    """
    Retrieve accounts for a linked user
    """
    try:
        if user_id not in linked_items:
            return jsonify({'error': 'User not linked'}), 404

        access_token = linked_items[user_id]['access_token']

        # Get accounts
        from plaid.model.accounts_get_request import AccountsGetRequest
        response = client.accounts_get(AccountsGetRequest(access_token=access_token))

        accounts = [
            {
                'account_id': acc.account_id,
                'name': acc.name,
                'subtype': acc.subtype,
                'type': acc.type,
                'balances': {
                    'available': acc.balances.available,
                    'current': acc.balances.current,
                    'limit': acc.balances.limit,
                }
            }
            for acc in response.accounts
        ]

        return jsonify({'accounts': accounts}), 200

    except ApiException as e:
        return jsonify({'error': f'Failed to retrieve accounts: {str(e)}'}), 400


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """
    Handle Plaid webhook notifications
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        # Verify webhook signature
        event = verify_webhook(payload, sig_header, PLAID_SECRET)

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
    """Handle TRANSACTIONS webhook event"""
    app.logger.info(f'Transactions update: {event}')
    # Process transactions update
    # In production: fetch new transactions, update database, etc.


def handle_item_update(event):
    """Handle ITEM webhook event"""
    app.logger.info(f'Item update: {event}')
    # Process item update (e.g., consent expired, login required)
    # In production: notify user, trigger re-authentication, etc.


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
