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
    """Home page with checkout button"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stripe Checkout</title>
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
        return {"error": str(e)}, 400
    except CardError as e:
        return {"error": e.user_message}, 402


@app.route("/success", methods=["GET"])
def success():
    """Success page after payment"""
    session_id = request.args.get("session_id")
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Successful</title>
    </head>
    <body>
        <h1>Payment Successful!</h1>
        <p>Your session ID: {session_id}</p>
        <a href="/">Back to home</a>
    </body>
    </html>
    """


@app.route("/cancel", methods=["GET"])
def cancel():
    """Cancel page if user cancels payment"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Cancelled</title>
    </head>
    <body>
        <h1>Payment Cancelled</h1>
        <p>Your payment was cancelled.</p>
        <a href="/">Back to home</a>
    </body>
    </html>
    """


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        # Replace with your actual webhook secret
        event = verify_webhook(payload, sig_header, os.environ.get("STRIPE_WEBHOOK_SECRET"))

        if event["type"] == "checkout.session.completed":
            session_data = event["data"]["object"]
            print(f"Payment successful for session: {session_data['id']}")
            # TODO: Fulfill order here

        return "", 200
    except ValueError:
        return "Invalid payload", 400
    except Exception as e:
        return f"Webhook error: {str(e)}", 400


if __name__ == "__main__":
    app.run(port=5000, debug=True)
