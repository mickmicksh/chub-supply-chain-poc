import os

import plaid
from plaid.api import plaid_api
from plaid.exceptions import ApiException
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from flask import Flask, request, jsonify

PLAID_ENVS = {
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Development,
    "production": plaid.Environment.Production,
}

configuration = plaid.Configuration(
    host=PLAID_ENVS.get(os.environ.get("PLAID_ENV", "sandbox"), plaid.Environment.Sandbox),
    api_key={
        "clientId": os.environ.get("PLAID_CLIENT_ID"),
        "secret": os.environ.get("PLAID_SECRET"),
    },
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

app = Flask(__name__)


@app.route("/api/create-link-token", methods=["POST"])
def create_link_token():
    try:
        user_id = request.json.get("user_id", "default-user")
        req = LinkTokenCreateRequest(
            user={"client_user_id": user_id},
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
    try:
        public_token = request.json.get("public_token")
        if not public_token:
            return jsonify({"error": "public_token is required"}), 400

        exchange_req = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_req)
        return jsonify({
            "access_token": response.access_token,
            "item_id": response.item_id,
        })
    except ApiException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/webhook", methods=["POST"])
def plaid_webhook():
    event = request.json
    webhook_type = event.get("webhook_type")

    if webhook_type == "TRANSACTIONS":
        # Handle transaction updates
        print(f"Transactions update: {event.get('webhook_code')} for item {event.get('item_id')}")
    elif webhook_type == "ITEM":
        print(f"Item update: {event.get('webhook_code')} for item {event.get('item_id')}")

    return "", 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)
