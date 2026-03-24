# Stripe Checkout Integration

A Flask application demonstrating Stripe Checkout integration for Python.

## Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register) with API keys

## Setup

### 1. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example file and add your Stripe API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your Stripe credentials:
- **STRIPE_SECRET_KEY**: Find at https://dashboard.stripe.com/apikeys
- **STRIPE_PUBLISHABLE_KEY**: Find at https://dashboard.stripe.com/apikeys
- **STRIPE_WEBHOOK_SECRET**: Set up webhooks at https://dashboard.stripe.com/webhooks

### 4. Run the application

```bash
python app.py
```

The app will start at `http://localhost:5000`

## Testing

### Using Test Cards

When in test mode (using `sk_test_*` keys), Stripe provides test card numbers:

| Card Number | Behavior |
|------------|----------|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 0002` | Payment declined |
| `4000 0025 0000 3155` | Requires 3D Secure authentication |

Use any future expiration date and any 3-digit CVC.

### Testing the Webhook

To test webhooks locally, use [Stripe CLI](https://stripe.com/docs/stripe-cli):

```bash
# Install Stripe CLI (https://stripe.com/docs/stripe-cli)

# Forward webhook events to your local app
stripe listen --forward-to localhost:5000/webhook

# In another terminal, trigger a test event
stripe trigger payment_intent.succeeded
```

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
├── .env                  # Environment variables (create from .env.example)
└── README.md             # This file
```

## Key Features

- ✅ Stripe Checkout integration with Flask
- ✅ CSRF protection with `stripe-checkout-guard`
- ✅ Webhook signature verification
- ✅ Success and cancellation pages
- ✅ Error handling
- ✅ Test mode support

## API Endpoints

### GET `/`
Homepage with checkout button

### POST `/create-checkout-session`
Creates a Stripe Checkout session and redirects to Stripe's hosted checkout page

### GET `/success`
Displays success page after payment

### GET `/cancel`
Displays cancellation page if payment was cancelled

### POST `/webhook`
Receives and processes Stripe webhook events

## Production Deployment

Before deploying to production:

1. Switch to live API keys (sk_live_* and pk_live_*)
2. Set `debug=False` in app.py
3. Use a production WSGI server (gunicorn, uWSGI)
4. Enable HTTPS
5. Configure proper webhook signing secrets
6. Set up proper error logging and monitoring

## Documentation

- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Python SDK](https://github.com/stripe/stripe-python)
- [Flask Documentation](https://flask.palletsprojects.com/)

## Support

For issues with Stripe integration, check:
- [Stripe Support](https://support.stripe.com/)
- [Stripe API Documentation](https://stripe.com/docs/api)
