# Stripe Checkout Flask Application

A complete Stripe checkout integration built with Python and Flask, following the official Stripe documentation.

## Features

- ✅ Stripe Checkout Session creation
- ✅ Card payment processing
- ✅ Webhook signature verification
- ✅ CSRF protection on payment routes
- ✅ Error handling for failed transactions
- ✅ Session management

## Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register) with test API keys
- pip package manager

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Copy the example file and fill in your Stripe API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your Stripe keys from [https://dashboard.stripe.com/apikeys](https://dashboard.stripe.com/apikeys):

```
STRIPE_SECRET_KEY=sk_test_your_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

### 3. Run the Application

```bash
python app.py
```

The app will start at `http://localhost:5000`

## Testing the Checkout Flow

1. Navigate to `http://localhost:5000`
2. Click "Buy Now" to create a checkout session
3. You'll be redirected to Stripe's hosted checkout page
4. Use Stripe's test card numbers:

| Card Number | Behavior |
|-------------|----------|
| 4242 4242 4242 4242 | Success |
| 4000 0000 0000 0002 | Decline |
| 4000 0025 0000 3155 | 3D Secure required |

Use any future expiration date and any 3-digit CVC.

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies (pinned versions)
├── .env.example          # Environment variable template
├── .env                  # Your local environment variables (not in git)
├── CLAUDE.md             # Project guidelines
└── README.md             # This file
```

## Key Routes

### GET `/`
Home page with checkout button

### POST `/create-checkout-session`
Creates a new Stripe checkout session and redirects to the Stripe-hosted checkout page

### GET `/success`
Success page after payment completion

### GET `/cancel`
Cancel page if user cancels during checkout

### POST `/webhook`
Webhook endpoint to receive Stripe events (like checkout.session.completed)

## Webhook Setup

To receive webhook events locally, you can use the Stripe CLI:

```bash
# Install Stripe CLI from https://stripe.com/docs/stripe-cli
stripe login
stripe listen --forward-to localhost:5000/webhook
```

This will give you a webhook signing secret to add to your `.env` file.

## Security Notes

- Never commit `.env` to git (it contains secret keys)
- Always use `STRIPE_SECRET_KEY` (not publishable key) on the server
- The `@stripe_ext.protect` decorator handles CSRF protection
- Webhook signatures are verified automatically by `verify_webhook()`

## Error Handling

The application handles common errors:

- **CardError**: Card was declined or had issues
- **InvalidRequestError**: Invalid parameters sent to Stripe

See `app.py` for error handling implementation.

## Production Deployment

Before deploying to production:

1. Update `FLASK_SECRET_KEY` to a secure random value
2. Set `FLASK_ENV=production`
3. Add your live Stripe API keys (not test keys)
4. Configure HTTPS/SSL
5. Set up proper logging and monitoring
6. Test thoroughly with actual test transactions

## Support

For more information, see:
- [Stripe Checkout Documentation](https://stripe.com/docs/checkout)
- [Stripe Python SDK](https://github.com/stripe/stripe-python)
- [Flask Documentation](https://flask.palletsprojects.com/)
