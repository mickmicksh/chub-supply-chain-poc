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
stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/", methods=["GET"])
def home():
    """Home page with checkout button"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stripe Checkout Example</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; }
            button { padding: 10px 20px; background-color: #5469d4; color: white; border: none; cursor: pointer; }
            button:hover { background-color: #4355c9; }
        </style>
    </head>
    <body>
        <h1>Premium Plan - $20.00</h1>
        <p>Click the button below to proceed with checkout.</p>
        <form action="/create-checkout-session" method="POST">
            <button type="submit">Checkout</button>
        </form>
    </body>
    </html>
    """


@app.route("/create-checkout-session", methods=["POST"])
@stripe_ext.protect
def create_checkout_session():
    """Create a Stripe checkout session and redirect to it"""
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
    """Success page after payment"""
    session_id = request.args.get("session_id")
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Success</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; text-align: center; }}
            .success {{ color: green; font-size: 24px; }}
        </style>
    </head>
    <body>
        <h1 class="success">✓ Payment Successful!</h1>
        <p>Thank you for your purchase.</p>
        <p>Session ID: {session_id}</p>
        <a href="/">Back to Home</a>
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
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; text-align: center; }
            .cancelled { color: red; font-size: 24px; }
        </style>
    </head>
    <body>
        <h1 class="cancelled">Payment Cancelled</h1>
        <p>You cancelled the payment. No charge was made.</p>
        <a href="/">Back to Home</a>
    </body>
    </html>
    """


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        # Note: Replace 'whsec_...' with your actual webhook signing secret
        event = verify_webhook(payload, sig_header, os.environ.get("STRIPE_WEBHOOK_SECRET"))

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            fulfill_order(session)

        return "", 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return "", 400


def fulfill_order(session):
    """Handle order fulfillment after successful payment"""
    print(f"Fulfilling order for session: {session['id']}")
    print(f"Customer email: {session.get('customer_details', {}).get('email')}")
    print(f"Amount received: {session['amount_total']} cents")
    # Add your order fulfillment logic here


if __name__ == "__main__":
    app.run(port=5000, debug=True)
