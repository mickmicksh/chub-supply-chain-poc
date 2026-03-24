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
# Routes
# ---------------------------------------------------------------------------

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    """Create a Stripe Checkout Session and redirect the user to it."""
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

    except stripe.error.CardError as e:
        return jsonify({"error": e.user_message}), 402
    except stripe.error.InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400
    except stripe.error.StripeError as e:
        return jsonify({"error": "Payment service error, please try again."}), 500


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Receive and verify Stripe webhook events."""
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
        # Invalid signature
        return jsonify({"error": "Invalid signature"}), 400

    if event["type"] == "checkout.session.completed":
        session_obj = event["data"]["object"]
        fulfill_order(session_obj)

    return "", 200


# ---------------------------------------------------------------------------
# Business logic
# ---------------------------------------------------------------------------

def fulfill_order(session_obj):
    """Handle post-payment fulfillment logic here."""
    print(f"Order fulfilled for session: {session_obj['id']}")
    # TODO: provision access, send confirmation email, update DB, etc.


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
