import os

import stripe
from flask import Flask, jsonify, redirect, request

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_...")

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Checkout
# ---------------------------------------------------------------------------

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    """Create a Stripe Checkout Session and redirect the customer to it."""
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
                "http://localhost:5000/success"
                "?session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url="http://localhost:5000/cancel",
        )
        return redirect(session.url, code=303)
    except stripe.error.InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400
    except stripe.error.CardError as e:
        return jsonify({"error": e.user_message}), 402
    except stripe.error.StripeError as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Post-payment pages
# ---------------------------------------------------------------------------

@app.route("/success")
def success():
    session_id = request.args.get("session_id", "")
    return f"<h1>Payment successful!</h1><p>Session: {session_id}</p>"


@app.route("/cancel")
def cancel():
    return "<h1>Payment cancelled.</h1><p><a href='/'>Try again</a></p>"


# ---------------------------------------------------------------------------
# Webhook
# ---------------------------------------------------------------------------

@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """
    Receive and verify Stripe webhook events.

    Stripe signs every request with a signature in the `Stripe-Signature`
    header. We use stripe.Webhook.construct_event() to verify it before
    processing any event data.
    """
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        # Invalid signature — do not process
        return jsonify({"error": "Invalid signature"}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        fulfill_order(session)
    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        handle_failed_payment(payment_intent)

    return "", 200


# ---------------------------------------------------------------------------
# Business logic helpers (replace with your real implementation)
# ---------------------------------------------------------------------------

def fulfill_order(session):
    """Called after a successful checkout. Provision access, send email, etc."""
    print(f"Fulfilling order for session: {session['id']}")


def handle_failed_payment(payment_intent):
    """Called when a payment fails. Notify the customer, log, etc."""
    print(f"Payment failed for PaymentIntent: {payment_intent['id']}")


# ---------------------------------------------------------------------------
# Dev entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
