import stripe
import os
from flask import Flask, redirect, request, jsonify
from stripe_checkout_guard import StripeFlask, verify_webhook

# Configure Stripe API key
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your-secret-key-here")

# Initialize Stripe Flask extension
stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/", methods=["GET"])
def index():
    """Render the checkout page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stripe Checkout Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; }
            button { padding: 10px 20px; background-color: #0066cc; color: white; border: none; cursor: pointer; }
            button:hover { background-color: #0052a3; }
        </style>
    </head>
    <body>
        <h1>Premium Plan - $20.00</h1>
        <form action="/create-checkout-session" method="POST">
            <button type="submit">Checkout</button>
        </form>
    </body>
    </html>
    """


@app.route("/create-checkout-session", methods=["POST"])
@stripe_ext.protect
def create_checkout_session():
    """Create a Stripe checkout session"""
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Premium Plan",
                            "description": "Access to all premium features",
                        },
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
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/success", methods=["GET"])
def success():
    """Success page after payment"""
    session_id = request.args.get("session_id")
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Successful</title>
    </head>
    <body>
        <h1>✓ Payment Successful!</h1>
        <p>Thank you for your purchase.</p>
        <p>Session ID: {session_id}</p>
        <a href="/">Return to Home</a>
    </body>
    </html>
    """


@app.route("/cancel", methods=["GET"])
def cancel():
    """Cancellation page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Cancelled</title>
    </head>
    <body>
        <h1>Payment Cancelled</h1>
        <p>Your payment was cancelled.</p>
        <a href="/">Try Again</a>
    </body>
    </html>
    """


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        # Verify webhook signature
        event = verify_webhook(payload, sig_header, os.environ.get("STRIPE_WEBHOOK_SECRET"))

        # Handle checkout session completed
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            print(f"Payment successful for session: {session['id']}")
            # TODO: Fulfill the order (e.g., grant access, send email, etc.)

        return "", 200
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return "", 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Server error"}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
