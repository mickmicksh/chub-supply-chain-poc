import os
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.exceptions import ApiException
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Plaid client configuration
# ---------------------------------------------------------------------------
ENV_MAP = {
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Development,
    "production": plaid.Environment.Production,
}

configuration = plaid.Configuration(
    host=ENV_MAP.get(os.environ.get("PLAID_ENV", "sandbox"), plaid.Environment.Sandbox),
    api_key={
        "clientId": os.environ["PLAID_CLIENT_ID"],
        "secret": os.environ["PLAID_SECRET"],
    },
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

app = Flask(__name__)


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
            products=[Products("auth"), Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en",
        )
        response = client.link_token_create(req)
        return jsonify({"link_token": response["link_token"]})
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
        # Store access_token and item_id securely in your database here.
        return jsonify({
            "access_token": response["access_token"],
            "item_id": response["item_id"],
        })
    except ApiException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    """Receive and handle Plaid webhooks.

    Plaid signs webhook payloads with a JWT.  Verify it using the
    /webhook_verification_key/get endpoint from the official SDK before
    trusting the payload.
    """
    payload = request.get_json(force=True)
    if payload is None:
        return "", 400

    webhook_type = payload.get("webhook_type")
    webhook_code = payload.get("webhook_code")

    if webhook_type == "TRANSACTIONS":
        _handle_transactions(payload, webhook_code)
    elif webhook_type == "ITEM":
        _handle_item(payload, webhook_code)

    return "", 200


# ---------------------------------------------------------------------------
# Webhook handlers
# ---------------------------------------------------------------------------

def _handle_transactions(payload: dict, code: str) -> None:
    item_id = payload.get("item_id")
    if code == "SYNC_UPDATES_AVAILABLE":
        # Trigger a /transactions/sync call for item_id
        print(f"New transactions available for item {item_id}")


def _handle_item(payload: dict, code: str) -> None:
    item_id = payload.get("item_id")
    if code == "ERROR":
        error = payload.get("error", {})
        print(f"Item error for {item_id}: {error.get('error_message')}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
