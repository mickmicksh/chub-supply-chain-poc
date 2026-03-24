"""Plaid Link integration - bank account connection flow."""

import os

import plaid
from plaid.api import plaid_api
from plaid.exceptions import ApiException
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import (
    LinkTokenCreateRequestUser,
)
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from flask import Flask, request, jsonify

# ---------------------------------------------------------------------------
# Plaid client configuration
# ---------------------------------------------------------------------------
PLAID_CLIENT_ID = os.environ.get("PLAID_CLIENT_ID", "")
PLAID_SECRET = os.environ.get("PLAID_SECRET", "")
PLAID_ENV = os.environ.get("PLAID_ENV", "sandbox")

PLAID_HOST = {
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Development,
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

# ---------------------------------------------------------------------------
# Flask application
# ---------------------------------------------------------------------------
app = Flask(__name__)


@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Create a Plaid Link token so the front-end can open Link."""
    try:
        body = request.get_json(silent=True) or {}
        user_id = body.get("user_id", "default-user")

        link_request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=user_id),
            client_name="My App",
            products=[Products("auth"), Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en",
        )
        response = client.link_token_create(link_request)
        return jsonify({"link_token": response.link_token})
    except ApiException as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange a public token from Link for a permanent access token."""
    try:
        public_token = request.json.get("public_token")
        if not public_token:
            return jsonify({"error": "public_token is required"}), 400

        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token,
        )
        response = client.item_public_token_exchange(exchange_request)
        return jsonify({
            "access_token": response.access_token,
            "item_id": response.item_id,
        })
    except ApiException as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive Plaid webhooks (transactions updates, etc.)."""
    # Plaid signs webhooks with a JWT in the Plaid-Verification header.
    # In production, verify the JWT using Plaid's /webhook_verification_key
    # endpoint via the official SDK before trusting the payload.
    event = request.get_json(silent=True) or {}
    webhook_type = event.get("webhook_type", "")
    webhook_code = event.get("webhook_code", "")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions_webhook(webhook_code, event)

    return "", 200


# ---------------------------------------------------------------------------
# Webhook handlers
# ---------------------------------------------------------------------------

def _handle_transactions_webhook(code: str, event: dict) -> None:
    """Process transaction-related webhook events."""
    if code == "SYNC_UPDATES_AVAILABLE":
        item_id = event.get("item_id")
        app.logger.info("Transactions update available for item %s", item_id)
        # TODO: call /transactions/sync to fetch new data
    elif code == "INITIAL_UPDATE":
        app.logger.info("Initial transaction pull complete")
    elif code == "HISTORICAL_UPDATE":
        app.logger.info("Historical transaction pull complete")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
