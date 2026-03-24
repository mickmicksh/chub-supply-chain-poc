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
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.country_code import CountryCode
from plaid.model.products import Products

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _verify_webhook(payload: bytes, jwt_header: str) -> bool:
    """Verify a Plaid webhook using its signed JWT header.

    Plaid signs webhooks with a rotating key pair; for Sandbox testing you
    can skip verification by setting PLAID_SKIP_WEBHOOK_VERIFY=true.
    See: https://plaid.com/docs/api/webhooks/webhook-verification/
    """
    if os.environ.get("PLAID_SKIP_WEBHOOK_VERIFY", "").lower() == "true":
        return True

    # In production use plaid_client.webhook_verification_key_get() to fetch
    # the current public key and verify the JWT signature properly.
    # This placeholder raises to remind you to implement it before going live.
    raise NotImplementedError(
        "Implement JWT-based webhook verification before deploying to production. "
        "See https://plaid.com/docs/api/webhooks/webhook-verification/"
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Create a short-lived Link token to initialise Plaid Link on the client."""
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
        body = json.loads(exc.body) if exc.body else {}
        return jsonify({"error": body}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange a public token (from the client) for a permanent access token."""
    public_token = request.json.get("public_token") if request.is_json else None
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        req = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_client.item_public_token_exchange(req)
        # Store access_token and item_id securely in your database — never
        # return the access_token to the client.
        access_token = response["access_token"]
        item_id = response["item_id"]
        # TODO: persist (item_id, access_token) for this user
        return jsonify({"item_id": item_id})
    except ApiException as exc:
        body = json.loads(exc.body) if exc.body else {}
        return jsonify({"error": body}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive and dispatch Plaid webhook events."""
    payload = request.get_data()
    jwt_header = request.headers.get("Plaid-Verification", "")

    try:
        _verify_webhook(payload, jwt_header)
    except NotImplementedError as exc:
        app.logger.error("Webhook verification not implemented: %s", exc)
        return jsonify({"error": "webhook verification required"}), 500
    except Exception as exc:  # noqa: BLE001
        app.logger.warning("Invalid webhook signature: %s", exc)
        return "", 400

    event = request.get_json(force=True)
    webhook_type = event.get("webhook_type")
    webhook_code = event.get("webhook_code")

    app.logger.info("Plaid webhook: %s / %s", webhook_type, webhook_code)

    if webhook_type == "TRANSACTIONS":
        _handle_transactions(event)
    elif webhook_type == "ITEM":
        _handle_item(event)

    return "", 200


# ---------------------------------------------------------------------------
# Webhook handlers
# ---------------------------------------------------------------------------

def _handle_transactions(event: dict) -> None:
    """Handle TRANSACTIONS webhook events."""
    code = event.get("webhook_code")
    item_id = event.get("item_id")
    if code == "SYNC_UPDATES_AVAILABLE":
        app.logger.info("New transactions ready for item %s", item_id)
        # TODO: trigger a /transactions/sync call for this item_id


def _handle_item(event: dict) -> None:
    """Handle ITEM webhook events (errors, login required, etc.)."""
    code = event.get("webhook_code")
    item_id = event.get("item_id")
    if code == "ERROR":
        app.logger.error("Item error for %s: %s", item_id, event.get("error"))
    elif code == "PENDING_EXPIRATION":
        app.logger.warning("Item %s access will expire soon", item_id)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
