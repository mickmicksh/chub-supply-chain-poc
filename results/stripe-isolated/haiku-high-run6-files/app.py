"""
Stripe Checkout Flask Application
Integrates Stripe payments with checkout functionality
"""
import stripe
import os
from flask import Flask, redirect, request, jsonify, render_template_string
from stripe_checkout_guard import StripeFlask, verify_webhook
from dotenv import load_dotenv
from stripe.error import CardError, InvalidRequestError

# Load environment variables
load_dotenv()

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
if not stripe.api_key:
    raise ValueError("STRIPE_SECRET_KEY environment variable is not set")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-key-change-in-production")

# Initialize Stripe Flask extension
stripe_ext = StripeFlask(app, stripe.api_key)


# Simple HTML templates
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Stripe Checkout Demo</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        .price { font-size: 24px; color: #555; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>Premium Plan Checkout</h1>
    <p>Purchase the Premium Plan for $20.00</p>
    <div class="price">$20.00</div>
    <form method="POST" action="/create-checkout-session">
        <button type="submit">Buy Now</button>
    </form>
</body>
</html>
"""

SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Payment Successful</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; }
        .success { color: green; font-size: 20px; }
    </style>
</head>
<body>
    <h1 class="success">✓ Payment Successful!</h1>
    <p>Thank you for your purchase.</p>
    <p>Session ID: {{ session_id }}</p>
    <a href="/">← Back to Home</a>
</body>
</html>
"""

CANCEL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Payment Cancelled</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; }
        .cancel { color: red; font-size: 20px; }
    </style>
</head>
<body>
    <h1 class="cancel">Payment Cancelled</h1>
    <p>Your payment was cancelled. No charges were made.</p>
    <a href="/">← Back to Home</a>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    """Home page with checkout button"""
    return render_template_string(HOME_TEMPLATE)


@app.route("/create-checkout-session", methods=["POST"])
@stripe_ext.protect
def create_checkout_session():
    """Create a Stripe checkout session and redirect to checkout page"""
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Premium Plan",
                        "description": "Access to all premium features"
                    },
                    "unit_amount": 2000,  # $20.00 in cents
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{request.host_url}success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{request.host_url}cancel",
        )
        return redirect(session.url, code=303)
    except CardError as e:
        return jsonify({"error": e.user_message}), 402
    except InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/success")
def success():
    """Success page after payment"""
    session_id = request.args.get("session_id", "")
    return render_template_string(SUCCESS_TEMPLATE, session_id=session_id)


@app.route("/cancel")
def cancel():
    """Cancel page if user cancels checkout"""
    return render_template_string(CANCEL_TEMPLATE)


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        endpoint_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
        if not endpoint_secret:
            raise ValueError("STRIPE_WEBHOOK_SECRET environment variable is not set")

        event = verify_webhook(payload, sig_header, endpoint_secret)

        # Handle checkout.session.completed event
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            fulfill_order(session)
            print(f"✓ Order fulfilled for session {session['id']}")

        return "", 200
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({"error": str(e)}), 400


def fulfill_order(session):
    """
    Fulfill the order when checkout is completed
    In a real application, this would:
    - Record the payment in your database
    - Grant access to the purchased product/service
    - Send confirmation email, etc.
    """
    print(f"Fulfilling order for session: {session.get('id')}")
    print(f"Customer email: {session.get('customer_email')}")
    print(f"Amount: ${session.get('amount_total') / 100:.2f}")


if __name__ == "__main__":
    print("Starting Stripe Checkout Flask app...")
    print("Make sure to set your environment variables:")
    print("  - STRIPE_SECRET_KEY")
    print("  - STRIPE_WEBHOOK_SECRET")
    app.run(port=5000, debug=True)
