import os
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_link_verify import LinkVerifier, verify_webhook
from plaid.exceptions import ApiException
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure Plaid API
PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox').lower()
plaid_env = plaid.Environment.Sandbox if PLAID_ENV == 'sandbox' else plaid.Environment.Production

configuration = plaid.Configuration(
    host=plaid_env,
    api_key={
        'clientId': os.environ.get('PLAID_CLIENT_ID'),
        'secret': os.environ.get('PLAID_SECRET'),
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
verifier = LinkVerifier(os.environ.get('PLAID_SECRET'))


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """Create a Plaid Link token for initiating the bank connection flow."""
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

        return jsonify({'link_token': response.link_token}), 200
    except ApiException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to create link token: {str(e)}'}), 500


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """Exchange a public token for an access token after user connects their bank."""
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
    except Exception as e:
        return jsonify({'error': f'Failed to exchange token: {str(e)}'}), 500


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """Handle Plaid webhook events (transactions updates, etc)."""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        event = verify_webhook(payload, sig_header, os.environ.get('PLAID_SECRET'))

        webhook_type = event.get('webhook_type')
        if webhook_type == 'TRANSACTIONS':
            handle_transactions_update(event)

        return '', 200
    except Exception as e:
        app.logger.error(f'Webhook error: {str(e)}')
        return '', 400


def handle_transactions_update(event):
    """Process transaction update events from Plaid."""
    item_id = event.get('item_id')
    new_transactions = event.get('new_transactions', 0)
    modified_transactions = event.get('modified_transactions', 0)
    removed_transactions = event.get('removed_transactions', 0)

    app.logger.info(
        f'Transactions update for item {item_id}: '
        f'+{new_transactions} modified {modified_transactions} -{removed_transactions}'
    )


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    if not os.environ.get('PLAID_CLIENT_ID') or not os.environ.get('PLAID_SECRET'):
        print('ERROR: Missing required environment variables PLAID_CLIENT_ID and PLAID_SECRET')
        print('Please create a .env file with your Plaid credentials (see .env.example)')
        exit(1)

    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
