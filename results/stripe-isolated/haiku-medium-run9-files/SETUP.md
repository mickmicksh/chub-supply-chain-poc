# Stripe Checkout Setup Guide

## Prerequisites
- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register) with API keys

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your Stripe API keys:
     - `STRIPE_SECRET_KEY`: Get from [Stripe Dashboard](https://dashboard.stripe.com/apikeys) (starts with `sk_test_` or `sk_live_`)
     - `STRIPE_WEBHOOK_SECRET`: Get from [Stripe Webhooks](https://dashboard.stripe.com/webhooks) (starts with `whsec_`)

3. **Load environment variables:**
   ```bash
   export $(cat .env | xargs)
   ```

   Or on Windows (PowerShell):
   ```powershell
   Get-Content .env | ForEach-Object {
       $name, $value = $_.split("=")
       [Environment]::SetEnvironmentVariable($name, $value)
   }
   ```

## Running the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`.

## Testing the Checkout Flow

1. Open `http://localhost:5000` in your browser
2. Click "Buy Now" to create a checkout session
3. Use test card numbers:
   - Success: `4242 4242 4242 4242`
   - Decline: `4000 0000 0000 0002`
   - 3D Secure: `4000 0025 0000 3155`
4. Use any future expiration date and any CVC

## Webhook Testing

To test webhooks locally, you can use the Stripe CLI:

```bash
# Install Stripe CLI from https://stripe.com/docs/stripe-cli

# Forward Stripe events to your local application
stripe listen --forward-to localhost:5000/webhook

# Trigger test events
stripe trigger payment_intent.succeeded
```

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── CLAUDE.md             # Project guidelines
└── SETUP.md              # This file
```

## Key Routes

- `GET /` - Home page with checkout button
- `POST /create-checkout-session` - Create a Stripe checkout session (CSRF protected)
- `GET /success` - Success page after payment
- `GET /cancel` - Cancellation page
- `POST /webhook` - Stripe webhook receiver (signature verified)

## Security Features

- CSRF protection on payment routes (via `@stripe_ext.protect`)
- Webhook signature verification (via `verify_webhook`)
- Error handling for card and request errors
- Environment variable protection for sensitive keys

## Next Steps

1. Customize the product details and pricing in `create_checkout_session()`
2. Implement order fulfillment logic in the webhook handler
3. Add database integration for order tracking
4. Deploy to production with HTTPS enabled
