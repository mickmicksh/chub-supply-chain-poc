# Stripe Checkout Python Flask Application

A complete Stripe Checkout integration built with Python and Flask, featuring secure payment processing, webhook handling, and test card support.

## Features

- ✅ Stripe Checkout integration
- ✅ CSRF protection and webhook signature verification
- ✅ Session management
- ✅ Error handling for card failures
- ✅ Webhook support for order fulfillment
- ✅ Test mode with test cards

## Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register)
- pip package manager

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Stripe API Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Navigate to Developers > API Keys
3. Copy your **Secret Key** (starts with `sk_`)
4. Copy your **Publishable Key** (starts with `pk_`)
5. Navigate to Webhooks and create an endpoint or use your webhook secret (starts with `whsec_`)

### 3. Configure Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` and add your Stripe keys:

```
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
FLASK_ENV=development
```

**Important**: Never commit `.env` to version control!

## Running the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

## Testing

### Test Cards

Use these test card numbers in the Stripe checkout form:

| Card Number | Behavior |
|---|---|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 0002` | Card declined |
| `4000 0025 0000 3155` | 3D Secure required |

### Testing the Checkout Flow

1. Open http://localhost:5000 in your browser
2. Click "Buy Now"
3. You'll be redirected to Stripe Checkout
4. Enter test card number `4242 4242 4242 4242`
5. Enter any future expiration date (e.g., 12/25)
6. Enter any 3-digit CVC (e.g., 123)
7. Enter any email address
8. Click "Pay"
9. You'll be redirected to the success page

### Testing Webhook Events

For local testing, you can use the Stripe CLI:

```bash
# Install Stripe CLI (https://stripe.com/docs/stripe-cli)
stripe listen --forward-to localhost:5000/webhook

# Get your webhook signing secret and add it to .env
# The CLI will output the signing secret at the beginning
```

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Local environment variables (not in git)
├── README.md             # This file
└── CLAUDE.md             # Project guidelines
```

## API Endpoints

- `GET /` - Home page with checkout button
- `POST /create-checkout-session` - Create a Stripe checkout session
- `GET /success` - Success page after payment
- `GET /cancel` - Cancellation page
- `POST /webhook` - Stripe webhook receiver

## Error Handling

The application includes error handling for:
- Invalid card information
- Declined cards
- Network errors
- Invalid webhook signatures

## Security Features

- CSRF protection on payment routes (via `@stripe_ext.protect`)
- Webhook signature verification
- Environment-based configuration
- Session-based state management

## Production Deployment

Before deploying to production:

1. Generate production API keys from Stripe Dashboard
2. Update environment variables in your hosting platform
3. Configure your webhook endpoint in Stripe Dashboard
4. Set `FLASK_ENV=production`
5. Use a production-grade WSGI server (e.g., Gunicorn)
6. Enable HTTPS

Example production run:

```bash
gunicorn -w 4 app:app
```

## Troubleshooting

### "stripe_checkout_guard not found"
Make sure you've installed all dependencies: `pip install -r requirements.txt`

### "Invalid API Key"
Double-check that your `STRIPE_SECRET_KEY` is correct in `.env`

### "Webhook signature verification failed"
Ensure your `STRIPE_WEBHOOK_SECRET` matches the one shown in Stripe Dashboard

### "Invalid request"
Make sure your success/cancel URLs match your current hostname

## Documentation

- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Python SDK](https://github.com/stripe/stripe-python)
- [Flask Documentation](https://flask.palletsprojects.com/)

## Support

For issues with Stripe integration, visit [Stripe Support](https://support.stripe.com)
