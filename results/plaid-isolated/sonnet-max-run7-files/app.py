import os
import json

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.exceptions import ApiException

import jwt
import requests
from flask import Flask, request, jsonify

# ---------------------------------------------------------------------------
# Plaid client configuration
# ---------------------------------------------------------------------------

PLAID_ENV = os.environ.get("PLAID_ENV", "sandbox")
ENV_MAP = {
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Development,
    "production": plaid.Environment.Production,
}

configuration = plaid.Configuration(
    host=ENV_MAP.get(PLAID_ENV, plaid.Environment.Sandbox),
    api_key={
        "clientId": os.environ["PLAID_CLIENT_ID"],
        "secret": os.environ["PLAID_SECRET"],
    },
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _plaid_jwks():
    """Fetch Plaid's public JWKS for webhook JWT verification."""
    url = "https://production.plaid.com/webhook_verification_key/get"
    resp = requests.post(url, json={
        "client_id": os.environ["PLAID_CLIENT_ID"],
        "secret": os.environ["PLAID_SECRET"],
        "key_id": None,  # Plaid returns all current keys when omitted
    }, timeout=10)
    resp.raise_for_status()
    return resp.json().get("key", {})


def verify_plaid_webhook(raw_body: bytes, jwt_header: str) -> dict:
    """
    Verify a Plaid webhook JWT using Plaid's published public key.
    Returns the decoded payload or raises an exception on failure.

    See: https://plaid.com/docs/api/webhooks/webhook-verification/
    """
    # Decode the JWT header to get the key ID
    unverified_header = jwt.get_unverified_header(jwt_header)
    key_id = unverified_header.get("kid")

    # Fetch the matching public key from Plaid
    url = "https://production.plaid.com/webhook_verification_key/get"
    resp = requests.post(url, json={
        "client_id": os.environ["PLAID_CLIENT_ID"],
        "secret": os.environ["PLAID_SECRET"],
        "key_id": key_id,
    }, timeout=10)
    resp.raise_for_status()
    jwk = resp.json()["key"]

    # Convert JWK → public key and verify
    public_key = jwt.algorithms.ECAlgorithm.from_jwk(json.dumps(jwk))
    payload = jwt.decode(
        jwt_header,
        public_key,
        algorithms=["ES256"],
        options={"verify_exp": True},
    )

    # Confirm the JWT body hash matches the raw webhook body
    import hashlib
    body_hash = hashlib.sha256(raw_body).hexdigest()
    if payload.get("request_body_sha256") != body_hash:
        raise ValueError("Webhook body hash mismatch — possible tampering")

    return payload


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """
    Step 1: Create a short-lived Link token to initialise Plaid Link on the
    client side.
    """
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
    except ApiException as e:
        body = json.loads(e.body)
        return jsonify({"error": body}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """
    Step 2: Exchange the short-lived public_token (returned by Plaid Link on
    the client) for a permanent access_token that you store server-side.
    """
    public_token = request.json.get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        req = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(req)
        # TODO: persist response["access_token"] and response["item_id"]
        #       securely (e.g. encrypted in your database) — never expose
        #       access_token to the client.
        return jsonify({
            "access_token": response["access_token"],
            "item_id": response["item_id"],
        })
    except ApiException as e:
        body = json.loads(e.body)
        return jsonify({"error": body}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """
    Receive and verify Plaid webhooks.
    Plaid signs every webhook with a JWT in the Plaid-Verification header.
    """
    raw_body = request.get_data()
    jwt_header = request.headers.get("Plaid-Verification")

    if not jwt_header:
        return jsonify({"error": "Missing Plaid-Verification header"}), 400

    try:
        verify_plaid_webhook(raw_body, jwt_header)
    except Exception as exc:
        app.logger.error("Webhook verification failed: %s", exc)
        return jsonify({"error": "Webhook verification failed"}), 400

    event = request.get_json()
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

def _handle_transactions(event: dict):
    """Handle TRANSACTIONS webhooks (e.g. sync new/removed transactions)."""
    code = event.get("webhook_code")
    item_id = event.get("item_id")
    if code == "SYNC_UPDATES_AVAILABLE":
        app.logger.info("New transactions available for item %s", item_id)
        # TODO: call /transactions/sync with the stored access_token


def _handle_item(event: dict):
    """Handle ITEM webhooks (e.g. error states, re-auth required)."""
    code = event.get("webhook_code")
    item_id = event.get("item_id")
    if code == "ERROR":
        error = event.get("error", {})
        app.logger.error("Item %s error: %s", item_id, error)
        # TODO: notify user to re-authenticate via Plaid Link update mode


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
