# Stripe Checkout - Python Flask Application

A simple Flask application demonstrating Stripe Checkout integration with webhook support.

## Quick Start

### 1. Get Stripe API Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Copy your **Secret Key** (starts with `sk_test_` or `sk_live_`)
3. Create a webhook endpoint:
   - Go to [Webhooks](https://dashboard.stripe.com/webhooks)
   - Click "Add endpoint"
   - For local testing, use a tool like [ngrok](https://ngrok.com/) to expose your local port
   - Point to `http://your-ngrok-url/webhook`
   - Select `checkout.session.completed` event
   - Copy the **Signing Secret** (starts with `whsec_`)

### 2. Set Up Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Stripe keys
# STRIPE_SECRET_KEY=sk_test_...
# STRIPE_WEBHOOK_SECRET=whsec_...
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The app will be running at `http://localhost:5000`

## Testing

### Test Card Numbers

| Number | Behavior |
|--------|----------|
| 4242424242424242 | Success |
| 4000000000000002 | Decline |
| 4000002500003155 | 3D Secure required |

Use any future expiration date and any CVC.

### Testing Locally with Webhooks

To test webhooks locally:

1. **Install ngrok:**
   ```bash
   # macOS
   brew install ngrok

   # Or download from https://ngrok.com/download
   ```

2. **Start ngrok:**
   ```bash
   ngrok http 5000
   ```

3. **Add webhook endpoint in Stripe Dashboard:**
   - Use the URL from ngrok (e.g., `https://abc123.ngrok.io/webhook`)
   - Copy the signing secret

4. **Update .env with the webhook secret**

5. **Test webhook:**
   ```bash
   # In another terminal, trigger a test event
   stripe trigger checkout.session.completed
   ```

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies (pinned versions)
├── .env.example          # Example environment variables
├── CLAUDE.md             # Project guidelines
└── README.md             # This file
```

## Features

- ✅ Simple checkout page
- ✅ Stripe checkout session creation
- ✅ CSRF protection via stripe-checkout-guard
- ✅ Webhook signature verification
- ✅ Success/cancel pages
- ✅ Error handling

## Production Deployment

Before deploying to production:

1. Update URLs in `app.py` from `localhost:5000` to your production domain
2. Use live Stripe keys (`sk_live_` and `whsec_`)
3. Change `SECRET_KEY` in `.env` to a strong random value
4. Set `debug=False` in `app.run()`
5. Use a production WSGI server (e.g., Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Next Steps

- Add database integration to store orders
- Implement email confirmations
- Add customer metadata to checkout sessions
- Set up multiple product pricing tiers
- Implement subscription billing

## Documentation

- [Stripe Checkout Documentation](https://stripe.com/docs/checkout)
- [Stripe Python SDK](https://github.com/stripe/stripe-python)
- [Flask Documentation](https://flask.palletsprojects.com/)
