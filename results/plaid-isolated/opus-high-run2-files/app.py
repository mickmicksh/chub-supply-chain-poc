"""Plaid Link integration - bank account connection flow."""

import hashlib
import hmac
import os
import time

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.exceptions import ApiException
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Plaid client setup
# ---------------------------------------------------------------------------

PLAID_CLIENT_ID = os.environ.get("PLAID_CLIENT_ID")
PLAID_SECRET = os.environ.get("PLAID_SECRET")
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

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

app = Flask(__name__)


@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Create a Link token so the client can open Plaid Link."""
    try:
        user_id = request.json.get("user_id", "user-default") if request.json else "user-default"
        req = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=user_id),
            client_name="My App",
            products=[Products("auth"), Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en",
        )
        response = client.link_token_create(req)
        return jsonify({"link_token": response.link_token})
    except ApiException as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange a public token from Link for a persistent access token."""
    if not request.json or not request.json.get("public_token"):
        return jsonify({"error": "public_token is required"}), 400

    public_token = request.json["public_token"]

    try:
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
    except ApiException as exc:
        return jsonify({"error": str(exc)}), 400


def _verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify a Plaid webhook signature using HMAC-SHA256."""
    expected = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive and verify Plaid webhooks."""
    payload = request.get_data()
    sig_header = request.headers.get("Plaid-Verification", "")

    if not _verify_webhook_signature(payload, sig_header, PLAID_SECRET):
        return jsonify({"error": "Invalid webhook signature"}), 401

    event = request.get_json()

    if event.get("webhook_type") == "TRANSACTIONS":
        _handle_transactions_update(event)

    return "", 200


# ---------------------------------------------------------------------------
# Webhook handlers
# ---------------------------------------------------------------------------


def _handle_transactions_update(event: dict) -> None:
    """Process a TRANSACTIONS webhook event.

    TODO: Replace with your own business logic (e.g. sync to database).
    """
    item_id = event.get("item_id")
    webhook_code = event.get("webhook_code")
    print(f"Transactions update for item {item_id}: {webhook_code}")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
