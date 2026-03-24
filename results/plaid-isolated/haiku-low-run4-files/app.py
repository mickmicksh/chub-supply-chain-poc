"""Flask app for Plaid Link integration."""

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_link_verify import LinkVerifier, verify_webhook
from flask import Flask, request, jsonify, render_template
from plaid.exceptions import ApiException

from config import get_config

app = Flask(__name__)
config = get_config()

# Configure Plaid
plaid_configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox if config.PLAID_ENV == 'sandbox' else plaid.Environment.Production,
    api_key={
        'clientId': config.PLAID_CLIENT_ID,
        'secret': config.PLAID_SECRET,
    }
)

api_client = plaid.ApiClient(plaid_configuration)
plaid_client = plaid_api.PlaidApi(api_client)
verifier = LinkVerifier(config.PLAID_SECRET)


@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect
def create_link_token():
    """Create a Link token for initiating the Plaid Link flow."""
    try:
        user_id = request.json.get('user_id', 'user-123')

        request_data = LinkTokenCreateRequest(
            user={'client_user_id': user_id},
            client_name='My App',
            products=['auth', 'transactions'],
            country_codes=['US'],
            language='en',
        )

        response = plaid_client.link_token_create(request_data)
        return jsonify({'link_token': response.link_token})

    except ApiException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/exchange-token', methods=['POST'])
@verifier.protect
def exchange_token():
    """Exchange public token for access token."""
    try:
        public_token = request.json.get('public_token')

        if not public_token:
            return jsonify({'error': 'public_token is required'}), 400

        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_client.item_public_token_exchange(exchange_request)

        return jsonify({
            'access_token': response.access_token,
            'item_id': response.item_id,
        })

    except ApiException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    """Handle Plaid webhooks."""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Plaid-Verification')

        event = verify_webhook(payload, sig_header, config.PLAID_SECRET)

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
    """Handle transaction update webhook."""
    app.logger.info(f'Transactions update: {event}')
    # Add your logic to handle transaction updates


def handle_item_update(event):
    """Handle item update webhook."""
    app.logger.info(f'Item update: {event}')
    # Add your logic to handle item updates


@app.route('/', methods=['GET'])
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    if not config.PLAID_CLIENT_ID or not config.PLAID_SECRET:
        raise ValueError('PLAID_CLIENT_ID and PLAID_SECRET must be set in .env')

    app.run(debug=config.FLASK_ENV == 'development', port=5000)
