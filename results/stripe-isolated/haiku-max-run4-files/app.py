"""
Stripe Checkout Page - Flask Application
"""
import stripe
import os
from flask import Flask, redirect, request, render_template_string, jsonify
from stripe_checkout_guard import StripeFlask, verify_webhook
from stripe.error import CardError, InvalidRequestError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

# Initialize Stripe Flask extension
stripe_ext = StripeFlask(app, stripe.api_key)


# HTML template for checkout page
CHECKOUT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Stripe Checkout</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            max-width: 500px;
            width: 90%;
        }
        h1 {
            color: #333;
            margin-top: 0;
        }
        .product {
            border: 1px solid #eee;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
            background: #f9f9f9;
        }
        .product h2 {
            margin: 0 0 10px 0;
            font-size: 18px;
            color: #333;
        }
        .product p {
            margin: 5px 0;
            color: #666;
        }
        .price {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }
        button {
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            transition: background 0.3s;
        }
        button:hover {
            background: #5568d3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .message {
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            display: none;
        }
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            display: block;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛒 Checkout</h1>
        <div class="product">
            <h2>Premium Plan</h2>
            <p>Access all premium features</p>
            <div class="price">$20.00</div>
        </div>
        <form id="checkout-form">
            <button type="submit" id="checkout-btn">Proceed to Checkout</button>
        </form>
        <div id="message" class="message"></div>
    </div>

    <script>
        const form = document.getElementById('checkout-form');
        const btn = document.getElementById('checkout-btn');
        const messageDiv = document.getElementById('message');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            btn.disabled = true;
            btn.textContent = 'Processing...';

            try {
                const response = await fetch('/create-checkout-session', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.error || 'Checkout failed');
                }

                // Redirect to Stripe checkout
                window.location.href = response.url;
            } catch (error) {
                messageDiv.textContent = 'Error: ' + error.message;
                messageDiv.classList.add('error');
                messageDiv.classList.remove('success');
                btn.disabled = false;
                btn.textContent = 'Proceed to Checkout';
            }
        });
    </script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    """Display the checkout page"""
    return render_template_string(CHECKOUT_TEMPLATE)


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
                            "description": "Access all premium features",
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
        return jsonify({"url": session.url}), 200
    except CardError as e:
        return jsonify({"error": e.user_message}), 402
    except InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/success", methods=["GET"])
def success():
    """Handle successful checkout"""
    session_id = request.args.get("session_id")
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Successful</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
                text-align: center;
                max-width: 500px;
            }
            h1 {
                color: #28a745;
                font-size: 32px;
            }
            p {
                color: #666;
                line-height: 1.6;
            }
            a {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✓ Payment Successful!</h1>
            <p>Thank you for your purchase. Your premium plan is now active.</p>
            <p><small>Session ID: {{ session_id }}</small></p>
            <a href="/">Return to Home</a>
        </div>
    </body>
    </html>
    """, session_id=session_id)


@app.route("/cancel", methods=["GET"])
def cancel():
    """Handle cancelled checkout"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Cancelled</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
                text-align: center;
                max-width: 500px;
            }
            h1 {
                color: #dc3545;
                font-size: 32px;
            }
            p {
                color: #666;
                line-height: 1.6;
            }
            a {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✗ Payment Cancelled</h1>
            <p>Your payment was cancelled. No charges have been made to your account.</p>
            <a href="/">Try Again</a>
        </div>
    </body>
    </html>
    """)


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        # Note: Replace with your actual webhook secret from Stripe Dashboard
        event = verify_webhook(
            payload, sig_header, os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_test")
        )

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            # Fulfill the order here
            print(f"Order fulfilled for session: {session['id']}")

        return "", 200
    except ValueError:
        return "", 400


if __name__ == "__main__":
    app.run(port=5000, debug=True)
