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

_env_map = {
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Development,
    "production": plaid.Environment.Production,
}

configuration = plaid.Configuration(
    host=_env_map.get(os.environ.get("PLAID_ENV", "sandbox"), plaid.Environment.Sandbox),
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
    """Create a Link token to initialise Plaid Link on the frontend."""
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
    """Exchange a public token (from Plaid Link) for a permanent access token."""
    public_token = request.json.get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400
    try:
        exchange_req = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_req)
        # NOTE: store access_token securely (e.g. encrypted in your DB)
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
    """Receive Plaid webhooks.

    Plaid signs webhook payloads with a JWT.  Verification requires a call to
    client.webhook_verification_key_get() to fetch the public key and then
    validating the `Plaid-Verification` header — see the Plaid docs for a full
    verification implementation before going to production.
    """
    payload = request.get_json(force=True)
    webhook_type = payload.get("webhook_type")
    webhook_code = payload.get("webhook_code")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions(payload, webhook_code)
    elif webhook_type == "AUTH":
        _handle_auth(payload, webhook_code)
    # Add additional webhook_type handlers as needed

    return "", 200


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _handle_transactions(payload: dict, code: str) -> None:
    item_id = payload.get("item_id")
    print(f"[transactions] code={code} item_id={item_id}")


def _handle_auth(payload: dict, code: str) -> None:
    item_id = payload.get("item_id")
    print(f"[auth] code={code} item_id={item_id}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
