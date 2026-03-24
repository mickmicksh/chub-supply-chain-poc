"""Flask app with Plaid Link integration for bank account connections."""
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_link_verify import LinkVerifier, verify_webhook
from plaid.exceptions import ApiException
from flask import Flask, request, jsonify
import config
import os

# Initialize Flask app
app = Flask(__name__)

# Validate required environment variables
if not config.PLAID_CLIENT_ID or not config.PLAID_SECRET:
    raise ValueError('PLAID_CLIENT_ID and PLAID_SECRET environment variables are required')

# Configure Plaid API client
plaid_env = plaid.Environment.Sandbox if config.PLAID_ENV == 'sandbox' else plaid.Environment.Production
configuration = plaid.Configuration(
    host=plaid_env,
    api_key={
        'clientId': config.PLAID_CLIENT_ID,
        'secret': config.PLAID_SECRET,
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
verifier = LinkVerifier(config.PLAID_SECRET)


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """Create a Plaid Link token for the user to connect their bank account."""
    try:
        user_id = request.json.get('user_id', 'user-123')

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name='My Banking App',
            products=config.PLAID_PRODUCTS,
            country_codes=config.PLAID_COUNTRY_CODES,
            language=config.PLAID_LANGUAGE,
        )

        response = client.link_token_create(request_data)
        return jsonify({'link_token': response.link_token})

    except ApiException as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """Exchange public token for access token after user completes Link flow."""
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
    """Handle webhook events from Plaid (transactions, item updates, etc.)."""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        event = verify_webhook(payload, sig_header, config.PLAID_SECRET)

        # Process different webhook types
        if event['webhook_type'] == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif event['webhook_type'] == 'ITEM':
            handle_item_update(event)

        return '', 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400


def handle_transactions_update(event):
    """Handle transaction-related webhook events."""
    print(f"Transactions update: {event['webhook_code']}")
    # TODO: Implement transaction sync logic


def handle_item_update(event):
    """Handle item-related webhook events."""
    print(f"Item update: {event['webhook_code']}")
    # TODO: Implement item update logic


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=config.DEBUG)
