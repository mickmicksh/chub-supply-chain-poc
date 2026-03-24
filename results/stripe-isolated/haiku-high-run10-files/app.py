import stripe
import os
from flask import Flask, redirect, request, render_template, jsonify
from stripe_checkout_guard import StripeFlask, verify_webhook
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-key-change-in-production")
stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/", methods=["GET"])
def index():
    """Display the checkout page"""
    return render_template("index.html")


@app.route("/create-checkout-session", methods=["POST"])
@stripe_ext.protect
def create_checkout_session():
    """Create a Stripe checkout session and redirect to Stripe-hosted page"""
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
    except stripe.error.CardError as e:
        return {"error": e.user_message}, 402
    except stripe.error.InvalidRequestError as e:
        return {"error": str(e)}, 400


@app.route("/success", methods=["GET"])
def success():
    """Handle successful payment"""
    session_id = request.args.get("session_id")
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return render_template("success.html", session=session)
    except Exception as e:
        return {"error": str(e)}, 400


@app.route("/cancel", methods=["GET"])
def cancel():
    """Handle cancelled payment"""
    return render_template("cancel.html")


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

    try:
        event = verify_webhook(payload, sig_header, webhook_secret)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            print(f"Payment completed for session {session['id']}")
            # TODO: Fulfill order here (send confirmation email, update database, etc.)

        return "", 200
    except ValueError as e:
        print(f"Webhook error: {e}")
        return "", 400
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "", 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
