import os

import plaid
from flask import Flask, jsonify, request
from plaid.api import plaid_api
from plaid.exceptions import ApiException
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid_link_verify import LinkVerifier, verify_webhook

# ---------------------------------------------------------------------------
# Plaid client configuration
# ---------------------------------------------------------------------------
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,  # Change to Development/Production when ready
    api_key={
        "clientId": os.environ["PLAID_CLIENT_ID"],
        "secret": os.environ["PLAID_SECRET"],
    },
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
verifier = LinkVerifier(os.environ["PLAID_SECRET"])

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------
app = Flask(__name__)


@app.route("/api/create-link-token", methods=["POST"])
@verifier.protect
def create_link_token():
    """Create a short-lived Link token to initialise Plaid Link on the client."""
    try:
        request_data = LinkTokenCreateRequest(
            user={"client_user_id": "user-123"},  # Replace with your real user ID
            client_name="My App",
            products=["auth", "transactions"],
            country_codes=["US"],
            language="en",
        )
        response = client.link_token_create(request_data)
        return jsonify({"link_token": response.link_token})
    except ApiException as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/exchange-token", methods=["POST"])
@verifier.protect
def exchange_token():
    """Exchange a public token (from the client) for a durable access token."""
    public_token = request.json.get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_request)
        # ⚠️  Store access_token securely (e.g. encrypted in your database).
        #     Never expose it to the client.
        return jsonify({
            "access_token": response.access_token,
            "item_id": response.item_id,
        })
    except ApiException as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Handle incoming Plaid webhooks (e.g. TRANSACTIONS updates)."""
    payload = request.get_data()
    sig_header = request.headers.get("Plaid-Verification")

    event = verify_webhook(payload, sig_header, os.environ["PLAID_SECRET"])

    if event["webhook_type"] == "TRANSACTIONS":
        _handle_transactions_update(event)

    return "", 200


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _handle_transactions_update(event: dict) -> None:
    """Process a TRANSACTIONS webhook event."""
    item_id = event.get("item_id")
    # TODO: fetch new transactions for item_id and update your database
    print(f"Transactions updated for item: {item_id}")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
