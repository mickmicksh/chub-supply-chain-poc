"""
Plaid Link integration — bank account connection flow.

Endpoints:
  POST /api/create-link-token   — create a Link token to initialise Plaid Link
  POST /api/exchange-token      — exchange a public token for a permanent access token
  POST /api/webhook             — receive and verify Plaid webhook events
"""

import os

import plaid
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from plaid.api import plaid_api
from plaid.exceptions import ApiException
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

load_dotenv()

# ---------------------------------------------------------------------------
# Plaid client
# ---------------------------------------------------------------------------

_ENV_MAP = {
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Development,
    "production": plaid.Environment.Production,
}

configuration = plaid.Configuration(
    host=_ENV_MAP.get(os.environ.get("PLAID_ENV", "sandbox"), plaid.Environment.Sandbox),
    api_key={
        "clientId": os.environ["PLAID_CLIENT_ID"],
        "secret": os.environ["PLAID_SECRET"],
    },
)

api_client = plaid.ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

app = Flask(__name__)


@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Return a short-lived Link token to initialise Plaid Link on the client."""
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
        response = plaid_client.link_token_create(link_request)
        return jsonify({"link_token": response["link_token"]})

    except ApiException as exc:
        return jsonify({"error": exc.body}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange the one-time public token returned by Plaid Link for a permanent
    access token and item ID to be stored server-side."""
    body = request.get_json(silent=True) or {}
    public_token = body.get("public_token")

    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_client.item_public_token_exchange(exchange_request)

        # TODO: persist access_token and item_id securely (e.g. encrypted DB column)
        return jsonify(
            {
                "access_token": response["access_token"],
                "item_id": response["item_id"],
            }
        )

    except ApiException as exc:
        return jsonify({"error": exc.body}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive Plaid webhook events.

    Plaid signs webhook payloads with a JWT in the `Plaid-Verification` header.
    Verify it using Plaid's /webhook_verification_key/get endpoint before
    processing the event (see Plaid docs for full JWT verification flow).
    """
    sig_header = request.headers.get("Plaid-Verification")
    if not sig_header:
        return jsonify({"error": "Missing Plaid-Verification header"}), 400

    # NOTE: For production, verify the JWT signature against Plaid's public key.
    # See: https://plaid.com/docs/api/webhooks/webhook-verification/
    event = request.get_json(silent=True) or {}
    webhook_type = event.get("webhook_type")
    webhook_code = event.get("webhook_code")

    app.logger.info("Plaid webhook received: %s / %s", webhook_type, webhook_code)

    if webhook_type == "TRANSACTIONS":
        _handle_transactions_webhook(event)

    return "", 200


# ---------------------------------------------------------------------------
# Webhook handlers
# ---------------------------------------------------------------------------


def _handle_transactions_webhook(event: dict) -> None:
    """Handle TRANSACTIONS webhook events (stub — add your business logic)."""
    webhook_code = event.get("webhook_code")
    item_id = event.get("item_id")
    app.logger.info("Transactions update for item %s: %s", item_id, webhook_code)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
