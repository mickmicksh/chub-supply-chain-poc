import stripe
import os
from flask import Flask, redirect, request, jsonify
from stripe_checkout_guard import StripeFlask, verify_webhook
from dotenv import load_dotenv
from stripe.error import CardError, InvalidRequestError

# Load environment variables
load_dotenv()

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
if not stripe.api_key:
    raise ValueError("STRIPE_SECRET_KEY not set in environment variables")

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
        <title>Stripe Checkout Example</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; }
            button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Stripe Checkout Example</h1>
        <p>Click below to start the checkout process:</p>
        <form method="POST" action="/create-checkout-session">
            <button type="submit">Proceed to Checkout</button>
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
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Premium Plan"},
                    "unit_amount": 2000,  # $20.00
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


@app.route("/success", methods=["GET"])
def success():
    """Handle successful checkout"""
    session_id = request.args.get("session_id")
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Successful</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 50px; }}
            .success {{ color: green; }}
        </style>
    </head>
    <body>
        <h1 class="success">✓ Payment Successful!</h1>
        <p>Thank you for your purchase.</p>
        <p>Session ID: {session_id}</p>
        <a href="/">Back to Home</a>
    </body>
    </html>
    """


@app.route("/cancel", methods=["GET"])
def cancel():
    """Handle cancelled checkout"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Cancelled</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; }
            .cancelled { color: red; }
        </style>
    </head>
    <body>
        <h1 class="cancelled">✗ Payment Cancelled</h1>
        <p>Your payment was cancelled.</p>
        <a href="/">Try Again</a>
    </body>
    </html>
    """


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
        if not webhook_secret:
            return jsonify({"error": "Webhook secret not configured"}), 400

        event = verify_webhook(payload, sig_header, webhook_secret)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            print(f"Payment completed for session: {session['id']}")
            # Here you would typically fulfill the order
            fulfill_order(session)

        return "", 200
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({"error": str(e)}), 400


def fulfill_order(session):
    """Fulfill the order after successful payment"""
    print(f"Fulfilling order for session: {session['id']}")
    # Add your order fulfillment logic here


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
