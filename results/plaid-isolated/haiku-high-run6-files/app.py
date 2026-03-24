"""
Plaid Link Integration - Flask Backend
Handles bank account connections via Plaid Link
"""

import os
import logging
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_link_verify import LinkVerifier, verify_webhook
from flask import Flask, request, jsonify

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure Plaid
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


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """
    Create a Link token for Plaid Link frontend integration.

    Expected JSON body:
    {
        "user_id": "user-123",  # Your internal user ID
        "client_name": "My App"  # Display name in Plaid Link
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        client_name = data.get('client_name', 'My App')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name=client_name,
            products=['auth', 'transactions'],
            country_codes=['US'],
            language='en',
        )

        response = client.link_token_create(request_data)
        logger.info(f'Link token created for user {user_id}')

        return jsonify({
            'link_token': response.link_token,
            'expiration': response.expiration
        })

    except Exception as e:
        logger.error(f'Error creating link token: {str(e)}')
        return jsonify({'error': f'Failed to create link token: {str(e)}'}), 400


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """
    Exchange public token for access token after user completes Plaid Link.

    Expected JSON body:
    {
        "public_token": "public-production-xxx"
    }
    """
    try:
        data = request.get_json()
        public_token = data.get('public_token')

        if not public_token:
            return jsonify({'error': 'public_token is required'}), 400

        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        response = client.item_public_token_exchange(exchange_request)

        logger.info(f'Token exchanged successfully for item {response.item_id}')

        return jsonify({
            'access_token': response.access_token,
            'item_id': response.item_id,
        })

    except Exception as e:
        logger.error(f'Error exchanging token: {str(e)}')
        return jsonify({'error': f'Failed to exchange token: {str(e)}'}), 400


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """
    Handle Plaid webhooks for transaction updates and other events.

    Verifies webhook signature and processes events.
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        # Verify webhook signature
        event = verify_webhook(
            payload,
            sig_header,
            os.environ.get('PLAID_SECRET')
        )

        logger.info(f'Webhook received: {event.get("webhook_type")}')

        # Handle different webhook types
        webhook_type = event.get('webhook_type')
        if webhook_type == 'TRANSACTIONS':
            handle_transactions_update(event)
        elif webhook_type == 'ITEM':
            handle_item_update(event)
        else:
            logger.warning(f'Unhandled webhook type: {webhook_type}')

        return '', 200

    except Exception as e:
        logger.error(f'Error processing webhook: {str(e)}')
        return '', 400


def handle_transactions_update(event):
    """
    Process TRANSACTIONS webhook event.
    Called when new transactions are available for an item.
    """
    item_id = event.get('item_id')
    webhook_code = event.get('webhook_code')
    logger.info(f'Transactions update for item {item_id}: {webhook_code}')

    # TODO: Implement your transaction sync logic here
    # You can fetch transactions using client.transactions_get()


def handle_item_update(event):
    """
    Process ITEM webhook event.
    Called when item status changes (e.g., auth expired).
    """
    item_id = event.get('item_id')
    webhook_code = event.get('webhook_code')
    logger.info(f'Item update for {item_id}: {webhook_code}')

    # TODO: Implement your item status handling here
    # E.g., notify user if authentication needs to be re-authenticated


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(port=5000, debug=True)
