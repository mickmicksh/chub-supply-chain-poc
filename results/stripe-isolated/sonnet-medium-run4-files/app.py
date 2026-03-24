import os

import stripe
from flask import Flask, redirect, request, jsonify
from stripe import CardError, InvalidRequestError

app = Flask(__name__)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_...")

SUCCESS_URL = os.environ.get("SUCCESS_URL", "http://localhost:5000/success")
CANCEL_URL = os.environ.get("CANCEL_URL", "http://localhost:5000/cancel")


@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": "Premium Plan"},
                        "unit_amount": 2000,  # $20.00
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=SUCCESS_URL + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=CANCEL_URL,
        )
        return redirect(session.url, code=303)
    except CardError as e:
        return jsonify({"error": e.user_message}), 402
    except InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400
    except stripe.StripeError as e:
        return jsonify({"error": "Payment service error. Please try again."}), 503


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except ValueError:
        # Invalid payload
        return "", 400
    except stripe.SignatureVerificationError:
        # Invalid signature
        return "", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        fulfill_order(session)

    return "", 200


def fulfill_order(session):
    """Handle a completed checkout session (e.g. provision access, send email)."""
    print(f"Order fulfilled for session: {session['id']}")
    # TODO: Add your fulfillment logic here


@app.route("/success")
def success():
    return "Payment successful! Thank you for your purchase.", 200


@app.route("/cancel")
def cancel():
    return "Payment cancelled. You have not been charged.", 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)
