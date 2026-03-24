# Stripe Checkout Integration

A Python Flask application implementing Stripe Checkout for processing payments securely.

## Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register) with API keys
- pip package manager

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd stripe-checkout
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Get your Stripe API keys from [https://dashboard.stripe.com/apikeys](https://dashboard.stripe.com/apikeys)

3. Edit `.env` and add your keys:
   ```
   STRIPE_SECRET_KEY=sk_test_your_key_here
   STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
   FLASK_SECRET_KEY=your-secret-key-here
   ```

### 5. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Testing

### Test Cards

Use these test card numbers in the checkout form:

| Number | Behavior |
|--------|----------|
| 4242 4242 4242 4242 | Successful payment |
| 4000 0000 0000 0002 | Card declined |
| 4000 0025 0000 3155 | 3D Secure authentication required |

### Webhook Testing

To test webhooks locally, use the [Stripe CLI](https://stripe.com/docs/stripe-cli):

```bash
# Install Stripe CLI (if not already installed)
# Then forward webhooks to your local server
stripe listen --forward-to localhost:5000/webhook

# In another terminal, trigger a test event
stripe trigger checkout.session.completed
```

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── CLAUDE.md             # Project guidelines
└── README.md             # This file
```

## Features

- **Secure Checkout**: Uses Stripe-Checkout-Guard for CSRF protection and webhook verification
- **Error Handling**: Proper error handling for card errors and invalid requests
- **Webhook Support**: Handles Stripe webhook events for payment confirmation
- **Responsive UI**: Simple, clean checkout interface

## API Routes

### `GET /`
Home page with checkout button

### `POST /create-checkout-session`
Creates a Stripe checkout session and redirects to Stripe's hosted checkout

### `GET /success`
Redirect target after successful payment

### `GET /cancel`
Redirect target if user cancels payment

### `POST /webhook`
Webhook endpoint for Stripe events (signature verification required)

## Production Deployment

### Before Going Live

1. **Replace Test Keys**: Update environment variables with live Stripe keys (sk_live_...)
2. **Update URLs**: Replace localhost URLs in `create_checkout_session()` with your production domain
3. **Enable HTTPS**: Ensure your application runs over HTTPS
4. **Configure Webhooks**: Set up webhook endpoints in Stripe Dashboard pointing to your production domain
5. **Set Flask Debug**: Set `debug=False` in production

### Deployment Steps

1. Set up a production server (e.g., using Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. Use a reverse proxy (e.g., nginx) for better performance and security

3. Set up environment variables securely using your hosting platform's secrets management

4. Configure HTTPS using Let's Encrypt or your hosting provider's SSL certificate

## Troubleshooting

### "Invalid API Key" Error
- Ensure `STRIPE_SECRET_KEY` is set correctly in `.env`
- Check that you're using the secret key (starts with `sk_`), not the publishable key

### "Webhook signature verification failed"
- Ensure `STRIPE_WEBHOOK_SECRET` is correct
- When testing locally with Stripe CLI, use the signing secret provided by `stripe listen`

### 404 on Webhook Endpoint
- Ensure the webhook URL is publicly accessible
- In Stripe Dashboard, verify the webhook endpoint is configured correctly

## Resources

- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Python SDK](https://github.com/stripe/stripe-python)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Stripe Dashboard](https://dashboard.stripe.com)

## License

MIT
