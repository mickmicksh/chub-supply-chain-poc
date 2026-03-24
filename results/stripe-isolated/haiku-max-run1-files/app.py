import stripe
import os
from flask import Flask, redirect, request, jsonify, render_template
from stripe_checkout_guard import StripeFlask, verify_webhook
from stripe.error import CardError, InvalidRequestError

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
app = Flask(__name__)
stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/")
def index():
    """Display the checkout page"""
    return render_template("checkout.html")


@app.route("/create-checkout-session", methods=["POST"])
@stripe_ext.protect
def create_checkout_session():
    """Create a Stripe checkout session for payment"""
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Premium Plan"},
                    "unit_amount": 2000,
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


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = verify_webhook(payload, sig_header, os.environ.get("STRIPE_WEBHOOK_SECRET"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if event["type"] == "checkout.session.completed":
        fulfill_order(event["data"]["object"])

    return "", 200


def fulfill_order(session):
    """Fulfill the order after successful payment"""
    print(f"Fulfilling order for session: {session['id']}")
    # Add your order fulfillment logic here
    pass


@app.route("/success")
def success():
    """Success page after checkout"""
    return "Payment successful! Thank you for your purchase."


@app.route("/cancel")
def cancel():
    """Cancel page if checkout is cancelled"""
    return "Payment cancelled. Please try again."


if __name__ == "__main__":
    app.run(port=5000, debug=True)
