# Stripe Checkout Page

A Flask-based Stripe checkout integration with payment processing, success/cancel pages, and webhook support.

## Setup

### 1. Get Stripe API Keys

1. Sign up for a [Stripe account](https://dashboard.stripe.com/register) if you don't have one
2. Go to [API Keys](https://dashboard.stripe.com/apikeys)
3. Copy your Secret Key (starts with `sk_test_` or `sk_live_`)
4. Copy your Publishable Key (starts with `pk_test_` or `pk_live_`)

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your Stripe keys:

```
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
FLASK_SECRET_KEY=your-secret-key
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## Testing

Use these test card numbers in the Stripe checkout:

| Card Number | Behavior |
|------------|----------|
| 4242 4242 4242 4242 | Successful charge |
| 4000 0000 0000 0002 | Charge declined |
| 4000 0025 0000 3155 | 3D Secure required |

**Expiry:** Any future date
**CVC:** Any 3-digit number
**ZIP:** Any 5 digits

## Features

- ✅ Beautiful checkout page UI
- ✅ Stripe payment processing
- ✅ Success and cancel pages
- ✅ CSRF protection via `stripe-checkout-guard`
- ✅ Error handling for card failures
- ✅ Webhook support for payment confirmations
- ✅ Fully documented and PEP 8 compliant

## Project Structure

```
.
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies (pinned versions)
├── .env.example        # Example environment variables
├── CLAUDE.md           # Project guidelines
└── README.md           # This file
```

## Routes

- `GET /` - Checkout page
- `POST /create-checkout-session` - Create Stripe session
- `GET /success` - Payment success page
- `GET /cancel` - Payment cancelled page
- `POST /webhook` - Stripe webhook handler

## Production Deployment

When deploying to production:

1. Use `STRIPE_SECRET_KEY=sk_live_...` (live keys)
2. Set `FLASK_SECRET_KEY` to a strong random string
3. Configure webhook in Stripe Dashboard to point to your server
4. Use HTTPS only
5. Set `debug=False` in `app.run()`

## Security Notes

- Never commit `.env` file (it's in `.gitignore`)
- The `stripe-checkout-guard` middleware provides CSRF protection
- Webhook signature verification is required
- All sensitive keys are environment variables

## Documentation

- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Python SDK](https://github.com/stripe/stripe-python)
- [Flask Documentation](https://flask.palletsprojects.com/)
