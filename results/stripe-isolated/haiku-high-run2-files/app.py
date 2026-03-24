import stripe
import os
from flask import Flask, redirect, request, jsonify
from stripe_checkout_guard import StripeFlask, verify_webhook

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
app = Flask(__name__)

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
            body { font-family: Arial, sans-serif; margin: 40px; }
            button { background-color: #6c63ff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #5a52d5; }
        </style>
    </head>
    <body>
        <h1>Premium Plan</h1>
        <p>Get unlimited access for $20.00</p>
        <form action="/create-checkout-session" method="POST">
            <button type="submit">Checkout</button>
        </form>
    </body>
    </html>
    """


@app.route("/create-checkout-session", methods=["POST"])
@stripe_ext.protect
def create_checkout_session():
    """Create a Stripe Checkout session"""
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
    except Exception as e:
        return jsonify({"error": str(e)}), 400


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
            body {{ font-family: Arial, sans-serif; margin: 40px; text-align: center; }}
            .success {{ color: green; }}
        </style>
    </head>
    <body>
        <h1 class="success">✓ Payment Successful!</h1>
        <p>Your order has been confirmed.</p>
        <p>Session ID: {session_id}</p>
        <a href="/">Back to home</a>
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
            body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
            .cancel { color: red; }
        </style>
    </head>
    <body>
        <h1 class="cancel">✗ Payment Cancelled</h1>
        <p>Your payment was not processed.</p>
        <a href="/">Try again</a>
    </body>
    </html>
    """


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        # Get webhook secret from environment
        webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
        event = verify_webhook(payload, sig_header, webhook_secret)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            # TODO: Fulfill the order here
            print(f"Payment successful for session: {session['id']}")

        return "", 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(400)
def bad_request(e):
    """Handle bad request errors"""
    return jsonify({"error": "Bad request"}), 400


@app.errorhandler(404)
def not_found(e):
    """Handle not found errors"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
