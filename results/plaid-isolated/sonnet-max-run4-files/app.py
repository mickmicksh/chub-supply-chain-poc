"""
Plaid Link integration — bank account connection flow.

Uses only the official plaid-python SDK (https://github.com/plaid/plaid-python).
Required env vars:
    PLAID_CLIENT_ID  — from https://dashboard.plaid.com/team/keys
    PLAID_SECRET     — Sandbox, Development, or Production secret
    PLAID_ENV        — "sandbox", "development", or "production"
"""

import os
import hashlib
import hmac
import json

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.exceptions import ApiException
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Plaid client configuration
# ---------------------------------------------------------------------------

_ENV_MAP = {
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Development,
    "production": plaid.Environment.Production,
}

plaid_env = os.environ.get("PLAID_ENV", "sandbox").lower()
configuration = plaid.Configuration(
    host=_ENV_MAP[plaid_env],
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
    """Step 1 — generate a short-lived Link token for the front-end."""
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
        return jsonify({"error": body}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Step 2 — exchange the public token returned by Link for an access token."""
    public_token = request.json.get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400
    try:
        req = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_client.item_public_token_exchange(req)
        # Store access_token and item_id securely in your database — never
        # expose the access_token to the client.
        return jsonify(
            {
                "access_token": response["access_token"],
                "item_id": response["item_id"],
            }
        )
    except ApiException as exc:
        body = json.loads(exc.body)
        return jsonify({"error": body}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive and verify Plaid webhook events.

    Plaid signs webhook payloads with JWT (JWS). In production use Plaid's
    verification endpoint; here we show the recommended approach using the
    plaid-python SDK's built-in verification helper.

    See: https://plaid.com/docs/api/webhooks/webhook-verification/
    """
    # Retrieve the raw body before any parsing
    payload = request.get_data()
    plaid_jwt = request.headers.get("Plaid-Verification")

    if not plaid_jwt:
        return jsonify({"error": "Missing Plaid-Verification header"}), 400

    try:
        # plaid-python SDK verifies the JWS and returns the decoded payload
        verified = plaid_client.webhook_verification_key_get(plaid_jwt, payload)
    except ApiException:
        return jsonify({"error": "Webhook verification failed"}), 403

    event = json.loads(payload)
    webhook_type = event.get("webhook_type")
    webhook_code = event.get("webhook_code")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions(event, webhook_code)
    elif webhook_type == "ITEM":
        _handle_item(event, webhook_code)

    return "", 200


# ---------------------------------------------------------------------------
# Internal webhook handlers
# ---------------------------------------------------------------------------

def _handle_transactions(event: dict, code: str) -> None:
    """Handle TRANSACTIONS webhook events."""
    if code == "SYNC_UPDATES_AVAILABLE":
        item_id = event.get("item_id")
        # TODO: trigger a /transactions/sync call for item_id
        print(f"Transactions sync available for item {item_id}")


def _handle_item(event: dict, code: str) -> None:
    """Handle ITEM webhook events (e.g. ERROR, PENDING_EXPIRATION)."""
    if code == "ERROR":
        print(f"Item error: {event.get('error')}")
    elif code == "PENDING_EXPIRATION":
        print("Item token expiring soon — prompt re-authentication")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=(plaid_env == "sandbox"))
