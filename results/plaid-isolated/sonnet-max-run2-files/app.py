import os
import json
import hashlib
import hmac

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.exceptions import ApiException
from flask import Flask, request, jsonify

# ---------------------------------------------------------------------------
# Plaid client configuration
# ---------------------------------------------------------------------------

PLAID_CLIENT_ID = os.environ["PLAID_CLIENT_ID"]
PLAID_SECRET = os.environ["PLAID_SECRET"]
PLAID_ENV = os.environ.get("PLAID_ENV", "sandbox")

_ENV_MAP = {
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Development,
    "production": plaid.Environment.Production,
}

configuration = plaid.Configuration(
    host=_ENV_MAP[PLAID_ENV],
    api_key={
        "clientId": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
    },
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _verify_webhook(payload: bytes, jwt_header: str) -> bool:
    """Verify Plaid webhook authenticity using HMAC-SHA256.

    In production, use Plaid's JWT-based webhook verification as documented at
    https://plaid.com/docs/api/webhooks/webhook-verification/
    This helper is a simplified stand-in for non-production environments.
    """
    expected = hmac.new(
        PLAID_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, jwt_header or "")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Create a Link token to initialise Plaid Link on the client."""
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
        body = json.loads(exc.body) if exc.body else {}
        return jsonify({"error": body.get("error_message", str(exc))}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange a public token (from Link) for a permanent access token."""
    public_token = request.json.get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        req = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(req)
        return jsonify({
            "access_token": response["access_token"],
            "item_id": response["item_id"],
        })
    except ApiException as exc:
        body = json.loads(exc.body) if exc.body else {}
        return jsonify({"error": body.get("error_message", str(exc))}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive and process Plaid webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get("Plaid-Verification", "")

    if not _verify_webhook(payload, sig_header):
        return jsonify({"error": "invalid signature"}), 401

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
        # Fetch new/modified/removed transactions via /transactions/sync
        print(f"[webhook] transactions sync available for item {item_id}")
    elif code == "INITIAL_UPDATE":
        print(f"[webhook] initial transactions ready for item {item_id}")


def _handle_item(event: dict, code: str) -> None:
    item_id = event.get("item_id")
    if code == "ERROR":
        print(f"[webhook] item error for {item_id}: {event.get('error')}")
    elif code == "PENDING_EXPIRATION":
        print(f"[webhook] item {item_id} access will expire soon — prompt re-auth")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
