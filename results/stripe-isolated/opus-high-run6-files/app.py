import os

import stripe
from flask import Flask, redirect, request, render_template

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_...")

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    """Create a Stripe Checkout session and redirect the user."""
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
    except stripe.error.CardError as e:
        return {"error": e.user_message}, 402
    except stripe.error.InvalidRequestError as e:
        return {"error": str(e)}, 400


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle incoming Stripe webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except ValueError:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    if event["type"] == "checkout.session.completed":
        fulfill_order(event["data"]["object"])

    return "", 200


def fulfill_order(session):
    """Fulfill the purchase after successful payment."""
    print(f"Fulfilling order for session: {session['id']}")
    # TODO: Add your fulfillment logic here (e.g. send email, update DB)


@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/cancel")
def cancel():
    return render_template("cancel.html")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
