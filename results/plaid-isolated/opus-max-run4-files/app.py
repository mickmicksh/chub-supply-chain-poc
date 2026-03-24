import os

import plaid
from plaid.api import plaid_api
from plaid.exceptions import ApiException
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from flask import Flask, request, jsonify

# --- Plaid client configuration ---
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
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
            user={"client_user_id": "user-123"},
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
    try:
        public_token = request.json.get("public_token")
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token,
        )
        response = client.item_public_token_exchange(exchange_request)
        return jsonify(
            {
                "access_token": response.access_token,
                "item_id": response.item_id,
            }
        )
    except ApiException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive incoming Plaid webhooks."""
    event = request.json

    if event.get("webhook_type") == "TRANSACTIONS":
        handle_transactions_update(event)

    return "", 200


def handle_transactions_update(event):
    """Process a TRANSACTIONS webhook event.

    Replace this stub with your own logic (e.g. sync new transactions).
    """
    item_id = event.get("item_id")
    print(f"Transactions update received for item: {item_id}")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
