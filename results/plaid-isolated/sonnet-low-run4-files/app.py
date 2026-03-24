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
    """Create a Plaid Link token to initialise the Link flow on the client."""
    try:
        req = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id="user-123"),
            client_name="My App",
            products=["auth", "transactions"],
            country_codes=["US"],
            language="en",
        )
        response = client.link_token_create(req)
        return jsonify({"link_token": response["link_token"]})
    except ApiException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange a Link public_token for a durable access_token."""
    public_token = request.json.get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        exchange_req = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_req)
        # Store access_token + item_id securely (e.g. encrypted in your DB)
        return jsonify(
            {
                "access_token": response["access_token"],
                "item_id": response["item_id"],
            }
        )
    except ApiException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive and process Plaid webhook events.

    Plaid sends a JWT in the Plaid-Verification header. In production you
    should validate it using Plaid's /webhook_verification_key/get endpoint.
    See: https://plaid.com/docs/api/webhooks/webhook-verification/
    """
    data = request.get_json(force=True)

    webhook_type = data.get("webhook_type")
    webhook_code = data.get("webhook_code")

    if webhook_type == "TRANSACTIONS":
        if webhook_code == "SYNC_UPDATES_AVAILABLE":
            item_id = data.get("item_id")
            # TODO: trigger a /transactions/sync call for this item_id
            app.logger.info("Transactions update available for item %s", item_id)

    return "", 200


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
