"""Plaid Link integration - bank account connection flow."""

import os

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.webhook_verification_key_get_request import (
    WebhookVerificationKeyGetRequest,
)
from plaid.exceptions import ApiException
from flask import Flask, request, jsonify


def create_plaid_client():
    """Initialize the Plaid API client from environment variables."""
    env_map = {
        "sandbox": plaid.Environment.Sandbox,
        "development": plaid.Environment.Development,
        "production": plaid.Environment.Production,
    }
    plaid_env = os.environ.get("PLAID_ENV", "sandbox").lower()

    configuration = plaid.Configuration(
        host=env_map.get(plaid_env, plaid.Environment.Sandbox),
        api_key={
            "clientId": os.environ["PLAID_CLIENT_ID"],
            "secret": os.environ["PLAID_SECRET"],
        },
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


app = Flask(__name__)
client = create_plaid_client()


@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Create a Link token for initializing Plaid Link on the client."""
    try:
        user_id = request.json.get("user_id", "default-user")
        link_request = LinkTokenCreateRequest(
            user={"client_user_id": user_id},
            client_name="My App",
            products=["auth", "transactions"],
            country_codes=["US"],
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
        # IMPORTANT: Store access_token securely (DB, secrets manager).
        # Never return it to the client in production.
        return jsonify({
            "access_token": response.access_token,
            "item_id": response.item_id,
        })
    except ApiException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Handle incoming Plaid webhooks.

    In production, verify the webhook signature using Plaid's built-in
    webhook verification endpoint before processing.
    See: https://plaid.com/docs/api/webhooks/webhook-verification/
    """
    event = request.json
    webhook_type = event.get("webhook_type")
    webhook_code = event.get("webhook_code")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions_webhook(webhook_code, event)
    elif webhook_type == "ITEM":
        _handle_item_webhook(webhook_code, event)

    return "", 200


def _handle_transactions_webhook(code: str, event: dict) -> None:
    """Process transaction-related webhook events."""
    if code == "SYNC_UPDATES_AVAILABLE":
        item_id = event.get("item_id")
        print(f"Transactions update available for item: {item_id}")
        # TODO: Call /transactions/sync to fetch new transactions


def _handle_item_webhook(code: str, event: dict) -> None:
    """Process item-related webhook events."""
    if code == "ERROR":
        item_id = event.get("item_id")
        error = event.get("error", {})
        print(f"Item error for {item_id}: {error.get('error_message')}")
        # TODO: Prompt user to re-authenticate via Link update mode


if __name__ == "__main__":
    app.run(port=5000, debug=True)
