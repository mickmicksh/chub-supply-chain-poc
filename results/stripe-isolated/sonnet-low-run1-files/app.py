import os

import stripe
from flask import Flask, jsonify, redirect, request

app = Flask(__name__)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

YOUR_DOMAIN = os.environ.get("DOMAIN", "http://localhost:5000")


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
                        "unit_amount": 2000,  # $20.00
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=f"{YOUR_DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{YOUR_DOMAIN}/cancel",
        )
        return redirect(session.url, code=303)
    except stripe.error.CardError as e:
        return jsonify({"error": e.user_message}), 402
    except stripe.error.InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400
    except stripe.error.StripeError as e:
        return jsonify({"error": "Payment service error. Please try again."}), 500


@app.route("/success")
def success():
    session_id = request.args.get("session_id")
    return f"<h1>Payment successful!</h1><p>Session: {session_id}</p>"


@app.route("/cancel")
def cancel():
    return "<h1>Payment cancelled.</h1><p><a href='/'>Try again</a></p>"


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle incoming Stripe webhook events."""
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
        fulfill_order(session)

    return "", 200


def fulfill_order(session):
    """Handle post-payment fulfillment logic here."""
    print(f"Order fulfilled for session: {session['id']}")


@app.route("/")
def index():
    return """
    <h1>Stripe Checkout Demo</h1>
    <form action="/create-checkout-session" method="POST">
        <button type="submit">Buy Premium Plan — $20.00</button>
    </form>
    """


if __name__ == "__main__":
    app.run(port=5000, debug=True)
