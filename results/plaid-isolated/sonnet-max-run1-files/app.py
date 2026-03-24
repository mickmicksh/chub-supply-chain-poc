"""
Plaid Link integration — bank account connection flow.
Uses only the official plaid-python SDK (no third-party wrappers needed).
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
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

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
    host=_ENV_MAP.get(os.environ["PLAID_ENV"], plaid.Environment.Sandbox),
    api_key={
        "clientId": os.environ["PLAID_CLIENT_ID"],
        "secret": os.environ["PLAID_SECRET"],
    },
)

api_client = plaid.ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)

app = Flask(__name__)


# ---------------------------------------------------------------------------
# 1. Create Link token  (called by your frontend to initialise Plaid Link UI)
# ---------------------------------------------------------------------------

@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Return a short-lived link_token for the Plaid Link UI."""
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


# ---------------------------------------------------------------------------
# 2. Exchange public token  (called after the user completes Plaid Link)
# ---------------------------------------------------------------------------

@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange the one-time public_token for a permanent access_token."""
    public_token = request.get_json(force=True).get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        req = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_client.item_public_token_exchange(req)
        # Store access_token & item_id securely in your database — never expose
        # the access_token to the client.
        access_token = response["access_token"]
        item_id = response["item_id"]

        # TODO: persist (access_token, item_id) for this user in your DB
        print(f"[exchange] item_id={item_id}")  # replace with real storage

        return jsonify({"item_id": item_id})
    except ApiException as exc:
        body = json.loads(exc.body)
        return jsonify({"error": body}), 400


# ---------------------------------------------------------------------------
# 3. Webhook handler  (Plaid pushes events here — verify the signature first)
# ---------------------------------------------------------------------------

def _verify_plaid_webhook(payload: bytes, jwt_header: str) -> bool:
    """
    Lightweight verification: confirm the request contains the expected HMAC.
    For full JWT verification use plaid_client.webhook_verification_key_get()
    as shown in Plaid's official webhook verification docs.
    """
    secret = os.environ["PLAID_SECRET"].encode()
    expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    # jwt_header carries a signed JWT; for sandbox/dev a simple HMAC check is
    # sufficient.  In production, verify the full JWT with Plaid's public key.
    return hmac.compare_digest(expected, jwt_header or "")


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive and process Plaid webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get("Plaid-Verification", "")

    # NOTE: For production, follow Plaid's JWT webhook verification guide:
    # https://plaid.com/docs/api/webhooks/webhook-verification/
    # The HMAC check below is suitable for sandbox testing only.
    if not _verify_plaid_webhook(payload, sig_header):
        return jsonify({"error": "invalid signature"}), 400

    event = request.get_json(force=True)
    webhook_type = event.get("webhook_type")
    webhook_code = event.get("webhook_code")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions(event, webhook_code)
    elif webhook_type == "ITEM":
        _handle_item(event, webhook_code)

    return "", 200


def _handle_transactions(event: dict, code: str) -> None:
    item_id = event.get("item_id")
    print(f"[webhook] TRANSACTIONS/{code} — item_id={item_id}")
    # TODO: sync transactions for this item


def _handle_item(event: dict, code: str) -> None:
    item_id = event.get("item_id")
    print(f"[webhook] ITEM/{code} — item_id={item_id}")
    # TODO: handle item errors / re-auth flows


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
