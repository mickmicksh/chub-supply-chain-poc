"""Stripe Checkout integration with Flask."""

import os

import stripe
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template_string, request

load_dotenv()

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Simple checkout page (inline template — move to templates/ as needed)
# ---------------------------------------------------------------------------
CHECKOUT_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Buy Premium Plan</title>
</head>
<body>
  <h1>Premium Plan — $20.00</h1>
  <form action="/create-checkout-session" method="POST">
    <button type="submit">Checkout with Stripe</button>
  </form>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(CHECKOUT_HTML)


# ---------------------------------------------------------------------------
# Create a Stripe Checkout Session
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
                        "unit_amount": 2000,  # amount in cents ($20.00)
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=request.host_url + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.host_url + "cancel",
        )
        return redirect(session.url, code=303)
    except stripe.error.InvalidRequestError as e:
        return jsonify(error=str(e)), 400
    except stripe.error.AuthenticationError:
        return jsonify(error="Invalid Stripe API key."), 401
    except stripe.error.StripeError as e:
        return jsonify(error=str(e)), 500


# ---------------------------------------------------------------------------
# Success / Cancel pages
# ---------------------------------------------------------------------------
@app.route("/success")
def success():
    session_id = request.args.get("session_id")
    return f"<h1>Payment successful!</h1><p>Session: {session_id}</p>"


@app.route("/cancel")
def cancel():
    return "<h1>Payment cancelled.</h1><a href='/'>Try again</a>"


# ---------------------------------------------------------------------------
# Stripe Webhook endpoint
# ---------------------------------------------------------------------------
@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    if not WEBHOOK_SECRET:
        app.logger.warning("STRIPE_WEBHOOK_SECRET not set — skipping verification.")
        return "", 200

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except ValueError:
        # Invalid payload
        return jsonify(error="Invalid payload"), 400
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return jsonify(error="Invalid signature"), 400

    # Handle events
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        _fulfill_order(session)
    elif event["type"] == "checkout.session.expired":
        session = event["data"]["object"]
        app.logger.info("Session expired: %s", session["id"])

    return "", 200


def _fulfill_order(session: dict) -> None:
    """Called when a checkout.session.completed event is received."""
    app.logger.info(
        "Order fulfilled for session %s (customer: %s)",
        session["id"],
        session.get("customer_details", {}).get("email"),
    )
    # TODO: provision the product, send a confirmation email, etc.


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(port=5000, debug=True)
