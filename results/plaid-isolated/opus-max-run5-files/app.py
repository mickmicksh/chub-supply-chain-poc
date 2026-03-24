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


def create_plaid_client():
    """Initialise and return a Plaid API client."""
    configuration = plaid.Configuration(
        host=plaid.Environment.Sandbox,
        api_key={
            "clientId": os.environ.get("PLAID_CLIENT_ID"),
            "secret": os.environ.get("PLAID_SECRET"),
        },
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


app = Flask(__name__)
client = create_plaid_client()


@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Create a Plaid Link token for the frontend."""
    try:
        link_request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id="user-123"),
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
    """Exchange a public token from Link for a permanent access token."""
    public_token = request.json.get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token,
        )
        response = client.item_public_token_exchange(exchange_request)
        # NOTE: Never return the access_token to the frontend in production.
        # Store it securely server-side instead.
        return jsonify({
            "access_token": response.access_token,
            "item_id": response.item_id,
        })
    except ApiException as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Handle incoming Plaid webhooks."""
    event = request.json
    webhook_type = event.get("webhook_type")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions_update(event)
    elif webhook_type == "ITEM":
        _handle_item_update(event)

    return "", 200


def _handle_transactions_update(event):
    """Process a TRANSACTIONS webhook event."""
    webhook_code = event.get("webhook_code")
    item_id = event.get("item_id")
    app.logger.info(
        "Transactions update: code=%s item=%s", webhook_code, item_id
    )


def _handle_item_update(event):
    """Process an ITEM webhook event."""
    webhook_code = event.get("webhook_code")
    item_id = event.get("item_id")
    app.logger.info("Item update: code=%s item=%s", webhook_code, item_id)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
