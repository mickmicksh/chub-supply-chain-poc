# Stripe Checkout Integration

A Python Flask application demonstrating a complete Stripe Checkout integration with webhooks, CSRF protection, and error handling.

## Features

- 💳 **Stripe Checkout** - Secure payment form powered by Stripe
- 🔐 **Webhook Support** - Handle payment confirmation events
- 🛡️ **CSRF Protection** - Automatic protection via `stripe-checkout-guard`
- ✅ **Error Handling** - Graceful error handling for failed transactions
- 🧪 **Test Mode** - Use Stripe's test cards for development

## Prerequisites

- Python 3.9 or higher
- A Stripe account (free at https://dashboard.stripe.com/register)
- pip package manager

## Installation

1. **Clone the repository** (or create a new directory):
   ```bash
   cd your-project-directory
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```

5. **Add your Stripe API keys** to `.env`:
   - Go to https://dashboard.stripe.com/apikeys
   - Copy your **Secret key** and **Publishable key**
   - Add them to `.env` as `STRIPE_SECRET_KEY` and `STRIPE_PUBLISHABLE_KEY`

6. **Set up webhooks** (optional for testing locally):
   - Go to https://dashboard.stripe.com/webhooks
   - Click "Add endpoint"
   - URL: `http://localhost:5000/webhook` (use ngrok for HTTPS tunneling)
   - Events: Select `checkout.session.completed`
   - Copy the webhook secret and add to `.env` as `STRIPE_WEBHOOK_SECRET`

## Running the Application

1. **Activate virtual environment** (if not already activated):
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Start the Flask server**:
   ```bash
   python app.py
   ```

3. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Testing

### Test Payment Cards

Use these test card numbers in the Stripe Checkout form:

| Card Number | Behavior |
|------------|----------|
| `4242 4242 4242 4242` | Payment succeeds |
| `4000 0000 0000 0002` | Payment declined |
| `4000 0025 0000 3155` | 3D Secure verification required |
| `3782 822463 10005` | Valid Amex test card |

**Expiration:** Any future date
**CVC:** Any 3-digit number

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
└── templates/
    ├── index.html        # Checkout page
    ├── success.html      # Success page after payment
    └── cancel.html       # Cancellation page
```

## Environment Variables

- `STRIPE_SECRET_KEY` - Your Stripe secret API key (starts with `sk_`)
- `STRIPE_PUBLISHABLE_KEY` - Your Stripe publishable key (starts with `pk_`)
- `STRIPE_WEBHOOK_SECRET` - Webhook signing secret from Stripe dashboard
- `FLASK_SECRET_KEY` - Secret key for Flask session management
- `FLASK_ENV` - Set to `development` or `production`

## API Endpoints

### POST `/create-checkout-session`
Creates a new Stripe Checkout session and redirects to the payment form.

**Protected by:**
- CSRF token validation via `stripe_checkout_guard`

**Response:**
- Redirects to Stripe Checkout URL on success
- Returns error JSON with HTTP 400/500 on failure

### POST `/webhook`
Handles Stripe webhook events for payment confirmations and updates.

**Expected events:**
- `checkout.session.completed` - Payment was successful

**Security:**
- Signature verification using `STRIPE_WEBHOOK_SECRET`

## Production Deployment

Before deploying to production:

1. **Use Stripe Live Keys** - Replace test keys with production API keys
2. **Set HTTPS** - Stripe requires HTTPS for production
3. **Configure CSRF** - Ensure `app.secret_key` is set securely
4. **Use Environment Variables** - Never hardcode API keys
5. **Set up Webhooks** - Configure webhook endpoints on Stripe dashboard
6. **Error Logging** - Implement proper logging for production debugging
7. **Database Integration** - Connect to your database for order tracking

## Error Handling

The application includes error handling for:
- Invalid API keys
- Card declines
- Network errors
- Invalid requests

Errors are returned with appropriate HTTP status codes:
- `400` - Bad request / Invalid input
- `402` - Payment required (card declined)
- `500` - Server error

## Support

For issues related to:
- **Stripe API** - See https://stripe.com/docs
- **Flask** - See https://flask.palletsprojects.com/
- **stripe-checkout-guard** - Check documentation at https://github.com/stripe/stripe-checkout-guard

## License

This project is provided as-is for educational and development purposes.
