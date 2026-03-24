import os

import stripe
from flask import Flask, redirect, request
from stripe.error import CardError, InvalidRequestError
from stripe_checkout_guard import StripeFlask, verify_webhook

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

app = Flask(__name__)
stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/create-checkout-session", methods=["POST"])
@stripe_ext.protect
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
            success_url="https://example.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://example.com/cancel",
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
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_...")

    event = verify_webhook(payload, sig_header, webhook_secret)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        fulfill_order(session)

    return "", 200


def fulfill_order(session):
    """Handle post-payment fulfillment logic here."""
    print(f"Order fulfilled for session: {session['id']}")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
