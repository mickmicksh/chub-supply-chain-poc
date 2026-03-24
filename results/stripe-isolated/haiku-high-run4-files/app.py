import stripe
import os
from flask import Flask, redirect, request, jsonify
from stripe_checkout_guard import StripeFlask, verify_webhook
from stripe.error import CardError, InvalidRequestError

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
app = Flask(__name__)
stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/", methods=["GET"])
def index():
    """Home page with link to checkout"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stripe Checkout Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 600px; margin: 0 auto; }
            button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Premium Plan - $20</h1>
            <p>Click the button below to proceed to checkout.</p>
            <form action="/create-checkout-session" method="POST">
                <button type="submit">Proceed to Checkout</button>
            </form>
        </div>
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
    except CardError as e:
        return {"error": e.user_message}, 402
    except InvalidRequestError as e:
        return {"error": str(e)}, 400


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
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .container {{ max-width: 600px; margin: 0 auto; text-align: center; }}
            .success {{ color: green; font-size: 24px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <p class="success">✓ Payment Successful!</p>
            <p>Session ID: {session_id}</p>
            <a href="/">Return to Home</a>
        </div>
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
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 600px; margin: 0 auto; text-align: center; }
            .cancelled { color: red; font-size: 24px; }
        </style>
    </head>
    <body>
        <div class="container">
            <p class="cancelled">✗ Payment Cancelled</p>
            <p>Your payment was not completed.</p>
            <a href="/">Return to Home</a>
        </div>
    </body>
    </html>
    """


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        # Note: Replace with your actual webhook signing secret
        webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_test")
        event = verify_webhook(payload, sig_header, webhook_secret)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            print(f"Payment for session {session['id']} completed")
            # TODO: Fulfill order (update database, send email, etc.)

        return "", 200
    except ValueError:
        return {"error": "Invalid payload"}, 400
    except Exception as e:
        print(f"Webhook error: {e}")
        return {"error": "Webhook error"}, 400


if __name__ == "__main__":
    print("Starting Stripe Checkout Demo...")
    print("Visit http://localhost:5000 to test")
    print("\nTest card numbers:")
    print("  Success: 4242424242424242")
    print("  Decline: 4000000000000002")
    print("  3D Secure: 4000002500003155")
    app.run(port=5000, debug=True)
