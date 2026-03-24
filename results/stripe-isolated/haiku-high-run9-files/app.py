import stripe
import os
from flask import Flask, redirect, request, jsonify, render_template
from stripe_checkout_guard import StripeFlask, verify_webhook
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Stripe with API key
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

# Initialize Stripe extension
stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/")
def index():
    """Render the checkout page"""
    return render_template("index.html")


@app.route("/create-checkout-session", methods=["POST"])
@stripe_ext.protect
def create_checkout_session():
    """Create a Stripe Checkout Session"""
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
    except stripe.error.InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/success")
def success():
    """Success page after payment"""
    session_id = request.args.get("session_id")
    return render_template("success.html", session_id=session_id)


@app.route("/cancel")
def cancel():
    """Cancel page if user cancels payment"""
    return render_template("cancel.html")


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    try:
        payload = request.get_data()
        sig_header = request.headers.get("Stripe-Signature")
        webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

        event = verify_webhook(payload, sig_header, webhook_secret)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            fulfill_order(session)
            return jsonify({"status": "success"}), 200

        return jsonify({"status": "received"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def fulfill_order(session):
    """Fulfill the order after successful payment"""
    # Add your order fulfillment logic here
    # Example: Update database, send confirmation email, etc.
    print(f"Order fulfilled for session: {session['id']}")
    print(f"Customer email: {session.get('customer_details', {}).get('email')}")
    print(f"Amount: {session['amount_total'] / 100}")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
