"""
Plaid Link integration — bank account connection flow.

Endpoints:
  POST /api/create-link-token   — create a Link token to initialise Plaid Link on the client
  POST /api/exchange-token      — exchange the public_token returned by Link for an access_token
  POST /api/webhook             — receive and verify Plaid webhook events
"""

import hashlib
import hmac
import os

import plaid
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

# ---------------------------------------------------------------------------
# Plaid client configuration
# ---------------------------------------------------------------------------

_ENV_MAP = {
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Development,
    "production": plaid.Environment.Production,
}

PLAID_ENV = _ENV_MAP.get(os.environ.get("PLAID_ENV", "sandbox"), plaid.Environment.Sandbox)

configuration = plaid.Configuration(
    host=PLAID_ENV,
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


# ---------------------------------------------------------------------------
# Webhook verification helper (no third-party package needed)
# ---------------------------------------------------------------------------

def _verify_webhook_signature(payload: bytes, sig_header: str, secret: str) -> bool:
    """
    Verify a Plaid webhook using the JWT verification flow.

    Plaid sends a signed JWT in the ``Plaid-Verification`` header.
    For Sandbox testing you may skip verification; in production always verify.
    See: https://plaid.com/docs/api/webhooks/webhook-verification/
    """
    if not sig_header:
        return False
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    # In production replace this with Plaid's JWT verification flow.
    # This HMAC check is suitable for development / sandbox only.
    return hmac.compare_digest(expected, sig_header)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Return a short-lived Link token for the client to open Plaid Link."""
    try:
        req = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id="user-123"),
            client_name="My App",
            products=[Products("auth"), Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en",
        )
        response = plaid_client.link_token_create(req)
        return jsonify({"link_token": response["link_token"]})
    except ApiException as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange the public_token from Plaid Link for a permanent access_token."""
    public_token = request.json.get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        req = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_client.item_public_token_exchange(req)
        # Store access_token and item_id securely in your database.
        return jsonify({
            "access_token": response["access_token"],
            "item_id": response["item_id"],
        })
    except ApiException as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive Plaid webhook events (transactions updates, auth events, etc.)."""
    payload = request.get_data()
    sig_header = request.headers.get("Plaid-Verification", "")

    if not _verify_webhook_signature(payload, sig_header, os.environ["PLAID_SECRET"]):
        return jsonify({"error": "Invalid signature"}), 400

    event = request.get_json()
    webhook_type = event.get("webhook_type")
    webhook_code = event.get("webhook_code")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions(event, webhook_code)
    elif webhook_type == "AUTH":
        _handle_auth(event, webhook_code)
    # Add additional webhook_type handlers as needed.

    return "", 200


# ---------------------------------------------------------------------------
# Webhook handlers (stubs — add your business logic here)
# ---------------------------------------------------------------------------

def _handle_transactions(event: dict, code: str) -> None:
    item_id = event.get("item_id")
    if code == "SYNC_UPDATES_AVAILABLE":
        print(f"[webhook] New transactions available for item {item_id}")
    elif code == "INITIAL_UPDATE":
        print(f"[webhook] Initial transaction pull complete for item {item_id}")


def _handle_auth(event: dict, code: str) -> None:
    item_id = event.get("item_id")
    print(f"[webhook] AUTH event {code} for item {item_id}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
