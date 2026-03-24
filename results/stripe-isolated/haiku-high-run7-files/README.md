# Stripe Checkout Payment Integration

A complete Flask application for accepting payments using Stripe Checkout. This project demonstrates how to create a secure payment flow with server-side session management, webhook handling, and production-ready error handling.

## Features

- 🛒 Complete checkout flow
- 🔒 Secure payment processing with Stripe Checkout
- 🎣 Webhook support for order fulfillment
- 🛡️ CSRF protection via stripe-checkout-guard
- 📧 Customer email capture
- 🎨 Modern, responsive UI
- ✅ Error handling and validation

## Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register)
- Stripe API keys (Secret Key and Publishable Key)
- Webhook endpoint set up in Stripe Dashboard

## Installation

1. **Clone or initialize the project:**

```bash
git clone <repository-url>
cd stripe-checkout-python
```

2. **Create a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Stripe keys
# STRIPE_SECRET_KEY=sk_test_...
# STRIPE_WEBHOOK_SECRET=whsec_...
```

## Getting Your Stripe API Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Copy your **Secret Key** (starts with `sk_test_` or `sk_live_`)
3. Copy your **Publishable Key** (starts with `pk_test_` or `pk_live_`)
4. Add them to your `.env` file

## Setting Up Webhooks

1. Go to [Stripe Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add Endpoint"
3. Enter your endpoint URL: `https://yourdomain.com/webhook`
4. Select events: `checkout.session.completed`
5. Copy the webhook signing secret (`whsec_...`)
6. Add it to your `.env` file as `STRIPE_WEBHOOK_SECRET`

## Running the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Testing

### Test Card Numbers

Use these test card numbers in the checkout:

| Card Number | Behavior |
|-------------|----------|
| `4242424242424242` | Success |
| `4000000000000002` | Decline |
| `4000002500003155` | 3D Secure required |

Use any future expiry date and any 3-digit CVC.

### Local Webhook Testing

To test webhooks locally:

1. **Install Stripe CLI:**
   - Download from https://stripe.com/docs/stripe-cli

2. **Authenticate with Stripe:**
   ```bash
   stripe login
   ```

3. **Forward webhook events:**
   ```bash
   stripe listen --forward-to localhost:5000/webhook
   ```

4. **Trigger test events:**
   ```bash
   stripe trigger checkout.session.completed
   ```

## Project Structure

```
.
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment variables
├── .gitignore              # Git ignore rules
├── templates/
│   ├── index.html          # Checkout page
│   ├── success.html        # Success page
│   └── cancel.html         # Cancellation page
└── README.md               # This file
```

## Security Considerations

1. **Never commit `.env` file** - Use `.env.example` for templates
2. **Always use HTTPS in production** - Stripe requires secure connections
3. **Validate webhook signatures** - stripe-checkout-guard handles this
4. **Use CSRF protection** - Enabled via stripe-checkout-guard middleware
5. **Keep dependencies updated** - Run `pip install --upgrade -r requirements.txt`
6. **Use webhook secret** - Never expose your webhook signing secret

## Customization

### Changing Product Details

Edit the `create_checkout_session` function in `app.py`:

```python
line_items=[{
    "price_data": {
        "currency": "usd",
        "product_data": {
            "name": "Your Product Name",
            "description": "Product description",
        },
        "unit_amount": 5000,  # Price in cents ($50.00)
    },
    "quantity": 1,
}]
```

### Using Stripe Product/Price IDs

Instead of inline price data:

```python
line_items=[{
    "price": "price_1234567890",  # Stripe Price ID
    "quantity": 1,
}]
```

### Custom Success/Cancel URLs

Modify the URLs in `create_checkout_session`:

```python
success_url="https://yourdomain.com/order-success?session_id={CHECKOUT_SESSION_ID}",
cancel_url="https://yourdomain.com/order-cancelled",
```

## Deployment

### Heroku

1. Create `Procfile`:
   ```
   web: gunicorn app:app
   ```

2. Deploy:
   ```bash
   git push heroku main
   ```

3. Set environment variables:
   ```bash
   heroku config:set STRIPE_SECRET_KEY=sk_live_...
   heroku config:set STRIPE_WEBHOOK_SECRET=whsec_...
   ```

### Other Platforms

Remember to:
- Change `debug=False` in production
- Set a strong `FLASK_SECRET_KEY`
- Use `https://` URLs for production
- Update Stripe webhook endpoint to production URL

## Troubleshooting

### "Invalid API Key"
- Verify you're using the secret key (starts with `sk_`), not the publishable key
- Make sure you're in the same Stripe account

### "Webhook signature verification failed"
- Ensure `STRIPE_WEBHOOK_SECRET` matches the one in Stripe Dashboard
- Check that webhook is forwarding to the correct endpoint

### CSRF Protection Errors
- stripe-checkout-guard automatically handles CSRF
- Ensure the form includes proper headers

## API Reference

### Create Checkout Session
- **Route:** `POST /create-checkout-session`
- **Protection:** CSRF protection enabled
- **Returns:** Redirect to Stripe Checkout URL

### Webhook Handler
- **Route:** `POST /webhook`
- **Events:** `checkout.session.completed`
- **Verification:** Automatic signature verification

## Support

For issues with:
- **Stripe API:** See [Stripe Documentation](https://stripe.com/docs)
- **stripe-checkout-guard:** Check the package documentation
- **Flask:** Refer to [Flask Documentation](https://flask.palletsprojects.com)

## License

MIT License - feel free to use this project as a starting point for your application.
