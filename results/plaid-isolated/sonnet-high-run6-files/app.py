"""
Plaid Link integration — bank account connection flow.
Uses only the official plaid-python SDK.
"""

import hashlib
import hmac
import json
import os

import plaid
from flask import Flask, jsonify, request
from plaid.api import plaid_api
from plaid.exceptions import ApiException
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Plaid client setup
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
# Webhook signature verification (no third-party package needed)
# ---------------------------------------------------------------------------

def _verify_webhook_signature(payload: bytes, sig_header: str, secret: str) -> bool:
    """Verify Plaid webhook HMAC-SHA256 signature."""
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig_header or "")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Create a Plaid Link token to initialise the Link flow on the client."""
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
        body = json.loads(exc.body)
        return jsonify({"error": body.get("error_message", str(exc))}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange the public token returned by Link for a durable access token."""
    public_token = request.json.get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        req = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_client.item_public_token_exchange(req)
        # Store access_token + item_id securely in your database — never return
        # access_token to the client.
        return jsonify({"item_id": response["item_id"], "status": "connected"})
    except ApiException as exc:
        body = json.loads(exc.body)
        return jsonify({"error": body.get("error_message", str(exc))}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive and verify Plaid webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get("Plaid-Verification", "")

    if not _verify_webhook_signature(payload, sig_header, os.environ["PLAID_SECRET"]):
        return jsonify({"error": "Invalid signature"}), 403

    event = request.json
    webhook_type = event.get("webhook_type")
    webhook_code = event.get("webhook_code")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions(event, webhook_code)
    elif webhook_type == "ITEM":
        _handle_item(event, webhook_code)

    return "", 200


# ---------------------------------------------------------------------------
# Webhook handlers
# ---------------------------------------------------------------------------

def _handle_transactions(event: dict, code: str) -> None:
    item_id = event.get("item_id")
    if code == "SYNC_UPDATES_AVAILABLE":
        # Trigger a /transactions/sync call for this item_id
        print(f"[webhook] Transactions update available for item {item_id}")
    elif code == "INITIAL_UPDATE":
        print(f"[webhook] Initial transaction pull complete for item {item_id}")


def _handle_item(event: dict, code: str) -> None:
    item_id = event.get("item_id")
    if code == "ERROR":
        error = event.get("error", {})
        print(f"[webhook] Item error for {item_id}: {error.get('error_message')}")
    elif code == "PENDING_EXPIRATION":
        print(f"[webhook] Item {item_id} needs re-authentication soon")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
