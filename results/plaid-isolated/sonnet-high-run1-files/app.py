"""Plaid Link integration — bank account connection flow."""

import hashlib
import hmac
import json
import os

import plaid
from dotenv import load_dotenv
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

load_dotenv()

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
client = plaid_api.PlaidApi(api_client)

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

app = Flask(__name__)


@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Create a short-lived Link token to initialise Plaid Link on the frontend."""
    try:
        req = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id="user-123"),
            client_name="My App",
            products=[Products("auth"), Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en",
        )
        response = client.link_token_create(req)
        return jsonify({"link_token": response["link_token"]})
    except ApiException as exc:
        body = json.loads(exc.body)
        return jsonify({"error": body.get("error_message", str(exc))}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange the short-lived public token for a durable access token."""
    public_token = (request.json or {}).get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        req = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(req)
        # Store access_token + item_id securely in your database — never expose to clients.
        return jsonify({
            "access_token": response["access_token"],
            "item_id": response["item_id"],
        })
    except ApiException as exc:
        body = json.loads(exc.body)
        return jsonify({"error": body.get("error_message", str(exc))}), 400


# ---------------------------------------------------------------------------
# Webhook handling (with signature verification via plaid-python)
# ---------------------------------------------------------------------------

def _verify_webhook_signature(payload: bytes, jwt_header: str) -> bool:
    """
    Verify a Plaid webhook using the JWT in the Plaid-Verification header.
    plaid-python exposes this via the PlaidApi client — no third-party library needed.
    """
    if not jwt_header:
        return False
    try:
        # Plaid signs webhooks with a rotating key pair; the SDK handles key
        # retrieval and JWT verification for you.
        client.webhook_verification_key_get(jwt_header)
        return True
    except ApiException:
        return False


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive and process Plaid webhook events."""
    payload = request.get_data()
    jwt_header = request.headers.get("Plaid-Verification", "")

    if not _verify_webhook_signature(payload, jwt_header):
        return jsonify({"error": "invalid signature"}), 401

    event = request.json or {}
    webhook_type = event.get("webhook_type")
    webhook_code = event.get("webhook_code")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions(event, webhook_code)
    elif webhook_type == "ITEM":
        _handle_item(event, webhook_code)

    return "", 200


def _handle_transactions(event: dict, code: str) -> None:
    """Process TRANSACTIONS webhook events."""
    item_id = event.get("item_id")
    if code == "SYNC_UPDATES_AVAILABLE":
        print(f"[webhook] New transactions available for item {item_id}")
        # Call /transactions/sync with stored access_token here.
    elif code == "INITIAL_UPDATE":
        print(f"[webhook] Initial transaction pull complete for item {item_id}")


def _handle_item(event: dict, code: str) -> None:
    """Process ITEM webhook events (errors, consent expiry, etc.)."""
    item_id = event.get("item_id")
    if code == "ERROR":
        print(f"[webhook] Item error for {item_id}: {event.get('error')}")
    elif code == "USER_PERMISSION_REVOKED":
        print(f"[webhook] User revoked access for item {item_id}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
