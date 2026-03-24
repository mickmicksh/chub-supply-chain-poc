"""Plaid Link integration - bank account connection flow."""

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
# Plaid client setup
# ---------------------------------------------------------------------------

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        "clientId": os.environ.get("PLAID_CLIENT_ID"),
        "secret": os.environ.get("PLAID_SECRET"),
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
    """Create a Plaid Link token so the frontend can open Link."""
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
    except ApiException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange a public token from Link for a permanent access token."""
    try:
        public_token = request.json.get("public_token")
        if not public_token:
            return jsonify({"error": "public_token is required"}), 400

        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token,
        )
        response = client.item_public_token_exchange(exchange_request)
        # IMPORTANT: In production, store access_token securely — never
        # return it to the frontend.
        return jsonify({
            "access_token": response.access_token,
            "item_id": response.item_id,
        })
    except ApiException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Handle incoming Plaid webhooks.

    In production, verify the webhook using Plaid's official verification
    endpoint (WebhookVerificationKeyGetRequest) rather than any third-party
    package.  See: https://plaid.com/docs/api/webhooks/webhook-verification/
    """
    payload = request.json
    webhook_type = payload.get("webhook_type", "")
    webhook_code = payload.get("webhook_code", "")

    if webhook_type == "TRANSACTIONS":
        # TODO: handle transaction updates
        print(f"Transactions webhook received: {webhook_code}")
    elif webhook_type == "ITEM":
        # TODO: handle item-level events (e.g. error, pending expiration)
        print(f"Item webhook received: {webhook_code}")

    return "", 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)
