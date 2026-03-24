# Stripe Checkout Integration

A Python Flask application for integrating Stripe Checkout payments. This implementation includes server-side session handling, webhook verification, and production-ready error handling.

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── templates/            # HTML templates
│   ├── index.html        # Checkout page
│   ├── success.html      # Payment success page
│   └── cancel.html       # Payment cancellation page
└── README.md             # This file
```

## Prerequisites

- Python 3.9+
- pip package manager
- A [Stripe account](https://dashboard.stripe.com/register) with API keys

## Installation

1. **Clone or navigate to this project**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

5. **Add your Stripe credentials to `.env`**
   - Get your API keys from [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
   - Get your webhook signing secret from [Webhooks settings](https://dashboard.stripe.com/webhooks)

   ```
   STRIPE_SECRET_KEY=sk_test_your_secret_key
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
   FLASK_SECRET_KEY=your_random_secret_key
   ```

## Running the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

## Testing

### Test Cards

Stripe provides test cards for development:

| Card Number | Behavior |
|------------|----------|
| 4242 4242 4242 4242 | Successful payment |
| 4000 0000 0000 0002 | Payment declined |
| 4000 0025 0000 3155 | 3D Secure authentication required |

All test cards use:
- Any future expiration date
- Any 3-digit CVC code

### Webhook Testing

For local webhook testing:

1. **Install Stripe CLI**
   ```bash
   # macOS
   brew install stripe/stripe-cli/stripe

   # Linux/Windows - see https://stripe.com/docs/stripe-cli
   ```

2. **Forward webhooks to your local server**
   ```bash
   stripe listen --forward-to localhost:5000/webhook
   ```

3. **The CLI will output your webhook signing secret** - add it to `.env`

## Deployment

### Before Going Live

1. **Switch to live keys** in your `.env` file
   - Use `sk_live_` instead of `sk_test_`

2. **Set Flask debug mode off**
   ```bash
   FLASK_ENV=production
   ```

3. **Use a production WSGI server** instead of Flask's development server:
   ```bash
   pip install gunicorn
   gunicorn app:app
   ```

4. **Set up HTTPS** - Stripe requires HTTPS for production
   - Use a reverse proxy like Nginx
   - Obtain SSL certificates (Let's Encrypt is free)

5. **Update success/cancel URLs** in `app.py` to your production domain

6. **Configure webhooks** in Stripe Dashboard pointing to your production domain

### Environment Variables for Production

```
STRIPE_SECRET_KEY=sk_live_your_live_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_live_webhook_secret
FLASK_SECRET_KEY=a_very_long_random_secret_key
FLASK_ENV=production
```

## API Endpoints

### GET `/`
Home page with checkout button

**Response:** HTML checkout page

### POST `/create-checkout-session`
Creates a Stripe checkout session and redirects to Stripe's hosted checkout

**Response:** 303 redirect to Stripe Checkout URL or error JSON

### GET `/success`
Confirmation page after successful payment

**Query Parameters:**
- `session_id` - Stripe checkout session ID

**Response:** HTML success confirmation page

### GET `/cancel`
Cancellation page if user exits checkout

**Response:** HTML cancellation page

### POST `/webhook`
Handles Stripe webhook events

**Headers:** `Stripe-Signature` - Webhook signature for verification

**Body:** JSON webhook event

**Response:** 200 on success, 400 on validation failure

## Webhook Events

The application currently handles:

- `checkout.session.completed` - Payment successful, order fulfilled

You can extend the webhook handler to handle additional events:
- `charge.refunded` - Process refunds
- `customer.subscription.created` - Handle subscriptions
- `charge.failed` - Handle failed payments

## Customization

### Changing the Product

Edit the line items in `app.py` `create_checkout_session()`:

```python
line_items=[
    {
        "price_data": {
            "currency": "usd",
            "product_data": {
                "name": "Your Product Name",
                "description": "Optional product description",
                "images": ["https://your-image-url.com/image.jpg"],
            },
            "unit_amount": 5000,  # $50.00 in cents
        },
        "quantity": 1,
    }
],
```

### Multiple Products

```python
line_items=[
    {
        "price_data": {
            "currency": "usd",
            "product_data": {"name": "Product 1"},
            "unit_amount": 2000,
        },
        "quantity": 1,
    },
    {
        "price_data": {
            "currency": "usd",
            "product_data": {"name": "Product 2"},
            "unit_amount": 3000,
        },
        "quantity": 2,
    },
]
```

### Subscription Payments

Change `mode="payment"` to `mode="subscription"` and use a price ID instead of price_data.

## Error Handling

The application includes error handling for:

- **InvalidRequestError** - Malformed Stripe API requests (400 response)
- **CardError** - Card declined or other card issues (402 response)
- **Generic exceptions** - Unexpected errors (500 response)

Webhook errors return 400 for invalid signatures/payload.

## Security Notes

- ✅ Webhook signature verification enabled via `stripe-checkout-guard`
- ✅ CSRF protection on payment routes via middleware
- ✅ Server-side session validation
- ✅ Error messages don't leak sensitive information
- ⚠️ Never expose your `STRIPE_SECRET_KEY` - keep it in environment variables
- ⚠️ Always use HTTPS in production

## Troubleshooting

### "Invalid API Key" error
- Check that `STRIPE_SECRET_KEY` is set correctly in `.env`
- Ensure you're using the test key (`sk_test_`) for development

### Webhook events not received
- Verify webhook secret is correct
- Check Stripe Dashboard > Webhooks for delivery logs
- Ensure your server is accessible to Stripe (not behind a firewall)

### CSRF protection errors
- Ensure `app.secret_key` is set (handled by `FLASK_SECRET_KEY`)
- Check that POST requests include proper form data

## Additional Resources

- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Python SDK](https://github.com/stripe/stripe-python)
- [Stripe Testing Guide](https://stripe.com/docs/testing)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)

## License

MIT
