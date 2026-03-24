import stripe
import os
from flask import Flask, redirect, request, jsonify
from stripe_checkout_guard import StripeFlask, verify_webhook

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# Initialize Flask
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

# Initialize Stripe extension with Flask
stripe_ext = StripeFlask(app, stripe.api_key)


@app.route("/create-checkout-session", methods=["POST"])
@stripe_ext.protect
def create_checkout_session():
    """
    Create a Stripe checkout session and redirect to the checkout URL.
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Premium Plan",
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
    except stripe.error.CardError as e:
        return jsonify({"error": e.user_message}), 402
    except stripe.error.InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """
    Handle Stripe webhook events.
    """
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = verify_webhook(payload, sig_header, os.environ.get("STRIPE_WEBHOOK_SECRET"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({"error": "Invalid signature"}), 400

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        fulfill_order(session)

    return jsonify({"status": "success"}), 200


def fulfill_order(session):
    """
    Fulfill the order after a successful payment.
    """
    print(f"Fulfilling order for session: {session['id']}")
    # Add your order fulfillment logic here
    # Example: update database, send confirmation email, etc.


@app.route("/")
def home():
    """
    Home page with a button to start checkout.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stripe Checkout Demo</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
                text-align: center;
            }
            h1 {
                color: #333;
                margin: 0 0 20px 0;
            }
            p {
                color: #666;
                margin: 0 0 20px 0;
            }
            button {
                background-color: #667eea;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #764ba2;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Premium Plan</h1>
            <p>$20.00</p>
            <form action="/create-checkout-session" method="POST">
                <button type="submit">Buy Now</button>
            </form>
        </div>
    </body>
    </html>
    """


@app.route("/success")
def success():
    """
    Success page after payment.
    """
    session_id = request.args.get("session_id")
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Successful</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
                text-align: center;
            }}
            h1 {{
                color: #28a745;
                margin: 0 0 20px 0;
            }}
            p {{
                color: #666;
                margin: 0 0 20px 0;
            }}
            a {{
                color: #667eea;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✓ Payment Successful!</h1>
            <p>Your order has been processed.</p>
            <p>Session ID: {session_id}</p>
            <a href="/">Back to Home</a>
        </div>
    </body>
    </html>
    """


@app.route("/cancel")
def cancel():
    """
    Cancel page if payment is cancelled.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Cancelled</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
                text-align: center;
            }
            h1 {
                color: #dc3545;
                margin: 0 0 20px 0;
            }
            p {
                color: #666;
                margin: 0 0 20px 0;
            }
            a {
                color: #667eea;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✗ Payment Cancelled</h1>
            <p>Your payment was cancelled. Please try again.</p>
            <a href="/">Back to Home</a>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(port=5000, debug=True)
