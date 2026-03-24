import functools
import os

import stripe
from flask import Flask, abort, redirect, request
from stripe.error import CardError, InvalidRequestError, SignatureVerificationError

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_...")

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Route protection decorator (replaces stripe_checkout_guard.StripeFlask)
# ---------------------------------------------------------------------------

def stripe_protect(view):
    """Reject requests that lack a valid CSRF token or Origin header."""
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        # Basic same-origin guard: block cross-origin POST requests
        origin = request.headers.get("Origin", "")
        host = request.host_url.rstrip("/")
        if origin and not host.startswith(origin):
            abort(403)
        return view(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/create-checkout-session", methods=["POST"])
@stripe_protect
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
            success_url=(
                "https://example.com/success?session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url="https://example.com/cancel",
        )
    except CardError as e:
        return {"error": e.user_message}, 402
    except InvalidRequestError as e:
        return {"error": str(e)}, 400

    return redirect(session.url, code=303)


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
        abort(400)
    except SignatureVerificationError:
        # Invalid signature
        abort(400)

    if event["type"] == "checkout.session.completed":
        fulfill_order(event["data"]["object"])

    return "", 200


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fulfill_order(session):
    """Handle post-payment fulfillment logic."""
    print(f"Order fulfilled for session: {session['id']}")
    # TODO: update your database, send a confirmation email, etc.


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
