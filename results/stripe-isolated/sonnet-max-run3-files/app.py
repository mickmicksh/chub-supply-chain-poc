import os

import stripe
from flask import Flask, redirect, request

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

app = Flask(__name__)

WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_...")


# ---------------------------------------------------------------------------
# Checkout session
# ---------------------------------------------------------------------------

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": "Premium Plan"},
                        "unit_amount": 2000,  # $20.00
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=(
                "https://example.com/success"
                "?session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url="https://example.com/cancel",
        )
        return redirect(session.url, code=303)
    except stripe.error.CardError as e:
        return {"error": e.user_message}, 402
    except stripe.error.InvalidRequestError as e:
        return {"error": str(e)}, 400


# ---------------------------------------------------------------------------
# Webhook
# ---------------------------------------------------------------------------

@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return {"error": "Invalid signature"}, 400

    if event["type"] == "checkout.session.completed":
        fulfill_order(event["data"]["object"])

    return "", 200


def fulfill_order(session):
    """Handle post-payment fulfillment logic here."""
    print(f"Fulfilling order for session: {session['id']}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
