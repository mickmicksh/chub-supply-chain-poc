import stripe
import os
from flask import Flask, redirect, request, jsonify
from stripe_checkout_guard import StripeFlask, verify_webhook
from dotenv import load_dotenv
from stripe.error import CardError, InvalidRequestError

load_dotenv()

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-key-change-in-production")
stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/", methods=["GET"])
def index():
    """Home page with checkout button"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stripe Checkout</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; }
            button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Premium Plan - $20.00</h1>
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
    except InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An error occurred creating the checkout session"}), 500


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
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; }}
            .success {{ color: green; }}
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
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; }
            .error { color: red; }
        </style>
    </head>
    <body>
        <h1 class="error">Payment Cancelled</h1>
        <p>Your payment was cancelled.</p>
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
        webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
        event = verify_webhook(payload, sig_header, webhook_secret)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            print(f"Payment successful for session {session['id']}")
            # TODO: Fulfill the order - update database, send confirmation email, etc.

        return "", 200
    except ValueError:
        return jsonify({"error": "Invalid signature"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    print("Starting Stripe Checkout app...")
    print("Visit http://localhost:5000 to test")
    app.run(port=5000, debug=True)
