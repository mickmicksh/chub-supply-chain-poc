import os

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

PLAID_CLIENT_ID = os.environ.get("PLAID_CLIENT_ID", "")
PLAID_SECRET = os.environ.get("PLAID_SECRET", "")
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
        user_id = request.json.get("user_id", "default-user")
        link_request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=user_id),
            client_name="My App",
            products=[Products("auth"), Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en",
        )
        response = client.link_token_create(link_request)
        return jsonify({"link_token": response.link_token})
    except ApiException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange a public token from Link for a persistent access token."""
    try:
        public_token = request.json.get("public_token")
        if not public_token:
            return jsonify({"error": "public_token is required"}), 400

        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token,
        )
        response = client.item_public_token_exchange(exchange_request)
        # NOTE: In production, store access_token securely (e.g. encrypted DB).
        return jsonify({
            "access_token": response.access_token,
            "item_id": response.item_id,
        })
    except ApiException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Handle incoming Plaid webhooks."""
    payload = request.json
    webhook_type = payload.get("webhook_type", "")
    webhook_code = payload.get("webhook_code", "")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions_webhook(webhook_code, payload)
    elif webhook_type == "ITEM":
        _handle_item_webhook(webhook_code, payload)

    return "", 200


# ---------------------------------------------------------------------------
# Webhook handlers
# ---------------------------------------------------------------------------

def _handle_transactions_webhook(code: str, payload: dict) -> None:
    """Process transaction-related webhooks."""
    if code == "SYNC_UPDATES_AVAILABLE":
        item_id = payload.get("item_id")
        # TODO: call /transactions/sync for this item_id
        print(f"Transactions sync available for item {item_id}")


def _handle_item_webhook(code: str, payload: dict) -> None:
    """Process item-related webhooks (e.g. errors, pending expiration)."""
    if code == "ERROR":
        item_id = payload.get("item_id")
        error = payload.get("error", {})
        print(f"Item error for {item_id}: {error}")
    elif code == "PENDING_EXPIRATION":
        item_id = payload.get("item_id")
        print(f"Item {item_id} access is expiring soon - prompt user to re-link")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not PLAID_CLIENT_ID or not PLAID_SECRET:
        print("WARNING: PLAID_CLIENT_ID and PLAID_SECRET env vars are not set.")
        print("Get them from https://dashboard.plaid.com/developers/keys")
    app.run(port=5000, debug=True)
