# Stripe Checkout - Python Flask Integration

A complete Stripe Checkout implementation in Python using Flask with webhook handling, CSRF protection, and production-ready error handling.

## Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register)
- Stripe API keys (Secret and Publishable keys)
- pip package manager

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **stripe** - Official Stripe Python SDK
- **stripe-checkout-guard** - Flask middleware for secure Stripe integration
- **Flask** - Web framework
- **python-dotenv** - Environment variable management

### 2. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Add your Stripe API keys to `.env`:
   - Get your **Secret Key** from [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
   - Get your **Publishable Key** from the same location
   - Set up a webhook endpoint and get your **Webhook Secret**

   ```bash
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLIC_KEY=pk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Project Structure

```
.
├── app.py                    # Main Flask application
├── requirements.txt          # Project dependencies
├── .env.example             # Example environment variables
├── CLAUDE.md                # Project guidelines
├── README.md                # This file
└── templates/
    ├── index.html           # Checkout page
    ├── success.html         # Success page
    └── cancel.html          # Cancellation page
```

## Features

### Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Checkout page |
| `/create-checkout-session` | POST | Create Stripe checkout session |
| `/success` | GET | Success page after payment |
| `/cancel` | GET | Cancellation page |
| `/webhook` | POST | Stripe webhook endpoint |

### Security Features

- **CSRF Protection**: Enabled via `@stripe_ext.protect` decorator
- **Webhook Verification**: Signature verification to ensure authenticity
- **Session Management**: Secure session handling via stripe-checkout-guard

### Error Handling

The application handles:
- Card errors (declined cards, etc.)
- Invalid requests (missing fields, etc.)
- Webhook errors (invalid signatures, etc.)

## Testing

### Test Card Numbers

Use these card numbers when testing in Stripe test mode:

| Card Number | Behavior |
|-------------|----------|
| 4242 4242 4242 4242 | Succeeds |
| 4000 0000 0000 0002 | Declines |
| 4000 0025 0000 3155 | Requires 3D Secure |

**Expiry**: Any future date
**CVC**: Any 3-4 digit number

### Manual Testing

1. Navigate to `http://localhost:5000`
2. Click "Proceed to Checkout"
3. Enter test card details
4. Complete the payment
5. Check the success page

## Webhook Setup

To receive webhook events (for order fulfillment):

1. Install Stripe CLI:
   ```bash
   # macOS
   brew install stripe/stripe-cli/stripe

   # Or download from https://stripe.com/docs/stripe-cli
   ```

2. Forward webhook events to your local app:
   ```bash
   stripe listen --forward-to localhost:5000/webhook
   ```

3. This will output your webhook signing secret - add it to `.env`:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

## Production Deployment

Before deploying to production:

1. **Use production API keys** - Update `STRIPE_SECRET_KEY` and `STRIPE_PUBLIC_KEY`
2. **Update URLs** - Change success/cancel URLs in `app.py` to your domain
3. **Enable HTTPS** - Ensure your webhook endpoint uses HTTPS
4. **Set Flask debug to False** - Change `debug=True` to `debug=False` in `app.py`
5. **Use a production WSGI server** - Replace Flask development server with gunicorn/uWSGI
6. **Add logging** - Implement proper logging for production monitoring

## Customization

### Change Product Details

Edit the product information in `app.py`:

```python
"product_data": {
    "name": "Your Product Name",
    "description": "Your product description"
},
"unit_amount": 2000,  # Price in cents ($20.00)
```

### Update Styling

Modify CSS in `templates/index.html`, `templates/success.html`, and `templates/cancel.html`

### Add More Products

Extend the `line_items` array in `create_checkout_session()` to support multiple products

## Troubleshooting

### "API Key Error"
- Verify `STRIPE_SECRET_KEY` is set correctly in `.env`
- Check that you're using the Secret Key, not the Publishable Key

### "Webhook signature verification failed"
- Ensure `STRIPE_WEBHOOK_SECRET` matches the webhook endpoint secret
- Verify the webhook is forwarding to `localhost:5000/webhook`

### "CSRF validation failed"
- Clear your browser cookies
- Ensure the form is submitted with POST method

## Resources

- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Python SDK](https://stripe.com/docs/libraries/python)
- [Stripe Webhook Documentation](https://stripe.com/docs/webhooks)
- [Stripe Testing](https://stripe.com/docs/testing)

## License

This is a demonstration project for educational purposes.
