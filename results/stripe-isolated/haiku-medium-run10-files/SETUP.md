# Stripe Checkout Setup Guide

## Prerequisites
- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register)

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get Your Stripe API Keys:**
   - Go to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
   - Copy your **Secret Key** (starts with `sk_test_` for testing)
   - Copy your **Publishable Key** (starts with `pk_test_` for testing)

3. **Get Your Webhook Signing Secret:**
   - Go to [Stripe Webhooks](https://dashboard.stripe.com/webhooks)
   - Create a new endpoint for `http://localhost:5000/webhook`
   - Subscribe to `checkout.session.completed` event
   - Copy the **Signing Secret** (starts with `whsec_`)

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add:
   - `STRIPE_SECRET_KEY`: Your Stripe Secret Key
   - `STRIPE_WEBHOOK_SECRET`: Your Webhook Signing Secret
   - `FLASK_SECRET_KEY`: A random string for session security

5. **Run the application:**
   ```bash
   python app.py
   ```
   The app will be available at `http://localhost:5000`

## Testing

Use Stripe's test card numbers:

| Card Number | Behavior |
|---|---|
| `4242 4242 4242 4242` | Success |
| `4000 0000 0000 0002` | Decline |
| `4000 0025 0000 3155` | 3D Secure required |

Use any future expiration date and any 3-digit CVC.

## Routes

- `GET /` - Home page with checkout button
- `POST /create-checkout-session` - Creates a Stripe Checkout session
- `GET /success` - Success page after payment
- `GET /cancel` - Cancel page if user cancels
- `POST /webhook` - Webhook endpoint for Stripe events

## Next Steps

1. **Replace test URLs** - Update success/cancel URLs to your production domain
2. **Implement order fulfillment** - Add your business logic in the webhook handler
3. **Add database** - Store order information for tracking
4. **Deploy** - Move `FLASK_ENV` to production and use production Stripe keys
