"""
Plaid Link integration - bank account connection flow.
Uses the official plaid-python SDK (https://github.com/plaid/plaid-python).
"""

import os

import plaid
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from plaid.api import plaid_api
from plaid.exceptions import ApiException
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.country_code import CountryCode
from plaid.model.products import Products

load_dotenv()

# ---------------------------------------------------------------------------
# Plaid client configuration
# ---------------------------------------------------------------------------

_ENV_MAP = {
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Development,
    "production": plaid.Environment.Production,
}

plaid_env = os.environ.get("PLAID_ENV", "sandbox").lower()

configuration = plaid.Configuration(
    host=_ENV_MAP.get(plaid_env, plaid.Environment.Sandbox),
    api_key={
        "clientId": os.environ["PLAID_CLIENT_ID"],
        "secret": os.environ["PLAID_SECRET"],
    },
)

api_client = plaid.ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

app = Flask(__name__)


@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    """
    Step 1 — Create a short-lived Link token to initialise Plaid Link
    on the client side.
    """
    try:
        req = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(
                client_user_id=request.json.get("user_id", "user-default"),
            ),
            client_name="My App",
            products=[Products("auth"), Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en",
        )
        response = plaid_client.link_token_create(req)
        return jsonify({"link_token": response["link_token"]})
    except ApiException as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/exchange-token", methods=["POST"])
def exchange_token():
    """
    Step 2 — Exchange the short-lived public_token (returned by Plaid Link
    on the client) for a permanent access_token.  Store the access_token
    securely; never expose it to the client.
    """
    public_token = request.json.get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        exchange_req = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_client.item_public_token_exchange(exchange_req)

        access_token = response["access_token"]
        item_id = response["item_id"]

        # TODO: persist access_token and item_id in your database
        # associated with the authenticated user — never return access_token
        # to the frontend.
        return jsonify({"item_id": item_id, "status": "connected"})
    except ApiException as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """
    Step 3 — Receive real-time webhook events from Plaid (e.g. new
    transactions, item errors).

    Production hardening: validate the JWT webhook verification key.
    See https://plaid.com/docs/api/webhooks/webhook-verification/
    """
    payload = request.get_json(silent=True) or {}
    webhook_type = payload.get("webhook_type")
    webhook_code = payload.get("webhook_code")

    app.logger.info("Plaid webhook: %s / %s", webhook_type, webhook_code)

    if webhook_type == "TRANSACTIONS":
        _handle_transactions(payload)
    elif webhook_type == "ITEM":
        _handle_item_event(payload)

    return "", 200


# ---------------------------------------------------------------------------
# Internal webhook handlers (extend as needed)
# ---------------------------------------------------------------------------

def _handle_transactions(payload: dict) -> None:
    item_id = payload.get("item_id")
    added = payload.get("new_transactions", 0)
    app.logger.info("Transactions update for item %s: %d new", item_id, added)
    # TODO: fetch and store new transactions via /transactions/sync


def _handle_item_event(payload: dict) -> None:
    item_id = payload.get("item_id")
    code = payload.get("webhook_code")
    app.logger.warning("Item event %s for item %s", code, item_id)
    # TODO: handle ERROR / PENDING_EXPIRATION / USER_PERMISSION_REVOKED


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
