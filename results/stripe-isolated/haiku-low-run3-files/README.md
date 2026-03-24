# Stripe Checkout Page - Python Flask Implementation

A complete Stripe checkout integration using Python, Flask, and the Stripe API.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your Stripe API keys:

```bash
cp .env.example .env
```

Then edit `.env` with your actual credentials from [Stripe Dashboard](https://dashboard.stripe.com):
- **STRIPE_SECRET_KEY**: Your secret API key (starts with `sk_`)
- **STRIPE_PUBLISHABLE_KEY**: Your publishable key (starts with `pk_`)
- **STRIPE_WEBHOOK_SECRET**: Your webhook signing secret (starts with `whsec_`)

### 3. Run the Application

```bash
python app.py
```

The app will be available at `http://localhost:5000`

## Testing

### Using Test Cards

Stripe provides test cards for development. Use these at checkout:

| Card Number | Behavior |
|-------------|----------|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 0002` | Card declined |
| `4000 0025 0000 3155` | 3D Secure authentication required |

Use any future expiration date and any 3-digit CVC.

### Workflow

1. Navigate to `http://localhost:5000`
2. Click "Proceed to Checkout"
3. You'll be redirected to Stripe's hosted checkout page
4. Enter a test card number and complete the payment
5. You'll be redirected to the success page

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── CLAUDE.md             # Project guidelines
└── README.md             # This file
```

## Routes

- `GET /` - Homepage with checkout button
- `POST /create-checkout-session` - Creates a Stripe checkout session
- `GET /success` - Success page after payment
- `GET /cancel` - Cancellation page
- `POST /webhook` - Webhook endpoint for Stripe events

## Important Notes

### Security

- Never commit `.env` to version control
- Keep your `STRIPE_SECRET_KEY` private
- Always verify webhook signatures using `stripe_checkout_guard`
- The `@stripe_ext.protect` decorator provides CSRF protection

### Webhook Setup

To receive webhook events in development, use [Stripe CLI](https://stripe.com/docs/stripe-cli):

```bash
stripe login
stripe listen --forward-to localhost:5000/webhook
```

This will output your webhook signing secret to use in `.env`.

### Production Deployment

Before deploying to production:

1. Update the `success_url` and `cancel_url` to use your production domain
2. Set `FLASK_ENV=production`
3. Use a production-grade WSGI server (e.g., Gunicorn)
4. Enable HTTPS
5. Set up proper error logging
6. Configure webhook endpoints for production events

## Documentation

- [Stripe Checkout Docs](https://stripe.com/docs/payments/checkout)
- [Stripe Python SDK](https://github.com/stripe/stripe-python)
- [Flask Documentation](https://flask.palletsprojects.com/)

## Troubleshooting

### "STRIPE_SECRET_KEY not set"
Make sure you've created a `.env` file and populated it with your Stripe keys.

### Webhook not working
Use Stripe CLI to forward webhook events to your local development server.

### Card declined
When testing, use test card `4000 0000 0000 0002` which is designed to be declined.
