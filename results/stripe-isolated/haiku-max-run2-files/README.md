# Stripe Checkout Integration

A Flask web application with Stripe Checkout integration for handling payments.

## Setup Instructions

### 1. Get Stripe API Keys

1. Sign up at [Stripe Dashboard](https://dashboard.stripe.com/register)
2. Navigate to Developers → API keys
3. Copy your Secret Key and Publishable Key

### 2. Configure Environment Variables

Edit the `.env` file with your Stripe keys:

```
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The app will be available at `http://localhost:5000`

## Testing with Test Cards

Use these test card numbers in the Stripe Checkout:

| Number | Behavior |
|--------|----------|
| 4242424242424242 | Success |
| 4000000000000002 | Decline |
| 4000002500003155 | 3D Secure required |

Use any future date for expiration and any 3-digit number for CVC.

## Webhook Setup (Production)

For production, set up Stripe webhooks:

1. Go to Developers → Webhooks in Stripe Dashboard
2. Add endpoint: `https://yourdomain.com/webhook`
3. Select `checkout.session.completed` event
4. Copy the signing secret to `STRIPE_WEBHOOK_SECRET`

## Project Structure

- `app.py` - Main Flask application with Stripe integration
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (update with your keys)
- `.gitignore` - Git ignore patterns

## Routes

- `GET /` - Home page with checkout button
- `POST /create-checkout-session` - Create checkout session (protected)
- `GET /success` - Success page after payment
- `GET /cancel` - Cancellation page
- `POST /webhook` - Stripe webhook endpoint
