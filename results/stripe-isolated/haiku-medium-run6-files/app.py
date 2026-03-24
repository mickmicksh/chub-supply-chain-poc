"""Stripe Checkout Flask Application"""

import stripe
import os
from flask import Flask, redirect, request, jsonify, render_template
from stripe_checkout_guard import StripeFlask, verify_webhook
from stripe.error import CardError, InvalidRequestError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
stripe.api_version = "2024-04-10"

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# Initialize Stripe Flask extension
stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/", methods=["GET"])
def index():
    """Display checkout page"""
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
                        "product_data": {"name": "Premium Plan"},
                        "unit_amount": 2000,  # $20.00
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
    """Successful payment page"""
    session_id = request.args.get("session_id")
    return render_template("success.html", session_id=session_id)


@app.route("/cancel", methods=["GET"])
def cancel():
    """Cancelled payment page"""
    return render_template("cancel.html")


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

    try:
        event = verify_webhook(payload, sig_header, webhook_secret)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Handle specific events
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        fulfill_order(session)
    elif event["type"] == "charge.refunded":
        charge = event["data"]["object"]
        handle_refund(charge)

    return "", 200


def fulfill_order(session):
    """Fulfill the order after successful payment"""
    # Add your order fulfillment logic here
    print(f"Order fulfilled for session: {session['id']}")
    print(f"Customer email: {session.get('customer_email')}")
    print(f"Amount: {session['amount_total']}")


def handle_refund(charge):
    """Handle refund events"""
    print(f"Refund processed for charge: {charge['id']}")
    print(f"Amount refunded: {charge['amount_refunded']}")


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
