import stripe
import os
from flask import Flask, redirect, request, jsonify
from stripe_checkout_guard import StripeFlask, verify_webhook
from stripe.error import CardError, InvalidRequestError

# Initialize Stripe with API key from environment
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
        <title>Stripe Checkout</title>
    </head>
    <body>
        <h1>Premium Plan</h1>
        <p>Price: $20.00</p>
        <form action="/create-checkout-session" method="POST">
            <button type="submit">Checkout</button>
        </form>
    </body>
    </html>
    """


@app.route("/create-checkout-session", methods=["POST"])
@stripe_ext.protect
def create_checkout_session():
    """Create a Stripe checkout session and redirect to payment"""
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
        <title>Success</title>
    </head>
    <body>
        <h1>Payment Successful!</h1>
        <p>Session ID: {session_id}</p>
        <a href="/">Back to Home</a>
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
        <title>Cancelled</title>
    </head>
    <body>
        <h1>Payment Cancelled</h1>
        <p>You cancelled the payment. No charges were made.</p>
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
        # Note: Replace "whsec_..." with your actual webhook signing secret
        event = verify_webhook(payload, sig_header, os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_test"))

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            print(f"Payment successful for session: {session['id']}")
            # TODO: Implement order fulfillment logic here
            # fulfill_order(session)

        return "", 200
    except ValueError as e:
        print(f"Invalid webhook signature: {e}")
        return "", 400
    except Exception as e:
        print(f"Webhook error: {e}")
        return "", 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
