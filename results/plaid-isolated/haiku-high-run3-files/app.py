import os
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_link_verify import LinkVerifier, verify_webhook
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from plaid.exceptions import ApiException

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure Plaid API
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


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the server is running."""
    return jsonify({'status': 'healthy'}), 200


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """
    Create a Plaid Link token for initiating the account connection flow.

    Expected JSON body:
    {
        "client_user_id": "user-123"
    }
    """
    try:
        data = request.get_json() or {}
        user_id = data.get('client_user_id', 'user-default')

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


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """
    Exchange a public token for an access token after user completes Link flow.

    Expected JSON body:
    {
        "public_token": "public-token-from-link"
    }
    """
    try:
        data = request.get_json() or {}
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


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """
    Handle incoming webhooks from Plaid.
    Verifies webhook signature and processes events.
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        event = verify_webhook(
            payload,
            sig_header,
            os.environ.get('PLAID_SECRET')
        )

        # Process based on webhook type
        if event.get('webhook_type') == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif event.get('webhook_type') == 'ITEM':
            handle_item_update(event)

        return '', 200
    except Exception as e:
        app.logger.error(f'Webhook processing error: {str(e)}')
        return '', 400


def handle_transactions_update(event):
    """Handle transaction update webhook events."""
    app.logger.info(f'Transaction update: {event.get("item_id")}')
    # TODO: Implement transaction update logic
    pass


def handle_item_update(event):
    """Handle item update webhook events."""
    app.logger.info(f'Item update: {event.get("item_id")}')
    # TODO: Implement item update logic
    pass


@app.errorhandler(400)
def bad_request(error):
    """Handle bad request errors."""
    return jsonify({'error': 'Bad request'}), 400


@app.errorhandler(404)
def not_found(error):
    """Handle not found errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle server errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
