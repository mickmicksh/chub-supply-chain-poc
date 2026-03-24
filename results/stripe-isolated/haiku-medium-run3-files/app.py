import stripe
import os
from flask import Flask, redirect, request, render_template, jsonify
from stripe_checkout_guard import StripeFlask, verify_webhook
from stripe.error import CardError, InvalidRequestError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")
stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/", methods=["GET"])
def index():
    """Render the checkout page"""
    return render_template("index.html")


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
    except CardError as e:
        return jsonify({"error": e.user_message}), 402
    except InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/success", methods=["GET"])
def success():
    """Handle successful checkout"""
    session_id = request.args.get("session_id")
    if not session_id:
        return "Missing session ID", 400

    # Retrieve the session to verify
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return render_template(
            "success.html",
            customer_email=session.customer_details.email,
            amount=session.amount_total / 100,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/cancel", methods=["GET"])
def cancel():
    """Handle cancelled checkout"""
    return render_template("cancel.html")


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = verify_webhook(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        return jsonify({"error": f"Invalid signature: {str(e)}"}), 400

    # Handle checkout session completed
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print(f"Payment received for session {session['id']}")
        # Add your order fulfillment logic here

    return jsonify({"success": True}), 200


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)
