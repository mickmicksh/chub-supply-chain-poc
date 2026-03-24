# Stripe Checkout Integration

A Python Flask application with integrated Stripe checkout for processing payments securely.

## Features

- ✅ Stripe Checkout integration with server-side sessions
- ✅ Webhook signature verification for security
- ✅ CSRF protection on payment routes
- ✅ Error handling for card failures
- ✅ Success and cancellation pages
- ✅ Test card support for development

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── templates/
│   ├── index.html        # Checkout page
│   ├── success.html      # Success page
│   └── cancel.html       # Cancellation page
└── README.md             # This file
```

## Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register)
- API keys from your Stripe dashboard

## Setup Instructions

### 1. Get Your Stripe API Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Navigate to Developers → API Keys
3. Copy your **Secret Key** and **Publishable Key**
4. Go to Webhooks and create a new endpoint
5. Copy your **Webhook Signing Secret**

### 2. Create Environment Variables

Copy the `.env.example` file to `.env` and fill in your Stripe keys:

```bash
cp .env.example .env
```

Edit `.env` with your actual keys:
```
STRIPE_SECRET_KEY=sk_test_your_actual_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_actual_webhook_secret
SECRET_KEY=your_flask_secret_key_for_production
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Usage

### Checkout Flow

1. **Visit the homepage** at `http://localhost:5000/`
2. **Review the product** - Premium Plan ($20.00)
3. **Click "Checkout"** to open the Stripe payment form
4. **Enter test card details**:
   - Success: `4242 4242 4242 4242`
   - Decline: `4000 0000 0000 0002`
   - 3D Secure: `4000 0025 0000 3155`
5. Use any future date for expiry and any 3-digit CVC

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Checkout page |
| `/create-checkout-session` | POST | Create Stripe checkout session |
| `/success` | GET | Success page with session details |
| `/cancel` | GET | Cancellation page |
| `/webhook` | POST | Stripe webhook receiver |
| `/health` | GET | Health check |

## Testing

### Test Card Numbers

| Card Number | Behavior |
|-------------|----------|
| `4242424242424242` | Successful payment |
| `4000000000000002` | Card declined |
| `4000002500003155` | Requires 3D Secure authentication |

**Note**: Use any future date for expiry (e.g., 12/25) and any 3-digit CVC.

### Webhook Testing

To test webhooks locally, use the Stripe CLI:

```bash
# Install Stripe CLI: https://stripe.com/docs/stripe-cli
stripe listen --forward-to localhost:5000/webhook

# In another terminal, trigger events
stripe trigger payment_intent.succeeded
```

## Production Deployment

Before deploying to production:

1. **Use HTTPS** - Required for Stripe checkout
2. **Update URLS** - Change `localhost:5000` to your domain in `app.py`
3. **Use Production Keys** - Switch from test to live Stripe keys
4. **Set SECRET_KEY** - Use a strong, random value in `.env`
5. **Configure CORS** - Set appropriate allowed origins
6. **Enable Rate Limiting** - Protect against abuse
7. **Set Debug Mode to False** - Change `debug=False` in `app.py`
8. **Use Environment Variables** - Never hardcode sensitive data

### Example Deployment Steps

```bash
# Set environment variables in production
export STRIPE_SECRET_KEY="sk_live_..."
export STRIPE_PUBLISHABLE_KEY="pk_live_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."
export SECRET_KEY="your-production-secret-key"

# Run with production WSGI server
pip install gunicorn
gunicorn app:app --bind 0.0.0.0:5000
```

## Security Notes

- ✅ All sensitive credentials are stored in environment variables
- ✅ Webhook signatures are verified using `stripe-checkout-guard`
- ✅ CSRF protection is enabled on payment routes
- ✅ PCI compliance is handled by Stripe Checkout
- ✅ Test/Live mode separation is enforced via API keys

## Error Handling

The application handles common Stripe errors:

- **CardError** - Card was declined (402 status)
- **InvalidRequestError** - Invalid request parameters (400 status)
- **AuthenticationError** - Invalid API key (401 status)
- **RateLimitError** - Rate limit exceeded (429 status)

## Troubleshooting

### "STRIPE_SECRET_KEY not set"
- Ensure `.env` file exists and is properly configured
- Check that `python-dotenv` is installed: `pip install python-dotenv`

### "Invalid signature" webhook error
- Verify your webhook signing secret matches in `.env`
- Ensure webhook endpoint is publicly accessible
- Check Stripe dashboard for webhook logs

### "Session not found"
- Verify the session ID is being passed correctly
- Check that the success URL matches your configuration
- Ensure checkout session hasn't expired (sessions expire after 24 hours)

## Documentation

- [Stripe Checkout Docs](https://stripe.com/docs/payments/checkout)
- [Stripe Python SDK](https://github.com/stripe/stripe-python)
- [Webhook Security](https://stripe.com/docs/webhooks)
- [Testing](https://stripe.com/docs/testing)

## License

This project is provided as-is for educational and commercial use.

## Support

For Stripe-specific issues, visit [Stripe Support](https://stripe.com/help).
