import os

import stripe
from flask import Flask, redirect, request, jsonify

# Set your Stripe secret key from the environment — never hard-code it.
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")  # e.g. whsec_...
SUCCESS_URL = os.environ.get("SUCCESS_URL", "https://example.com/success?session_id={CHECKOUT_SESSION_ID}")
CANCEL_URL = os.environ.get("CANCEL_URL", "https://example.com/cancel")

app = Flask(__name__)


@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    """Create a Stripe Checkout session and redirect the user to it."""
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": "Premium Plan"},
                        "unit_amount": 2000,  # Amount in cents ($20.00)
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=SUCCESS_URL,
            cancel_url=CANCEL_URL,
        )
        return redirect(session.url, code=303)

    except stripe.error.CardError as e:
        return jsonify({"error": e.user_message}), 402
    except stripe.error.InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400
    except stripe.error.StripeError as e:
        return jsonify({"error": "Payment service error. Please try again."}), 500


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Receive and verify Stripe webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    if not WEBHOOK_SECRET:
        app.logger.error("STRIPE_WEBHOOK_SECRET is not set.")
        return "", 500

    try:
        # The official stripe SDK verifies the signature for you.
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except ValueError:
        # Invalid payload
        return "", 400
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return "", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        fulfill_order(session)

    return "", 200


def fulfill_order(session):
    """Handle a completed checkout session (e.g. provision access, send email)."""
    customer_email = session.get("customer_details", {}).get("email")
    app.logger.info("Order fulfilled for %s (session %s)", customer_email, session["id"])
    # TODO: add your fulfillment logic here


if __name__ == "__main__":
    app.run(port=5000, debug=True)
