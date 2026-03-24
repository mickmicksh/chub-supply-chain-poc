# Stripe Checkout Page - Python

A complete Stripe checkout implementation in Python using Flask, with webhook handling, error management, and production-ready security features.

## Features

✅ **Secure Checkout Flow** - Built with `stripe-checkout-guard` middleware for CSRF protection and webhook verification
✅ **Hosted Checkout** - Redirects to Stripe's hosted checkout page (recommended for PCI compliance)
✅ **Webhook Handling** - Automatically processes payment completion events
✅ **Error Handling** - Comprehensive error management for card errors and invalid requests
✅ **Test Cards** - Includes test card numbers for development
✅ **Beautiful UI** - Modern, responsive checkout experience

## Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register) (free to create)
- pip package manager

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Get your API keys from [Stripe Dashboard](https://dashboard.stripe.com/apikeys):
   - Sign in to your Stripe account
   - Go to Developers > API keys
   - Copy your Secret Key and Publishable Key

3. Set up webhook (for local testing with `stripe listen`):
   - Install Stripe CLI from https://stripe.com/docs/stripe-cli
   - Run: `stripe listen --forward-to localhost:5000/webhook`
   - Copy the webhook signing secret to your `.env` file

4. Update your `.env` file:
```env
STRIPE_SECRET_KEY=sk_test_your_actual_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_actual_secret_here
```

### 3. Run the Application

```bash
python app.py
```

The app will start at `http://localhost:5000`

## Testing the Checkout

1. Open `http://localhost:5000` in your browser
2. Click "Proceed to Checkout"
3. Use one of the test card numbers:

| Card Number | Result |
|---|---|
| `4242 4242 4242 4242` | ✅ Payment succeeds |
| `4000 0000 0000 0002` | ❌ Payment is declined |
| `4000 0025 0000 3155` | ⚠️ Requires 3D Secure authentication |

Use any future expiration date and any 3-digit CVC.

## Project Structure

```
.
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variable template
├── templates/
│   ├── index.html           # Checkout page
│   ├── success.html         # Success page
│   └── cancel.html          # Cancellation page
└── README.md
```

## How It Works

### 1. **Checkout Session Creation** (`/create-checkout-session`)
- User clicks checkout button
- Flask creates a Stripe checkout session
- User is redirected to Stripe's hosted checkout page
- CSRF protection via `@stripe_ext.protect` decorator

### 2. **Payment Processing**
- User completes payment on Stripe's secure checkout
- Redirected to success/cancel page with session ID

### 3. **Webhook Handling** (`/webhook`)
- Stripe sends webhook event when payment completes
- Signature verified for security
- Order fulfillment triggered (e.g., send confirmation email)

## Error Handling

The app handles common Stripe errors:

- **CardError** - Declined cards, invalid CVV, etc. (returns 402)
- **InvalidRequestError** - Missing/invalid parameters (returns 400)

## Customization

### Change Product Details
Edit in `app.py`:
```python
line_items=[{
    "price_data": {
        "currency": "usd",
        "product_data": {"name": "Your Product Name"},
        "unit_amount": 5000,  # Price in cents ($50.00)
    },
    "quantity": 1,
}]
```

### Add Order Fulfillment Logic
Edit the `fulfill_order()` function to:
- Send confirmation emails
- Create user accounts
- Update database records
- Issue licenses
- Send digital products

```python
def fulfill_order(session):
    customer_email = session.get('customer_details', {}).get('email')
    # Your fulfillment logic here
```

## Production Deployment

Before deploying to production:

1. **Update URLs** - Change `localhost:5000` to your production domain
2. **Use Production Keys** - Switch from `sk_test_` to `sk_live_` keys
3. **Set Flask Debug to False** - `app.run(debug=False)`
4. **Use HTTPS** - Stripe requires secure connections
5. **Set Webhook Endpoints** - Configure in Stripe Dashboard > Webhooks
6. **Store Secrets Securely** - Use environment variables or secrets management

## Troubleshooting

### "Webhook secret mismatch"
- Make sure `STRIPE_WEBHOOK_SECRET` in your `.env` matches Stripe's webhook signing secret
- For local testing, run: `stripe listen --forward-to localhost:5000/webhook`

### "API key not found"
- Verify you've set `STRIPE_SECRET_KEY` in your `.env`
- Keys should start with `sk_test_` (development) or `sk_live_` (production)

### "Module not found"
- Run `pip install -r requirements.txt` to install dependencies

## Resources

- [Stripe Checkout Docs](https://stripe.com/docs/payments/checkout)
- [Stripe API Reference](https://stripe.com/docs/api)
- [Stripe CLI Documentation](https://stripe.com/docs/stripe-cli)
- [Stripe Testing Guide](https://stripe.com/docs/testing)

## License

This project is provided as-is for learning and development purposes.
