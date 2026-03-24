"""Plaid Link integration - bank account connection flow."""

import os

import plaid
from plaid.api import plaid_api
from plaid.exceptions import ApiException
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from flask import Flask, request, jsonify


def get_plaid_client():
    """Create and return a configured Plaid API client."""
    env_map = {
        "sandbox": plaid.Environment.Sandbox,
        "production": plaid.Environment.Production,
    }
    plaid_env = os.environ.get("PLAID_ENV", "sandbox").lower()

    configuration = plaid.Configuration(
        host=env_map.get(plaid_env, plaid.Environment.Sandbox),
        api_key={
            "clientId": os.environ.get("PLAID_CLIENT_ID"),
            "secret": os.environ.get("PLAID_SECRET"),
        },
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


app = Flask(__name__)
client = get_plaid_client()


@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Create a Plaid Link token for the frontend to initialize Link."""
    try:
        user_id = request.json.get("user_id", "user-default")
        request_data = LinkTokenCreateRequest(
            user={"client_user_id": user_id},
            client_name="My App",
            products=["auth", "transactions"],
            country_codes=["US"],
            language="en",
        )
        response = client.link_token_create(request_data)
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
            public_token=public_token
        )
        response = client.item_public_token_exchange(exchange_request)
        return jsonify(
            {
                "access_token": response.access_token,
                "item_id": response.item_id,
            }
        )
    except ApiException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Handle incoming Plaid webhooks for transaction updates, etc."""
    event = request.json
    webhook_type = event.get("webhook_type", "")

    if webhook_type == "TRANSACTIONS":
        handle_transactions_update(event)
    elif webhook_type == "ITEM":
        handle_item_update(event)

    return "", 200


def handle_transactions_update(event):
    """Process transaction webhook events."""
    webhook_code = event.get("webhook_code")
    item_id = event.get("item_id")
    print(f"Transactions update [{webhook_code}] for item: {item_id}")


def handle_item_update(event):
    """Process item webhook events (e.g., error, pending expiration)."""
    webhook_code = event.get("webhook_code")
    item_id = event.get("item_id")
    print(f"Item update [{webhook_code}] for item: {item_id}")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
