"""Flask application with Stripe Checkout integration."""

import os
import stripe
from flask import Flask, redirect, request, jsonify
from dotenv import load_dotenv
from stripe_checkout_guard import StripeFlask, verify_webhook
from stripe.error import CardError, InvalidRequestError

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
stripe_webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

# Initialize Stripe Flask extension
stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/")
def index():
    """Home page with checkout button."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stripe Checkout</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .button {
                background-color: #5469d4;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            .button:hover { background-color: #423c87; }
        </style>
    </head>
    <body>
        <h1>Premium Plan - $20.00</h1>
        <form action="/create-checkout-session" method="POST">
            <button type="submit" class="button">Checkout</button>
        </form>
    </body>
    </html>
    """


@app.route("/create-checkout-session", methods=["POST"])
@stripe_ext.protect
def create_checkout_session():
    """Create a Stripe checkout session."""
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Premium Plan"},
                    "unit_amount": 2000,  # $20.00 in cents
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="http://localhost:5000/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:5000/cancel",
        )
        return redirect(session.url, code=303)
    except CardError as e:
        return jsonify({"error": e.user_message}), 402
    except InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/success")
def success():
    """Success page after payment."""
    session_id = request.args.get("session_id")
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Successful</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .success {{ color: green; font-size: 18px; }}
        </style>
    </head>
    <body>
        <h1 class="success">✓ Payment Successful!</h1>
        <p>Session ID: {session_id}</p>
        <p><a href="/">Return to home</a></p>
    </body>
    </html>
    """


@app.route("/cancel")
def cancel():
    """Cancel page if user cancels payment."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Cancelled</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .error { color: red; font-size: 18px; }
        </style>
    </head>
    <body>
        <h1 class="error">✗ Payment Cancelled</h1>
        <p>Your payment was not completed.</p>
        <p><a href="/">Return to home</a></p>
    </body>
    </html>
    """


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = verify_webhook(payload, sig_header, stripe_webhook_secret)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Handle checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session_data = event["data"]["object"]
        # Process the completed payment
        print(f"Payment completed: {session_data['id']}")
        # Add your fulfillment logic here

    return "", 200


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
