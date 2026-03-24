import hashlib
import hmac
import json
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
from plaid.model.country_code import CountryCode
from plaid.model.products import Products

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Plaid client configuration
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
# Helper: webhook signature verification (official Plaid approach)
# ---------------------------------------------------------------------------
def _verify_webhook_signature(payload: bytes, sig_header: str | None) -> bool:
    """Verify the Plaid-Verification JWT header using HMAC-SHA256.

    Plaid signs webhook payloads with a JWT whose body contains a
    `request_body_sha256` claim. This helper validates that claim
    against the raw request body.

    See: https://plaid.com/docs/api/webhooks/webhook-verification/
    """
    if not sig_header:
        return False

    secret = os.environ.get("PLAID_WEBHOOK_SECRET", "")
    try:
        # The header is a compact JWT: <header>.<payload>.<signature>
        _header_b64, claims_b64, sig_b64 = sig_header.split(".")

        # Pad base64url to standard base64 length before decoding
        def _b64_decode(s: str) -> bytes:
            s += "=" * (-len(s) % 4)
            return __import__("base64").urlsafe_b64decode(s)

        claims = json.loads(_b64_decode(claims_b64))
        expected_body_hash = claims["request_body_sha256"]

        # Verify the body hash
        actual_body_hash = hashlib.sha256(payload).hexdigest()
        if not hmac.compare_digest(expected_body_hash, actual_body_hash):
            return False

        # Verify the JWT signature
        signing_input = f"{_header_b64}.{claims_b64}".encode()
        expected_sig = hmac.new(
            secret.encode(), signing_input, hashlib.sha256
        ).digest()
        return hmac.compare_digest(_b64_decode(sig_b64), expected_sig)

    except Exception:
        return False


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
        response = client.link_token_create(req)
        return jsonify({"link_token": response["link_token"]})
    except ApiException as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange a public token (from Plaid Link) for a durable access token."""
    public_token = request.json.get("public_token") if request.json else None
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        req = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(req)
        # NOTE: store access_token securely (e.g. encrypted in your DB).
        # Never expose it to the frontend.
        return jsonify({
            "access_token": response["access_token"],
            "item_id": response["item_id"],
        })
    except ApiException as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive and verify Plaid webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get("Plaid-Verification")

    if not _verify_webhook_signature(payload, sig_header):
        return jsonify({"error": "Invalid webhook signature"}), 400

    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400

    webhook_type = event.get("webhook_type")
    webhook_code = event.get("webhook_code")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions(event, webhook_code)
    elif webhook_type == "ITEM":
        _handle_item(event, webhook_code)
    # Add more webhook_type handlers as needed

    return "", 200


# ---------------------------------------------------------------------------
# Webhook handlers
# ---------------------------------------------------------------------------

def _handle_transactions(event: dict, code: str | None) -> None:
    item_id = event.get("item_id")
    if code == "SYNC_UPDATES_AVAILABLE":
        # Trigger a /transactions/sync call for this item_id
        print(f"[webhook] Transaction sync available for item {item_id}")
    elif code == "INITIAL_UPDATE":
        print(f"[webhook] Initial transaction pull complete for item {item_id}")


def _handle_item(event: dict, code: str | None) -> None:
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
    app.run(port=5000, debug=os.environ.get("FLASK_DEBUG", "0") == "1")
