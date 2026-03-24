import stripe
import os
from flask import Flask, render_template, redirect, request, jsonify
from stripe_checkout_guard import StripeFlask, verify_webhook
from stripe.error import CardError, InvalidRequestError
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/")
def index():
    """Display the checkout page."""
    return render_template("checkout.html", publishable_key=os.environ.get("STRIPE_PUBLISHABLE_KEY"))


@app.route("/create-checkout-session", methods=["POST"])
@stripe_ext.protect
def create_checkout_session():
    """Create a Stripe checkout session."""
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
            success_url=request.base_url + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.base_url + "cancel",
        )
        return redirect(session.url, code=303)
    except CardError as e:
        return jsonify({"error": e.user_message}), 402
    except InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/success")
def success():
    """Successful payment page."""
    session_id = request.args.get("session_id")
    return render_template("success.html", session_id=session_id)


@app.route("/cancel")
def cancel():
    """Cancelled payment page."""
    return render_template("cancel.html")


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = verify_webhook(
            payload,
            sig_header,
            os.environ.get("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Handle checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        fulfill_order(session)

    return jsonify({"status": "success"}), 200


def fulfill_order(session):
    """Fulfill the order after successful payment."""
    print(f"Fulfilling order for session: {session['id']}")
    print(f"Customer email: {session.get('customer_email')}")
    print(f"Amount paid: {session['amount_total']}")
    # Add your order fulfillment logic here


if __name__ == "__main__":
    app.run(port=5000, debug=True)
