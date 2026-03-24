# Stripe Checkout Integration

A Python Flask application that implements Stripe Checkout for accepting payments.

## Features

- 🛒 Simple checkout flow with Stripe
- ✅ Payment success handling
- ❌ Payment cancellation handling
- 🔔 Webhook support for payment confirmations
- 🔒 CSRF protection with stripe-checkout-guard
- 📝 Signature verification for webhooks

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and add your Stripe API keys:

```bash
cp .env.example .env
```

Then edit `.env` with your Stripe keys from https://dashboard.stripe.com/apikeys

### 3. Run the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

## Testing

### Using Test Cards

Stripe provides test cards for development:

| Card Number | Behavior |
|-------------|----------|
| 4242424242424242 | Successful payment |
| 4000000000000002 | Card declined |
| 4000002500003155 | Requires 3D Secure |

Use any future expiration date and any 3-digit CVC.

### Webhook Testing

For local webhook testing, use [Stripe CLI](https://stripe.com/docs/stripe-cli):

```bash
# Install Stripe CLI and login
stripe listen --forward-to localhost:5000/webhook

# In another terminal, trigger a test event
stripe trigger payment_intent.succeeded
```

## Project Structure

- `app.py` - Main Flask application with Stripe integration
- `requirements.txt` - Python dependencies (pinned versions)
- `.env.example` - Environment variables template
- `CLAUDE.md` - Project guidelines

## API Endpoints

- `GET /` - Home page with checkout button
- `POST /create-checkout-session` - Create Stripe checkout session
- `GET /success` - Success page after payment
- `GET /cancel` - Cancellation page
- `POST /webhook` - Stripe webhook receiver

## Production Deployment

Before deploying to production:

1. ✅ Update `success_url` and `cancel_url` to use your production domain
2. ✅ Use production Stripe API keys
3. ✅ Set `FLASK_ENV=production`
4. ✅ Use a production WSGI server (Gunicorn, uWSGI)
5. ✅ Enable HTTPS
6. ✅ Configure proper database for order storage
7. ✅ Add email confirmation system

## Error Handling

The application includes error handling for:
- Missing API keys
- Invalid webhook signatures
- Card errors
- Session creation failures

## Security

- CSRF protection on payment routes via stripe-checkout-guard
- Webhook signature verification
- Environment variable separation (no hardcoded secrets)

## References

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Checkout](https://stripe.com/docs/payments/checkout)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)
- [Flask Documentation](https://flask.palletsprojects.com/)
