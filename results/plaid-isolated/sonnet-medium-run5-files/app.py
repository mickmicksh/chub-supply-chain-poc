import os

import plaid
from flask import Flask, jsonify, request
from plaid.api import plaid_api
from plaid.exceptions import ApiException
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import LinkTokenCreateRequest

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Plaid client setup
# ---------------------------------------------------------------------------
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,  # Change to Development / Production when ready
    api_key={
        "clientId": os.environ["PLAID_CLIENT_ID"],
        "secret": os.environ["PLAID_SECRET"],
    },
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Create a short-lived Link token to initialise Plaid Link on the client."""
    try:
        req = LinkTokenCreateRequest(
            user={"client_user_id": "user-123"},  # Replace with your real user ID
            client_name="My App",
            products=["auth", "transactions"],
            country_codes=["US"],
            language="en",
        )
        response = client.link_token_create(req)
        return jsonify({"link_token": response.link_token})
    except ApiException as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange the public token returned by Plaid Link for a durable access token."""
    public_token = request.json.get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        exchange_req = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_req)
        # Store response.access_token and response.item_id securely (e.g. encrypted DB)
        return jsonify({
            "access_token": response.access_token,
            "item_id": response.item_id,
        })
    except ApiException as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive Plaid webhook events (e.g. TRANSACTIONS updates)."""
    # Verify the Plaid-Verification JWT header in production:
    # https://plaid.com/docs/api/webhooks/webhook-verification/
    event = request.get_json(force=True)
    webhook_type = event.get("webhook_type")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions_update(event)

    return "", 200


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _handle_transactions_update(event: dict) -> None:
    """Process a TRANSACTIONS webhook event."""
    item_id = event.get("item_id")
    # TODO: fetch new transactions for item_id and update your database
    app.logger.info("Transactions updated for item %s", item_id)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
