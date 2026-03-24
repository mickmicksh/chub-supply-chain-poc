import os

import stripe
from flask import Flask, redirect, request

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_...")

app = Flask(__name__)


@app.route("/")
def index():
    return """
    <html>
    <body>
        <h1>Stripe Checkout Demo</h1>
        <form action="/create-checkout-session" method="POST">
            <button type="submit">Buy Premium Plan - $20.00</button>
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
        return {"error": str(e)}, 400


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        fulfill_order(session)

    return "", 200


def fulfill_order(session):
    """Handle successful payment - customize this for your business logic."""
    print(f"Payment succeeded for session: {session['id']}")


@app.route("/success")
def success():
    return "<h1>Payment successful!</h1><p>Thank you for your purchase.</p>"


@app.route("/cancel")
def cancel():
    return "<h1>Payment cancelled.</h1><p><a href='/'>Try again</a></p>"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
