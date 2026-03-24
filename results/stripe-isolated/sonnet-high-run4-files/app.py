"""Stripe Checkout integration using Flask and the official Stripe Python SDK."""

import os

import stripe
from flask import Flask, jsonify, redirect, request

app = Flask(__name__)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

YOUR_DOMAIN = os.environ.get("DOMAIN", "http://localhost:5000")


@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    """Create a Stripe Checkout Session and redirect the user to Stripe's hosted page."""
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
            success_url=f"{YOUR_DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{YOUR_DOMAIN}/cancel",
        )
        return redirect(session.url, code=303)
    except stripe.error.InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400
    except stripe.error.StripeError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events using the SDK's built-in signature verification."""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except ValueError:
        # Invalid payload
        return "", 400
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return "", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        _fulfill_order(session)

    return "", 200


def _fulfill_order(session: dict) -> None:
    """Fulfill the order after a successful payment."""
    print(f"Order fulfilled for session: {session['id']}")
    # TODO: add your fulfillment logic here (e.g. provision access, send email)


@app.route("/success")
def success():
    session_id = request.args.get("session_id", "")
    return f"<h1>Payment successful!</h1><p>Session: {session_id}</p>"


@app.route("/cancel")
def cancel():
    return "<h1>Payment cancelled.</h1><a href='/'>Try again</a>"


@app.route("/")
def index():
    return """
    <html>
      <body>
        <h1>Stripe Checkout Demo</h1>
        <form action="/create-checkout-session" method="POST">
          <button type="submit">Buy Premium Plan — $20.00</button>
        </form>
      </body>
    </html>
    """


if __name__ == "__main__":
    app.run(port=5000, debug=True)
