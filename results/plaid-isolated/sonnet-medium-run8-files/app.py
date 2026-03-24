"""
Plaid Link integration — bank account connection flow.

Environment variables required (see .env.example):
  PLAID_CLIENT_ID   — from https://dashboard.plaid.com
  PLAID_SECRET      — sandbox / development / production secret
  PLAID_ENV         — sandbox | development | production
  PLAID_WEBHOOK_URL — (optional) your webhook endpoint for Plaid to call
"""

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
plaid_client = plaid_api.PlaidApi(api_client)

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

app = Flask(__name__)


# --- 1. Create a Link token (called by your frontend to initialise Plaid Link) ---

@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Return a short-lived link_token so the browser can open Plaid Link."""
    try:
        body = request.get_json(silent=True) or {}
        user_id = str(body.get("user_id", "user-default"))

        req = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=user_id),
            client_name="My App",
            products=[Products("auth"), Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en",
            # Uncomment to receive async item updates:
            # webhook=os.environ.get("PLAID_WEBHOOK_URL"),
        )
        response = plaid_client.link_token_create(req)
        return jsonify({"link_token": response["link_token"]})

    except ApiException as exc:
        error_body = json.loads(exc.body)
        return jsonify({"error": error_body}), exc.status


# --- 2. Exchange the public token (called after the user completes Link) ---

@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange the one-time public_token for a permanent access_token."""
    body = request.get_json(silent=True) or {}
    public_token = body.get("public_token")

    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        req = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_client.item_public_token_exchange(req)

        # TODO: persist access_token + item_id securely in your database
        return jsonify({
            "access_token": response["access_token"],
            "item_id": response["item_id"],
        })

    except ApiException as exc:
        error_body = json.loads(exc.body)
        return jsonify({"error": error_body}), exc.status


# --- 3. Webhook handler (Plaid pushes async events here) ---

@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive and verify Plaid webhook events."""
    raw_body = request.get_data()
    sig_header = request.headers.get("Plaid-Verification", "")

    # Verify the HMAC-SHA256 signature so we only accept Plaid's requests.
    expected_sig = hmac.new(
        os.environ["PLAID_SECRET"].encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_sig, sig_header):
        return jsonify({"error": "invalid signature"}), 400

    event = request.get_json(force=True)
    webhook_type = event.get("webhook_type")
    webhook_code = event.get("webhook_code")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions(event, webhook_code)
    elif webhook_type == "ITEM":
        _handle_item(event, webhook_code)

    return "", 200


# ---------------------------------------------------------------------------
# Webhook helpers
# ---------------------------------------------------------------------------

def _handle_transactions(event: dict, code: str) -> None:
    item_id = event.get("item_id")
    if code == "SYNC_UPDATES_AVAILABLE":
        # Use /transactions/sync to pull new/modified/removed transactions.
        print(f"[webhook] New transactions available for item {item_id}")
    else:
        print(f"[webhook] TRANSACTIONS/{code} — item {item_id}")


def _handle_item(event: dict, code: str) -> None:
    item_id = event.get("item_id")
    if code == "ERROR":
        print(f"[webhook] Item error for {item_id}: {event.get('error')}")
    else:
        print(f"[webhook] ITEM/{code} — item {item_id}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
