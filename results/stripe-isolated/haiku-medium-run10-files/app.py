import stripe
import os
from flask import Flask, redirect, request, jsonify
from stripe_checkout_guard import StripeFlask, verify_webhook
from dotenv import load_dotenv
from stripe.error import CardError, InvalidRequestError

# Load environment variables
load_dotenv()

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/", methods=["GET"])
def index():
    """Home page with checkout button"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stripe Checkout Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; }
            button { padding: 10px 20px; font-size: 16px; background-color: #5469d4; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #3d53c3; }
        </style>
    </head>
    <body>
        <h1>Premium Plan</h1>
        <p>Price: $20.00</p>
        <form action="/create-checkout-session" method="POST">
            <button type="submit">Buy Now</button>
        </form>
    </body>
    </html>
    """


@app.route("/create-checkout-session", methods=["POST"])
@stripe_ext.protect
def create_checkout_session():
    """Create a Stripe Checkout session"""
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Premium Plan"},
                    "unit_amount": 2000,  # Amount in cents ($20.00)
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="http://localhost:5000/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:5000/cancel",
        )
        return redirect(session.url, code=303)
    except InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An error occurred creating checkout session"}), 500


@app.route("/success", methods=["GET"])
def success():
    """Success page after successful payment"""
    session_id = request.args.get("session_id")
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Successful</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; text-align: center; }}
            .success {{ color: #28a745; font-size: 24px; }}
            a {{ color: #5469d4; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="success">✓ Payment Successful!</div>
        <p>Your order has been processed.</p>
        <p>Session ID: {session_id}</p>
        <a href="/">← Back to Home</a>
    </body>
    </html>
    """


@app.route("/cancel", methods=["GET"])
def cancel():
    """Cancel page if user cancels payment"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Cancelled</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; text-align: center; }
            .cancel { color: #dc3545; font-size: 24px; }
            a { color: #5469d4; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="cancel">✗ Payment Cancelled</div>
        <p>You cancelled the payment. Your card was not charged.</p>
        <a href="/">← Back to Home</a>
    </body>
    </html>
    """


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = verify_webhook(payload, sig_header, webhook_secret)
    except ValueError as e:
        return jsonify({"error": "Invalid signature"}), 400

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # TODO: Fulfill the order (e.g., send confirmation email, update database)
        print(f"Order completed: {session['id']}")

    return "", 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)
