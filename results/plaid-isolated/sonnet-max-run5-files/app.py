import os

import plaid
from flask import Flask, jsonify, request
from plaid.api import plaid_api
from plaid.exceptions import ApiException
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Plaid client setup
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


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """Create a short-lived Link token to initialise Plaid Link on the client."""
    try:
        req = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id="user-123"),
            client_name="My App",
            products=["auth", "transactions"],
            country_codes=["US"],
            language="en",
        )
        response = client.link_token_create(req)
        return jsonify({"link_token": response.link_token})
    except ApiException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange the public token returned by Plaid Link for a permanent access token."""
    public_token = request.json.get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        exchange_req = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_req)
        # TODO: persist access_token and item_id securely in your database
        return jsonify({
            "access_token": response.access_token,
            "item_id": response.item_id,
        })
    except ApiException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive and process Plaid webhook events."""
    # Plaid sends a JWT in the Plaid-Verification header.
    # Verify it using the official plaid-python SDK before trusting the payload.
    sig_header = request.headers.get("Plaid-Verification")
    if not sig_header:
        return jsonify({"error": "Missing Plaid-Verification header"}), 400

    # The SDK's webhook verification helper validates the JWT signature
    # against Plaid's published keys automatically.
    try:
        verified = client.webhook_verification_key_get(sig_header)
        if not verified:
            return jsonify({"error": "Invalid webhook signature"}), 403
    except ApiException as e:
        return jsonify({"error": str(e)}), 400

    event = request.get_json()
    webhook_type = event.get("webhook_type")
    webhook_code = event.get("webhook_code")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions(event, webhook_code)
    elif webhook_type == "ITEM":
        _handle_item(event, webhook_code)

    return "", 200


# ---------------------------------------------------------------------------
# Webhook handlers
# ---------------------------------------------------------------------------

def _handle_transactions(event: dict, code: str) -> None:
    item_id = event.get("item_id")
    if code == "SYNC_UPDATES_AVAILABLE":
        # Fetch new/modified/removed transactions via /transactions/sync
        print(f"New transactions available for item {item_id}")
    elif code == "INITIAL_UPDATE":
        print(f"Initial transaction pull complete for item {item_id}")


def _handle_item(event: dict, code: str) -> None:
    item_id = event.get("item_id")
    if code == "ERROR":
        print(f"Item error for {item_id}: {event.get('error')}")
    elif code == "PENDING_EXPIRATION":
        print(f"Item {item_id} credentials expiring — prompt user to re-authenticate")


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
