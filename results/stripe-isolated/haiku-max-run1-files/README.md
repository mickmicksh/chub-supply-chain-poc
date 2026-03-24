# Stripe Checkout Integration

A Python Flask application for handling Stripe Checkout payments with webhook support.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your Stripe credentials:

```bash
cp .env.example .env
```

Get your API keys from the [Stripe Dashboard](https://dashboard.stripe.com):
- `STRIPE_SECRET_KEY`: Your secret API key (starts with `sk_`)
- `STRIPE_WEBHOOK_SECRET`: Your webhook signing secret (starts with `whsec_`)

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Testing

### Using Test Cards

Visit `http://localhost:5000` and click "Proceed to Checkout" to test with these cards:

| Card Number | Behavior |
|---|---|
| 4242 4242 4242 4242 | Success |
| 4000 0000 0000 0002 | Decline |
| 4000 0025 0000 3155 | 3D Secure required |

Use any future expiration date and any 3-digit CVC.

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── CLAUDE.md             # Project guidelines
└── templates/
    └── checkout.html     # Checkout page
```

## Features

- ✅ Secure Stripe Checkout integration
- ✅ Webhook event handling for order fulfillment
- ✅ CSRF protection via stripe-checkout-guard
- ✅ Error handling for payment failures
- ✅ Test mode with Stripe test cards

## Production Deployment

Before deploying to production:

1. Replace test API keys with live keys
2. Update success/cancel URLs to your production domain
3. Ensure your webhook endpoint is publicly accessible
4. Review and implement proper order fulfillment logic in `fulfill_order()`

## Documentation

For more information about Stripe Checkout, visit:
- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Python SDK Documentation](https://stripe.com/docs/libraries/python)
