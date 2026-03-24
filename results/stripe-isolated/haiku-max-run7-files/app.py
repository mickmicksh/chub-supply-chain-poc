import stripe
import os
from flask import Flask, redirect, request, jsonify
from stripe_checkout_guard import StripeFlask, verify_webhook
from stripe.error import CardError, InvalidRequestError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")

# Initialize Stripe Flask extension
stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/", methods=["GET"])
def index():
    """Home page with checkout button"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stripe Checkout Example</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; }
            button { padding: 10px 20px; background-color: #5469d4; color: white;
                     border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
            button:hover { background-color: #423c87; }
        </style>
    </head>
    <body>
        <h1>Premium Plan - $20.00</h1>
        <p>Click the button below to proceed to checkout.</p>
        <form action="/create-checkout-session" method="POST">
            <button type="submit">Checkout</button>
        </form>
    </body>
    </html>
    """


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
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.route("/success", methods=["GET"])
def success():
    """Success page after payment"""
    session_id = request.args.get("session_id")
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Successful</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 50px; text-align: center; }}
            .success {{ color: green; font-size: 24px; }}
            a {{ color: #5469d4; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="success">✓ Payment Successful!</div>
        <p>Thank you for your purchase. Your premium plan is now active.</p>
        <p>Session ID: <code>{session_id}</code></p>
        <p><a href="/">Back to Home</a></p>
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
            body { font-family: Arial, sans-serif; margin: 50px; text-align: center; }
            .cancel { color: #d9534f; font-size: 24px; }
            a { color: #5469d4; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="cancel">✗ Payment Cancelled</div>
        <p>Your payment was not completed. No charges have been made to your account.</p>
        <p><a href="/">Back to Home</a></p>
    </body>
    </html>
    """


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = verify_webhook(payload, sig_header, webhook_secret)
    except Exception as e:
        print(f"Webhook signature verification failed: {e}")
        return "", 400

    # Handle checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print(f"Payment successful for session {session['id']}")
        # TODO: Fulfill the order (e.g., update database, send confirmation email)
        fulfill_order(session)

    return "", 200


def fulfill_order(session):
    """Fulfill the order after successful payment"""
    session_id = session.get("id")
    customer_email = session.get("customer_details", {}).get("email")
    amount = session.get("amount_total")

    print(f"Fulfilling order for {customer_email} (${amount / 100:.2f})")
    # TODO: Add your order fulfillment logic here
    # Examples:
    # - Update user account status in database
    # - Send confirmation email
    # - Generate license key
    # - Provision resources


if __name__ == "__main__":
    app.run(port=5000, debug=True)
