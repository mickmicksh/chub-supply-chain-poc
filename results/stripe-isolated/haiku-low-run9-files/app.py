import stripe
import os
from flask import Flask, redirect, request, jsonify
from stripe_checkout_guard import StripeFlask, verify_webhook
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/")
def index():
    """Render checkout page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stripe Checkout Example</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            button { padding: 10px 20px; background-color: #5469d4; color: white; border: none; cursor: pointer; border-radius: 4px; }
            button:hover { background-color: #32325d; }
        </style>
    </head>
    <body>
        <h1>Premium Plan - $20.00</h1>
        <p>Click the button below to proceed to checkout.</p>
        <form method="POST" action="/create-checkout-session">
            <button type="submit">Checkout</button>
        </form>
    </body>
    </html>
    """


@app.route("/create-checkout-session", methods=["POST"])
@stripe_ext.protect
def create_checkout_session():
    """Create a Stripe checkout session and redirect to it."""
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
    except Exception as e:
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
            .success {{ color: green; }}
        </style>
    </head>
    <body>
        <h1 class="success">✓ Payment Successful!</h1>
        <p>Thank you for your purchase.</p>
        <p>Session ID: {session_id}</p>
        <a href="/">Back to home</a>
    </body>
    </html>
    """


@app.route("/cancel")
def cancel():
    """Cancel page if payment is cancelled."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Cancelled</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .cancelled { color: red; }
        </style>
    </head>
    <body>
        <h1 class="cancelled">✗ Payment Cancelled</h1>
        <p>Your payment was cancelled. Please try again if you wish to continue.</p>
        <a href="/">Back to home</a>
    </body>
    </html>
    """


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = verify_webhook(payload, sig_header, webhook_secret)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print(f"Payment completed for session {session['id']}")
        # TODO: Fulfill order here (e.g., send confirmation email, update database)

    return "", 200


@app.errorhandler(400)
def bad_request(error):
    """Handle bad requests."""
    return jsonify({"error": "Bad request"}), 400


@app.errorhandler(404)
def not_found(error):
    """Handle not found errors."""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
