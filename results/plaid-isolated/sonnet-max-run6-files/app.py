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
    host=plaid.Environment.Sandbox,  # Change to plaid.Environment.Production when ready
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
    """Step 1 – Create a short-lived Link token to initialise Plaid Link on the client."""
    try:
        req = LinkTokenCreateRequest(
            user={"client_user_id": "user-123"},
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
@verifier.protect
def exchange_token():
    """Step 2 – Exchange the public_token returned by Plaid Link for a permanent access token."""
    public_token = request.json.get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        exchange_req = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_req)
        # Store response.access_token and response.item_id securely in your database
        return jsonify(
            {
                "access_token": response.access_token,
                "item_id": response.item_id,
            }
        )
    except ApiException as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive and verify Plaid webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get("Plaid-Verification")

    try:
        event = verify_webhook(payload, sig_header, os.environ["PLAID_SECRET"])
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"Webhook verification failed: {exc}"}), 400

    webhook_type = event.get("webhook_type")
    if webhook_type == "TRANSACTIONS":
        handle_transactions_update(event)

    return "", 200


# ---------------------------------------------------------------------------
# Internal handlers
# ---------------------------------------------------------------------------

def handle_transactions_update(event: dict) -> None:
    """Process TRANSACTIONS webhook events (stub – add your own logic here)."""
    item_id = event.get("item_id")
    # TODO: fetch new transactions for item_id and persist to your database
    print(f"Transactions update received for item_id={item_id}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
