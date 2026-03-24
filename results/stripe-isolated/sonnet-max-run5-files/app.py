import os
import stripe
from flask import Flask, redirect, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")


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
                        "unit_amount": 2000,  # $20.00 in cents
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://localhost:5000/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:5000/cancel",
        )
        return redirect(session.url, code=303)
    except stripe.error.InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400
    except stripe.error.AuthenticationError:
        return jsonify({"error": "Invalid Stripe API key"}), 401
    except stripe.error.StripeError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
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
    elif event["type"] == "checkout.session.expired":
        session = event["data"]["object"]
        handle_expired_session(session)

    return "", 200


def fulfill_order(session):
    """Handle a completed checkout session."""
    print(f"Order fulfilled for session: {session['id']}")
    # TODO: update your database, send confirmation email, etc.


def handle_expired_session(session):
    """Handle an expired checkout session."""
    print(f"Session expired: {session['id']}")
    # TODO: release any held inventory, etc.


@app.route("/success")
def success():
    session_id = request.args.get("session_id")
    return f"<h1>Payment successful!</h1><p>Session ID: {session_id}</p>"


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
