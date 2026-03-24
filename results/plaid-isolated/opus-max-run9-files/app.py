"""Plaid Link integration - bank account connection flow."""

import os

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import (
    LinkTokenCreateRequestUser,
)
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.exceptions import ApiException
from flask import Flask, request, jsonify

# ---------------------------------------------------------------------------
# Plaid client setup
# ---------------------------------------------------------------------------

PLAID_ENV_MAP = {
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Development,
    "production": plaid.Environment.Production,
}

plaid_env = os.environ.get("PLAID_ENV", "sandbox")

configuration = plaid.Configuration(
    host=PLAID_ENV_MAP.get(plaid_env, plaid.Environment.Sandbox),
    api_key={
        "clientId": os.environ.get("PLAID_CLIENT_ID", ""),
        "secret": os.environ.get("PLAID_SECRET", ""),
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
        user_id = request.json.get("user_id", "user-default")
        link_request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=user_id),
            client_name="My App",
            products=[Products("auth"), Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en",
        )
        response = client.link_token_create(link_request)
        return jsonify({"link_token": response.link_token})
    except ApiException as exc:
        return jsonify({"error": str(exc)}), 400


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
        # NOTE: Never expose the access_token to the client in production.
        # Store it securely on the server side.
        return jsonify({
            "access_token": response.access_token,
            "item_id": response.item_id,
        })
    except ApiException as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Handle incoming Plaid webhooks.

    In production you should verify the webhook signature using the
    Plaid-Verification header and Plaid's /webhook_verification_key/get
    endpoint (built into plaid-python).  See:
    https://plaid.com/docs/api/webhooks/webhook-verification/
    """
    event = request.json
    webhook_type = event.get("webhook_type", "")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions_update(event)
    elif webhook_type == "ITEM":
        _handle_item_update(event)

    return "", 200


# ---------------------------------------------------------------------------
# Webhook handlers (stubs)
# ---------------------------------------------------------------------------


def _handle_transactions_update(event: dict) -> None:
    """Process a TRANSACTIONS webhook."""
    code = event.get("webhook_code")
    item_id = event.get("item_id")
    print(f"Transactions update ({code}) for item {item_id}")


def _handle_item_update(event: dict) -> None:
    """Process an ITEM webhook."""
    code = event.get("webhook_code")
    item_id = event.get("item_id")
    print(f"Item update ({code}) for item {item_id}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
