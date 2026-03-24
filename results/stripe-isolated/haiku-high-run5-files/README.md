# Stripe Checkout - Python Flask App

A complete Flask application for integrating Stripe Checkout with webhook support.

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

Then edit `.env` and add:
- `STRIPE_SECRET_KEY`: Your Stripe secret API key (from https://dashboard.stripe.com/apikeys)
- `STRIPE_WEBHOOK_SECRET`: Your webhook signing secret (from https://dashboard.stripe.com/webhooks)

### 3. Run the App

```bash
python app.py
```

The app will start on `http://localhost:5000`

## Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home page with checkout button |
| `/create-checkout-session` | POST | Creates Stripe checkout session |
| `/success` | GET | Success page (redirect after payment) |
| `/cancel` | GET | Cancellation page |
| `/webhook` | POST | Handles Stripe webhook events |

## Testing

### Test with Stripe Test Cards

Use these test card numbers on the checkout page:

| Number | Behavior |
|--------|----------|
| 4242424242424242 | ✅ Success |
| 4000000000000002 | ❌ Decline |
| 4000002500003155 | ⚠️ 3D Secure required |

Use any future expiration date and any CVC.

### Webhook Testing

To test webhooks locally, you can use the Stripe CLI:

```bash
stripe listen --forward-to localhost:5000/webhook
```

Then trigger test events:

```bash
stripe trigger payment_intent.succeeded
```

## Project Structure

```
.
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── CLAUDE.md          # Project guidelines
└── README.md          # This file
```

## Security Notes

- The `@stripe_ext.protect` decorator handles CSRF protection on payment routes
- Webhook signatures are verified with `verify_webhook()`
- Keep your `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` private
- Never commit `.env` to version control

## Next Steps

1. Replace the placeholder webhook secret in `.env`
2. Implement `fulfill_order()` function to handle successful payments
3. Deploy to production (update URLs in `success_url` and `cancel_url`)
4. Register webhook endpoints in Stripe Dashboard
