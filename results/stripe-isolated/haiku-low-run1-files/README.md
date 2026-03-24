# Stripe Checkout Integration - Python Flask

A complete Flask application for handling Stripe checkout payments with webhook support.

## Project Structure

```
.
├── app.py                 # Main Flask application with Stripe integration
├── requirements.txt       # Python dependencies (pinned versions)
├── .env.example          # Example environment variables
├── CLAUDE.md             # Project guidelines
└── README.md             # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register)
- Stripe API keys (Secret Key and Webhook Secret)

### 2. Installation

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the example environment file and add your Stripe credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Stripe API keys:

```
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
FLASK_SECRET_KEY=your_flask_secret_key_here
```

**Getting your API keys:**
1. Go to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Copy your **Secret Key** (starts with `sk_`)
3. For webhooks, go to [Webhooks](https://dashboard.stripe.com/webhooks) and create an endpoint pointing to your `/webhook` route
4. Copy the **Webhook Secret** (starts with `whsec_`)

### 4. Running the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Features

- **Home Page** (`/`): Display product with price and checkout button
- **Checkout** (`/create-checkout-session`): Create Stripe checkout session
- **Webhook** (`/webhook`): Handle Stripe events (payment completion, etc.)
- **Success Page** (`/success`): Confirmation after successful payment
- **Cancel Page** (`/cancel`): Handles cancelled payments

## Testing

### Test Card Numbers

Use these test card numbers in the Stripe checkout:

| Number | Behavior |
|--------|----------|
| `4242424242424242` | Successful payment |
| `4000000000000002` | Card declined |
| `4000002500003155` | 3D Secure required |

### Testing Webhooks Locally

For local webhook testing, use [Stripe CLI](https://stripe.com/docs/stripe-cli):

```bash
# Install Stripe CLI (macOS with Homebrew)
brew install stripe/stripe-cli/stripe

# Login to your Stripe account
stripe login

# Forward webhook events to your local app
stripe listen --forward-to localhost:5000/webhook

# In another terminal, trigger test events
stripe trigger payment_intent.succeeded
```

## Dependencies

All dependencies are pinned to specific versions in `requirements.txt`:

- **stripe** (12.1.0): Official Stripe Python SDK
- **stripe-checkout-guard** (1.0.0): Flask middleware for Stripe integration
  - Handles webhook signature verification
  - CSRF protection on payment routes
  - Session management
- **Flask** (3.0.0): Web framework

## Project Guidelines

See `CLAUDE.md` for code style and project guidelines:
- Python 3.9+
- PEP 8 compliance
- All dependencies pinned in `requirements.txt`

## Error Handling

The application includes error handling for:
- `CardError`: Payment card was declined
- `InvalidRequestError`: Invalid request parameters
- Webhook signature verification errors

Errors return appropriate HTTP status codes and JSON error messages.

## Security Notes

1. **Never commit `.env`**: Keep Stripe keys out of version control
2. **Webhook Signature Verification**: All webhooks are verified using `stripe_checkout_guard`
3. **CSRF Protection**: The `@stripe_ext.protect` decorator adds CSRF protection
4. **Secret Key**: Use a strong, randomly generated `FLASK_SECRET_KEY` in production

## Production Deployment

When deploying to production:

1. Update success/cancel URLs to your production domain
2. Use production Stripe keys (starts with `pk_live_` and `sk_live_`)
3. Set up proper error logging and monitoring
4. Enable HTTPS for all routes
5. Configure proper webhook endpoints in Stripe Dashboard
6. Use environment variables for all sensitive configuration

## Troubleshooting

### "ModuleNotFoundError: No module named 'stripe'"
Make sure you've activated the virtual environment and installed dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "STRIPE_SECRET_KEY not found"
Make sure you've created a `.env` file with your Stripe keys (or set them as environment variables).

### Webhooks not working
1. Verify your webhook endpoint is publicly accessible
2. Check the webhook secret matches in your Stripe Dashboard
3. Use Stripe CLI locally for testing: `stripe listen --forward-to localhost:5000/webhook`

## Resources

- [Stripe Python SDK Documentation](https://stripe.com/docs/api/python)
- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Testing Guide](https://stripe.com/docs/testing)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)
