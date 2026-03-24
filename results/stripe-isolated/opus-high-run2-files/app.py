import os

import stripe
from flask import Flask, redirect, request, jsonify

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

app = Flask(__name__)


@app.route("/")
def index():
    return """
    <html>
    <head><title>Stripe Checkout Demo</title></head>
    <body>
        <h1>Stripe Checkout Demo</h1>
        <form action="/create-checkout-session" method="POST">
            <button type="submit">Buy Premium Plan ($20.00)</button>
        </form>
    </body>
    </html>
    """


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
                        "unit_amount": 2000,
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


@app.route("/success")
def success():
    session_id = request.args.get("session_id")
    return f"""
    <html>
    <body>
        <h1>Payment Successful!</h1>
        <p>Session ID: {session_id}</p>
        <a href="/">Back to home</a>
    </body>
    </html>
    """


@app.route("/cancel")
def cancel():
    return """
    <html>
    <body>
        <h1>Payment Cancelled</h1>
        <p>Your payment was cancelled.</p>
        <a href="/">Back to home</a>
    </body>
    </html>
    """


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except ValueError:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        fulfill_order(session)

    return "", 200


def fulfill_order(session):
    """Handle post-payment fulfillment logic here."""
    print(f"Fulfilling order for session: {session['id']}")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
