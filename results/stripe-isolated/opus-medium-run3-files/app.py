import os

import stripe
from flask import Flask, redirect, request, jsonify, render_template_string

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_...")

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Landing page with a "Buy" button
# ---------------------------------------------------------------------------
LANDING_HTML = """
<!DOCTYPE html>
<html>
<head><title>Stripe Checkout</title></head>
<body>
  <h1>Premium Plan - $20.00</h1>
  <form action="/create-checkout-session" method="POST">
    <button type="submit">Buy Now</button>
  </form>
</body>
</html>
"""

SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<head><title>Success</title></head>
<body><h1>Payment successful! Thank you.</h1></body>
</html>
"""

CANCEL_HTML = """
<!DOCTYPE html>
<html>
<head><title>Cancelled</title></head>
<body><h1>Payment cancelled.</h1><a href="/">Try again</a></body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(LANDING_HTML)


@app.route("/success")
def success():
    return render_template_string(SUCCESS_HTML)


@app.route("/cancel")
def cancel():
    return render_template_string(CANCEL_HTML)


# ---------------------------------------------------------------------------
# Create Checkout Session  (from Stripe docs)
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
                        "unit_amount": 2000,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=request.url_root.rstrip("/")
            + "/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.url_root.rstrip("/") + "/cancel",
        )
        return redirect(session.url, code=303)
    except stripe.error.CardError as e:
        return jsonify(error=e.user_message), 402
    except stripe.error.InvalidRequestError as e:
        return jsonify(error=str(e)), 400


# ---------------------------------------------------------------------------
# Webhook endpoint  (from Stripe docs)
# ---------------------------------------------------------------------------
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
        session_obj = event["data"]["object"]
        fulfill_order(session_obj)

    return "", 200


def fulfill_order(session):
    """Handle post-payment fulfilment logic here."""
    print(f"Fulfilling order for session: {session['id']}")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(port=5000, debug=True)
