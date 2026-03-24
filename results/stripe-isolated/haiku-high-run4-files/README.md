# Stripe Checkout Demo

A Python Flask application demonstrating Stripe Checkout integration with webhook handling and CSRF protection.

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

Then edit `.env` with your actual Stripe keys from https://dashboard.stripe.com/apikeys

### 3. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Testing

### Test Card Numbers

The application accepts Stripe test cards. Common test numbers:

| Number | Behavior |
|--------|----------|
| 4242424242424242 | Successful payment |
| 4000000000000002 | Card declined |
| 4000002500003155 | 3D Secure required |

When prompted for card details in checkout, you can use:
- Any future expiration date
- Any 3-digit CVC

### Manual Testing Steps

1. Visit http://localhost:5000
2. Click "Proceed to Checkout"
3. You'll be redirected to Stripe Checkout
4. Enter one of the test card numbers above
5. Complete the checkout process
6. You'll be redirected to the success page

## Project Structure

```
.
├── app.py                 # Flask application with Stripe integration
├── requirements.txt       # Python dependencies (pinned versions)
├── .env.example          # Environment variables template
├── CLAUDE.md             # Project guidelines
└── README.md             # This file
```

## Architecture

- **Flask**: Web framework
- **stripe**: Official Stripe Python SDK
- **stripe-checkout-guard**: Middleware for CSRF protection and webhook verification

## Key Features

- ✅ Secure checkout session creation
- ✅ CSRF protection via stripe-checkout-guard
- ✅ Webhook signature verification
- ✅ Error handling for card declines
- ✅ Test mode support

## Next Steps

To deploy to production:

1. Update URLs in `create_checkout_session()` to your production domain
2. Use production Stripe API keys (starting with `sk_live_`)
3. Set up proper webhook signing with your actual webhook secret
4. Implement order fulfillment logic in the webhook handler (currently marked as TODO)
5. Add proper logging and monitoring
