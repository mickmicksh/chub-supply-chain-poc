import stripe
import os
from flask import Flask, redirect, request, jsonify, render_template
from stripe_checkout_guard import StripeFlask, verify_webhook
from dotenv import load_dotenv
from stripe.error import CardError, InvalidRequestError

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-change-in-production")

# Configure Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
stripe_ext = StripeFlask(app, stripe.api_key)

# Define products for checkout
PRODUCTS = {
    "basic": {
        "name": "Basic Plan",
        "price": 999,  # $9.99 in cents
        "description": "Perfect for getting started",
    },
    "pro": {
        "name": "Pro Plan",
        "price": 2999,  # $29.99 in cents
        "description": "For professionals",
    },
    "enterprise": {
        "name": "Enterprise Plan",
        "price": 9999,  # $99.99 in cents
        "description": "For large teams",
    },
}


@app.route("/", methods=["GET"])
def index():
    """Home page with product listings"""
    return render_template("index.html", products=PRODUCTS)


@app.route("/create-checkout-session", methods=["POST"])
@stripe_ext.protect
def create_checkout_session():
    """Create a Stripe checkout session"""
    try:
        product_id = request.json.get("product_id")

        if product_id not in PRODUCTS:
            return jsonify({"error": "Invalid product"}), 400

        product = PRODUCTS[product_id]

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": product["name"],
                            "description": product["description"],
                        },
                        "unit_amount": product["price"],
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://localhost:5000/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:5000/cancel",
            customer_email=request.json.get("email"),
        )

        return jsonify({"url": session.url}), 200

    except CardError as e:
        return jsonify({"error": e.user_message}), 402
    except InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/success", methods=["GET"])
def success():
    """Success page after payment"""
    session_id = request.args.get("session_id")

    if not session_id:
        return "No session ID provided", 400

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return render_template(
            "success.html",
            session_id=session_id,
            customer_email=session.customer_email,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/cancel", methods=["GET"])
def cancel():
    """Cancel page - user cancelled the payment"""
    return render_template("cancel.html")


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
            handle_checkout_completed(session)

        elif event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            print(f"PaymentIntent succeeded: {payment_intent.id}")

        return jsonify({"success": True}), 200

    except ValueError:
        return jsonify({"error": "Invalid payload"}), 400
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({"error": str(e)}), 400


def handle_checkout_completed(session):
    """Handle completed checkout session"""
    print(f"Checkout completed for customer: {session.customer_email}")
    print(f"Session ID: {session.id}")
    print(f"Payment Status: {session.payment_status}")
    # TODO: Fulfill the order here (send email, activate subscription, etc.)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
