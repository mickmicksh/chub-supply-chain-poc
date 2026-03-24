"""Plaid Link integration for bank account connections."""

import os

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.webhook_verification_key_get_request import (
    WebhookVerificationKeyGetRequest,
)
from plaid.exceptions import ApiException
from flask import Flask, request, jsonify

# --- Plaid client setup ---

PLAID_CLIENT_ID = os.environ.get("PLAID_CLIENT_ID", "")
PLAID_SECRET = os.environ.get("PLAID_SECRET", "")
PLAID_ENV = os.environ.get("PLAID_ENV", "sandbox")

PLAID_HOST = {
    "sandbox": plaid.Environment.Sandbox,
    "production": plaid.Environment.Production,
}.get(PLAID_ENV, plaid.Environment.Sandbox)

configuration = plaid.Configuration(
    host=PLAID_HOST,
    api_key={
        "clientId": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
    },
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# --- Flask app ---

app = Flask(__name__)


@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Create a Link token for initializing Plaid Link on the client."""
    try:
        user_id = request.json.get("user_id", "default-user")
        req = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=user_id),
            client_name="My App",
            products=[Products("auth"), Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en",
        )
        response = client.link_token_create(req)
        return jsonify({"link_token": response.link_token})
    except ApiException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange a public token from Link for a permanent access token."""
    try:
        public_token = request.json.get("public_token")
        if not public_token:
            return jsonify({"error": "public_token is required"}), 400

        exchange_req = ItemPublicTokenExchangeRequest(
            public_token=public_token,
        )
        response = client.item_public_token_exchange(exchange_req)
        return jsonify({
            "access_token": response.access_token,
            "item_id": response.item_id,
        })
    except ApiException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Handle incoming Plaid webhooks.

    In production, verify the webhook signature using Plaid's
    /webhook_verification_key/get endpoint and JWT validation.
    See: https://plaid.com/docs/api/webhooks/webhook-verification/
    """
    event = request.json
    webhook_type = event.get("webhook_type", "")
    webhook_code = event.get("webhook_code", "")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions_webhook(webhook_code, event)
    elif webhook_type == "ITEM":
        _handle_item_webhook(webhook_code, event)

    return "", 200


def _handle_transactions_webhook(code: str, event: dict) -> None:
    """Process transaction-related webhook events."""
    item_id = event.get("item_id", "")
    if code == "SYNC_UPDATES_AVAILABLE":
        print(f"Transactions sync available for item: {item_id}")
    elif code == "INITIAL_UPDATE":
        print(f"Initial transaction pull complete for item: {item_id}")
    elif code == "HISTORICAL_UPDATE":
        print(f"Historical transactions ready for item: {item_id}")


def _handle_item_webhook(code: str, event: dict) -> None:
    """Process item-related webhook events."""
    item_id = event.get("item_id", "")
    if code == "ERROR":
        print(f"Item error for {item_id}: {event.get('error', {})}")
    elif code == "PENDING_EXPIRATION":
        print(f"Access token expiring soon for item: {item_id}")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
