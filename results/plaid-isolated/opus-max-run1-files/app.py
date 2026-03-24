import os

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.exceptions import ApiException
from flask import Flask, request, jsonify

# --- Plaid client setup ---

PLAID_ENVS = {
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Development,
    "production": plaid.Environment.Production,
}

configuration = plaid.Configuration(
    host=PLAID_ENVS.get(os.environ.get("PLAID_ENV", "sandbox"), plaid.Environment.Sandbox),
    api_key={
        "clientId": os.environ.get("PLAID_CLIENT_ID"),
        "secret": os.environ.get("PLAID_SECRET"),
    },
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# --- Flask app ---

app = Flask(__name__)


@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Create a Link token so the client can open Plaid Link."""
    try:
        request_data = LinkTokenCreateRequest(
            user={"client_user_id": request.json.get("user_id", "user-default")},
            client_name="My App",
            products=["auth", "transactions"],
            country_codes=["US"],
            language="en",
        )
        response = client.link_token_create(request_data)
        return jsonify({"link_token": response.link_token})
    except ApiException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange a public token from Link for a persistent access token."""
    public_token = request.json.get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_request)
        # IMPORTANT: In production, store access_token securely — never return
        # it directly to the client.
        return jsonify({
            "access_token": response.access_token,
            "item_id": response.item_id,
        })
    except ApiException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Handle incoming Plaid webhooks (transactions, item updates, etc.)."""
    event = request.json
    webhook_type = event.get("webhook_type")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions_update(event)
    elif webhook_type == "ITEM":
        _handle_item_update(event)

    return "", 200


# --- Webhook handlers ---

def _handle_transactions_update(event: dict) -> None:
    webhook_code = event.get("webhook_code")
    item_id = event.get("item_id")
    app.logger.info("Transactions webhook: code=%s item=%s", webhook_code, item_id)
    # TODO: Fetch new transactions with client.transactions_get(...)


def _handle_item_update(event: dict) -> None:
    webhook_code = event.get("webhook_code")
    item_id = event.get("item_id")
    app.logger.info("Item webhook: code=%s item=%s", webhook_code, item_id)
    # TODO: Handle LOGIN_REPAIRED, PENDING_EXPIRATION, etc.


if __name__ == "__main__":
    app.run(port=5000, debug=True)
