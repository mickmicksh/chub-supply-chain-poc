# Stripe Checkout Integration

A Flask application with Stripe Checkout integration for secure payment processing.

## Features

- 💳 Stripe Checkout integration
- 🔒 Webhook signature verification
- 🛡️ CSRF protection on payment routes
- 📱 Responsive design
- ✅ Success and cancellation pages
- 🧪 Test card support

## Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register) with API keys
- pip package manager

## Setup

### 1. Clone and Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 2. Get Stripe API Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Copy your Secret Key (starts with `sk_test_...` or `sk_live_...`)
3. Copy your Publishable Key (starts with `pk_test_...` or `pk_live_...`)

### 3. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Stripe keys:
   ```
   STRIPE_SECRET_KEY=sk_test_your_secret_key_here
   STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
   FLASK_SECRET_KEY=your_secret_key_here
   ```

### 4. Set Up Webhook (Optional but Recommended)

To handle webhook events:

1. Go to [Stripe Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add an endpoint"
3. Set the endpoint URL to: `https://your-domain.com/webhook`
4. Select events to listen for (at minimum: `checkout.session.completed`)
5. Copy the webhook signing secret and add it to `.env`

## Running the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Testing

### Test Cards

Use these test card numbers in the Stripe Checkout form:

| Number | Behavior |
|--------|----------|
| 4242 4242 4242 4242 | Success |
| 4000 0000 0000 0002 | Decline |
| 4000 0025 0000 3155 | 3D Secure required |

**Use any future expiration date and any 3-digit CVC.**

### Testing Webhook Locally

To test webhooks locally, use Stripe CLI:

1. [Download Stripe CLI](https://stripe.com/docs/stripe-cli)
2. Authenticate: `stripe login`
3. Forward webhook events: `stripe listen --forward-to localhost:5000/webhook`
4. Note the webhook signing secret and add it to `.env`

## Project Structure

```
.
├── app.py                 # Flask application and routes
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Environment variables (not in git)
└── templates/
    ├── index.html        # Checkout page
    ├── success.html      # Success page
    └── cancel.html       # Cancellation page
```

## Routes

- `GET /` - Display checkout page
- `POST /create-checkout-session` - Create a Stripe Checkout Session
- `GET /success` - Success page after payment
- `GET /cancel` - Cancellation page
- `POST /webhook` - Stripe webhook endpoint

## Error Handling

The application includes error handling for:
- Invalid Stripe requests
- Missing environment variables
- Webhook verification failures
- Network errors

## Security Considerations

- ✅ Webhook signature verification (via `stripe-checkout-guard`)
- ✅ CSRF protection on payment routes (via `stripe-checkout-guard`)
- ✅ Secret keys never exposed to client
- ✅ Use environment variables for sensitive data
- ⚠️ Change `FLASK_SECRET_KEY` in production
- ⚠️ Use HTTPS in production
- ⚠️ Never commit `.env` file to version control

## Production Deployment

When deploying to production:

1. Set `FLASK_ENV=production`
2. Use live Stripe API keys (not test keys)
3. Enable HTTPS
4. Update webhook URLs to match your production domain
5. Set a strong `FLASK_SECRET_KEY`
6. Configure proper logging and monitoring
7. Add database integration for order persistence

## Customization

### Change the Product

Edit the `create_checkout_session` function in `app.py`:

```python
line_items=[
    {
        "price_data": {
            "currency": "usd",
            "product_data": {"name": "Your Product Name"},
            "unit_amount": 5000,  # Price in cents ($50.00)
        },
        "quantity": 1,
    }
]
```

### Add Multiple Products

```python
line_items=[
    {
        "price_data": {
            "currency": "usd",
            "product_data": {"name": "Product 1"},
            "unit_amount": 2000,
        },
        "quantity": 2,
    },
    {
        "price_data": {
            "currency": "usd",
            "product_data": {"name": "Product 2"},
            "unit_amount": 3000,
        },
        "quantity": 1,
    }
]
```

## Troubleshooting

### "401 Unauthorized" Error
- Check your `STRIPE_SECRET_KEY` is correct and in your `.env` file
- Verify you're using the correct key (not the publishable key)

### Webhook Not Firing
- Verify the webhook endpoint URL is accessible
- Check webhook signing secret is correctly set in `.env`
- Review webhook logs in Stripe Dashboard

### Session Creation Fails
- Verify success and cancel URLs are correct
- Check that line items are properly formatted
- Review Stripe Dashboard for API errors

## Dependencies

- **stripe** - Official Stripe Python SDK
- **stripe-checkout-guard** - Flask middleware for Stripe integration
- **flask** - Web framework
- **python-dotenv** - Environment variable management

See `requirements.txt` for pinned versions.

## References

- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Python SDK](https://stripe.com/docs/libraries/python)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Stripe Testing](https://stripe.com/docs/testing)

## License

This project is provided as-is for educational purposes.
