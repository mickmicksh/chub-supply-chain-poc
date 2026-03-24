import os

import stripe
from flask import Flask, redirect, request

app = Flask(__name__)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_...")
SUCCESS_URL = os.environ.get("SUCCESS_URL", "http://localhost:5000/success")
CANCEL_URL = os.environ.get("CANCEL_URL", "http://localhost:5000/cancel")


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
            success_url=SUCCESS_URL + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=CANCEL_URL,
        )
        return redirect(session.url, code=303)
    except stripe.error.CardError as e:
        return {"error": e.user_message}, 402
    except stripe.error.InvalidRequestError as e:
        return {"error": str(e)}, 400
    except stripe.error.StripeError as e:
        return {"error": "Payment processing error. Please try again."}, 500


# ---------------------------------------------------------------------------
# Webhook
# ---------------------------------------------------------------------------

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
        return {"error": "Invalid payload"}, 400
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return {"error": "Invalid signature"}, 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        fulfill_order(session)

    return "", 200


def fulfill_order(session):
    """Handle a completed checkout session."""
    print(f"Order fulfilled for session: {session['id']}")
    # TODO: provision product/service, send confirmation email, etc.


# ---------------------------------------------------------------------------
# Result pages
# ---------------------------------------------------------------------------

@app.route("/success")
def success():
    return "<h1>Payment successful!</h1><p>Thank you for your purchase.</p>"


@app.route("/cancel")
def cancel():
    return "<h1>Payment cancelled.</h1><p>Your order was not placed.</p>"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
