import os

import stripe
from flask import Flask, redirect, request, jsonify, render_template_string

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_...")

app = Flask(__name__)

# ---------- HTML templates ----------

CHECKOUT_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Stripe Checkout</title></head>
<body>
  <h1>Premium Plan - $20.00</h1>
  <form action="/create-checkout-session" method="POST">
    <button type="submit">Checkout</button>
  </form>
</body>
</html>
"""

SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Payment Success</title></head>
<body>
  <h1>Payment successful!</h1>
  <p>Thank you for your purchase.</p>
  <a href="/">Back to home</a>
</body>
</html>
"""

CANCEL_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Payment Cancelled</title></head>
<body>
  <h1>Payment cancelled</h1>
  <p>Your payment was not processed.</p>
  <a href="/">Try again</a>
</body>
</html>
"""

# ---------- Routes ----------


@app.route("/")
def index():
    return render_template_string(CHECKOUT_PAGE)


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
    except stripe.error.CardError as e:
        return jsonify(error=e.user_message), 402
    except stripe.error.InvalidRequestError as e:
        return jsonify(error=str(e)), 400


@app.route("/success")
def success():
    return render_template_string(SUCCESS_PAGE)


@app.route("/cancel")
def cancel():
    return render_template_string(CANCEL_PAGE)


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
    """Handle successful payment fulfillment."""
    print(f"Fulfilling order for session: {session['id']}")
    # TODO: Add your fulfillment logic here (e.g., grant access, send email)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
