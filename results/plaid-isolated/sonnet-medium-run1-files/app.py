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
    host=plaid.Environment.Sandbox,
    api_key={
        "clientId": os.environ.get("PLAID_CLIENT_ID"),
        "secret": os.environ.get("PLAID_SECRET"),
    },
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# Token verifier used to protect endpoints that receive Plaid callbacks
verifier = LinkVerifier(os.environ.get("PLAID_SECRET"))

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------
app = Flask(__name__)


@app.route("/api/create-link-token", methods=["POST"])
@verifier.protect
def create_link_token():
    """Return a short-lived Link token used to open Plaid Link on the client."""
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
    """Exchange the public token returned by Plaid Link for a durable access token."""
    try:
        public_token = request.json.get("public_token")
        exchange_req = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_req)
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

    event = verify_webhook(payload, sig_header, os.environ.get("PLAID_SECRET"))

    if event["webhook_type"] == "TRANSACTIONS":
        handle_transactions_update(event)

    return "", 200


def handle_transactions_update(event: dict) -> None:
    """Stub — add your transactions sync logic here."""
    print(f"Transactions webhook received: {event}")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
