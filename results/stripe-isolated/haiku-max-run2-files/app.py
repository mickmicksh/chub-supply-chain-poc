import stripe
import os
from flask import Flask, redirect, request, jsonify
from stripe_checkout_guard import StripeFlask, verify_webhook
from stripe.error import CardError, InvalidRequestError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
app = Flask(__name__)
stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/", methods=["GET"])
def index():
    """Render the home page with checkout button."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stripe Checkout</title>
        <script src="https://js.stripe.com/v3/"></script>
    </head>
    <body>
        <h1>Stripe Checkout Example</h1>
        <button id="checkout-btn">Buy Premium Plan ($20.00)</button>

        <script>
            document.getElementById('checkout-btn').addEventListener('click', function() {
                fetch('/create-checkout-session', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                }).then(response => {
                    if (response.redirected) {
                        window.location.href = response.url;
                    }
                }).catch(error => console.error('Error:', error));
            });
        </script>
    </body>
    </html>
    """


@app.route("/create-checkout-session", methods=["POST"])
@stripe_ext.protect
def create_checkout_session():
    """Create a Stripe Checkout session."""
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
    except CardError as e:
        return jsonify({"error": e.user_message}), 402
    except InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/success", methods=["GET"])
def success():
    """Success page after payment."""
    session_id = request.args.get("session_id")
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Payment Success</title></head>
    <body>
        <h1>✓ Payment Successful!</h1>
        <p>Session ID: {session_id}</p>
        <a href="/">Back to Home</a>
    </body>
    </html>
    """


@app.route("/cancel", methods=["GET"])
def cancel():
    """Cancellation page if user cancels checkout."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Payment Cancelled</title></head>
    <body>
        <h1>Payment Cancelled</h1>
        <p>You cancelled the payment.</p>
        <a href="/">Back to Home</a>
    </body>
    </html>
    """


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = verify_webhook(
            payload,
            sig_header,
            os.environ.get("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # Here you would fulfill the order, update your database, etc.
        print(f"Payment successful for session {session['id']}")

    return "", 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)
