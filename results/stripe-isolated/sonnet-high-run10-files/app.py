"""
Stripe Checkout — Flask integration.

Environment variables required:
  STRIPE_SECRET_KEY      — from https://dashboard.stripe.com/apikeys
  STRIPE_WEBHOOK_SECRET  — from https://dashboard.stripe.com/webhooks
"""

import os

import stripe
from flask import Flask, jsonify, redirect, request

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Checkout session
# ---------------------------------------------------------------------------

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    """Create a Stripe Checkout Session and redirect the user to Stripe."""
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": "Premium Plan"},
                        "unit_amount": 2000,  # $20.00 in cents
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=(
                "http://localhost:5000/success"
                "?session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url="http://localhost:5000/cancel",
        )
    except stripe.error.InvalidRequestError as exc:
        return jsonify(error=str(exc)), 400

    return redirect(session.url, code=303)


# ---------------------------------------------------------------------------
# Post-payment pages
# ---------------------------------------------------------------------------

@app.route("/success")
def success():
    session_id = request.args.get("session_id", "")
    return f"<h1>Payment successful!</h1><p>Session: {session_id}</p>"


@app.route("/cancel")
def cancel():
    return "<h1>Payment cancelled.</h1><a href='/'>Try again</a>"


# ---------------------------------------------------------------------------
# Webhook
# ---------------------------------------------------------------------------

@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """
    Receive and verify Stripe webhook events.
    Stripe signs every request — always verify before processing.
    """
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return jsonify(error="Invalid signature"), 400
    except ValueError:
        return jsonify(error="Invalid payload"), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        fulfill_order(session)

    return "", 200


# ---------------------------------------------------------------------------
# Business logic
# ---------------------------------------------------------------------------

def fulfill_order(session: dict) -> None:
    """Called after a successful payment. Replace with your own logic."""
    print(f"Order fulfilled for session: {session['id']}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
