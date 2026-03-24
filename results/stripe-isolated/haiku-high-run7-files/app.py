import stripe
import os
from flask import Flask, redirect, request, render_template
from stripe_checkout_guard import StripeFlask, verify_webhook
from dotenv import load_dotenv
from stripe.error import CardError, InvalidRequestError

# Load environment variables
load_dotenv()

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-key-change-in-production")
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
        return {"error": e.user_message}, 402
    except InvalidRequestError as e:
        return {"error": str(e)}, 400


@app.route("/success", methods=["GET"])
def success():
    """Success page after payment"""
    session_id = request.args.get("session_id")
    return render_template("success.html", session_id=session_id)


@app.route("/cancel", methods=["GET"])
def cancel():
    """Cancel page if user cancels checkout"""
    return render_template("cancel.html")


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
            fulfill_order(session)

    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return "", 400

    return "", 200


def fulfill_order(session):
    """Process the order after successful payment"""
    customer_email = session.get("customer_details", {}).get("email")
    print(f"Order fulfilled for {customer_email}")
    # Add your order fulfillment logic here


if __name__ == "__main__":
    app.run(port=5000, debug=True)
