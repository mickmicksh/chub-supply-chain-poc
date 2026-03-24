# Stripe Checkout Integration

A Python Flask application for accepting payments using Stripe Checkout.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Copy the example file and add your Stripe API keys:

```bash
cp .env.example .env
```

Then edit `.env` with your actual keys:
- **STRIPE_SECRET_KEY**: Found at https://dashboard.stripe.com/apikeys (Secret key)
- **STRIPE_WEBHOOK_SECRET**: Your webhook signing secret from your Stripe dashboard
- **FLASK_SECRET_KEY**: Any secure random string (for session management)

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Testing with Test Cards

Use these test card numbers in the Stripe Checkout form:

| Number | Behavior |
|--------|----------|
| 4242 4242 4242 4242 | Success |
| 4000 0000 0000 0002 | Decline |
| 4000 0025 0000 3155 | 3D Secure required |

Use any future expiration date and any 3-digit CVC.

## Project Structure

```
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies (pinned versions)
├── .env.example          # Example environment variables
└── README.md             # This file
```

## Features

- ✅ Secure checkout session creation
- ✅ Webhook handling for payment confirmation
- ✅ CSRF protection via `stripe-checkout-guard`
- ✅ Error handling for card and request errors
- ✅ Success/cancel pages

## Key Routes

- **GET `/`**: Home page with checkout button
- **POST `/create-checkout-session`**: Creates a Stripe checkout session
- **GET `/success`**: Success page (redirected after payment)
- **GET `/cancel`**: Cancellation page
- **POST `/webhook`**: Webhook endpoint for Stripe events

## Production Considerations

Before deploying to production:

1. Update `FLASK_SECRET_KEY` to a secure random value
2. Change `success_url` and `cancel_url` to your actual domain
3. Update `app.run()` parameters (remove `debug=True`, use a production server like Gunicorn)
4. Implement order fulfillment logic in the webhook handler
5. Use environment-based configuration for all sensitive data
6. Enable HTTPS for all payment routes

## Documentation

See the [Stripe Checkout Documentation](https://stripe.com/docs/checkout) for more details.
