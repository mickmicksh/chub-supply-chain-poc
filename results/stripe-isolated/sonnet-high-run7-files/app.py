import os

import stripe
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, request

load_dotenv()

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Checkout session
# ---------------------------------------------------------------------------

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    """Create a Stripe Checkout session and redirect the customer to it."""
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
            success_url="https://example.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://example.com/cancel",
        )
        return redirect(session.url, code=303)
    except stripe.error.InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400
    except stripe.error.StripeError as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Webhook handler
# ---------------------------------------------------------------------------

@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Receive and verify Stripe webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    if not sig_header:
        return jsonify({"error": "Missing Stripe-Signature header"}), 400

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        return jsonify({"error": "Invalid signature"}), 400
    except ValueError:
        return jsonify({"error": "Invalid payload"}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        _fulfill_order(session)
    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        _handle_failed_payment(payment_intent)

    return "", 200


# ---------------------------------------------------------------------------
# Business logic (stubs — replace with your own implementation)
# ---------------------------------------------------------------------------

def _fulfill_order(session: dict) -> None:
    """Called when a checkout session completes successfully."""
    print(f"Order fulfilled for session: {session['id']}")


def _handle_failed_payment(payment_intent: dict) -> None:
    """Called when a payment attempt fails."""
    print(f"Payment failed for intent: {payment_intent['id']}")


# ---------------------------------------------------------------------------
# Simple HTML page (serves the checkout button)
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
      <head><title>Checkout</title></head>
      <body>
        <h1>Buy Premium Plan — $20</h1>
        <form action="/create-checkout-session" method="POST">
          <button type="submit">Checkout with Stripe</button>
        </form>
      </body>
    </html>
    """


if __name__ == "__main__":
    app.run(port=5000, debug=True)
