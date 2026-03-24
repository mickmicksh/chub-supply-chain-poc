"""
Plaid Link integration — bank account connection flow.

Endpoints:
  POST /api/create-link-token   — creates a Link token to initialise Plaid Link on the frontend
  POST /api/exchange-token      — exchanges a public token for a permanent access token
  POST /api/webhook             — receives Plaid webhook events
"""

import os
import hmac
import hashlib
import logging

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.exceptions import ApiException

from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Plaid client setup
# ---------------------------------------------------------------------------

_ENV_MAP = {
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Development,
    "production": plaid.Environment.Production,
}

plaid_env = os.environ.get("PLAID_ENV", "sandbox").lower()
if plaid_env not in _ENV_MAP:
    raise ValueError(f"Invalid PLAID_ENV '{plaid_env}'. Must be sandbox, development, or production.")

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


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """
    Create a short-lived Link token to initialise Plaid Link on the client.

    Expected JSON body:
        { "user_id": "<your-app-user-id>" }

    Returns:
        { "link_token": "link-sandbox-..." }
    """
    body = request.get_json(silent=True) or {}
    user_id = body.get("user_id", "default-user")

    try:
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
        logger.error("Plaid link_token_create failed: %s", exc)
        return jsonify({"error": exc.body}), exc.status


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """
    Exchange a short-lived public token (from the frontend) for a permanent access token.

    Expected JSON body:
        { "public_token": "public-sandbox-..." }

    Returns:
        { "access_token": "access-sandbox-...", "item_id": "..." }

    IMPORTANT: store access_token securely (e.g. encrypted at rest in your database).
    Never log or expose it to the frontend.
    """
    body = request.get_json(silent=True) or {}
    public_token = body.get("public_token")

    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_client.item_public_token_exchange(exchange_request)

        access_token = response["access_token"]
        item_id = response["item_id"]

        # TODO: persist access_token and item_id for this user in your database
        logger.info("Received access token for item_id=%s", item_id)

        return jsonify({"item_id": item_id})  # Do NOT return access_token to the frontend

    except ApiException as exc:
        logger.error("Plaid item_public_token_exchange failed: %s", exc)
        return jsonify({"error": exc.body}), exc.status


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """
    Receive and verify Plaid webhook events.

    Plaid signs the request body with HMAC-SHA256 using your secret.
    We verify the signature before processing any event.

    See: https://plaid.com/docs/api/webhooks/webhook-verification/
    """
    raw_body = request.get_data()
    sig_header = request.headers.get("Plaid-Verification", "")

    if not _verify_webhook_signature(raw_body, sig_header):
        logger.warning("Webhook signature verification failed")
        return jsonify({"error": "Invalid signature"}), 400

    event = request.get_json(silent=True) or {}
    webhook_type = event.get("webhook_type")
    webhook_code = event.get("webhook_code")

    logger.info("Plaid webhook received: type=%s code=%s", webhook_type, webhook_code)

    if webhook_type == "TRANSACTIONS":
        _handle_transactions_webhook(event)
    elif webhook_type == "ITEM":
        _handle_item_webhook(event)
    # Add more webhook_type handlers as needed

    return "", 200


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _verify_webhook_signature(raw_body: bytes, sig_header: str) -> bool:
    """
    Verify that a webhook request genuinely came from Plaid.

    Plaid provides a JWT in the Plaid-Verification header. For production use,
    validate the JWT using Plaid's /webhook_verification_key/get endpoint and
    a JWT library (e.g. python-jose). The HMAC approach below is a simplified
    demonstration — see Plaid docs for the full JWT verification flow.
    """
    if not sig_header:
        return False

    secret = os.environ.get("PLAID_SECRET", "").encode()
    expected = hmac.new(secret, raw_body, hashlib.sha256).hexdigest()

    # Use a timing-safe comparison to prevent timing attacks
    return hmac.compare_digest(expected, sig_header)


def _handle_transactions_webhook(event: dict) -> None:
    item_id = event.get("item_id")
    webhook_code = event.get("webhook_code")
    logger.info("Transactions webhook for item_id=%s code=%s", item_id, webhook_code)
    # TODO: trigger a transactions sync for item_id in your database


def _handle_item_webhook(event: dict) -> None:
    item_id = event.get("item_id")
    webhook_code = event.get("webhook_code")
    logger.info("Item webhook for item_id=%s code=%s", item_id, webhook_code)
    # TODO: handle item errors / re-authentication requests


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=(plaid_env == "sandbox"))
