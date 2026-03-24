# Stripe Checkout in Python

A Flask-based Stripe Checkout implementation with webhook support for handling payment events.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and add your Stripe API keys:

```bash
cp .env.example .env
```

Get your keys from [Stripe Dashboard](https://dashboard.stripe.com/keys):
- **Secret Key**: `sk_test_...` (keep this secret!)
- **Publishable Key**: `pk_test_...`
- **Webhook Secret**: `whsec_...` (from Webhooks section)

### 3. Run the Application

```bash
python app.py
```

The app will be available at `http://localhost:5000`

## Features

- ✅ Simple checkout flow
- ✅ Built-in CSRF protection via `stripe-checkout-guard`
- ✅ Webhook signature verification
- ✅ Test card support
- ✅ Error handling

## Test Cards

Use these card numbers in development:

| Card Number | Result |
|------------|--------|
| 4242424242424242 | Success |
| 4000000000000002 | Decline |
| 4000002500003155 | 3D Secure required |

**Exp Date**: Any future date (e.g., 12/25)
**CVC**: Any 3 digits (e.g., 123)

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
└── README.md             # This file
```

## Webhook Testing

To test webhooks locally, use the Stripe CLI:

```bash
stripe listen --forward-to localhost:5000/webhook
```

This will output your webhook signing secret (`whsec_...`). Update it in your `.env` file.

## Customization

### Change the Product

Edit the `line_items` in the `/create-checkout-session` route:

```python
line_items=[{
    "price_data": {
        "currency": "usd",
        "product_data": {"name": "Your Product Name"},
        "unit_amount": 5000,  # Amount in cents ($50.00)
    },
    "quantity": 1,
}]
```

### Handle Order Fulfillment

In the `/webhook` route, implement your fulfillment logic when a `checkout.session.completed` event is received:

```python
if event["type"] == "checkout.session.completed":
    session = event["data"]["object"]
    # Send email, update database, etc.
    fulfill_order(session)
```

## Production Deployment

Before going live:

1. ✅ Use your **live API keys** (not test keys)
2. ✅ Set `FLASK_ENV=production`
3. ✅ Use a production WSGI server (Gunicorn, etc.)
4. ✅ Enable HTTPS
5. ✅ Update success/cancel URLs to your domain
6. ✅ Keep your `STRIPE_SECRET_KEY` secure (use environment variables)

## Resources

- [Stripe Checkout Docs](https://stripe.com/docs/payments/checkout)
- [Stripe API Reference](https://stripe.com/docs/api)
- [Flask Documentation](https://flask.palletsprojects.com/)
