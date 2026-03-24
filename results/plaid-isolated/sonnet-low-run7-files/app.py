"""
Plaid Link integration — bank account connection flow.

Endpoints:
  POST /api/create-link-token  — generate a Link token for the frontend
  POST /api/exchange-token     — exchange a public token for an access token
  POST /api/webhook            — receive and verify Plaid webhook events
"""

import os
import json
import time

import jwt
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.exceptions import ApiException

load_dotenv()

# ---------------------------------------------------------------------------
# Plaid client configuration
# ---------------------------------------------------------------------------

PLAID_ENV = os.environ.get("PLAID_ENV", "sandbox").lower()
PLAID_ENVIRONMENTS = {
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Development,
    "production": plaid.Environment.Production,
}

configuration = plaid.Configuration(
    host=PLAID_ENVIRONMENTS.get(PLAID_ENV, plaid.Environment.Sandbox),
    api_key={
        "clientId": os.environ["PLAID_CLIENT_ID"],
        "secret": os.environ["PLAID_SECRET"],
    },
)

api_client = plaid.ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)

# ---------------------------------------------------------------------------
# Webhook verification (official Plaid JWT approach)
# https://plaid.com/docs/api/webhooks/webhook-verification/
# ---------------------------------------------------------------------------

PLAID_JWKS_URL = "https://production.plaid.com/webhook_verification_key/get"
_jwks_cache: dict = {}  # key_id -> public key, with TTL


def _get_plaid_public_key(key_id: str) -> dict:
    """Fetch and cache Plaid's public key for webhook JWT verification."""
    cached = _jwks_cache.get(key_id)
    if cached and cached["expires_at"] > time.time():
        return cached["key"]

    response = requests.post(
        PLAID_JWKS_URL,
        json={
            "client_id": os.environ["PLAID_CLIENT_ID"],
            "secret": os.environ["PLAID_SECRET"],
            "key_id": key_id,
        },
        timeout=10,
    )
    response.raise_for_status()
    key_data = response.json()["key"]

    _jwks_cache[key_id] = {"key": key_data, "expires_at": time.time() + 3600}
    return key_data


def verify_plaid_webhook(token: str) -> dict:
    """
    Verify a Plaid webhook JWT and return the decoded payload.
    Raises jwt.InvalidTokenError on failure.
    """
    header = jwt.get_unverified_header(token)
    key_id = header.get("kid")
    if not key_id:
        raise ValueError("Webhook JWT missing 'kid' header")

    key_data = _get_plaid_public_key(key_id)
    public_key = jwt.algorithms.ECAlgorithm.from_jwk(json.dumps(key_data))

    return jwt.decode(
        token,
        public_key,
        algorithms=["ES256"],
        options={"require": ["iat", "request_body_sha256"]},
    )


# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

app = Flask(__name__)


@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Return a short-lived Link token for initialising Plaid Link on the client."""
    try:
        body = request.get_json(silent=True) or {}
        user_id = body.get("user_id", "user-default")

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
        return jsonify({"error": exc.body}), exc.status


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange a public token (from Plaid Link) for a durable access token."""
    try:
        body = request.get_json(silent=True) or {}
        public_token = body.get("public_token")
        if not public_token:
            return jsonify({"error": "public_token is required"}), 400

        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_client.item_public_token_exchange(exchange_request)

        # TODO: persist access_token + item_id securely in your database
        return jsonify({
            "access_token": response["access_token"],
            "item_id": response["item_id"],
        })

    except ApiException as exc:
        return jsonify({"error": exc.body}), exc.status


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive Plaid webhook events with JWT signature verification."""
    token = request.headers.get("Plaid-Verification")
    if not token:
        return jsonify({"error": "Missing Plaid-Verification header"}), 400

    try:
        verify_plaid_webhook(token)
    except (jwt.InvalidTokenError, ValueError) as exc:
        return jsonify({"error": f"Invalid webhook signature: {exc}"}), 401

    event = request.get_json(silent=True) or {}
    webhook_type = event.get("webhook_type")
    webhook_code = event.get("webhook_code")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions(event, webhook_code)
    elif webhook_type == "AUTH":
        _handle_auth(event, webhook_code)
    # Add more webhook_type handlers as needed

    return "", 200


# ---------------------------------------------------------------------------
# Webhook handlers (stubs — fill in your business logic)
# ---------------------------------------------------------------------------

def _handle_transactions(event: dict, code: str) -> None:
    item_id = event.get("item_id")
    if code == "SYNC_UPDATES_AVAILABLE":
        print(f"[webhook] New transactions available for item {item_id}")
        # TODO: call /transactions/sync with the stored access_token for this item
    elif code == "INITIAL_UPDATE":
        print(f"[webhook] Initial transaction pull complete for item {item_id}")


def _handle_auth(event: dict, code: str) -> None:
    item_id = event.get("item_id")
    print(f"[webhook] AUTH event '{code}' for item {item_id}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
