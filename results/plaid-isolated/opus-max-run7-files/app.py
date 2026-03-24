"""Plaid Link integration - bank account connection flow."""

import os

import plaid
from plaid.api import plaid_api
from plaid.exceptions import ApiException
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from flask import Flask, request, jsonify

# ---------------------------------------------------------------------------
# Plaid client setup
# ---------------------------------------------------------------------------

PLAID_ENV = os.environ.get("PLAID_ENV", "sandbox")

PLAID_HOSTS = {
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Development,
    "production": plaid.Environment.Production,
}

configuration = plaid.Configuration(
    host=PLAID_HOSTS.get(PLAID_ENV, plaid.Environment.Sandbox),
    api_key={
        "clientId": os.environ["PLAID_CLIENT_ID"],
        "secret": os.environ["PLAID_SECRET"],
    },
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

app = Flask(__name__)


@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Create a Link token so the frontend can open Plaid Link."""
    try:
        user_id = request.json.get("user_id", "user-default")
        link_request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=user_id),
            client_name="My App",
            products=[Products("auth"), Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en",
        )
        response = client.link_token_create(link_request)
        return jsonify({"link_token": response.link_token})
    except ApiException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange a public token from Link for a persistent access token."""
    try:
        public_token = request.json.get("public_token")
        if not public_token:
            return jsonify({"error": "public_token is required"}), 400

        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token,
        )
        response = client.item_public_token_exchange(exchange_request)
        # In production, store access_token + item_id securely in your DB.
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
    """Handle Plaid webhooks (transactions updates, etc.)."""
    # In production, verify the webhook signature using Plaid's
    # /webhook_verification_key/get endpoint. See:
    # https://plaid.com/docs/api/webhooks/webhook-verification/
    event = request.json
    webhook_type = event.get("webhook_type")
    webhook_code = event.get("webhook_code")

    if webhook_type == "TRANSACTIONS":
        # Handle transaction updates
        print(f"Transactions webhook: {webhook_code}")

    return "", 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)
