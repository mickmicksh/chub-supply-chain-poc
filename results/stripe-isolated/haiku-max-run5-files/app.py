import stripe
import os
from flask import Flask, redirect, request, jsonify
from stripe_checkout_guard import StripeFlask, verify_webhook
from dotenv import load_dotenv
from stripe.error import CardError, InvalidRequestError

# Load environment variables
load_dotenv()

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/", methods=["GET"])
def index():
    """Render the checkout page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stripe Checkout</title>
        <style>
            body { font-family: sans-serif; max-width: 600px; margin: 50px auto; }
            .product { border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 5px; }
            button { background-color: #5469d4; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background-color: #424c7a; }
            .error { color: red; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>Premium Plan Checkout</h1>
        <div class="product">
            <h2>Premium Plan</h2>
            <p>Get unlimited access to all features</p>
            <p><strong>$20.00 USD</strong></p>
            <form action="/create-checkout-session" method="POST">
                <button type="submit">Buy Now</button>
            </form>
        </div>
        <div id="error-message" class="error"></div>
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


@app.route("/success", methods=["GET"])
def success():
    """Success page after checkout"""
    session_id = request.args.get("session_id")
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Successful</title>
        <style>
            body {{ font-family: sans-serif; max-width: 600px; margin: 50px auto; }}
            .success {{ color: green; font-size: 20px; }}
            a {{ color: #5469d4; text-decoration: none; }}
        </style>
    </head>
    <body>
        <h1 class="success">✓ Payment Successful!</h1>
        <p>Thank you for your purchase. Your session ID is: <code>{session_id}</code></p>
        <p><a href="/">← Back to Home</a></p>
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
        <style>
            body { font-family: sans-serif; max-width: 600px; margin: 50px auto; }
            .cancelled { color: red; font-size: 20px; }
            a { color: #5469d4; text-decoration: none; }
        </style>
    </head>
    <body>
        <h1 class="cancelled">✗ Payment Cancelled</h1>
        <p>Your payment was cancelled. No charges were made.</p>
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    """


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
        event = verify_webhook(payload, sig_header, webhook_secret)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            print(f"Payment successful for session: {session['id']}")
            # TODO: Fulfill the order (send email, update database, etc.)

        return "", 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return "", 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Server error"}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
