# Stripe Checkout - Python Flask Integration

A complete Stripe Checkout integration built with Python and Flask. This project demonstrates how to create a checkout session, handle payments, and process webhooks securely.

## Features

✓ Secure checkout sessions with Stripe Checkout
✓ CSRF protection via stripe-checkout-guard middleware
✓ Webhook signature verification
✓ Error handling for card and request errors
✓ Test mode with Stripe test cards
✓ Success and cancellation pages

## Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register)
- Stripe API keys (test mode)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and add your Stripe API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your keys from the [Stripe Dashboard](https://dashboard.stripe.com/apikeys):

```env
STRIPE_SECRET_KEY=sk_test_your_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

### 3. Run the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

## Usage

### Home Page
Visit `http://localhost:5000/` to see the checkout page.

### Create Checkout Session
Click the "Checkout" button to create a Stripe Checkout session and be redirected to the Stripe-hosted payment page.

### Test Payments

Use these test card numbers in Stripe's hosted checkout:

| Card Number | Behavior |
|------------|----------|
| 4242 4242 4242 4242 | Success |
| 4000 0000 0000 0002 | Decline |
| 4000 0025 0000 3155 | 3D Secure required |

Use any future expiration date and any CVC.

### Webhook Setup (Local Testing)

To test webhooks locally, use [Stripe CLI](https://stripe.com/docs/stripe-cli):

```bash
# Install Stripe CLI and authenticate
stripe login

# Forward webhook events to your local server
stripe listen --forward-to localhost:5000/webhook

# Use the webhook signing secret from the CLI output
# Add it to your .env file as STRIPE_WEBHOOK_SECRET
```

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies with pinned versions
├── .env.example          # Environment variables template
├── CLAUDE.md             # Project guidelines
└── README.md             # This file
```

## Key Routes

- `GET /` - Home page with checkout button
- `POST /create-checkout-session` - Create a checkout session (CSRF-protected)
- `GET /success` - Success page after payment
- `GET /cancel` - Cancellation page
- `POST /webhook` - Stripe webhook endpoint

## Security Notes

- The `/create-checkout-session` route is protected with `@stripe_ext.protect` for CSRF protection
- Webhook signatures are verified using `verify_webhook()`
- All Stripe API calls use your secret key (never expose in frontend)
- Test mode API keys are used by default

## Error Handling

The application handles:
- `CardError` - Card declines and other card-related errors
- `InvalidRequestError` - Invalid Stripe API parameters
- Webhook signature verification errors

## Production Deployment

Before deploying to production:

1. Switch to **live** Stripe API keys (not test keys)
2. Update success/cancel URLs to your production domain
3. Implement proper order fulfillment logic in `fulfill_order()`
4. Set up proper logging and monitoring
5. Use environment-specific configuration
6. Enable HTTPS for all routes
7. Set up proper error tracking and alerting

## Documentation

For more information:
- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Python SDK](https://github.com/stripe/stripe-python)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [stripe-checkout-guard](https://github.com/stripe-checkout-guard/stripe-checkout-guard)

## License

This project is provided as-is for educational and development purposes.
