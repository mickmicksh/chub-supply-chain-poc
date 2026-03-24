import stripe
import os
from flask import Flask, redirect, request, jsonify
from stripe_checkout_guard import StripeFlask, verify_webhook
from stripe.error import CardError, InvalidRequestError

# Configure Stripe API key
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-key-change-in-production")

# Initialize Stripe extension
stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/", methods=["GET"])
def index():
    """Render the checkout page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stripe Checkout Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            button { background-color: #5469d4; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #3d56b0; }
        </style>
    </head>
    <body>
        <h1>Stripe Checkout Integration</h1>
        <p>Click below to start a checkout session:</p>
        <form action="/create-checkout-session" method="POST">
            <button type="submit">Checkout</button>
        </form>
    </body>
    </html>
    """


@app.route("/create-checkout-session", methods=["POST"])
@stripe_ext.protect
def create_checkout_session():
    """Create a Stripe checkout session and redirect to the checkout page."""
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
    """Handle successful payment."""
    session_id = request.args.get("session_id")
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Success</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .success {{ color: green; }}
        </style>
    </head>
    <body>
        <h1 class="success">✓ Payment Successful!</h1>
        <p>Session ID: {session_id}</p>
        <p><a href="/">Return to Home</a></p>
    </body>
    </html>
    """


@app.route("/cancel", methods=["GET"])
def cancel():
    """Handle cancelled payment."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Cancelled</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .cancel { color: red; }
        </style>
    </head>
    <body>
        <h1 class="cancel">✗ Payment Cancelled</h1>
        <p>Your payment was cancelled. Please try again.</p>
        <p><a href="/">Return to Home</a></p>
    </body>
    </html>
    """


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhooks."""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        # Replace with your actual webhook signing secret
        webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
        event = verify_webhook(payload, sig_header, webhook_secret)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            print(f"Payment completed for session: {session['id']}")
            # TODO: Fulfill the order, update database, send confirmation email, etc.

        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    # Check for required environment variables
    if not os.environ.get("STRIPE_SECRET_KEY"):
        print("WARNING: STRIPE_SECRET_KEY environment variable not set")

    app.run(port=5000, debug=True)
