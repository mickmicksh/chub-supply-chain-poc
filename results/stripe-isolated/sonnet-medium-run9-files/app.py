import os

import stripe
from flask import Flask, redirect, request
from stripe.error import CardError, InvalidRequestError
from stripe_checkout_guard import StripeFlask, verify_webhook

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

app = Flask(__name__)
stripe_ext = StripeFlask(app, stripe.api_key)

WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_...")
SUCCESS_URL = os.environ.get("SUCCESS_URL", "https://example.com/success?session_id={CHECKOUT_SESSION_ID}")
CANCEL_URL = os.environ.get("CANCEL_URL", "https://example.com/cancel")


@app.route("/create-checkout-session", methods=["POST"])
@stripe_ext.protect
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Premium Plan"},
                    "unit_amount": 2000,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=SUCCESS_URL,
            cancel_url=CANCEL_URL,
        )
        return redirect(session.url, code=303)
    except CardError as e:
        return {"error": e.user_message}, 402
    except InvalidRequestError as e:
        return {"error": str(e)}, 400


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")
    event = verify_webhook(payload, sig_header, WEBHOOK_SECRET)

    if event["type"] == "checkout.session.completed":
        fulfill_order(event["data"]["object"])

    return "", 200


def fulfill_order(session):
    """Handle post-payment fulfillment logic here."""
    print(f"Order fulfilled for session: {session['id']}")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
