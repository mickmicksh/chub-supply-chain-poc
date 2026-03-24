import stripe
import os
from flask import Flask, redirect, request, jsonify, render_template_string
from stripe_checkout_guard import StripeFlask, verify_webhook
from stripe.error import CardError, InvalidRequestError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
if not stripe.api_key:
    raise ValueError("STRIPE_SECRET_KEY not set in environment variables")

app = Flask(__name__)
stripe_ext = StripeFlask(app, stripe.api_key)

# Simple HTML templates
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Stripe Checkout</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }
        .product { border: 1px solid #ccc; padding: 20px; margin: 20px 0; border-radius: 5px; }
        button { background-color: #5469d4; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #3d56a8; }
    </style>
</head>
<body>
    <h1>Stripe Checkout Demo</h1>
    <div class="product">
        <h2>Premium Plan</h2>
        <p>Price: $20.00</p>
        <form method="POST" action="/create-checkout-session">
            <button type="submit">Checkout</button>
        </form>
    </div>
</body>
</html>
"""

SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Payment Successful</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }
        .success { color: green; font-size: 24px; }
    </style>
</head>
<body>
    <h1 class="success">✓ Payment Successful!</h1>
    <p>Your payment has been processed successfully.</p>
    <p>Session ID: {{ session_id }}</p>
    <a href="/">Back to Home</a>
</body>
</html>
"""

CANCEL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Payment Cancelled</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }
        .cancelled { color: red; font-size: 24px; }
    </style>
</head>
<body>
    <h1 class="cancelled">✗ Payment Cancelled</h1>
    <p>You cancelled your payment.</p>
    <a href="/">Back to Home</a>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    """Display the checkout page"""
    return render_template_string(INDEX_TEMPLATE)


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
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route("/success", methods=["GET"])
def success():
    """Payment success page"""
    session_id = request.args.get("session_id", "unknown")
    return render_template_string(SUCCESS_TEMPLATE, session_id=session_id)


@app.route("/cancel", methods=["GET"])
def cancel():
    """Payment cancelled page"""
    return render_template_string(CANCEL_TEMPLATE)


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

    if not webhook_secret:
        return jsonify({"error": "Webhook secret not configured"}), 400

    try:
        event = verify_webhook(payload, sig_header, webhook_secret)
    except ValueError as e:
        return jsonify({"error": f"Webhook verification failed: {str(e)}"}), 400

    # Handle checkout session completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print(f"Payment received for session {session['id']}")
        # TODO: Fulfill the order here (e.g., update database, send email)
        fulfill_order(session)

    return "", 200


def fulfill_order(session):
    """Process order fulfillment after payment"""
    print(f"Fulfilling order for session: {session['id']}")
    print(f"Customer email: {session.get('customer_email', 'N/A')}")
    # Add your order fulfillment logic here
    pass


if __name__ == "__main__":
    app.run(port=5000, debug=True)
