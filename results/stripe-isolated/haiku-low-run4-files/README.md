# Stripe Checkout - Python Flask Integration

This project demonstrates how to build a Stripe checkout page using Python and Flask. It includes payment processing, webhook handling, and error management.

## Project Structure

```
.
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── templates/
│   ├── index.html         # Checkout page
│   ├── success.html       # Success page
│   └── cancel.html        # Cancellation page
└── CLAUDE.md              # Project guidelines
```

## Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register)
- Stripe API keys (Secret and Publishable)
- Webhook signing secret

## Setup Instructions

### 1. Get Your Stripe API Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Copy your **Secret Key** (starts with `sk_test_` or `sk_live_`)
3. Copy your **Publishable Key** (starts with `pk_test_` or `pk_live_`)

### 2. Set Up Webhook Secret

1. Go to [Stripe Webhooks Settings](https://dashboard.stripe.com/webhooks)
2. Create a new webhook endpoint for your local development or production URL
3. Copy the **Signing Secret** (starts with `whsec_`)

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Stripe API keys:
   ```
   STRIPE_SECRET_KEY=sk_test_your_key_here
   STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
   ```

### 5. Run the Application

```bash
python app.py
```

The app will start on `http://localhost:5000`

## Testing

### Test Payment Flow

1. Open `http://localhost:5000` in your browser
2. Click "Proceed to Checkout"
3. Use one of the test card numbers:
   - **Success**: `4242 4242 4242 4242`
   - **Decline**: `4000 0000 0000 0002`
   - **3D Secure**: `4000 0025 0000 3155`
4. Use any future expiration date and any 3-digit CVC

### Test Webhook Locally

To test webhooks locally, you can use [Stripe CLI](https://stripe.com/docs/stripe-cli):

```bash
# Install Stripe CLI (if not already installed)
# https://stripe.com/docs/stripe-cli#install

# Authenticate with Stripe
stripe login

# Forward webhook events to your local server
stripe listen --forward-to localhost:5000/webhook

# In another terminal, trigger a test webhook
stripe trigger payment_intent.succeeded
```

## How It Works

### 1. Create Checkout Session (`/create-checkout-session`)
- User submits checkout form
- Server creates a Stripe checkout session
- User is redirected to Stripe's hosted checkout page

### 2. Success Redirect (`/success`)
- After successful payment, user is redirected here
- Session ID is available as a query parameter
- You can fetch session details and fulfill the order

### 3. Webhook Handler (`/webhook`)
- Stripe sends webhook events to this endpoint
- `stripe-checkout-guard` middleware verifies the signature
- On `checkout.session.completed`, you can:
  - Update database
  - Send confirmation emails
  - Generate invoices
  - Fulfill orders

## Security Features

The project uses `stripe-checkout-guard` middleware which provides:

- ✅ **Webhook Signature Verification**: Ensures webhooks are from Stripe
- ✅ **CSRF Protection**: Protects your checkout endpoint from CSRF attacks
- ✅ **Session Management**: Handles secure session creation

## Customization

### Modify Checkout Items

Edit `/create-checkout-session` in `app.py`:

```python
line_items=[
    {
        "price_data": {
            "currency": "usd",
            "product_data": {"name": "Your Product Name"},
            "unit_amount": 5000,  # $50.00 in cents
        },
        "quantity": 1,
    }
]
```

### Add Order Fulfillment Logic

Edit the `handle_checkout_session_completed()` function in `app.py`:

```python
def handle_checkout_session_completed(session):
    """Handle completed checkout session"""
    customer_email = session.get('customer_email')
    session_id = session['id']

    # Add your logic here:
    # - Save order to database
    # - Send confirmation email
    # - Generate invoice
    # - Update inventory
    # etc.
```

### Customize Success/Cancel Pages

Edit the HTML files in `templates/` to match your brand.

## Troubleshooting

### Webhook Not Triggering

1. Ensure `STRIPE_WEBHOOK_SECRET` is set correctly
2. Check that your webhook endpoint is configured in [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
3. Review webhook delivery logs in the Stripe Dashboard

### Checkout Session Creation Fails

1. Verify `STRIPE_SECRET_KEY` is correct
2. Check that your Stripe account is in test mode (for development)
3. Review error logs for specific error messages

### Session State Issues

1. Ensure `FLASK_SECRET_KEY` is set
2. Clear browser cookies if you encounter session errors

## Resources

- [Stripe Checkout Documentation](https://stripe.com/docs/checkout)
- [Stripe Python API Reference](https://stripe.com/docs/api/checkout/sessions)
- [Stripe Test Cards](https://stripe.com/docs/testing)
- [Webhook Signing](https://stripe.com/docs/webhooks/signatures)

## Production Deployment

### Before Going Live

1. **Switch to Live Keys**: Update to live API keys (sk_live_* and pk_live_*)
2. **Configure Webhook URLs**: Update webhook endpoints to your production domain
3. **HTTPS Required**: Ensure your domain uses HTTPS
4. **Secure Secrets**: Use environment variables or secrets manager for sensitive data
5. **Error Handling**: Implement comprehensive error handling and logging
6. **Testing**: Thoroughly test the payment flow with real transactions (use small amounts)
7. **Compliance**: Ensure PCI compliance (use Stripe Checkout to minimize PCI scope)

### Environment Variables for Production

```
STRIPE_SECRET_KEY=sk_live_your_live_key
STRIPE_WEBHOOK_SECRET=whsec_your_live_webhook_secret
FLASK_ENV=production
FLASK_SECRET_KEY=your_secure_random_key
```

## License

This project is provided as-is for educational purposes.
